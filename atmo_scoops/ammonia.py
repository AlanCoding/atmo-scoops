"""Fixed ammonia tubes with controlled once-through flow and finite inventory.

Quasi-steady exchanger wall/flow approximation; inventory exhaustion rejects a
trial. This module is coupled to the inlet and compressor thermal equations.
"""
from dataclasses import dataclass, asdict
import math
import numpy as np
from CoolProp.CoolProp import PropsSI
from .liquid_cooling import LiquidCooling, properties

@dataclass(frozen=True)
class AmmoniaCooling:
    enabled: bool = False
    cold_K: float = 200.
    hot_target_K: float = 300.
    pressure_Pa: float = 2e6
    areas_m2: tuple = (170000.,6000.,6000.,6000.)
    maximum_flows_kg_s: tuple = (9000.,400.,400.,400.)
    inventories_kg: tuple = (700000.,60000.,60000.,60000.)
    radius_m: float = .001
    wall_m: float = .0001
    radius_over_pitch: float = .1
    design_velocity_m_s: float = 2.
    radiator_K: float = 340.
    carnot_fraction: float = .35
    refrigerator_input_W_kg: float = 500.
    def validate(self,blocks=4):
        if not isinstance(self.enabled,bool):raise ValueError('ammonia.enabled must be boolean')
        if not self.enabled:return
        for k,v in asdict(self).items():
            if k=='enabled':continue
            if isinstance(v,(tuple,list)):
                if len(v)!=blocks:raise ValueError('One ammonia area, flow and inventory per stage required')
            else:v=(v,)
            if any(not math.isfinite(x) or x<=0 for x in v):raise ValueError('Positive finite ammonia inputs required')
        if not 200<=self.cold_K<self.hot_target_K-5. or not self.wall_m<self.radius_m:raise ValueError('Ammonia temperatures/wall outside supported domain')
        if not self.radius_over_pitch<.25 or self.carnot_fraction>1:raise ValueError('Invalid ammonia geometry/efficiency')
    def specification(self):
        return LiquidCooling(cold_K=self.cold_K,hot_K=self.hot_target_K,pressure_Pa=self.pressure_Pa,
            radius_m=self.radius_m,wall_m=self.wall_m,velocity_m_s=self.design_velocity_m_s,
            radiator_K=self.radiator_K,carnot_fraction=self.carnot_fraction,
            refrigerator_input_W_kg=self.refrigerator_input_W_kg)

class Bank:
    def __init__(self,cold):self.cold=cold;self.hcold=0.;self.liquid=True
    def temperature(self,h):return self.cold
    def enthalpy(self,T):return 450.*(T-self.cold) # unused sizing compatibility


def geometry(spec,frontal):
    s=spec.specification();T,p=properties(s);ro=s.radius_m;ri=ro-s.wall_m
    # Conservative fully developed laminar coefficient, without turbulent bonus.
    hi=float(min(3.66*p['L']/(2*ri)));rho=float(np.mean(p['D']))
    boiling=PropsSI('T','P',s.pressure_Pa,'Q',0,'Ammonia')
    out=[]
    for area,flow,inventory in zip(spec.areas_m2,spec.maximum_flows_kg_s,spec.inventories_kg):
        solid=area*ro/2;void=solid*(ri/ro)**2;mass=(solid-void)*s.metal_density_kg_m3
        N=flow/(rho*s.velocity_m_s*math.pi*ri**2);length=area/(2*math.pi*ro*N)
        env=solid/(math.pi*spec.radius_over_pitch**2)
        out.append(dict(mass_kg=mass,solid_m3=solid,envelope_m3=env,gas_m3=env-solid,
            porosity=1-math.pi*spec.radius_over_pitch**2,wetted_m2=area,depth_m=env/frontal,frontal_m2=frontal,
            wire_radius_m=ro,pitch_m=ro/spec.radius_over_pitch,deployed_physical_m2=0.,
            liquid=dict(cold_K=s.cold_K,target_K=s.hot_K,maximum_flow_kg_s=flow,inventory_kg=inventory,
                cold_h=float(p['H'][0]),delta_h=float(p['H'][-1]-p['H'][0]),cp=(p['H'][-1]-p['H'][0])/(s.hot_K-s.cold_K),
                wall_resistance=ro*math.log(ro/ri)/s.wall_k_W_m_K,liquid_resistance=ro/(ri*hi),
                length_m=length,parallel_paths=N,density=rho,mu=float(max(p['V'])),
                rho_min=float(min(p['D'])),hold_up_kg=void*float(max(p['D'])),
                tube_inner_radius_m=ri,boiling_K=boiling,pressure_Pa=s.pressure_Pa)))
    return out


def exchange(gas_UA,Tgas,geom):
    a=geom['liquid'];A=geom['wetted_m2'];cold=a['cold_K'];delta=max(0.,Tgas-cold)
    if delta<=1e-9 or gas_UA<=0:return 0.,dict(liquid_flow_kg_s=0.,liquid_pump_W=0.,liquid_wall_K=cold,liquid_out_K=cold,liquid_dp_Pa=0.)
    UA=1/(1/gas_UA+(a['wall_resistance']+a['liquid_resistance'])/A)
    target=min(a['target_K']-1.,cold+.8*delta)
    # Throttle flow to use the chosen enthalpy rise when capacity permits.
    flow=min(a['maximum_flow_kg_s'],UA/(a['cp']*math.log(delta/(Tgas-target))))
    C=flow*a['cp'];effective=C*(-math.expm1(-UA/C))
    heat=effective*delta;Tout=cold+heat/C
    # Liquid-side resistance uses a conservative laminar h at all flow settings.
    wall=Tout+heat/A*a['liquid_resistance']
    ri=a['tube_inner_radius_m'];v=flow/(a['density']*a['parallel_paths']*math.pi*ri**2)
    Re=max(1e-20,a['density']*v*2*ri/a['mu'])
    f=64/Re if Re<2300 else (.79*math.log(Re)-1.64)**-2
    dp=f*a['length_m']/(2*ri)*a['density']*v*v/2+1e5
    power=flow/a['rho_min']*dp/.65
    return effective,dict(liquid_flow_kg_s=flow,liquid_pump_W=power,liquid_wall_K=wall,liquid_out_K=Tout,liquid_dp_Pa=dp)


def install(o,r,spec,hw,perf):
    """Add actual duty/flow-dependent regeneration and installation budgets."""
    s=spec.specification();T,p=properties(s);hc=p['H'][0]
    coast=o['cycle']['deployed_s'];sun=o['cycle']['sunlit_s']
    W=Q=inventory=tank=used=passpump=peakpump=0.;reports=[];tube_mass=0.
    for rack in r['racks']:
        a=rack['liquid'];m=rack['liquid_used_kg'];pump=rack['liquid_pump_J'];heat=rack['absorbed_J']+pump
        mean_h=hc+heat/max(m,1e-20)
        Tout=float(np.interp(mean_h,p['H'],T))
        overflow=max(0.,mean_h-p['H'][-1])
        tt=np.linspace(s.cold_K,Tout,101)
        cp=np.interp(tt,T,p['C'])
        coeff=np.maximum((s.radiator_K+s.approach_K)/(tt-s.approach_K)-1,0)/s.carnot_fraction
        work=m*float(np.trapezoid(cp*coeff,tt))
        # Conservative full hot-to-cold line-fill restoration allowance.
        line=a['hold_up_kg'];lineQ=line*(p['H'][-1]-hc)
        lineW=line*float(np.trapezoid(p['C']*np.maximum((s.radiator_K+s.approach_K)/(T-s.approach_K)-1,0)/s.carnot_fraction,T))
        W+=work+lineW;Q+=heat+lineQ
        inventory+=a['inventory_kg']+line;used+=m;passpump+=pump;peakpump+=rack['liquid_peak_pump_W']
        tank+=a['inventory_kg']/min(p['D'])/(1-s.tank_ullage_fraction)
        tube_mass+=rack['mass_kg']
        reports.append(dict(used_kg=m,available_kg=a['inventory_kg'],mean_return_K=Tout,enthalpy_over_target_J_kg=overflow,
            heat_J=heat,peak_wall_K=rack['liquid_max_wall_K'],boiling_K=a['boiling_K'],peak_dp_Pa=rack['liquid_max_dp_Pa'],
            line_fill_kg=line,peak_flow_kg_s=rack['liquid_peak_flow_kg_s']))
    regenpump=inventory/min(p['D'])*s.header_drop_Pa/s.pump_efficiency
    solar=(W+(passpump+regenpump)/s.battery_efficiency)/sun
    flux=s.radiator_emissivity*5.670374419e-8*s.radiator_K**4-s.environment_W_m2
    if flux<=0:raise ValueError('Ammonia radiator has no net heat rejection')
    loss=(passpump+regenpump)*(1/s.battery_efficiency-1)
    radiator=(Q+W+regenpump+loss)/sun/flux
    battery=max(passpump/(3600*perf.battery_Wh_kg*perf.battery_usable*s.battery_efficiency),peakpump/perf.battery_W_kg)
    masses=dict(ammonia_tube_support=tube_mass*s.tube_support_fraction,
        ammonia_tank=1.5*s.pressure_Pa*tank*s.tank_density_kg_m3/s.allowable_Pa*s.pressure_factor*(1+s.tank_margin_fraction),
        ammonia_refrigerator=W/sun/s.refrigerator_input_W_kg,ammonia_radiator=radiator*s.radiator_kg_m2,
        ammonia_pump=peakpump/s.pump_input_W_kg,
        ammonia_power_distribution=hw.distribution_kg_kW*max(solar,peakpump)/1000)
    before=sum(masses.values())+solar/perf.solar_W_kg+battery
    o['masses_kg'].update(masses);o['masses_kg']['solar']+=solar/perf.solar_W_kg;o['masses_kg']['battery']+=battery
    o['masses_kg']['design_margin']+=before*hw.design_margin
    o['total_dry_kg']+=before*(1+hw.design_margin)
    rejection_fluid=radiator*hw.warm_loop_fluid_kg_m2
    o['total_with_loop_fluid_kg']+=before*(1+hw.design_margin)+inventory+rejection_fluid
    o['solar_MW']+=solar/1e6;o['solar_area_m2']+=solar/perf.solar_W_m2
    o['ammonia']=dict(stages=reports,total_inventory_kg=inventory,used_kg=used,tank_m3=tank,
        radiator_m2=radiator,rejection_loop_fluid_kg=rejection_fluid,electrical_loss_J=loss,regenerated_heat_J=Q,refrigeration_J=W,rejected_J=Q+W+regenpump+loss,
        pass_pump_J=passpump,additional_solar_W=solar,coast_pump_J=regenpump,
        tube_metal_kg=tube_mass,additional_dry_mass_kg=before*(1+hw.design_margin))
    return o


def series_exchange(gas_UA,Tgas,gas_capacity,geom):
    """Counterflow effectiveness with a flow-controlled liquid outlet.

    Gas capacity uses the local real-gas cp; final duty is checked using real
    enthalpy endpoints by the compressor solver. Five kelvin control margin.
    """
    from scipy.optimize import brentq
    a=geom['liquid'];cold=a['cold_K'];delta=max(0.,Tgas-cold)
    if delta<=1e-9:return exchange(0.,Tgas,geom)
    area=geom['wetted_m2'];UA=1/(1/max(gas_UA,1e-30)+(a['wall_resistance']+a['liquid_resistance'])/area)
    def duty(m):
        Cl=m*a['cp'];Cmin=min(Cl,gas_capacity);Cmax=max(Cl,gas_capacity)
        Cr=Cmin/Cmax;NTU=UA/Cmin
        if abs(Cr-1)<1e-8:eps=NTU/(1+NTU)
        else:
            e=math.exp(-min(700.,NTU*(1-Cr)));eps=(1-e)/(1-Cr*e)
        return eps*Cmin*delta
    target=min(a['target_K']-5.,cold+.8*delta)
    top=a['maximum_flow_kg_s']
    error=lambda m:duty(m)/m/a['cp']-(target-cold)
    flow=top if error(top)>0 else brentq(error,max(1e-12,top*1e-12),top)
    # Reuse hydraulic calculation with the chosen flow represented as the cap.
    limited=dict(geom,liquid={**a,'maximum_flow_kg_s':flow})
    _,detail=exchange(gas_UA,Tgas,limited)
    # exchange may choose less flow for a bath; hydraulics must use series flow.
    ratio=flow/max(detail['liquid_flow_kg_s'],1e-30)
    if abs(ratio-1)>1e-8:
        ri=a['tube_inner_radius_m'];v=flow/(a['density']*a['parallel_paths']*math.pi*ri**2)
        Re=max(1e-20,a['density']*v*2*ri/a['mu']);f=64/Re if Re<2300 else (.79*math.log(Re)-1.64)**-2
        dp=f*a['length_m']/(2*ri)*a['density']*v*v/2+1e5
        detail.update(liquid_flow_kg_s=flow,liquid_dp_Pa=dp,liquid_pump_W=flow/a['rho_min']*dp/.65)
    Q=duty(flow);out=cold+Q/(flow*a['cp'])
    wall_hot=out+UA/area*(Tgas-out)*a['liquid_resistance']
    gas_out=Tgas-Q/gas_capacity
    wall_cold=cold+UA/area*(gas_out-cold)*a['liquid_resistance']
    detail.update(liquid_out_K=out,liquid_wall_K=max(wall_hot,wall_cold))
    fraction=min(1-1e-14,Q/(gas_capacity*delta))
    return -gas_capacity*math.log1p(-fraction),detail
