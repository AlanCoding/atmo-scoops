"""Public, side-effect-free inputs -> system outputs API for the scoop cycle.

Design choices, hardware capabilities and environmental assumptions are separate.
The pressure/access screens are necessary conditions, not an inlet validation.
"""
from dataclasses import dataclass, asdict, fields, replace
import math

from .two_volume import Reference, calculate
from .physical_cycle import Hardware, rear_geometry, evaluate
from .process import ProcessTargets
from .mixing import Mixing, validate as validate_mixing
from .inlet import FlowCapabilities, EncounterControls, ContinuousEncounter


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
    compressor_inlet_K: float = 1000.  # Dry stream; optional mixing solves actual inlet.
    metal_cold_K: float = 500.
    gas_metal_approach_K: float = 100.
    foil_thickness_m: float = .00025
    inlet_pressure_fraction: float = .7
    pump_suction_m3_s: float | None = None  # None means size from pressure target.
    intermediate_Pa: float = 300.
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


@dataclass(frozen=True)
class Scenario:
    atmosphere_name: str = 'reference'
    total_impulse_over_capture: float = 1.


def defaults():
    return dict(design=asdict(Design()),hardware=asdict(Hardware()),
                performance=asdict(Performance()),process=asdict(ProcessTargets()),scenario=asdict(Scenario()),flow=asdict(FlowCapabilities()),controls=asdict(EncounterControls()),mixing=asdict(Mixing()))


def inputs_from_dict(config):
    if not isinstance(config,dict):raise ValueError('Configuration must be a JSON object')
    names={'design':Design,'hardware':Hardware,'performance':Performance,'process':ProcessTargets,'scenario':Scenario,'flow':FlowCapabilities,'controls':EncounterControls,'mixing':Mixing}
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
            if k=='pump_suction_m3_s' and v is None:continue
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
                raise ValueError(f'{label}.{k} must be finite and nonnegative')
            if v==0 and k not in ('design_margin','rear_support_fraction','machinery_depth_m','radial_clearance_m','auxiliary_W','thruster_loss_retained'):
                raise ValueError(f'{label}.{k} must be positive')
    d=design
    if not 75<=d.perigee_km<d.apogee_km or d.apogee_km<=200:
        raise ValueError('Require 75 km <= perigee < apogee and apogee > 200 km')
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
    rear_geometry(d.rear_depth_m,d.rear_diameter_m)


def simulate(design=Design(),hardware=Hardware(),performance=Performance(),scenario=Scenario(),process=ProcessTargets(),flow=FlowCapabilities(),controls=EncounterControls(),mixing=Mixing(),n=801,history=False):
    """Return serialized inputs, outputs and named constraint residuals.

    No file writes. Positive constraint margins pass their local screen;
    unresolved shock/heat-transfer/structure constraints are listed separately.
    """
    validate(design,hardware,performance,scenario,process)
    validate_mixing(mixing)
    if isinstance(n,bool) or not isinstance(n,int) or n<101:raise ValueError('n must be an integer >= 101')
    d=design
    geom=rear_geometry(d.rear_depth_m,d.rear_diameter_m)
    base=replace(Reference(),**asdict(performance),**asdict(scenario),
        mouth_m=d.mouth_diameter_m,front_bore_m=d.front_diameter_m,front_length_m=d.front_depth_m,
        receiver_m3=geom['volume_m3'],receiver_K=d.warm_radiator_K+process.reject_approach_K,
        total_length_m=d.front_depth_m+d.rear_depth_m+d.machinery_depth_m,
        outside_diameter_m=max(d.mouth_diameter_m,d.front_diameter_m,d.rear_diameter_m)+2*d.radial_clearance_m,
        perigee_km=d.perigee_km,apogee_km=d.apogee_km,
        gas_K=d.compressor_inlet_K,metal_cold_K=d.metal_cold_K,
        metal_hot_K=d.compressor_inlet_K-d.gas_metal_approach_K,foil_thickness_m=d.foil_thickness_m,
        inlet_pressure_fraction=d.inlet_pressure_fraction,open_suction_override_m3_s=d.pump_suction_m3_s,
        intermediate_Pa=d.intermediate_Pa,
        warm_radiator_K=d.warm_radiator_K,thrust_burst_s=d.thrust_burst_s,exhaust_m_s=d.isp_s*9.80665)
    solver=ContinuousEncounter(flow,controls)
    r=calculate(base,n=n,process_targets=process,flow_solver=solver,mixing=mixing)
    out=evaluate(r,d.front_depth_m,d.rear_depth_m,hardware,rear_diameter_m=d.rear_diameter_m)
    out['mixing']=r['mixing']
    out['compressor_inlet_K']=r['inputs']['gas_K']
    out['metal_hot_K']=base.metal_hot_K
    out['metal_capacity_kJ_kg']=r['metal_capacity_J_kg']/1000
    out['intake_and_front_storage_heat_GJ']=r['intake_and_front_storage_heat_J']/1e9
    out['hot_compression_heat_GJ']=r['hot_compression_J']/1e9
    out['thermal_energy_balance_residual_J']=float(r['through_recovery_energy_residual_J'])
    out['front_pressure_target_ratio_actual']=r['max_front_over_ram']
    out['operating_mass_payoff_days']=(out['total_dry_kg']/out['net_liquid_equivalent_kg_day']
        if out['net_liquid_equivalent_kg_day']>0 else None)
    out['delivered_mass_payoff_days']=None  # Circular-apogee delivery is unresolved.
    margins=dict(
        compressor_access_m2=out['available_compressor_open_area_m2']-out['required_compressor_open_area_m2'],
        oxygen_kg=out['oxygen_mass_margin_kg'],
        metal_radiation_time_s=r['deployed_coast_s']-out['ideal_metal_cooldown_s'],
        positive_production_kg=out['net_liquid_equivalent_kg'])
    margins['cutoff_Pa']=controls.cutoff_Pa-r['final_front_Pa']
    margins['coolant_replacement_kg']=r['mixing']['nitrogen_available_kg']-r['mixing']['coolant_replacement_kg']
    out['total_with_working_fluids_kg']=out['total_with_loop_fluid_kg']+r['mixing']['injected_kg']
    for key in ('capture_impulse','escape_impulse','uncollected_mouth_impulse','geometric_intercept_impulse'):
        out[key+'_Ns']=solver.last[key]
    out['effective_ultimate_Pa']=solver.last['ultimate_Pa']
    out['final_front_pressure_Pa']=r['final_front_Pa']
    result=dict(status='Conditional continuous-inlet cycle; no shock validation or circular-delivery payoff',
        inputs=dict(design=asdict(d),hardware=asdict(hardware),performance=asdict(performance),
            process=asdict(process),scenario=asdict(scenario),flow=asdict(flow),controls=asdict(controls),mixing=asdict(mixing)),
        outputs=out,constraints=dict(margins=margins,
            all_implemented_screens_pass=bool(all(v>=-1e-8 for v in margins.values()) and solver.last['stop_reason']=='cutoff_pressure'),
            unresolved=['Shock position/start margin and calibrated capture/leakage coefficients',
                'Gas-to-metal conductance, rack pressure loss and temperature distribution',
                'Compressor performance map, spin-up and installed mass capability',
                'Hull drag, structural/dynamic loads and deployable mechanisms',
                'Finite-thrust orbit restoration and circular-apogee export']),
        resolved_cycle_inputs=r['inputs'],numerics=dict(samples=n))
    if history:result['history']=solver.last['history']
    return result
