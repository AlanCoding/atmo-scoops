"""Public, side-effect-free inputs -> system outputs API for the scoop cycle.

Design choices, hardware capabilities and environmental assumptions are separate.
The pressure/access screens are necessary conditions, not an inlet validation.
"""
from dataclasses import dataclass, asdict, fields, replace
import math

from .two_volume import Reference, calculate
from .physical_cycle import Hardware, rear_geometry, evaluate
from .process import ProcessTargets


@dataclass(frozen=True)
class Design:
    # Comparison coordinates, not optimized dimensions.
    front_depth_m: float = 250.
    rear_depth_m: float = 25.
    mouth_diameter_m: float = 18.3
    front_diameter_m: float = 18.3
    rear_diameter_m: float = 18.3
    machinery_depth_m: float = 20.
    radial_clearance_m: float = .85
    perigee_km: float = 100.
    apogee_km: float = 2000.
    opening_ram_fraction: float = .5
    compressor_inlet_K: float = 1000.
    metal_cold_K: float = 500.
    gas_metal_approach_K: float = 100.
    foil_thickness_m: float = .00025
    inlet_pressure_fraction: float = .7
    pump_suction_m3_s: float | None = None  # None means size from pressure target.
    intermediate_Pa: float = 300.
    recovery_s: float = 450.
    front_residual_fraction: float = .1
    mouth_closure: bool = True
    warm_radiator_K: float = 320.
    thrust_burst_s: float = 180.
    isp_s: float = 4000.


@dataclass(frozen=True)
class Performance:
    # Capability assumptions; do not let an optimizer invent better technology.
    isothermal_efficiency: float = .5
    motor_efficiency: float = .95
    deploy_s: float = 300.
    retract_s: float = 300.
    metal_density_kg_m3: float = 7870.
    hot_emissivity: float = .8
    solar_W_m2: float = 250.
    solar_W_kg: float = 150.
    warm_buffer_J_kg: float = 200000.
    battery_Wh_kg: float = 150.
    battery_usable: float = .8
    battery_W_kg: float = 1500.
    battery_charge_efficiency: float = .95
    battery_discharge_efficiency: float = .95
    thruster_efficiency: float = .6
    thruster_loss_retained: float = .2
    auxiliary_W: float = 10000.
    compressor_min_inlet_Pa: float = .1  # Capability floor, not a measured pump map.


@dataclass(frozen=True)
class Scenario:
    atmosphere_name: str = 'reference'
    total_impulse_over_capture: float = 1.
    open_mouth_support_over_ram: float = 1.
    open_mouth_discharge_coefficient: float = .8


def defaults():
    return dict(design=asdict(Design()),hardware=asdict(Hardware()),
                performance=asdict(Performance()),process=asdict(ProcessTargets()),scenario=asdict(Scenario()))


def inputs_from_dict(config):
    if not isinstance(config,dict):raise ValueError('Configuration must be a JSON object')
    names={'design':Design,'hardware':Hardware,'performance':Performance,'process':ProcessTargets,'scenario':Scenario}
    unknown=set(config)-set(names)
    if unknown:raise ValueError(f'Unknown configuration sections: {sorted(unknown)}')
    out={}
    for section,cls in names.items():
        values=config.get(section,{})
        if not isinstance(values,dict):raise ValueError(f'{section} must be an object')
        unknown=set(values)-{f.name for f in fields(cls)}
        if unknown:raise ValueError(f'Unknown {section} inputs: {sorted(unknown)}')
        out[section]=cls(**values)
    return out


def validate(design,hardware,performance,scenario,process):
    for label,obj in [('design',design),('hardware',hardware),('performance',performance),('process',process)]:
        for k,v in asdict(obj).items():
            if k=='mouth_closure':
                if not isinstance(v,bool):raise ValueError('mouth_closure must be boolean')
                continue
            if k=='pump_suction_m3_s' and v is None:continue
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
                raise ValueError(f'{label}.{k} must be finite and nonnegative')
            if v==0 and k not in ('design_margin','rear_support_fraction','machinery_depth_m','radial_clearance_m','auxiliary_W','thruster_loss_retained'):
                raise ValueError(f'{label}.{k} must be positive')
    d=design
    if not 75<=d.perigee_km<d.apogee_km or d.apogee_km<=200:
        raise ValueError('Require 75 km <= perigee < apogee and apogee > 200 km')
    for key in ('opening_ram_fraction','front_residual_fraction'):
        if not 0<getattr(d,key)<1:raise ValueError(f'{key} must lie strictly between 0 and 1')
    if not 0<d.inlet_pressure_fraction<=1:raise ValueError('Pressure target must be in (0,1]')
    hot=d.compressor_inlet_K-d.gas_metal_approach_K
    if not 298<=d.metal_cold_K<hot<=1042:
        raise ValueError('Metal requires 298 <= cold < inlet gas - approach <= 1042 K (implemented Fe property range)')
    if d.compressor_inlet_K<=d.warm_radiator_K+process.reject_approach_K:
        raise ValueError('Compressor inlet must exceed the warm receiver temperature')
    for key in ('isothermal_efficiency','motor_efficiency','hot_emissivity','battery_usable',
                'battery_charge_efficiency','battery_discharge_efficiency','thruster_efficiency','thruster_loss_retained'):
        if getattr(performance,key)>1:raise ValueError(f'{key} cannot exceed 1')
    if hardware.compressor_open_fraction>1 or hardware.access_discharge_coefficient>1:
        raise ValueError('Compressor open fraction and discharge coefficient cannot exceed 1')
    for key in ('carnot_fraction','emissivity','view_factor'):
        if getattr(process,key)>1:raise ValueError(f'process.{key} cannot exceed 1')
    if scenario.atmosphere_name not in ('reference','quiet','active','winter_midnight'):
        raise ValueError('Unknown atmosphere scenario')
    multiplier=scenario.total_impulse_over_capture
    if isinstance(multiplier,bool) or not isinstance(multiplier,(int,float)) or not math.isfinite(multiplier) or multiplier<1:
        raise ValueError('Total impulse multiplier must be finite and >= 1; captured momentum cannot be removed')
    for key in ('open_mouth_support_over_ram','open_mouth_discharge_coefficient'):
        v=getattr(scenario,key)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<v<=1:
            raise ValueError(f'{key} must be finite and in (0,1]')
    rear_geometry(d.rear_depth_m,d.rear_diameter_m)


def simulate(design=Design(),hardware=Hardware(),performance=Performance(),scenario=Scenario(),process=ProcessTargets(),n=801):
    """Return serialized inputs, outputs and named constraint residuals.

    No file writes. Positive constraint margins pass their local screen;
    unresolved shock/heat-transfer/structure constraints are listed separately.
    """
    validate(design,hardware,performance,scenario,process)
    if isinstance(n,bool) or not isinstance(n,int) or n<101:raise ValueError('n must be an integer >= 101')
    d=design
    geom=rear_geometry(d.rear_depth_m,d.rear_diameter_m)
    base=replace(Reference(),**asdict(performance),**asdict(scenario),
        mouth_m=d.mouth_diameter_m,front_bore_m=d.front_diameter_m,front_length_m=d.front_depth_m,
        receiver_m3=geom['volume_m3'],receiver_K=d.warm_radiator_K+process.reject_approach_K,
        total_length_m=d.front_depth_m+d.rear_depth_m+d.machinery_depth_m,
        outside_diameter_m=max(d.mouth_diameter_m,d.front_diameter_m,d.rear_diameter_m)+2*d.radial_clearance_m,
        perigee_km=d.perigee_km,apogee_km=d.apogee_km,opening_ram_fraction=d.opening_ram_fraction,
        gas_K=d.compressor_inlet_K,metal_cold_K=d.metal_cold_K,
        metal_hot_K=d.compressor_inlet_K-d.gas_metal_approach_K,foil_thickness_m=d.foil_thickness_m,
        inlet_pressure_fraction=d.inlet_pressure_fraction,open_suction_override_m3_s=d.pump_suction_m3_s,
        intermediate_Pa=d.intermediate_Pa,recovery_s=d.recovery_s,front_residual_fraction=d.front_residual_fraction,
        mouth_closure=d.mouth_closure,
        warm_radiator_K=d.warm_radiator_K,thrust_burst_s=d.thrust_burst_s,exhaust_m_s=d.isp_s*9.80665)
    r=calculate(base,n=n,process_targets=process)
    out=evaluate(r,d.front_depth_m,d.rear_depth_m,hardware,rear_diameter_m=d.rear_diameter_m)
    out['metal_hot_K']=base.metal_hot_K
    out['metal_capacity_kJ_kg']=r['metal_capacity_J_kg']/1000
    out['intake_and_front_storage_heat_GJ']=r['intake_and_front_storage_heat_J']/1e9
    out['hot_compression_heat_GJ']=r['hot_compression_J']/1e9
    out['thermal_energy_balance_residual_J']=float(r['through_recovery_energy_residual_J'])
    out['front_pressure_target_ratio_actual']=r['max_front_over_ram']
    out['operating_mass_payoff_days']=(out['total_dry_kg']/out['net_liquid_equivalent_kg_day']
        if out['net_liquid_equivalent_kg_day']>0 else None)
    out['delivered_mass_payoff_days']=None  # Circular-apogee delivery is unresolved.
    margins=dict(front_pressure_ratio=d.inlet_pressure_fraction-r['max_front_over_ram'],
        compressor_access_m2=out['available_compressor_open_area_m2']-out['required_compressor_open_area_m2'],
        oxygen_kg=out['oxygen_mass_margin_kg'],
        metal_radiation_time_s=r['deployed_coast_s']-out['ideal_metal_cooldown_s'],
        positive_production_kg=out['net_liquid_equivalent_kg'])
    if not d.mouth_closure:
        margins['open_pump_pressure_floor_Pa']=performance.compressor_min_inlet_Pa-r['final_front_Pa']
        margins['inbound_support_ratio']=scenario.open_mouth_support_over_ram-r['max_front_over_ram']
    return dict(status='Conditional current-architecture cycle; no shock validation or circular-delivery payoff',
        inputs=dict(design=asdict(d),hardware=asdict(hardware),performance=asdict(performance),process=asdict(process),scenario=asdict(scenario)),
        outputs=out,constraints=dict(margins=margins,all_implemented_screens_pass=all(v>=-1e-8 for v in margins.values()),
            unresolved=['Shock position/start margin and actual capture',
                'Open-mouth pressure support, admission and leakage coefficients',
                'Gas-to-metal conductance, rack pressure loss and temperature distribution',
                'Compressor performance map, spin-up and installed mass capability',
                'Hull drag, structural/dynamic loads and deployable mechanisms',
                'Finite-thrust orbit restoration and circular-apogee export']),
        resolved_cycle_inputs=asdict(base),numerics=dict(samples=n))
