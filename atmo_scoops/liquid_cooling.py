"""Standalone once-through liquid cooling / coast regeneration sizing.

Not coupled to capture or payoff: supplied gas duties and heat-transfer
coefficients are boundary conditions. See modeling/liquid_cooling/README.md.
"""
from dataclasses import dataclass, asdict
import math
import numpy as np
from CoolProp.CoolProp import PropsSI, PhaseSI

@dataclass(frozen=True)
class LiquidCooling:
    fluid: str = 'Ammonia'
    cold_K: float = 200.
    hot_K: float = 300.
    pressure_Pa: float = 2e6
    pass_s: float = 60.
    coast_s: float = 5135.
    sunlight_s: float = 2785.
    radius_m: float = .001
    wall_m: float = .0001
    velocity_m_s: float = 2.
    metal_density_kg_m3: float = 7870.
    wall_k_W_m_K: float = 16.
    allowable_Pa: float = 150e6
    pressure_factor: float = 1.5
    pump_efficiency: float = .65
    header_drop_Pa: float = 1e5
    heat_pump: bool = True
    carnot_fraction: float = .35
    radiator_K: float = 340.
    approach_K: float = 10.
    radiator_emissivity: float = .85
    environment_W_m2: float = 80.
    radiator_kg_m2: float = 5.
    refrigerator_input_W_kg: float = 500.
    pump_input_W_kg: float = 1000.
    solar_W_kg: float = 150.
    solar_W_m2: float = 250.
    tank_density_kg_m3: float = 2700.
    tank_margin_fraction: float = .5
    tank_ullage_fraction: float = .1
    tube_support_fraction: float = .3
    deployment_speed_m_s: float = 10.
    battery_Wh_kg: float = 150.
    battery_efficiency: float = .9
    battery_usable: float = .8

    def validate(self):
        for key,v in asdict(self).items():
            if key in ('fluid','heat_pump'):continue
            if not math.isfinite(v) or v<0:raise ValueError(f'Invalid {key}')
        if not 0<self.cold_K<self.hot_K or not 0<self.wall_m<self.radius_m:raise ValueError('Invalid temperatures or tube wall')
        if not 0<self.carnot_fraction<=1 or not 0<self.pump_efficiency<=1:raise ValueError('Invalid efficiency')
        if not 0<self.sunlight_s<=self.coast_s:raise ValueError('Invalid coast/sunlight')
        if not 0<=self.tank_ullage_fraction<1:raise ValueError('Invalid tank ullage')
        if min(self.pass_s,self.velocity_m_s,self.pressure_Pa,self.allowable_Pa,self.wall_k_W_m_K,self.deployment_speed_m_s,self.solar_W_kg,self.solar_W_m2,self.refrigerator_input_W_kg,self.pump_input_W_kg,self.battery_Wh_kg,self.battery_efficiency,self.battery_usable)<=0:raise ValueError('Positive operating coefficients required')


def properties(s):
    s.validate();T=np.linspace(s.cold_K,s.hot_K,161)
    if s.cold_K<=PropsSI('Ttriple',s.fluid):raise ValueError('Coolant below triple point')
    if any(PhaseSI('T',t,'P',s.pressure_Pa,s.fluid)!='liquid' for t in T):raise ValueError('Coolant must remain single-phase liquid')
    def prop(key):return np.array([PropsSI(key,'T',t,'P',s.pressure_Pa,s.fluid) for t in T])
    return T,{key:prop(key) for key in ('H','D','C','V','L')}


def size(duties, spec=LiquidCooling()):
    """duties: list of heat_J, gas_K, h_gas_W_m2_K, frontal_m2.

    Each chamber is a prescribed well-mixed gas bath for this component screen.
    Gas temperatures do not result from an inlet/compressor solution.
    """
    s=spec;T,p=properties(s);dh=p['H'][-1]-p['H'][0]
    if any(d['heat_J']<=0 or d['gas_K']<=s.hot_K or d['h_gas_W_m2_K']<=0 for d in duties):raise ValueError('Positive duties and gas/coolant approach required')
    ro=s.radius_m;ri=ro-s.wall_m;di=2*ri
    # Sample transport properties across the whole coolant path.
    Re=p['D']*s.velocity_m_s*di/p['V'];Pr=p['C']*p['V']/p['L']
    friction=np.where(Re<2300,64/Re,(.79*np.log(Re)-1.64)**-2)
    nu_t=(friction/8)*(Re-1000)*Pr/(1+12.7*np.sqrt(friction/8)*(Pr**(2/3)-1))
    Nu=np.where(Re<3000,3.66,np.maximum(3.66,nu_t))
    hi=float(np.min(Nu*p['L']/di));rho=float(np.mean(p['D']))
    stages=[]
    for d in duties:
        hg=d['h_gas_W_m2_K']
        U=1/(1/hg+ro*math.log(ro/ri)/s.wall_k_W_m_K+ro/(ri*hi))
        # Constant gas bath with variable cp(T), integrated along coolant path.
        integral=float(np.trapezoid(p['C']/(d['gas_K']-T),T))
        heat=d['heat_J']
        for _ in range(80):
            mdot=heat/dh/s.pass_s
            area=mdot*integral/U
            parallel=mdot/(rho*s.velocity_m_s*math.pi*ri**2)
            length=area/(2*math.pi*ro*parallel)
            dp=float(np.max(friction*p['D']))*length/di*s.velocity_m_s**2/2+s.header_drop_Pa
            pump=mdot/float(np.min(p['D']))*dp/s.pump_efficiency
            new=d['heat_J']+pump*s.pass_s
            if abs(new-heat)<1e-8*heat:break
            heat=new
        else:raise ValueError('Coolant pump/heat balance failed')
        tube_volume=area*ro/2
        hold_volume=tube_volume*(ri/ro)**2
        tube_mass=(tube_volume-hold_volume)*s.metal_density_kg_m3
        hi_local=Nu*p['L']/di
        U_local=1/(1/hg+ro*math.log(ro/ri)/s.wall_k_W_m_K+ro/(ri*hi_local))
        wall_inner=T+U_local*(d['gas_K']-T)*ro/(ri*hi_local)
        boiling=PropsSI('T','P',s.pressure_Pa,'Q',0,s.fluid)-float(np.max(wall_inner))
        stages.append(dict(**d,coolant_batch_kg=heat/dh,coolant_heat_J=heat,pump_W=pump,pump_J=pump*s.pass_s,
            wetted_m2=area,tube_metal_kg=tube_mass,tube_displacement_m3=tube_volume,
            tube_hold_up_kg=hold_volume*float(np.max(p['D'])),tube_hold_up_m3=hold_volume,
            parallel_paths=parallel,path_length_m=length,pressure_drop_Pa=dp,
            h_liquid_W_m2_K=hi,U_W_m2_K=U,liquid_wall_boiling_margin_K=boiling,
            tube_stress_margin_Pa=s.allowable_Pa-(s.pressure_Pa+dp)*ro/s.wall_m*s.pressure_factor,
            rack_depth_m=tube_volume/(math.pi*.1**2)/d['frontal_m2']))
    batch=sum(x['coolant_batch_kg'] for x in stages);Q=sum(x['coolant_heat_J'] for x in stages)
    # Additional line fill, not spent as usable once-through batch. Full hot-to-cold
    # regeneration of that fill is charged conservatively each cycle.
    hold=sum(x['tube_hold_up_kg'] for x in stages);regen_mass=batch+hold
    evap=T-s.approach_K;cond=s.radiator_K+s.approach_K
    if np.min(evap)<=0:raise ValueError('Invalid evaporator approach')
    if not s.heat_pump and s.radiator_K>=s.cold_K-s.approach_K:raise ValueError('Passive radiator cannot reach cold endpoint with finite approach')
    w_per_kg=float(np.trapezoid(p['C']*np.maximum(cond/evap-1,0)/s.carnot_fraction,T)) if s.heat_pump else 0.
    W=regen_mass*w_per_kg;Qregen=regen_mass*dh
    flux=s.radiator_emissivity*5.670374419e-8*s.radiator_K**4-s.environment_W_m2
    if flux<=0:raise ValueError('Radiator environmental load prevents net rejection')
    # Regenerate only in sunlight, directly powered; no free night refrigeration.
    pumpJ=sum(x['pump_J'] for x in stages)
    regeneration_pump_J=regen_mass/float(np.min(p['D']))*s.header_drop_Pa/s.pump_efficiency
    solar=(W+(pumpJ+regeneration_pump_J)/s.battery_efficiency)/s.sunlight_s
    rejection_s=s.sunlight_s if s.heat_pump else s.coast_s
    rejected=Qregen+W+regeneration_pump_J
    area=rejected/rejection_s/flux
    tank=batch/float(np.min(p['D']))/(1-s.tank_ullage_fraction)
    # Thin spherical pressure-vessel lower bound; divide into modules in real layout.
    tankmass=1.5*s.pressure_Pa*tank*s.tank_density_kg_m3/s.allowable_Pa*s.pressure_factor*(1+s.tank_margin_fraction)
    masses=dict(tubes=sum(x['tube_metal_kg'] for x in stages)*(1+s.tube_support_fraction),tank=tankmass,
        refrigerator=W/s.sunlight_s/s.refrigerator_input_W_kg,radiator=area*s.radiator_kg_m2,
        solar=solar/s.solar_W_kg,pump=sum(x['pump_W'] for x in stages)/s.pump_input_W_kg,
        pump_battery=(pumpJ+(0. if s.heat_pump else regeneration_pump_J*(1-s.sunlight_s/s.coast_s)))/(3600*s.battery_Wh_kg*s.battery_efficiency*s.battery_usable))
    motion=max(math.sqrt(area),math.sqrt(solar/s.solar_W_m2))/s.deployment_speed_m_s
    return dict(inputs=asdict(s),stages=stages,coolant_batch_kg=batch,line_fill_kg=hold,
        total_coolant_kg=regen_mass,coolant_tank_m3=tank,coolant_tank_equivalent_depth_m=tank/duties[0]['frontal_m2'],
        useful_capacity_J_kg=dh,gas_heat_J=sum(x['heat_J'] for x in duties),regenerated_heat_J=Qregen,line_fill_heat_allowance_J=hold*dh,
        refrigerator_J=W,regeneration_pump_J=regeneration_pump_J,rejected_J=rejected,rejection_s=rejection_s,solar_MW=solar/1e6,solar_m2=solar/s.solar_W_m2,
        radiator_m2=area,required_motion_s=motion,masses_kg=masses,dry_component_kg=sum(masses.values()),
        component_with_coolant_kg=sum(masses.values())+regen_mass,
        radiator_folded_m3=area*.02,solar_folded_m3=solar/40000,
        coolant_Re_range=[float(min(Re)),float(max(Re))],
        screen_pass=all(x['liquid_wall_boiling_margin_K']>0 and x['tube_stress_margin_Pa']>0 for x in stages),
        status='Standalone prescribed-duty component screen; not coupled capture or payoff')


def main():
    import argparse,json
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();data=json.loads(Path(args.config).read_text())
    result=size(data['duties'],LiquidCooling(**data['cooling']))
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
