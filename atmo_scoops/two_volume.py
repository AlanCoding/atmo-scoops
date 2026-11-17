"""Open-inlet two-compartment cycle with continuous admission and finite recovery.

No rotor geometry/speed, pump type, pump map, inlet CFD or mass closure is
inferred. All prescribed capacities and efficiency targets are serialized.
"""
from dataclasses import dataclass, asdict, replace
import math

import numpy as np
from scipy.integrate import cumulative_trapezoid, quad

from .atmosphere import make_profile
from .orbit import Orbit, R_EARTH
from .encounter import orbit_state, pressure_window
from .thermochemistry import gas, composition, enthalpy
from .process import liquefaction_train, coast_compressor, ProcessTargets
from .inlet import ContinuousEncounter
from .mixing import Mixing, endpoint
from .compressor import RealAir, evaluate_train_history


@dataclass(frozen=True)
class Reference:
    atmosphere_name: str = "reference"
    allow_nitrogen_propellant: bool = False
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


def calculate(c=Reference(), n=1601, process_targets=None, flow_solver=None, mixing=Mixing(), compressor=None, racks=None,ammonia=None):
    process_targets=process_targets or ProcessTargets()
    atm=make_profile(c.atmosphere_name);o=Orbit(c.perigee_km,c.apogee_km)
    edge,_=pressure_window(o,atm,.5)
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
    dry_Y=g.Y.copy();dry_K=c.gas_K
    mixed_K,Y,coolant_enthalpy,injection_work=endpoint(g,dry_Y,dry_K,mixing)
    if mixed_K<=c.receiver_K:raise ValueError('Mixed gas must remain above warm receiver temperature')
    c=replace(c,gas_K=mixed_K)
    g.TPY=c.gas_K,30.,Y
    R=float(g.cp_mass-g.cv_mass);gamma_hot=float(g.cp_mass/g.cv_mass)
    hhot=float(g.enthalpy_mass);uhot=float(g.int_energy_mass)
    g.TPY=c.receiver_K,1e5,Y
    hwarm=float(g.enthalpy_mass);uwarm=float(g.int_energy_mass)
    pumping=c.suction_capacity_factor*(1+mixing.ratio)*A*R*c.gas_K/(c.inlet_pressure_fraction*s['speed_m_s'][-1])
    if c.open_suction_override_m3_s is not None:
        pumping=c.open_suction_override_m3_s
    flow_solver=flow_solver or ContinuousEncounter()
    real_compressor=compressor is not None and compressor.mode=='real_gas'
    if real_compressor:
        compressor.validate()
        flow_solver.compressor_spec=compressor
        thermo=RealAir(g,Y)
    rack_context=None
    if racks and racks.enabled:
        if not real_compressor:raise ValueError('Finite racks require real-gas compressors')
        from .racks import Metal,geometry
        racks.validate(compressor.blocks)
        from .pcm import Cell
        stage_specs=[racks.for_stage(i) for i in range(compressor.blocks)]
        metals=[Metal(c.metal_cold_K) if rs.pcm_material=='none' else Cell(c.metal_cold_K,rs,c.metal_density_kg_m3) for rs in stage_specs]
        metal=metals[0]
        capacities=[m.enthalpy(min(c.metal_hot_K,m.pcm.max_core_K) if isinstance(m,Cell) else c.metal_hot_K)-m.hcold for m in metals]
        capacity=capacities[0]
        grid=np.linspace(-o.time_at_altitude(200),o.time_at_altitude(200),max(n,401))
        supply=orbit_state(o,grid,atm)
        intercepted=float(np.trapezoid(A*supply['density_kg_m3']*supply['speed_m_s'],grid))
        # Explicit capacity-based sizing rule; individual masses can override it.
        first=intercepted*max(hin[-1]-hhot,1.)/capacity
        pressure=max(1.,intercepted*R*c.receiver_K/c.receiver_m3)
        pfirst=max(1.,c.inlet_pressure_fraction*s['ram_Pa'][-1])
        ratio=max(1.,pressure/pfirst)**(1/compressor.blocks)
        stage_work=1200*c.gas_K*(ratio**.2857-1)/compressor.isentropic_efficiency
        later=intercepted*max(stage_work,1e5)/capacity
        masses=list(racks.masses_kg) if racks.masses_kg else [first*racks.mass_factors[0]]+[later*x*capacity/capacities[i+1] for i,x in enumerate(racks.mass_factors[1:])]
        geoms=[geometry(m,c.metal_density_kg_m3,math.pi*c.front_bore_m**2/4,rs) for m,rs in zip(masses,stage_specs)]
        if ammonia and ammonia.enabled:
            from .ammonia import Bank,geometry as liquid_geometry
            geoms=liquid_geometry(ammonia,math.pi*c.front_bore_m**2/4)
            metals=[Bank(ammonia.cold_K) for _ in geoms];metal=metals[0]
            capacities=[g['liquid']['delta_h'] for g in geoms]
        c=replace(c,front_length_m=max(c.front_length_m,geoms[0]['depth_m']))
        V=math.pi*c.front_bore_m**2/4*c.front_length_m
        # Molecular gas is allowed to become hot in a rejected trial. RealAir
        # rejects compressor operating states outside its documented domain.
        temperatures=np.linspace(200.,10000.,4001);hs=[];us=[];cps=[]
        for temp in temperatures:
            g.TPY=temp,30.,Y;hs.append(g.enthalpy_mass);us.append(g.int_energy_mass);cps.append(g.cp_mass)
        rack_context=dict(spec=racks,metal=metal,metals=metals,stage_specs=stage_specs,geometries=geoms,geometry=geoms[0],
            T=temperatures,h=np.array(hs),u=np.array(us),cp=np.array(cps))
        flow_solver.rack_context=rack_context
    flow_solver.injection_ratio=mixing.ratio
    flow_solver.injection_h=coolant_enthalpy+injection_work
    solved=flow_solver(c,o,atm,R,gamma_hot,pumping,n)
    a=solved['pre'];b=solved['post']
    t=a['time'];front=a['front'];rear=a['rear'];mdot=a['admission_rate'];hin=a['incoming_h']
    collected=a['admitted'];s=orbit_state(o,t,atm);edge=-float(t[0])
    tp=b['time'];fp=b['front'];rp=b['rear'];flow_post=b['pump_rate']
    post_admission=b['admission_rate'];post_leakage=b['leakage_rate']
    pumping=solved['rated_suction'];Sp=pumping
    leaked=solved['total_leak'];extra_intake=float(b['admitted'][-1]-b['admitted'][0])
    extra_energy=float(b['energy'][-1]-b['energy'][0])
    extra_impulse=float(b['impulse'][-1]-b['impulse'][0]);stop_reason=solved['stop_reason']
    # Retain both sides of the phase boundary (same time, different flow).
    time=np.r_[t,tp]
    front_all=np.r_[front,fp];rear_all=np.r_[rear,rp]
    pfront=front_all*R*c.gas_K/V
    gas_temperatures=np.full_like(time,c.gas_K)
    if rack_context:
        V=solved['thermal']['front_gas_m3']
        gas_temperatures=np.r_[a['gas_temperature'],b['gas_temperature']]
        pfront=np.r_[a['pressure'],b['pressure']]
    prear=rear_all*R*c.receiver_K/c.receiver_m3
    flow_open=solved['pre']['pump_rate']
    # Integrate inbound and outbound energy over their actual sampled histories.
    def duties(mf,mr,flow):
        p=mf*R*c.gas_K/V;q=mr*R*c.receiver_K/c.receiver_m3
        hot=flow*R*c.gas_K/c.isothermal_efficiency*np.log(c.intermediate_Pa/np.maximum(p,1e-30))
        hot=np.where(flow>0,np.maximum(0,hot),0.)
        warm=flow*R*c.receiver_K/c.isothermal_efficiency*np.log(np.maximum(q/c.intermediate_Pa,1))
        return hot,warm,(hot+warm)/c.motor_efficiency
    ho,wo,eo=duties(front,rear,flow_open)
    hp,wp,ep=duties(fp,rp,flow_post)
    ho+=solved['pre']['extra_hot_work'];hp+=solved['post']['extra_hot_work']
    eo=(ho+wo)/c.motor_efficiency+solved['pre']['idle_electric']
    ep=(hp+wp)/c.motor_efficiency+solved['post']['idle_electric']
    int2=lambda a,b:float(np.trapezoid(a,t)+np.trapezoid(b,tp))
    Ehot=int2(ho,hp);Ewarm=int2(wo,wp);Ecomp=int2(eo,ep)
    compressor_analysis=None
    spin_peak=0.
    if real_compressor:
        dive=evaluate_train_history(thermo,compressor,pfront,gas_temperatures,prear,
            np.r_[flow_open,flow_post],time,compressor.blocks,compressor.interstage_K,
            c.motor_efficiency,ultimate=np.r_[a['pump_floor'],b['pump_floor']],
            rated_suction=solved['rated_suction'],idle_fraction=flow_solver.capabilities.pump_idle_fraction,
            rack_context=rack_context)
        split=len(t)
        eo=dive['electric_W'][:split];ep=dive['electric_W'][split:]
        ho=dive['bank_power_W'][:split,0]*c.motor_efficiency
        hp=dive['bank_power_W'][split:,0]*c.motor_efficiency
        wo=dive['bank_power_W'][:split,1:].sum(axis=1)*c.motor_efficiency
        wp=dive['bank_power_W'][split:,1:].sum(axis=1)*c.motor_efficiency
        Ehot=int2(ho,hp);Ewarm=int2(wo,wp);Ecomp=int2(eo,ep)
        compressor_analysis=dict(dive={k:v for k,v in dive.items() if k not in ('electric_W','bank_power_W')})
        spin_peak=dive['spinup_peak_electric_W']
    injected=mixing.ratio*float(solved['pre']['admitted'][-1]+solved['post']['admitted'][-1]-solved['post']['admitted'][0])
    Einject=injected*injection_work
    injection_peak_W=mixing.ratio*max(float(mdot.max()),float(post_admission.max()))*injection_work
    stored=float(rp[-1]);residual=float(fp[-1]);vent=residual+leaked
    buffer_loss=0.;buffer_fraction=0.
    if rack_context:
        inventories=np.array(dive['interstage_inventory_kg'])
        # Small-holdup asymptotic model: stage pores retain gas at their local
        # pressure and temperature, then are vented before rack deployment.
        # Do not count that inventory as delivered to the rear tank.
        buffer_loss=float(inventories[-1])
        buffer_fraction=float(np.max(inventories))/max(stored,1e-30)
        if buffer_loss>=stored:raise ValueError('Interstage inventory exceeds collected batch')
        stored-=buffer_loss;vent+=buffer_loss
        rear_all=np.maximum(0.,rear_all-inventories)
        prear=rear_all*R*c.receiver_K/c.receiver_m3
    input_energy=solved['total_energy']+(solved['thermal']['initial_energy_J'] if rack_context else 0.)
    # Isothermal front inventory is a lumped requirement. Its net enthalpy and
    # internal-energy balance determines entry heat assigned to the rack.
    first_hot=float(solved['pre']['energy'][-1])-(float(rear[-1])+float(solved['pre']['leakage'][-1]))*hhot-float(front[-1])*uhot
    pumpdown_isothermal_heat=(front[-1]-fp[-1])*R*c.gas_K
    # The mixer may make gas colder than the hot rack. Route all compressor
    # heat to the warm loop in every case, including the unmixed control.
    Qhot=input_energy-(stored+leaked)*hhot-residual*uhot
    Qwarm=stored*(hhot-uwarm)+Ecomp
    rack_report=None
    if rack_context:
        front_heat=solved['thermal']['absorbed_J']
        stage_heats=dive['rack_heat_J']
        Qhot=front_heat+sum(stage_heats)
        leak_enthalpy=np.interp(gas_temperatures,rack_context['T'],rack_context['h'])
        leaked_energy=solved['thermal']['leaked_enthalpy_J']
        residual_energy=solved['thermal']['final_gas_energy_J']
        # Reference offsets differ between HEOS and Cantera; shift interstage
        # internal energy to the Cantera molecular reference before balancing.
        reference_offset=hwarm-thermo.state(1e5,c.receiver_K)['h_J_kg']
        buffer_energy=dive['interstage_energy_J'][-1]+buffer_loss*reference_offset
        Qwarm=solved['thermal']['pumped_enthalpy_J']+Ecomp-sum(stage_heats)-stored*uwarm-buffer_energy
        first_hot=front_heat
        from .racks import conductance
        peak_index=int(np.argmax(np.r_[mdot,post_admission]))
        solid_temperatures=np.r_[a['metal_temperature'],b['metal_temperature']]
        cp_peak=float(np.interp(gas_temperatures[peak_index],rack_context['T'],rack_context['cp']))
        front_UA,front_details=conductance(pfront[peak_index],(gas_temperatures[peak_index]+solid_temperatures[peak_index])/2,
            max(np.r_[mdot,post_admission][peak_index]*(1+mixing.ratio),np.r_[flow_open,flow_post][peak_index]),
            A,rack_context['geometries'][0],racks,R,cp_peak)
        front_details.update(UA_W_K=front_UA,gas_K=float(gas_temperatures[peak_index]),metal_K=float(solid_temperatures[peak_index]),pressure_Pa=float(pfront[peak_index]))
        rack_report=[]
        for i,geom in enumerate(rack_context['geometries']):
            heat=front_heat if i==0 else stage_heats[i]
            material=rack_context['metals'][i];total_h=material.hcold+heat/geom['mass_kg']
            extra={}
            if hasattr(material,'liquid'):
                hot=material.cold;peak=hot
                if i==0:
                    extra={k:v for k,v in solved['thermal'].items() if k.startswith('liquid_')}
                else:
                    peaks=dive['liquid_max'][i]
                    extra=dict(liquid_used_kg=dive['liquid_used_kg'][i],liquid_pump_J=dive['liquid_pump_J'][i],
                        liquid_peak_flow_kg_s=peaks[0],liquid_peak_pump_W=peaks[1],liquid_max_wall_K=peaks[2],liquid_max_dp_Pa=peaks[3])
                peak=extra['liquid_max_wall_K']
                extra.update(cooldown_s=0.,sizing_capacity_J_kg=capacities[i])
            elif isinstance(material,Cell):
                core_h=solved['thermal']['final_core_h_J_kg'] if i==0 else dive['rack_core_h_J_kg'][i]
                hot=material.surface_temperature(total_h,core_h)
                peak=solved['thermal']['max_metal_K'] if i==0 else max(hot,dive['rack_max_metal_K'][i])
                core_peak=solved['thermal']['max_core_K'] if i==0 else dive['rack_max_core_K'][i]
                melt_peak=solved['thermal']['max_melt_fraction'] if i==0 else dive['rack_max_melt_fraction'][i]
                cooling=material.cooldown_state(total_h,core_h,geom,c.hot_emissivity,racks)
                extra=dict(core_final_K=material.pcm.temperature(core_h),core_max_K=core_peak,
                    core_final_h_J_kg=core_h,core_max_allowed_K=material.pcm.max_core_K,
                    melt_fraction_final=material.pcm.melt_fraction(core_h),melt_fraction_max=melt_peak,
                    latent_energy_final_J=geom['pcm_kg']*material.pcm.latent_J_kg*material.pcm.melt_fraction(core_h),
                    sizing_capacity_J_kg=capacities[i],**cooling)
            else:
                hot=material.temperature(total_h)
                peak=solved['thermal']['max_metal_K'] if i==0 else max(hot,dive['rack_max_metal_K'][i])
                extra=dict(cooldown_s=material.cooldown(hot,geom,c.hot_emissivity,racks),sizing_capacity_J_kg=capacities[i])
            rack_report.append(dict(**geom,absorbed_J=heat,final_metal_K=hot,max_metal_K=peak,
                convection_at_peak_flow=front_details if i==0 else dive['rack_peak_flow_details'][i],**extra))
    capacity=quad(iron_cp,c.metal_cold_K,c.metal_hot_K,points=[700])[0]
    if Qhot<=0:raise ValueError('Injection exceeds the positive rack heat requirement')
    metal_mass=Qhot/capacity
    physical_area=metal_mass/(c.metal_density_kg_m3*c.foil_thickness_m)
    cooltime=metal_mass/(2*physical_area)*quad(lambda T:iron_cp(T)/
                (c.hot_emissivity*5.670374419e-8*T**4-80),c.metal_cold_K,c.metal_hot_K,points=[700])[0]
    if rack_context:
        metal_mass=sum(x['mass_kg'] for x in rack_report)
        physical_area=sum(x['deployed_physical_m2'] for x in rack_report)
        cooltime=max(x['cooldown_s'] for x in rack_report)
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
    if real_compressor:
        ct=np.linspace(0.,coast,401)
        remaining=stored*np.exp(-math.log(1000.)*ct/coast)
        rate=remaining*math.log(1000.)/coast
        cp=remaining*R*c.receiver_K/c.receiver_m3
        coast_train=evaluate_train_history(thermo,compressor,cp,c.receiver_K,np.full_like(ct,1e5),
            rate,ct,compressor.coast_blocks,c.receiver_K,c.motor_efficiency)
        # Same exponential evacuation schedule; evaluate real-gas stage work
        # instead of the former constant-temperature logarithmic work formula.
        feed['electricity_J']=coast_train['electricity_J']
        feed['rejected_heat_J']=coast_train['electricity_J']
        feed['peak_power_W']=max(float(coast_train['electric_W'].max()),coast_train['spinup_peak_electric_W'])
        feed['mean_power_W']=feed['electricity_J']/coast
        feed['compression_method']='HEOS isentropic endpoints with efficiency and interstage cooling'
        compressor_analysis['coast']={k:v for k,v in coast_train.items() if k not in ('electric_W','bank_power_W')}
    Ef=feed['electricity_J']
    # Explicit cleanup/separation work allowance, separate from N2-equivalent cold duty.
    g.TPY=c.receiver_K,1e5,Y
    x=g.X[g.X>0]
    Esep=stored*(R*c.receiver_K*(-float(np.sum(x*np.log(x))))/.2+50000.)
    Ecryo=plant['electricity_W']*coast
    Eaux=c.auxiliary_W*o.period
    Jcap=solved['capture_impulse'];Jescape=solved['escape_impulse']
    Jmouth=solved['uncollected_mouth_impulse']
    oxygen=solved['retained_oxygen']/(stored+buffer_loss)
    warmflux=process_targets.emissivity*process_targets.view_factor*5.670374419e-8*c.warm_radiator_K**4-process_targets.environment_W_m2
    budgets=[]
    for multiplier in sorted(set((0.,1.,2.,c.total_impulse_over_capture,3.))):
        J=multiplier*Jcap+Jescape+Jmouth;prop=J/c.exhaust_m_s
        Eprop=J*c.exhaust_m_s/(2*c.thruster_efficiency)
        Pprop=Eprop/c.thrust_burst_s
        retained_heat=Eprop*(1-c.thruster_efficiency)*c.thruster_loss_retained
        Eload=Ecomp+Einject+Ecryo+Ef+Esep+Eaux+Eprop
        Esun=Eload/(c.battery_charge_efficiency*c.battery_discharge_efficiency)
        Parray=Esun/sunlight
        # Conservative all-load battery-throughput allowance. Energy capacity
        # covers stowed demand + deployed eclipse demand, not whole-orbit load.
        Pdcoast=plant['electricity_W']+(Ef+Esep)/coast+c.auxiliary_W
        stowedE=Ecomp+Einject+Eprop+c.auxiliary_W*(o.period-coast)
        Ecapacity=(stowedE+Pdcoast*night)/c.battery_discharge_efficiency
        battery_energy_mass=Ecapacity/(3600*c.battery_Wh_kg*c.battery_usable)
        battery_power_mass=(Pprop+max(eo.max(),ep.max(),spin_peak)+injection_peak_W+c.auxiliary_W)/c.battery_W_kg
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
        if mixing.ratio>0:
            pieces['coolant_storage']=injected*mixing.storage_kg_per_kg_inventory
            pieces['coolant_injection']=mixing.injector_fixed_kg+mixing.injector_kg_per_kg_s*mixing.ratio*max(float(mdot.max()),float(post_admission.max()))+injection_peak_W/mixing.pump_W_kg
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
        leakage_mass_flow_kg_s=np.r_[solved['pre']['leakage_rate'],post_leakage].tolist())
    phases=[]
    for seconds in np.linspace(0,tp[-1],4):
        rem=float(np.interp(seconds,tp,fp))
        phases.append(dict(seconds_after_perigee=float(seconds),front_mass_kg=rem,
                           front_pressure_Pa=rem*R*c.gas_K/V))
    energy_residual=input_energy+Ecomp-(Qhot+Qwarm+stored*uwarm+residual*uhot+leaked*hhot)
    if rack_context:
        energy_residual=input_energy+Ecomp-(Qhot+Qwarm+stored*uwarm+residual_energy+leaked_energy+buffer_energy)
    tank_radius=(3*c.receiver_m3/(4*math.pi))**(1/3)
    tank_gauge=max(.0006,1e5*tank_radius/(2*150e6))
    return dict(status='Two-compartment requirement reference; conditional continuous intake and pump capability, no selected pump or mass-closed spacecraft',
        inputs=asdict(c),orbit_period_s=o.period,collection_s=edge,front_volume_m3=V,
        mouth_area_m2=A,gas_R_J_kg_K=R,gamma_hot=gamma_hot,capture_impulse_Ns=Jcap,escape_impulse_Ns=Jescape,
        initial_gas_seed_kg=1e-9 if rack_context else 0.,interstage_vent_kg=buffer_loss,interstage_max_batch_fraction=buffer_fraction,
        compressor_analysis=compressor_analysis,racks=rack_report,gas_temperature_K=gas_temperatures.tolist(),
        max_pumping_temperature_K=float(np.max(gas_temperatures[np.r_[flow_open,flow_post]>max(np.r_[flow_open,flow_post])*1e-6])) if rack_context else c.gas_K,
        warm_aftercooler_peak_W=(float(max(np.max(flow_open*(hhot-hwarm)+(eo if real_compressor else wo+eo-(ho+wo))),
            np.max(flow_post*(hhot-hwarm)+(ep if real_compressor else wp+ep-(hp+wp)))))),
        collection_time_s=t.tolist(),intake_mass_flow_kg_s=mdot.tolist(),ram_pressure_Pa=s['ram_Pa'].tolist(),
        coast_start_s=start,coast_end_s=end,deployed_coast_s=coast,sunlight_deployed_s=sunlight,
        captured_kg=float(collected[-1])+extra_intake,front_at_perigee_kg=float(front[-1]),
        inbound_admitted_kg=float(collected[-1]),outbound_admitted_kg=extra_intake,
        mouth_leakage_kg=leaked,final_front_vent_kg=residual,
        actual_recovery_s=float(tp[-1]),pump_stop_reason=stop_reason,
        transferred_inbound_kg=float(rear[-1]),transferred_outbound_kg=stored-float(rear[-1]),
        retained_kg=stored,vented_front_kg=vent,
        inbound_suction_m3_s=pumping,outbound_suction_m3_s=Sp,
        peak_intake_kg_s=float(mdot.max()),peak_transfer_kg_s=float(flow_open.max()),
        max_front_over_ram=float(max(pfront[:len(t)]/s['ram_Pa'])),
        perigee_front_Pa=float(pfront[len(t)-1]),final_front_Pa=float(pfront[-1]),
        final_receiver_Pa=float(prear[-1]),receiver_equivalent_sphere_diameter_m=(6*c.receiver_m3/math.pi)**(1/3),
        tank_wall_only_kg_at_1bar_150MPa_allowable=4*math.pi*tank_radius**2*tank_gauge*2700,
        tank_wall_gauge_m=tank_gauge,
        compression_electric_J=Ecomp,compression_peak_inbound_W=float(max(eo.max(),spin_peak)),
        compression_peak_outbound_W=float(ep.max()),compression_end_W=float(ep[-1]),
        hot_compression_J=Ehot,warm_compression_J=Ewarm,
        intake_and_front_storage_heat_J=first_hot,
        hot_store_J=Qhot,warm_store_capture_J=Qwarm,
        post_isothermal_heat_input_J=float(pumpdown_isothermal_heat),
        through_recovery_energy_residual_J=float(energy_residual),
        metal_capacity_J_kg=capacities[0] if rack_context else capacity,metal_mass_kg=metal_mass,metal_physical_area_m2=physical_area,
        metal_two_face_emitting_m2=sum(x['wetted_m2'] for x in rack_report) if rack_report else 2*physical_area,ideal_metal_radiation_cooling_s=cooltime,
        inlet_heat_peak_scale_W=float(np.max(mdot*(hin-hhot))),
        intake_heat_per_exposed_m2_W=float(np.max(mdot*(hin-hhot))/(2*physical_area)) if physical_area>0 else None,
        liquefaction=plant,coast_feed_compressor=feed,separation_energy_J=Esep,
        first_cycle_liquid_before_propellant_kg=stored*.999-injected,
        mixing=dict(inputs=asdict(mixing),dry_stream_K=dry_K,mixed_K=c.gas_K,
            nitrogen_available_kg=stored*.999/(1+mixing.ratio)*float(dry_Y[g.species_index('N2')]),
            injected_kg=injected,recovered_coolant_kg=stored*.999*mixing.ratio/(1+mixing.ratio),
            coolant_replacement_kg=injected-stored*.999*mixing.ratio/(1+mixing.ratio),
            injection_electric_J=Einject,coolant_inlet_enthalpy_J_kg=coolant_enthalpy,
            cycle_mass_residual_kg=float(collected[-1])+extra_intake+injected-stored-vent+(1e-9 if rack_context else 0.)),
        first_cycle_liquid_volume_m3=max(0.,stored*.999-injected)/900.,budgets=budgets,pumpdown_samples=phases,
        history=history,
        exclusions=['Achieved inlet capture, heat exchanger conductance and pressure loss',
            'Pump maps, module count, rotor speeds, mechanisms, mass and spin-up',
            'Actual hull drag, finite-thrust orbital replay',
            'Gas-solid coupled recovery temperature; inlet temperature is prescribed',
            'Metal/alloy compatibility, coatings, deployment mechanics, contacts and fatigue',
            'Tanks, compressors, thrusters, supports, actuators and margin missing from mass subtotal',
            'Species-resolved liquefaction and tank heat leaks; nitrogen-equivalent duty only',
            'Circularization, transfer/export hardware and delivered-mass payoff'])


