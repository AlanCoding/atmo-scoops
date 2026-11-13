"""Two-compartment cycle with optional mouth closure and finite residual recovery.

No rotor geometry/speed, pump type, pump map, inlet CFD or mass closure is
inferred. All prescribed capacities and efficiency targets are serialized.
"""
from dataclasses import dataclass, asdict
import math

import numpy as np
from scipy.integrate import cumulative_trapezoid, quad

from .atmosphere import make_profile
from .orbit import Orbit, R_EARTH
from .encounter import orbit_state, pressure_window
from .thermochemistry import gas, composition, enthalpy
from .process import liquefaction_train, coast_compressor, ProcessTargets
from .open_mouth import recover_open


@dataclass(frozen=True)
class Reference:
    atmosphere_name: str = "reference"
    opening_ram_fraction: float = .5
    perigee_km: float = 100.
    apogee_km: float = 2000.
    total_length_m: float = 295.
    outside_diameter_m: float = 20.
    mouth_m: float = 18.3
    front_bore_m: float = 18.3
    front_length_m: float = 250.
    gas_K: float = 1000.
    inlet_pressure_fraction: float = .7
    suction_capacity_factor: float = 1.  # Explicit control variation, not capture efficiency.
    open_suction_override_m3_s: float | None = None
    recovery_s: float = 450.
    front_residual_fraction: float = .1
    mouth_closure: bool = True
    compressor_min_inlet_Pa: float = .1
    open_mouth_support_over_ram: float = 1.
    open_mouth_discharge_coefficient: float = .8
    intermediate_Pa: float = 300.
    receiver_m3: float = math.pi*18.3**2/4*(25.-18.3/6)
    receiver_K: float = 340.
    isothermal_efficiency: float = .5
    motor_efficiency: float = .95
    deploy_s: float = 300.
    retract_s: float = 300.
    metal_cold_K: float = 500.
    metal_hot_K: float = 900.
    foil_thickness_m: float = .00025
    metal_density_kg_m3: float = 7870.
    hot_emissivity: float = .8
    warm_radiator_K: float = 320.
    solar_W_m2: float = 250.
    solar_W_kg: float = 150.
    warm_buffer_J_kg: float = 200000.
    battery_Wh_kg: float = 150.
    battery_usable: float = .8
    battery_W_kg: float = 1500.
    battery_charge_efficiency: float = .95
    battery_discharge_efficiency: float = .95
    exhaust_m_s: float = 4000.*9.80665
    thruster_efficiency: float = .6
    total_impulse_over_capture: float = 1.  # Capture-only floor; exterior drag unresolved.
    thrust_burst_s: float = 180.
    thruster_loss_retained: float = .2
    auxiliary_W: float = 10000.


def iron_cp(T):
    """NIST alpha/delta Fe Shomate, J/kg/K; proxy, not selected flight alloy."""
    if not 298 <= T <= 1042:raise ValueError('Outside implemented Fe range')
    a,b,c,d,e = ((18.42868,24.64301,-8.913720,9.664706,-.012643) if T<700
                else (-57767.65,137919.7,-122773.2,38682.42,3993.080))
    t=T/1000
    return (a+b*t+c*t*t+d*t**3+e/t**2)/.055845


def front_inventory(time, inflow, suction, volume):
    """Exact interval solution for linearly interpolated inflow and constant S.

    This is the same ODE used by the cycle, avoiding adaptive-solver overhead
    during optimization. Series expansion avoids cancellation for small k*dt.
    """
    dt=np.diff(time);x=suction/volume*dt
    a=np.ones_like(x);nonzero=x!=0
    a[nonzero]=-np.expm1(-x[nonzero])/x[nonzero]
    b=np.empty_like(x);small=np.abs(x)<1e-3
    b[small]=.5-x[small]/6+x[small]**2/24-x[small]**3/120
    b[~small]=(x[~small]+np.expm1(-x[~small]))/x[~small]**2
    forcing=inflow[:-1]*dt*a+np.diff(inflow)*dt*b
    decay=np.exp(-x);m=np.zeros(len(time))
    for i in range(len(dt)):m[i+1]=decay[i]*m[i]+forcing[i]
    return m


def calculate(c=Reference(), n=1601, process_targets=None):
    process_targets=process_targets or ProcessTargets()
    atm=make_profile(c.atmosphere_name);o=Orbit(c.perigee_km,c.apogee_km)
    edge,_=pressure_window(o,atm,c.opening_ram_fraction)
    t=np.linspace(-edge,0,n);s=orbit_state(o,t,atm)
    A=math.pi*c.mouth_m**2/4;V=math.pi*c.front_bore_m**2/4*c.front_length_m
    mdot=A*s['density_kg_m3']*s['speed_m_s']
    collected=cumulative_trapezoid(mdot,t,initial=0)
    f=np.trapezoid(mdot[:,None]*s['fractions'],t,axis=0)/collected[-1]
    oxygen=float(f[1]+f[2]+f[7]+f[8]*15.9994/30.0061)
    # Consistent incoming chemical-energy convention and molecular output.
    hin=np.array([enthalpy(float(T),composition(y))+.5*u*u for T,y,u in
                  zip(s['temperature_K'],s['fractions'],s['speed_m_s'])])
    g=gas();g.TPY=c.gas_K,30.,composition(f);g.equilibrate('TP',rtol=1e-10)
    Y=g.Y.copy();R=float(g.cp_mass-g.cv_mass);gamma_hot=float(g.cp_mass/g.cv_mass)
    hhot=float(g.enthalpy_mass);uhot=float(g.int_energy_mass)
    g.TPY=c.receiver_K,1e5,Y
    hwarm=float(g.enthalpy_mass);uwarm=float(g.int_energy_mass)
    pumping=c.suction_capacity_factor*A*R*c.gas_K/(c.inlet_pressure_fraction*s['speed_m_s'][-1])
    if c.open_suction_override_m3_s is not None:
        pumping=c.open_suction_override_m3_s
    # Constant suction-volume capacity while open; front mass has finite lag.
    front=np.maximum(front_inventory(t,mdot,pumping,V),0)
    rear=np.maximum(collected-front,0)
    tp=np.linspace(0,c.recovery_s,n)
    Sp=V*math.log(1/c.front_residual_fraction)/c.recovery_s
    fp=front[-1]*np.exp(-Sp*tp/V)
    rp=collected[-1]-fp
    leaked=extra_intake=extra_energy=extra_impulse=0.
    post_admission=np.zeros(n);post_leakage=np.zeros(n)
    stop_reason='residual_fraction_target'
    flow_post=Sp*fp/V
    if c.mouth_closure:
        # The configured low-pressure capability also bounds sealed recovery.
        floor_mass=c.compressor_min_inlet_Pa*V/(R*c.gas_K)
        if floor_mass>fp[-1]:
            duration=max(0.,V/Sp*math.log(front[-1]/floor_mass))
            tp=np.linspace(0,duration,n)
            fp=front[-1]*np.exp(-Sp*tp/V);rp=collected[-1]-fp
            flow_post=Sp*fp/V if duration>0 else np.zeros(n)
            stop_reason='inlet_pressure_floor'
    else:
        # Keep the same collection pump running on the outbound leg. The
        # pressure floor stops it; recovery_s is a maximum permitted run time.
        outbound=orbit_state(o,tp,atm)
        extra_h=np.array([enthalpy(float(T),composition(y))+.5*u*u for T,y,u in
            zip(outbound['temperature_K'],outbound['fractions'],outbound['speed_m_s'])])
        post=recover_open(tp,A*outbound['density_kg_m3']*outbound['speed_m_s'],
            c.open_mouth_support_over_ram*outbound['ram_Pa'],extra_h,outbound['speed_m_s'],
            front[-1],rear[-1],pumping,V,A,R,c.gas_K,gamma_hot,
            c.open_mouth_discharge_coefficient,c.compressor_min_inlet_Pa,
            outbound['fractions'][:,1]+outbound['fractions'][:,2]+outbound['fractions'][:,7]+
            outbound['fractions'][:,8]*15.9994/30.0061,oxygen)
        tp=post['time'];fp=post['front'];rp=post['rear'];flow_post=post['pump_rate']
        post_admission=post['admission_rate'];post_leakage=post['leakage_rate']
        extra_intake=float(post['admitted'][-1]);leaked=float(post['leaked'][-1])
        extra_energy=float(post['incoming_energy'][-1]);extra_impulse=float(post['impulse'][-1])
        stop_reason=post['stop_reason'];Sp=pumping
    # Retain both sides of the phase boundary (same time, different flow).
    time=np.r_[t,tp]
    front_all=np.r_[front,fp];rear_all=np.r_[rear,rp]
    pfront=front_all*R*c.gas_K/V
    prear=rear_all*R*c.receiver_K/c.receiver_m3
    flow_open=pumping*front/V
    # Separate phase integrals preserve the switch in pumping speed at closure.
    def duties(mf,mr,flow):
        p=mf*R*c.gas_K/V;q=mr*R*c.receiver_K/c.receiver_m3
        hot=flow*R*c.gas_K/c.isothermal_efficiency*np.log(c.intermediate_Pa/np.maximum(p,1e-30))
        hot=np.where(flow>0,np.maximum(0,hot),0.)
        warm=flow*R*c.receiver_K/c.isothermal_efficiency*np.log(np.maximum(q/c.intermediate_Pa,1))
        return hot,warm,(hot+warm)/c.motor_efficiency
    ho,wo,eo=duties(front,rear,flow_open)
    hp,wp,ep=duties(fp,rp,flow_post)
    int2=lambda a,b:float(np.trapezoid(a,t)+np.trapezoid(b,tp))
    Ehot=int2(ho,hp);Ewarm=int2(wo,wp);Ecomp=int2(eo,ep)
    stored=float(rp[-1]);residual=float(fp[-1]);vent=residual+leaked
    input_energy=float(np.trapezoid(mdot*hin,t))+extra_energy
    # Hot duty includes intake cooling and compressor intercooling. Post-pump
    # gas held at the prescribed inlet temperature is a work rating. Expansion
    # needs a small heat input; record recirculation from the compressor's hot
    # rejection explicitly. Real gas cools without it, reducing work demand.
    first_hot=float(np.trapezoid(mdot*hin,t))-float(rear[-1])*hhot-float(front[-1])*uhot
    pumpdown_isothermal_heat=(front[-1]-fp[-1])*R*c.gas_K
    Qhot=input_energy+Ehot-(stored+leaked)*hhot-residual*uhot
    Qwarm=stored*(hhot-uwarm)+Ewarm+(Ecomp-Ehot-Ewarm)
    capacity=quad(iron_cp,c.metal_cold_K,c.metal_hot_K,points=[700])[0]
    metal_mass=Qhot/capacity
    physical_area=metal_mass/(c.metal_density_kg_m3*c.foil_thickness_m)
    cooltime=metal_mass/(2*physical_area)*quad(lambda T:iron_cp(T)/
                (c.hot_emissivity*5.670374419e-8*T**4-80),c.metal_cold_K,c.metal_hot_K,points=[700])[0]
    safe=o.time_at_altitude(200)
    start=max(float(tp[-1]),safe)+c.deploy_s;end=o.period-safe-c.retract_s
    coast=end-start
    if coast<=0:raise ValueError('Deployment/recovery leaves no coast processing interval')
    tg,dt,rg,angle,_,_=o.eccentric_grid(40000)
    active=(tg>=start)&(tg<=end)
    shadow=(rg*np.cos(angle)<0)&(np.abs(rg*np.sin(angle))<R_EARTH)
    sunlight=float(dt[active & ~shadow].sum());night=max(0,coast-sunlight)
    if sunlight<=0:raise ValueError('No deployed sunlight in the modeled orbit orientation')
    plant=liquefaction_train(stored/coast,radiator_K=c.warm_radiator_K,targets=process_targets)
    feed=coast_compressor(stored,c.receiver_m3,c.receiver_K,coast,gas_R=R,
                         output_Pa=1e5,residual_fraction=.001,efficiency=.5)
    # The installed compressor mass is assigned by the system hardware model.
    feed={k:v for k,v in feed.items() if k!='hardware_mass_kg'}
    Ef=feed['electricity_J']
    # Explicit cleanup/separation work allowance, separate from N2-equivalent cold duty.
    g.TPY=c.receiver_K,1e5,Y
    x=g.X[g.X>0]
    Esep=stored*(R*c.receiver_K*(-float(np.sum(x*np.log(x))))/.2+50000.)
    Ecryo=plant['electricity_W']*coast
    Eaux=c.auxiliary_W*o.period
    Jcap=float(np.trapezoid(mdot*s['speed_m_s'],t))+extra_impulse
    if not c.mouth_closure:oxygen=post['retained_oxygen']/stored
    warmflux=process_targets.emissivity*process_targets.view_factor*5.670374419e-8*c.warm_radiator_K**4-process_targets.environment_W_m2
    budgets=[]
    for multiplier in sorted(set((0.,1.,2.,c.total_impulse_over_capture,3.))):
        J=multiplier*Jcap;prop=J/c.exhaust_m_s
        Eprop=J*c.exhaust_m_s/(2*c.thruster_efficiency)
        Pprop=Eprop/c.thrust_burst_s
        retained_heat=Eprop*(1-c.thruster_efficiency)*c.thruster_loss_retained
        Eload=Ecomp+Ecryo+Ef+Esep+Eaux+Eprop
        Esun=Eload/(c.battery_charge_efficiency*c.battery_discharge_efficiency)
        Parray=Esun/sunlight
        # Conservative all-load battery-throughput allowance. Energy capacity
        # covers stowed demand + deployed eclipse demand, not whole-orbit load.
        Pdcoast=plant['electricity_W']+(Ef+Esep)/coast+c.auxiliary_W
        stowedE=Ecomp+Eprop+c.auxiliary_W*(o.period-coast)
        Ecapacity=(stowedE+Pdcoast*night)/c.battery_discharge_efficiency
        battery_energy_mass=Ecapacity/(3600*c.battery_Wh_kg*c.battery_usable)
        battery_power_mass=(Pprop+max(eo.max(),ep.max())+c.auxiliary_W)/c.battery_W_kg
        battery_mass=max(battery_energy_mass,battery_power_mass)
        discharge_heat=Eload*(1/c.battery_discharge_efficiency-1)
        charge_heat=Eload/c.battery_discharge_efficiency*(1/c.battery_charge_efficiency-1)
        bufferE=(Qwarm+retained_heat+stowedE*(1/c.battery_discharge_efficiency-1)
                 +c.auxiliary_W*(o.period-coast))
        warmE=(Qwarm+retained_heat+discharge_heat+charge_heat+
               plant['radiator_heat_W']*coast+Ef+Esep+Eaux)
        radarea=warmE/coast/warmflux
        pieces=dict(hot_metal=metal_mass,
            shell_TPS_allowance=math.pi*c.outside_diameter_m*c.total_length_m*4,
            solar=Parray/c.solar_W_kg,battery=battery_mass,
            warm_radiator=radarea*process_targets.radiator_kg_m2,warm_buffer=bufferE/c.warm_buffer_J_kg,
            refrigerator=plant['mass_breakdown_kg']['refrigeration_package'])
        budgets.append(dict(total_impulse_over_capture=multiplier,oxygen_propellant_kg=prop,
            required_propellant_kg=prop,oxygen_only_sustainable=bool(prop<=stored*oxygen),
            all_captured_gas_mass_sufficient=bool(prop<stored),
            oxygen_available_kg=stored*oxygen,oxygen_balance_kg=stored*oxygen-prop,
            retained_after_reboost_kg=stored-prop,
            propulsion_electric_J=Eprop,impulse_equivalent_burst_W=Pprop,
            total_load_energy_J=Eload,solar_bus_W=Parray,solar_area_m2=Parray/c.solar_W_m2,
            battery_required_cell_discharge_J=Ecapacity,battery_energy_mass_kg=battery_energy_mass,
            battery_power_mass_kg=battery_power_mass,battery_mass_kg=battery_mass,
            warm_radiator_heat_W=warmE/coast,warm_radiator_emitting_m2=radarea,
            warm_buffer_energy_J=bufferE,warm_buffer_mass_kg=bufferE/c.warm_buffer_J_kg,
            assigned_masses_kg=pieces,assigned_mass_subtotal_kg=sum(pieces.values())))
    history=dict(time_s=time.tolist(),front_pressure_Pa=pfront.tolist(),rear_pressure_Pa=prear.tolist(),
        front_mass_kg=front_all.tolist(),rear_mass_kg=rear_all.tolist(),
        pump_mass_flow_kg_s=np.r_[flow_open,flow_post].tolist(),
        hot_pump_electric_W=(np.r_[ho,hp]/c.motor_efficiency).tolist(),
        pump_electric_W=np.r_[eo,ep].tolist(),
        intake_mass_flow_kg_s=np.r_[mdot,post_admission].tolist(),
        leakage_mass_flow_kg_s=np.r_[np.zeros(n),post_leakage].tolist())
    phases=[]
    for seconds in np.linspace(0,tp[-1],4):
        rem=float(np.interp(seconds,tp,fp))
        phases.append(dict(seconds_after_perigee=float(seconds),front_mass_kg=rem,
                           front_pressure_Pa=rem*R*c.gas_K/V))
    closure_energy_residual=input_energy+Ecomp-(Qhot+Qwarm+stored*uwarm+residual*uhot+leaked*hhot)
    tank_radius=(3*c.receiver_m3/(4*math.pi))**(1/3)
    tank_gauge=max(.0006,1e5*tank_radius/(2*150e6))
    return dict(status='Two-compartment requirement reference; prescribed capture and pump capacity, no selected pump or mass-closed spacecraft',
        inputs=asdict(c),orbit_period_s=o.period,collection_s=edge,front_volume_m3=V,
        mouth_area_m2=A,gas_R_J_kg_K=R,gamma_hot=gamma_hot,capture_impulse_Ns=Jcap,
        collection_time_s=t.tolist(),intake_mass_flow_kg_s=mdot.tolist(),ram_pressure_Pa=s['ram_Pa'].tolist(),
        coast_start_s=start,coast_end_s=end,deployed_coast_s=coast,sunlight_deployed_s=sunlight,
        captured_kg=float(collected[-1])+extra_intake,front_at_closure_kg=float(front[-1]),
        inbound_admitted_kg=float(collected[-1]),outbound_admitted_kg=extra_intake,
        mouth_leakage_kg=leaked,final_front_vent_kg=residual,
        actual_recovery_s=float(tp[-1]),pump_stop_reason=stop_reason,
        transferred_before_closure_kg=float(rear[-1]),recovered_after_closure_kg=stored-float(rear[-1]),
        retained_kg=stored,vented_front_kg=vent,
        open_suction_m3_s=pumping,closed_suction_m3_s=Sp,
        peak_intake_kg_s=float(mdot.max()),peak_transfer_kg_s=float(flow_open.max()),
        max_front_over_ram=float(max(front*R*c.gas_K/V/s['ram_Pa'])),
        closure_front_Pa=float(front[-1]*R*c.gas_K/V),final_front_Pa=float(pfront[-1]),
        final_receiver_Pa=float(prear[-1]),receiver_equivalent_sphere_diameter_m=(6*c.receiver_m3/math.pi)**(1/3),
        tank_wall_only_kg_at_1bar_150MPa_allowable=4*math.pi*tank_radius**2*tank_gauge*2700,
        tank_wall_gauge_m=tank_gauge,
        compression_electric_J=Ecomp,compression_peak_open_W=float(eo.max()),
        compression_peak_closed_W=float(ep.max()),compression_end_W=float(ep[-1]),
        hot_compression_J=Ehot,warm_compression_J=Ewarm,
        intake_and_front_storage_heat_J=first_hot,
        hot_store_J=Qhot,warm_store_capture_J=Qwarm,
        post_isothermal_heat_input_J=float(pumpdown_isothermal_heat),
        through_recovery_energy_residual_J=float(closure_energy_residual),
        metal_capacity_J_kg=capacity,metal_mass_kg=metal_mass,metal_physical_area_m2=physical_area,
        metal_two_face_emitting_m2=2*physical_area,ideal_metal_radiation_cooling_s=cooltime,
        inlet_heat_peak_scale_W=float(np.max(mdot*(hin-hhot))),
        intake_heat_per_exposed_m2_W=float(np.max(mdot*(hin-hhot))/(2*physical_area)),
        liquefaction=plant,coast_feed_compressor=feed,separation_energy_J=Esep,
        first_cycle_liquid_before_propellant_kg=stored*.999,
        first_cycle_liquid_volume_m3=stored*.999/900.,budgets=budgets,pumpdown_samples=phases,
        history=history,
        exclusions=['Achieved inlet capture, heat exchanger conductance and pressure loss',
            'Pump maps, module count, rotor speeds, mechanisms, mass and spin-up',
            'Actual hull drag, closed-door pressure drag and finite-thrust orbital replay',
            'Gas-solid coupled recovery temperature; inlet temperature is prescribed',
            'Metal/alloy compatibility, coatings, deployment mechanics, contacts and fatigue',
            'Tanks, compressors, thrusters, supports, actuators and margin missing from mass subtotal',
            'Species-resolved liquefaction and tank heat leaks; nitrogen-equivalent duty only',
            'Circularization, transfer/export hardware and delivered-mass payoff'])


