"""Real-fluid compression and transparent axial-bank mass screening.

HEOS mixture endpoints are thermodynamic calculations. Geometry/mass and off-design
capabilities remain explicit engineering assumptions, not qualified flight hardware.
"""
from dataclasses import dataclass, asdict
import math
import numpy as np
import CoolProp.CoolProp as CP
from scipy.optimize import brentq

_compression_cache = {}


@dataclass(frozen=True)
class Compressor:
    mode: str = 'real_gas'
    blocks: int = 4
    coast_blocks: int = 3
    isentropic_efficiency: float = .75
    interstage_K: float = 600.
    axial_velocity_m_s: float = 80.
    module_diameter_m: float = 1.
    hub_tip_ratio: float = .5
    blade_aspect_ratio: float = 2.
    tip_solidity: float = 1.
    blade_volume_factor: float = .12
    tip_speed_m_s: float = 250.
    loading_coefficient: float = .4
    material_density_kg_m3: float = 7800.
    allowable_stress_Pa: float = 400e6
    case_gauge_m: float = .00254
    disk_min_gauge_m: float = .005
    accessory_factor: float = 1.3
    mass_multiplier: float = 1.
    motor_W_kg: float = 1000.
    head_limit_ratio: float = 1e5
    minimum_train_ratio: float = 100.
    spinup_s: float = 120.
    thermodynamic_samples: int = 401

    def validate(self):
        if self.mode not in ('real_gas','legacy'):raise ValueError('Unknown compressor mode')
        for k,v in asdict(self).items():
            if k=='mode':continue
            if isinstance(v,bool) or not math.isfinite(v) or v<=0:raise ValueError(f'compressor.{k} must be positive')
        if any(not isinstance(v,int) or v>12 for v in (self.blocks,self.coast_blocks)):
            raise ValueError('Require 1–12 integer compressor blocks')
        if not isinstance(self.thermodynamic_samples,int) or self.thermodynamic_samples<101:
            raise ValueError('Require at least 101 thermodynamic samples')
        if not 0<self.isentropic_efficiency<=1 or not 0<self.hub_tip_ratio<1:
            raise ValueError('Invalid efficiency or hub ratio')
        if self.accessory_factor<1 or self.head_limit_ratio<=1 or not 1<=self.minimum_train_ratio<=self.head_limit_ratio:raise ValueError('Invalid capability factor')


class RealAir:
    """Frozen N2/O2/Ar HEOS mixture; reject significant unrepresented species.

    Trace species are reported and normalized out, never silently called exact.
    Property differences are used; HEOS/Cantera absolute enthalpies are not mixed.
    """
    def __init__(self, gas=None, Y=None):
        if gas is None:
            mass=np.array([.755,.232,.013]);self.omitted_mass_fraction=0.
        else:
            mass=np.array([Y[gas.species_index(s)] for s in ('N2','O2','Ar')])
            self.omitted_mass_fraction=max(0.,1-float(mass.sum()))
            if self.omitted_mass_fraction>1e-3:
                raise ValueError('HEOS compressor supports molecular N2/O2/Ar; omitted species exceed 0.1%')
        mass=mass/mass.sum();self.mass_fractions=mass.tolist()
        self.fluid=CP.AbstractState('HEOS','Nitrogen&Oxygen&Argon')
        self.fluid.set_mass_fractions(mass.tolist())
        self.fluid.specify_phase(CP.iphase_gas)

    def state(self,p,T):
        if not 1e-4<=p<=1e7 or not 200<=T<=2000:
            raise ValueError(f'Compressor property domain exceeded: {p:g} Pa, {T:g} K')
        f=self.fluid;f.update(CP.PT_INPUTS,float(p),float(T))
        return dict(p_Pa=float(p),T_K=float(T),h_J_kg=f.hmass(),s_J_kg_K=f.smass(),
                    cp_J_kg_K=f.cpmass(),rho_kg_m3=f.rhomass(),sound_m_s=f.speed_sound(),mu_Pa_s=f.viscosity(),Z=f.compressibility_factor())

    def compress(self,p1,T1,p2,eta):
        if not 0<eta<=1:raise ValueError('Invalid isentropic efficiency')
        # Equilibrium solver roundoff must not defeat cache reuse across mass
        # scenarios. These tolerances are far below the property-model accuracy.
        key=(tuple(round(x,12) for x in self.mass_fractions),round(float(p1),9),
             round(float(T1),9),round(float(p2),9),float(eta))
        if key in _compression_cache:return _compression_cache[key]
        a=self.state(p1,T1);p2=max(p1,p2)
        f=self.fluid
        def residual(T,kind,value):
            f.update(CP.PT_INPUTS,float(p2),float(T))
            return (f.smass() if kind=='s' else f.hmass())-value
        try:
            Ts=brentq(residual,T1,2000.,args=('s',a['s_J_kg_K']),xtol=1e-8) if p2>p1 else T1
            f.update(CP.PT_INPUTS,float(p2),Ts)
            hs=f.hmass();hout=a['h_J_kg']+(hs-a['h_J_kg'])/eta
            T2=brentq(residual,T1,2000.,args=('h',hout),xtol=1e-8) if p2>p1 else T1
        except ValueError as exc:
            raise ValueError('Compression endpoint outside 200–2000 K property domain') from exc
        b=self.state(p2,T2)
        result=dict(inlet=a,outlet=b,isentropic_h_J_kg=hs,shaft_J_kg=hout-a['h_J_kg'])
        if len(_compression_cache)>40000:_compression_cache.clear()
        _compression_cache[key]=result
        return result

    def train(self,p1,T1,p2,blocks,cool_K,eta):
        # Reciprocal inlet-temperature weights reduce hot-first-block loading.
        # This is an explicit allocation rule, not an optimum or a measured map.
        Ts=[T1]+[min(T1,cool_K)]*(blocks-1)
        weights=1/np.array(Ts);weights/=weights.sum()
        logratio=math.log(max(1.,p2/p1));p=p1;out=[]
        for temp,w in zip(Ts,weights):
            q=p*math.exp(logratio*w)
            b=self.compress(p,temp,q,eta);out.append(b);p=q
        return out


def bank_mass(Q,work_J_kg,power_W,spec,inlet):
    """Conservative constant-annulus axial row buildup with a stress-screened disk.

    WATE-S-inspired component accounting, NOT a reimplementation or validation
    of WATE-S. Uses bank maxima (Q/head/power may occur at different times).
    Motors are separate here and included once. No surge map is implied.
    """
    if Q<=0:return dict(total_kg=0.,spin_energy_J=0.,modules=0,rows=0)
    h=spec.hub_tip_ratio;rho=spec.material_density_kg_m3;U=spec.tip_speed_m_s
    annulus=Q/spec.axial_velocity_m_s
    module_area=math.pi*spec.module_diameter_m**2/4*(1-h*h)
    modules=max(1,math.ceil(annulus/module_area))
    diameter=math.sqrt(4*annulus/modules/math.pi/(1-h*h))
    rt=diameter/2;rh=h*rt;height=rt-rh;chord=height/spec.blade_aspect_ratio
    blades=max(3,math.ceil(spec.tip_solidity*math.pi*diameter/chord))
    # NASA CR-168049 printed p.14 Eq.(5) defines TOTAL row blade volume,
    # V_B=K*h_B**3/AR**2. Do not multiply that total by blade count again.
    rotating_blades=spec.blade_volume_factor*height*chord**2*rho
    omega=U/rt;rm=(rt+rh)/2
    blade_stress=.5*rho*U**2*(1-h*h)
    disk_self=.5*rho*(U*h)**2
    if max(blade_stress,disk_self)>=spec.allowable_stress_Pa:
        raise ValueError('Compressor centrifugal stress exceeds assumed allowable')
    force=rotating_blades*omega**2*rm
    disk_t=max(spec.disk_min_gauge_m,force/(2*math.pi*rh*(spec.allowable_stress_Pa-disk_self)))
    disk=math.pi*rh**2*disk_t*rho
    stage_length=2.34*chord
    case=math.pi*diameter*stage_length*spec.case_gauge_m*rho
    # Equal work per aerodynamic row; count additional rows for required head.
    rows=max(1,math.ceil(work_J_kg/(spec.loading_coefficient*(U*(1+h)/2)**2)))
    bare=modules*rows*(2*rotating_blades+disk+case)
    structural=bare*spec.accessory_factor*spec.mass_multiplier
    motors=power_W/spec.motor_W_kg
    inertia=rotating_blades*rm**2+.5*disk*rh**2
    spin=.5*inertia*omega**2*modules*rows*spec.mass_multiplier
    return dict(total_kg=structural+motors,structural_kg=structural,motor_kg=motors,
        modules=modules,rows=rows,module_diameter_m=diameter,annulus_m2=annulus,
        tip_speed_m_s=U,shaft_rpm=omega*60/(2*math.pi),row_chord_m=chord,
        bank_length_m=rows*stage_length,blade_root_stress_Pa=blade_stress,
        disk_gauge_m=disk_t,rotor_and_stator_kg=2*rotating_blades*modules*rows,
        disk_kg=disk*modules*rows,case_kg=case*modules*rows,
        spin_energy_J=spin,design_suction_m3_s=Q,design_head_J_kg=work_J_kg,
        design_electric_W=power_W,
        inlet_Re=inlet['rho_kg_m3']*math.hypot(spec.axial_velocity_m_s,U)*chord/inlet['mu_Pa_s'],
        relative_Mach=math.hypot(spec.axial_velocity_m_s,U)/inlet['sound_m_s'])


def evaluate_train_history(thermo,spec,pin,Tin,pout,net_flow,times,blocks,cool_K,motor_eta,
                           ultimate=0.,rated_suction=None,idle_fraction=0.,rack_context=None):
    """Integrate real-gas work and size each bank across its operating envelope."""
    # The flow solver retains many adaptive steps near cutoff. Thermodynamics
    # are smooth there: retain uniform-time samples plus key envelope extrema.
    # Keep this resolution independent and explicitly convergence-test it.
    full_times=np.asarray(times)
    pin=np.asarray(pin);pout=np.asarray(pout);net_flow=np.asarray(net_flow)
    if len(times)>spec.thermodynamic_samples:
        sample_times=np.unique(np.r_[np.linspace(times[0],times[-1],spec.thermodynamic_samples),
            times[np.argmax(net_flow)],times[np.argmax(pout)],times[np.argmin(pin)],
            times[np.argmax(pout/np.maximum(pin,1e-30))]])
        if np.ndim(Tin):Tin=np.interp(sample_times,full_times,Tin)
        pin=np.interp(sample_times,full_times,pin)
        pout=np.interp(sample_times,full_times,pout)
        net_flow=np.interp(sample_times,full_times,net_flow)
        if np.ndim(ultimate):ultimate=np.interp(sample_times,full_times,ultimate)
        times=sample_times
    n=len(times);powers=np.zeros((n,blocks));gross=np.zeros(n);cooling=np.zeros(n)
    maxima=[dict(Q=0.,work=0.,power=0.,inlet=None) for _ in range(blocks)]
    endpoints=[]
    rack_heats=np.zeros(blocks);rack_prev=np.zeros(blocks)
    liquid_used=np.zeros(blocks);liquid_pump=np.zeros(blocks);liquid_prev=np.zeros((blocks,2));liquid_max=np.zeros((blocks,4))
    rack_hot=np.zeros(blocks);rack_details=[{} for _ in range(blocks)]
    rack_time_history=[]
    core_h=np.zeros(blocks);core_peak=np.zeros(blocks);melt_peak=np.zeros(blocks)
    buffer_inventory=np.zeros(n)
    buffer_energy=np.zeros(n)
    if rack_context:
        from .racks import conductance
        metal=rack_context['metal'];geoms=rack_context['geometries'];rs=rack_context['spec']
        metals=rack_context.get('metals',[metal]*blocks)
        core_h=np.array([m.hcore_cold if hasattr(m,'pcm') else 0. for m in metals])
    for j,(p,q,mdot) in enumerate(zip(pin,pout,net_flow)):
        floor=float(ultimate[j]) if np.ndim(ultimate) else ultimate
        if mdot<=1e-15 or p<=floor:
            if j:
                buffer_inventory[j]=buffer_inventory[j-1]
                buffer_energy[j]=buffer_energy[j-1]
                if rack_context:
                    for k in range(1,blocks):
                        mat=metals[k]
                        if hasattr(mat,'pcm'):
                            total=mat.hcold+rack_heats[k]/geoms[k]['mass_kg']
                            core_h[k]=mat.advance_core(total,core_h[k],times[j]-times[j-1],geoms[k])
                            core_peak[k]=max(core_peak[k],mat.pcm.temperature(core_h[k]))
                            melt_peak[k]=max(melt_peak[k],mat.pcm.melt_fraction(core_h[k]))
            continue
        # Coast feed above its delivery pressure uses a regulator bypass.
        if rated_suction is None and p>=q:continue
        # Maintain a design pressure ratio when the tank is empty; downstream
        # throttling loses excess pressure. This avoids assuming small downstream
        # banks can swallow the first-bank Q at a near-unity startup ratio.
        target=max(float(q),float(p)*(spec.minimum_train_ratio if rated_suction is not None else 1.))
        temp=float(Tin[j]) if np.ndim(Tin) else Tin
        if rack_context:
            # Quasi-steady series flow, finite thermal capacity in each independent rack.
            weights=1/np.array([temp]+[cool_K]*(blocks-1));weights/=weights.sum()
            pp=float(p);train=[];qheat=np.zeros(blocks);current_liquid={}
            dt=0. if j==0 else times[j]-times[j-1]
            flow=mdot*p/(p-floor) if floor else mdot
            for i,wgt in enumerate(weights):
                qq=pp*math.exp(math.log(target/p)*wgt)
                stage=thermo.compress(pp,temp,qq,spec.isentropic_efficiency);train.append(stage)
                pp=qq
                if i<blocks-1:
                    k=i+1;geom=geoms[k]
                    mat=metals[k]
                    predicted=mat.hcold+(rack_heats[k]+dt*rack_prev[k])/geom['mass_kg']
                    if hasattr(mat,'pcm'):
                        pred_core=mat.advance_core(predicted,core_h[k],dt,geom)
                        Ts=mat.surface_temperature(predicted,pred_core)
                    else:Ts=mat.temperature(predicted)
                    hot=stage['outlet'];cp=hot['cp_J_kg_K']
                    UA,detail=conductance(pp,(hot['T_K']+Ts)/2,flow,geom['frontal_m2'],geom,rs,cp=cp)
                    if 'liquid' in geom:
                        from .ammonia import series_exchange
                        UA,ld=series_exchange(detail['h_W_m2_K']*geom['wetted_m2'],hot['T_K'],flow*cp,geom)
                        detail.update(ld)
                    current_liquid[k]=detail
                    target_T=Ts+(hot['T_K']-Ts)*math.exp(-UA/max(flow*cp,1e-30))
                    if not 200<=target_T<=2000:raise ValueError('Rack outlet exceeds real-gas property range')
                    cold=thermo.state(pp,target_T)
                    qheat[k]=flow*(hot['h_J_kg']-cold['h_J_kg'])
                    temp=target_T
                    rack_hot[k]=max(rack_hot[k],Ts)
                    detail.update(inlet_K=hot['T_K'],outlet_K=temp,metal_K=Ts,UA_W_K=UA,
                        gas_inventory_kg=geom['gas_m3']*cold['rho_kg_m3'],
                        residence_s=geom['gas_m3']*cold['rho_kg_m3']/max(flow,1e-30))
                    buffer_inventory[j]+=geom['gas_m3']*cold['rho_kg_m3']
                    buffer_energy[j]+=geom['gas_m3']*cold['rho_kg_m3']*(cold['h_J_kg']-pp/cold['rho_kg_m3'])
                    if not rack_details[k] or flow>rack_details[k].get('flow_kg_s',0):
                        rack_details[k]={**detail,'flow_kg_s':flow}
            for k in range(1,blocks):
                if 'liquid' in geoms[k]:
                    dd=current_liquid[k];rate=np.array([dd['liquid_flow_kg_s'],dd['liquid_pump_W']])
                    liquid_used[k]+=.5*dt*(liquid_prev[k,0]+rate[0])
                    liquid_pump[k]+=.5*dt*(liquid_prev[k,1]+rate[1]);liquid_prev[k]=rate
                    liquid_max[k]=np.maximum(liquid_max[k],[rate[0],rate[1],dd['liquid_wall_K'],dd['liquid_dp_Pa']])
            rack_heats+=.5*dt*(rack_prev+qheat);rack_prev=qheat
            for k in range(1,blocks):
                mat=metals[k]
                if hasattr(mat,'pcm'):
                    total=mat.hcold+rack_heats[k]/geoms[k]['mass_kg']
                    core_h[k]=mat.advance_core(total,core_h[k],dt,geoms[k])
                    core_peak[k]=max(core_peak[k],mat.pcm.temperature(core_h[k]))
                    melt_peak[k]=max(melt_peak[k],mat.pcm.melt_fraction(core_h[k]))
                    rack_hot[k]=max(rack_hot[k],mat.surface_temperature(total,core_h[k]))
            rack_time_history.append(dict(time_s=float(times[j]),inlets_K=[x['inlet']['T_K'] for x in train],outlets_K=[x['outlet']['T_K'] for x in train]))
        else:
            train=thermo.train(float(p),temp,target,blocks,cool_K,spec.isentropic_efficiency)
        # Preserve finite-backflow throughput overhead from the intake envelope.
        flow=mdot*p/(p-floor) if floor else mdot
        gross[j]=flow
        for i,b in enumerate(train):
            inlet=b['inlet'];Q=flow/inlet['rho_kg_m3']
            if i==0 and rated_suction is not None:Q=max(Q,rated_suction)
            w=max(0.,b['shaft_J_kg']);P=flow*w/motor_eta;powers[j,i]=P
            m=maxima[i]
            m['Q']=max(m['Q'],Q)
            if m['inlet'] is None or Q>=m['Q']:m['inlet']=inlet;m['flow']=mdot
            m['work']=max(m['work'],w);m['power']=max(m['power'],P)
        if j==int(np.argmax(net_flow)):endpoints=train
    banks=[bank_mass(m['Q'],m['work'],m['power'],spec,m['inlet']) for m in maxima]
    for b in banks:
        # Constant angular acceleration: peak shaft power = 2 E_rot / t_spin.
        # Prespin before collection; do not demand full pumping speed from rest.
        spin_peak=2*b['spin_energy_J']/motor_eta/spec.spinup_s
        b['spinup_peak_electric_W']=spin_peak
        if b['modules']:
            b['motor_kg']=max(b['design_electric_W'],spin_peak)/spec.motor_W_kg
            b['total_kg']=b['structural_kg']+b['motor_kg']
    spin=sum(b['spin_energy_J'] for b in banks)/motor_eta
    # Charge one complete spin-up per orbit, no recovered spin-down credit.
    duration=float(times[-1]-times[0]);spin_power=spin/duration
    idle=idle_fraction*float(powers.sum(axis=1).max())
    electric=powers.sum(axis=1)+idle+spin_power
    returned_electric=np.interp(full_times,times,electric)
    returned_powers=np.column_stack([np.interp(full_times,times,powers[:,i]) for i in range(blocks)])
    return dict(electric_W=returned_electric,bank_power_W=returned_powers,banks=banks,
        thermodynamic_evaluation_samples=len(times),
        total_mass_kg=sum(b['total_kg'] for b in banks),spinup_electric_J=spin,
        spinup_peak_electric_W=sum(b['spinup_peak_electric_W'] for b in banks),
        idle_electric_W=idle,peak_flow_states=endpoints,
        electricity_J=float(np.trapezoid(electric,times)),
        interstage_inventory_kg=np.interp(full_times,times,buffer_inventory).tolist(),
        interstage_energy_J=np.interp(full_times,times,buffer_energy).tolist(),
        liquid_used_kg=liquid_used.tolist(),liquid_pump_J=liquid_pump.tolist(),liquid_max=liquid_max.tolist(),
        rack_core_h_J_kg=core_h.tolist(),rack_max_core_K=core_peak.tolist(),rack_max_melt_fraction=melt_peak.tolist(),
        rack_heat_J=rack_heats.tolist(),rack_max_metal_K=rack_hot.tolist(),rack_peak_flow_details=rack_details,
        stage_temperature_history=rack_time_history,
        assumptions=asdict(spec),properties=dict(backend='CoolProp HEOS N2/O2/Ar',
            mass_fractions=thermo.mass_fractions,omitted_mass_fraction=thermo.omitted_mass_fraction,
            temperature_domain_K=[200,2000]))
