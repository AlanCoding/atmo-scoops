"""Installed capacities, controls and initial state; no cycle-dependent sizing."""
from dataclasses import dataclass,asdict,fields
import math
@dataclass(frozen=True)
class Design:
    perigee_km: float=85.
    apogee_km: float=2000.
    bore_m: float=30.
    clearance_m: float=.85
    length_diameter: float=10.
    rack_depth_m: tuple=(5.42,.40,.18,.20,.32)
    clear_depth_m: tuple=(0.,0.,0.,0.)
    rack_initial_K: tuple=(330.,330.,330.,330.,330.)
    materials: tuple=('sic','aluminum','aluminum','aluminum','aluminum')
    rod_radius_m: float=.001
    rod_pitch_m: float=.01
    suction_m3_s: tuple=(27464.,6207.,1723.,687.)
    head_J_kg: tuple=(941484.,1213000.,933924.,823743.)
    motor_MW: tuple=(35.,14.,11.,18.)
    rated_pressure_Pa: tuple=(2000.,10000.,30000.,6500.)
    coast_suction_m3_s: float=500.
    coast_suction_fractions: tuple=(1.,.25,.0625)
    coast_head_J_kg: float=5e6
    coast_motor_MW: float=30.
    plant_flow_kg_s: float=4.
    plant_electric_MW: float=40.
    precool_UA_W_K: float=200000.
    condenser_UA_W_K: float=250000.
    solar_area_m2: float=2e6
    battery_MWh: float=440.
    battery_MW: float=1600.
    bus_MW: float=1000.
    warm_radiator_m2: float=40000.
    warm_store_kg: float=600000.
    warm_initial_K: float=340.
    warm_max_K: float=450.
    battery_initial_soc: float=.8
    isp_s: float=1765.95
    burn_s: float=1200.
    liquid_tank_m3: float=20.
    reserve_kg: float=4500.
    mixing_ratio: float=0.
    plant_start_s: float=650.
    plant_stop_s: float=4200.
    pump_stop_s: float=600.
    cutoff_Pa: float=.1
    max_step_s: float=10.
    rtol: float=2e-5
    max_rhs_evaluations: int=250000
    jacobian_relative_step: float=1e-6

@dataclass(frozen=True)
class Capabilities:
    skin_friction_coefficient: float=0.
    skin_area_multiplier: float=1.
    eta_compressor: float=.75
    eta_motor: float=.95
    eta_thruster: float=.6
    retained_thruster_loss: float=.2
    thruster_kg_kW: float=2.
    bus_kg_kW: float=1.
    solar_W_m2: float=250.
    solar_W_kg: float=150.
    battery_Wh_kg: float=150.
    battery_W_kg: float=1500.
    battery_usable: float=.8
    charge_eta: float=.95
    discharge_eta: float=.95
    buffer_cp_J_kg_K: float=2000.
    radiator_kg_m2: float=5.
    radiator_emissivity: float=.85
    radiator_view: float=.8
    rack_view: float=.7
    environment_W_m2: float=80.
    deployment_m_s: float=10.
    machinery_kg_m3: float=250.
    fill_fraction: float=.7
    margin: float=.25
    idle_fraction: float=.01
    spin_s: float=120.
    brake_s: float=30.
    vacuum_regularization_kg: float=.001
    carnot_fraction: float=.15
    separation_J_kg: float=250000.
    auxiliary_W: float=10000.
    tank_heat_W: float=1000.
    heat_pump_kg_W_equivalent: float=.25
    exchanger_UA_per_kg: float=200.
    head_depth_m: float=1.5
    rack_mechanism_kg_m2: float=1.
    upper_gas_K: float=2000.

def read_config(config):
    unknown=set(config)-{'design','capabilities'}
    if unknown:raise ValueError(f'Unknown sections: {unknown}')
    def make(cls,name):
        data=config.get(name,{})
        if set(data)-{f.name for f in fields(cls)}:raise ValueError(f'Unknown {name} inputs')
        obj=cls(**data)
        for k,v in asdict(obj).items():
            if k=='materials':continue
            values=v if isinstance(v,(tuple,list)) else (v,)
            if any(not isinstance(z,(int,float)) or isinstance(z,bool) or not math.isfinite(z) or z<0 for z in values):raise ValueError(f'Invalid {name}.{k}')
        return obj
    d,c=make(Design,'design'),make(Capabilities,'capabilities')
    if any(len(getattr(d,k))!=n for k,n in [('rack_depth_m',5),('clear_depth_m',4),('rack_initial_K',5),('materials',5),('suction_m3_s',4),('head_J_kg',4),('motor_MW',4),('rated_pressure_Pa',4)]):raise ValueError('Invalid stage count')
    if (d.bore_m,d.clearance_m,d.length_diameter)!=(30.,.85,10.):raise ValueError('This release fixes 30 m bore / 31.7 m outside / 317 m length')
    if d.rod_pitch_m<=0 or not 0<d.rod_radius_m/d.rod_pitch_m<.25:raise ValueError('Invalid lattice')
    if not .2<d.battery_initial_soc<1 or min(d.max_step_s,d.rtol,d.warm_store_kg,d.battery_MWh,d.isp_s,d.burn_s)<=0:raise ValueError('Invalid integration/capacity')
    if any(v<=0 for v in (*d.rack_depth_m,*d.suction_m3_s,*d.head_J_kg,*d.motor_MW)):raise ValueError('Positive installed bank/rack required')
    if not all(0<z<=1 for z in (c.eta_compressor,c.eta_motor,c.eta_thruster,c.charge_eta,c.discharge_eta,c.fill_fraction)):raise ValueError('Invalid efficiency')
    if d.perigee_km!=85 or d.apogee_km<=250:raise ValueError('Initial molecular-air release fixes 85 km perigee; apogee must exceed 250 km')
    if len(d.coast_suction_fractions)!=3 or any(z<=0 for z in d.coast_suction_fractions):raise ValueError('Three positive coast suction fractions required')
    if not 0<d.pump_stop_s<d.plant_start_s<d.plant_stop_s:raise ValueError('Invalid processing schedule')
    if d.warm_max_K<=d.warm_initial_K:raise ValueError('Warm-store operating range must be positive')
    if not 0<c.battery_usable<1 or d.battery_initial_soc<=1-c.battery_usable:raise ValueError('Invalid initial usable battery reserve')
    if min(c.spin_s,c.brake_s,c.vacuum_regularization_kg,c.deployment_m_s,c.machinery_kg_m3,c.buffer_cp_J_kg_K,c.battery_Wh_kg,c.battery_W_kg,c.solar_W_kg,c.carnot_fraction,c.exchanger_UA_per_kg,d.coast_suction_m3_s,d.coast_head_J_kg,d.coast_motor_MW,d.liquid_tank_m3,d.cutoff_Pa)<=0:raise ValueError('Positive capacity/capability required')
    if d.jacobian_relative_step<=0:raise ValueError('Positive Jacobian differencing step required')
    if not isinstance(d.max_rhs_evaluations,int) or isinstance(d.max_rhs_evaluations,bool) or d.max_rhs_evaluations<1:raise ValueError('Positive integer RHS budget required')
    return d,c

def defaults():return dict(design=asdict(Design()),capabilities=asdict(Capabilities()))
