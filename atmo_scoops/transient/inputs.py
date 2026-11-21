"""Installed capacities, controls and initial state; no cycle-dependent sizing."""
from dataclasses import dataclass,asdict,fields
import math
@dataclass(frozen=True)
class Design:
    perigee_km: float=85.
    apogee_km: float=2000.
    inlet_ceiling_km: float=250.
    inlet_taper_km: float=50.
    bore_m: float=30.
    clearance_m: float=.85
    length_diameter: float=10.
    rack_depth_m: tuple=(5.42,.40,.18,.20,.32)
    clear_depth_m: tuple=(0.,0.,0.,0.)
    rack_initial_K: tuple=(330.,330.,330.,330.,330.)
    materials: tuple=('sic','aluminum','aluminum','aluminum','aluminum')
    rod_radius_m: float=.001
    rod_pitch_m: float=.01
    stage_pitch_m: tuple=()
    stage_radius_m: tuple=()
    plate_thickness_m: tuple=(.001,)*5
    plate_gap_m: tuple=(.003,)*5
    chamber_initial_pressure_Pa: float=.001
    plate_thermal_model: str="developing"
    plate_rows: tuple=(1,1,1,1,1)
    plate_offset_fraction: float=.5
    plate_row_clearance_m: float=0.
    explicit_stage_packing: int=0
    stage_hatch_buffer_m: float=0.
    rack_flow_layout: str="legacy_mixed"
    rack_pressure_model: str="layout"
    rack_loss_mode: str="pressure"
    propellant_storage: str="liquid"
    gas_volume_m3: float=500.
    gas_reserve_kg: float=4500.
    gas_initial_K: float=340.
    gas_initial_fractions: tuple=(.755,.232,.013)
    gas_rated_Pa: float=1.5e6
    gas_feed_min_Pa: float=100000.
    gas_feed_max_kg_s: float=5.
    gas_tank_count: int=4
    gas_fill_suction_m3_s: float=10.
    gas_fill_head_J_kg: float=1.5e6
    gas_fill_motor_MW: float=5.
    gas_fill_UA_W_K: float=50000.
    gas_thermal_UA_W_K: float=50000.
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
    vent_duration_s: float=120.
    cutoff_Pa: float=.1
    compression_model: str="HEOS"
    integrator: str="BDF"
    atol: float=1e-7
    max_step_s: float=10.
    integration_segment_s: float=0.
    rtol: float=2e-5
    early_reject: int=0
    max_rhs_evaluations: int=250000
    jacobian_relative_step: float=1e-6
    jacobian_absolute_step: float=0.

@dataclass(frozen=True)
class Capabilities:
    plate_entrance_credit: float=1.
    plate_restart_loss_K: float=.674
    rack_loss_multiplier: float=0.
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
            if k in ('materials','propellant_storage','rack_flow_layout','rack_pressure_model','rack_loss_mode','integrator','compression_model','plate_thermal_model'):continue
            values=v if isinstance(v,(tuple,list)) else (v,)
            if any(not isinstance(z,(int,float)) or isinstance(z,bool) or not math.isfinite(z) or z<0 for z in values):raise ValueError(f'Invalid {name}.{k}')
        return obj
    d,c=make(Design,'design'),make(Capabilities,'capabilities')
    if any(len(getattr(d,k))!=n for k,n in [('rack_depth_m',5),('clear_depth_m',4),('rack_initial_K',5),('materials',5),('suction_m3_s',4),('head_J_kg',4),('motor_MW',4),('rated_pressure_Pa',4)]):raise ValueError('Invalid stage count')
    if (d.bore_m,d.clearance_m,d.length_diameter)!=(30.,.85,10.):raise ValueError('This release fixes 30 m bore / 31.7 m outside / 317 m length')
    if d.rod_pitch_m<=0 or not 0<d.rod_radius_m/d.rod_pitch_m<(.5 if d.rack_flow_layout=='inline_bank' else .25):raise ValueError('Invalid lattice')
    if not .2<d.battery_initial_soc<1 or min(d.max_step_s,d.rtol,d.warm_store_kg,d.battery_MWh,d.isp_s,d.burn_s)<=0:raise ValueError('Invalid integration/capacity')
    if any(v<=0 for v in (*d.rack_depth_m,*d.suction_m3_s,*d.head_J_kg,*d.motor_MW)):raise ValueError('Positive installed bank/rack required')
    if not all(0<z<=1 for z in (c.eta_compressor,c.eta_motor,c.eta_thruster,c.charge_eta,c.discharge_eta,c.fill_fraction)):raise ValueError('Invalid efficiency')
    if d.perigee_km!=85 or d.apogee_km<=250:raise ValueError('Initial molecular-air release fixes 85 km perigee; apogee must exceed 250 km')
    if len(d.coast_suction_fractions)!=3 or any(z<=0 for z in d.coast_suction_fractions):raise ValueError('Three positive coast suction fractions required')
    if not 0<d.pump_stop_s<d.plant_start_s<d.plant_stop_s:raise ValueError('Invalid processing schedule')
    if d.warm_max_K<=d.warm_initial_K:raise ValueError('Warm-store operating range must be positive')
    if not 0<c.battery_usable<1 or d.battery_initial_soc<=1-c.battery_usable:raise ValueError('Invalid initial usable battery reserve')
    if min(c.spin_s,c.brake_s,c.vacuum_regularization_kg,c.deployment_m_s,c.machinery_kg_m3,c.buffer_cp_J_kg_K,c.battery_Wh_kg,c.battery_W_kg,c.solar_W_kg,c.carnot_fraction,c.exchanger_UA_per_kg,d.coast_suction_m3_s,d.coast_head_J_kg,d.coast_motor_MW,d.liquid_tank_m3,d.cutoff_Pa)<=0:raise ValueError('Positive capacity/capability required')
    if min(d.jacobian_relative_step,d.atol,d.vent_duration_s)<=0:raise ValueError('Positive numerical steps and vent duration required')
    if d.early_reject not in (0,1):raise ValueError('early_reject must be 0 or 1')
    if d.integration_segment_s!=0 and not d.integration_segment_s>=1:raise ValueError('Integration segments must be zero (events only) or at least one second')
    if not isinstance(d.max_rhs_evaluations,int) or isinstance(d.max_rhs_evaluations,bool) or d.max_rhs_evaluations<1:raise ValueError('Positive integer RHS budget required')
    if d.propellant_storage not in ('liquid','gas') or d.rack_flow_layout not in ('legacy_mixed','outlet_planes','inline_bank','parallel_plates'):raise ValueError('Unknown feed/rack architecture')
    radii=d.stage_radius_m or [d.rod_radius_m]*5
    pitches=d.stage_pitch_m or [d.rod_pitch_m]*5
    if len(radii)!=5 or len(pitches)!=5:raise ValueError('Five radii and pitches required')
    if any(r<.0002*(1-1e-12) for r in radii):raise ValueError('Rod radius must be at least 0.2 mm')
    limit=2.5 if d.rack_flow_layout=='inline_bank' else 4.
    if any(p<limit*r*(1-1e-12) or r<=0 for p,r in zip(pitches,radii)):raise ValueError('Invalid stage radius/pitch')
    if not 0<d.inlet_taper_km<d.inlet_ceiling_km-d.perigee_km:raise ValueError('Invalid inlet taper')
    if d.compression_model not in ('HEOS','HEOS_table'):raise ValueError('Unknown compression model')
    if d.integrator not in ('BDF','BDF_auto','LSODA'):raise ValueError('Unknown integrator')
    if d.rack_loss_mode not in ('pressure','power_only'):raise ValueError('Unknown rack loss mode')
    if d.rack_pressure_model not in ('layout','inline_laminar'):raise ValueError('Unknown rack pressure model')
    if c.rack_loss_multiplier and d.rack_flow_layout not in ('outlet_planes','inline_bank','parallel_plates') and d.rack_pressure_model!='inline_laminar':raise ValueError('Rack loss requires the outlet-plane geometry or explicit inline pressure model')
    if len(d.gas_initial_fractions)!=3 or abs(sum(d.gas_initial_fractions)-1)>1e-9:raise ValueError('Gas fractions must sum to one')
    if d.propellant_storage=='gas':
        if min(d.gas_volume_m3,d.gas_reserve_kg,d.gas_initial_K,d.gas_feed_min_Pa,d.gas_feed_max_kg_s,d.gas_fill_suction_m3_s,d.gas_fill_head_J_kg,d.gas_fill_motor_MW,d.gas_fill_UA_W_K,d.gas_thermal_UA_W_K)<=0:raise ValueError('Positive gas-feed capacities required')
        if not isinstance(d.gas_tank_count,int) or d.gas_tank_count<1:raise ValueError('Positive integer gas tank count required')
        if d.gas_rated_Pa<=d.gas_feed_min_Pa:raise ValueError('Gas pressure rating below regulator minimum')
    if d.rack_flow_layout=='parallel_plates':
        if d.rack_loss_mode!='power_only' or d.rack_pressure_model!='layout':raise ValueError('Plates currently require power_only mode and layout pressure model')
        if len(d.plate_thickness_m)!=5 or len(d.plate_gap_m)!=5 or min(*d.plate_thickness_m,*d.plate_gap_m)<=0:raise ValueError('Five positive plate thicknesses and gaps required')
    if d.plate_thermal_model not in ('developing','offset_equivalent'):raise ValueError('Unknown plate thermal model')
    if len(d.plate_rows)!=5 or any(not isinstance(n,int) or isinstance(n,bool) or n<1 for n in d.plate_rows):raise ValueError('Five positive integer plate row counts required')
    if not 0<=d.plate_offset_fraction<=.5 or not 0<=c.plate_entrance_credit<=1:raise ValueError('Invalid plate offset/entrance credit')
    if d.explicit_stage_packing not in (0,1):raise ValueError('explicit_stage_packing must be 0 or 1')
    if (max(d.plate_rows)>1 or d.explicit_stage_packing) and d.rack_flow_layout!='parallel_plates':raise ValueError('Explicit row/packing study requires plates')
    if d.plate_thermal_model=='offset_equivalent':
        if d.rack_flow_layout!='parallel_plates':raise ValueError('Offset-equivalent spacing requires plates')
        if any((g+t)/n<=t for g,t,n in zip(d.plate_gap_m,d.plate_thickness_m,d.plate_rows)):raise ValueError('Nonpositive effective thermal gap')
    return d,c

def defaults():return dict(design=asdict(Design()),capabilities=asdict(Capabilities()))
