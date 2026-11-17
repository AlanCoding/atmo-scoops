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
from .compressor import Compressor
from .racks import Racks
from .ammonia import AmmoniaCooling,install as install_ammonia
from .packaging import Packaging,allocation


@dataclass(frozen=True)
class Design:
    # Comparison coordinates, not optimized dimensions.
    front_depth_m: float = 250.
    rear_depth_m: float = 25.
    mouth_diameter_m: float = 18.3
    front_diameter_m: float = 18.3
    rear_diameter_m: float = 18.3
    machinery_depth_m: float = 100.  # Explicit allowance for resolved compressor banks; not optimized.
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
    deploy_s: float = 0.
    retract_s: float = 0.
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
    allow_nitrogen_propellant: bool = False


def defaults():
    return dict(design=asdict(Design()),hardware=asdict(Hardware()),
                performance=asdict(Performance()),process=asdict(ProcessTargets()),scenario=asdict(Scenario()),flow=asdict(FlowCapabilities()),controls=asdict(EncounterControls()),mixing=asdict(Mixing()),compressor=asdict(Compressor()),racks=asdict(Racks()),packaging=asdict(Packaging()),ammonia=asdict(AmmoniaCooling()))


def inputs_from_dict(config):
    if not isinstance(config,dict):raise ValueError('Configuration must be a JSON object')
    names={'design':Design,'hardware':Hardware,'performance':Performance,'process':ProcessTargets,'scenario':Scenario,'flow':FlowCapabilities,'controls':EncounterControls,'mixing':Mixing,'compressor':Compressor,'racks':Racks,'packaging':Packaging,'ammonia':AmmoniaCooling}
    unknown=set(config)-set(names)
    if unknown:raise ValueError(f'Unknown configuration sections: {sorted(unknown)}')
    out={}
    for section,cls in names.items():
        values=config.get(section,{})
        if not isinstance(values,dict):raise ValueError(f'{section} must be an object')
        unknown=set(values)-{f.name for f in fields(cls)}
        if unknown:raise ValueError(f'Unknown {section} inputs: {sorted(unknown)}')
        if section=='racks':
            values={k:tuple(v) if k in ('masses_kg','mass_factors','pcm_materials','wire_radii_m') else v for k,v in values.items()}
        if section=='ammonia':values={k:tuple(v) if k in ('areas_m2','maximum_flows_kg_s','inventories_kg') else v for k,v in values.items()}
        out[section]=cls(**values)
    return out


def validate(design,hardware,performance,scenario,process):
    for label,obj in [('design',design),('hardware',hardware),('performance',performance),('process',process)]:
        for k,v in asdict(obj).items():
            if k=='pump_suction_m3_s' and v is None:continue
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
                raise ValueError(f'{label}.{k} must be finite and nonnegative')
            if v==0 and k not in ('deploy_s','retract_s','design_margin','rear_support_fraction','machinery_depth_m','radial_clearance_m','auxiliary_W','thruster_loss_retained'):
                raise ValueError(f'{label}.{k} must be positive')
    d=design
    if not 50<=d.perigee_km<d.apogee_km or d.apogee_km<=200:
        raise ValueError('Require 50 km <= perigee < apogee and apogee > 200 km')
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
    if not isinstance(scenario.allow_nitrogen_propellant,bool):raise ValueError('allow_nitrogen_propellant must be boolean')
    multiplier=scenario.total_impulse_over_capture
    if isinstance(multiplier,bool) or not isinstance(multiplier,(int,float)) or not math.isfinite(multiplier) or multiplier<1:
        raise ValueError('Total impulse multiplier must be finite and >= 1; captured momentum cannot be removed')
    rear_geometry(d.rear_depth_m,d.rear_diameter_m)


def simulate(design=Design(),hardware=Hardware(),performance=Performance(),scenario=Scenario(),process=ProcessTargets(),flow=FlowCapabilities(),controls=EncounterControls(),mixing=Mixing(),compressor=Compressor(),racks=Racks(),packaging=Packaging(),ammonia=AmmoniaCooling(),n=801,history=False):
    """Return serialized inputs, outputs and named constraint residuals.

    No file writes. Positive constraint margins pass their local screen;
    unresolved shock/heat-transfer/structure constraints are listed separately.
    """
    validate(design,hardware,performance,scenario,process)
    validate_mixing(mixing)
    compressor.validate()
    racks.validate(compressor.blocks);packaging.validate()
    if isinstance(n,bool) or not isinstance(n,int) or n<101:raise ValueError('n must be an integer >= 101')
    ammonia.validate(compressor.blocks)
    if ammonia.enabled:
        if not racks.enabled or any(x!='none' for x in (racks.pcm_materials or (racks.pcm_material,))):raise ValueError('Ammonia requires finite racks without simultaneous PCM')
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
    r=calculate(base,n=n,process_targets=process,flow_solver=solver,mixing=mixing,compressor=compressor,racks=racks,ammonia=ammonia)
    out=evaluate(r,r['inputs']['front_length_m'],d.rear_depth_m,hardware,rear_diameter_m=d.rear_diameter_m)
    if ammonia.enabled:install_ammonia(out,r,ammonia,hardware,performance)
    if racks.enabled and packaging.enabled:
        # Fixed-point deployment sizing: no production/rejection credit during motion.
        for iteration in range(30):
            packed=allocation(out,r,d,hardware,performance,compressor,packaging)
            required=max(performance.deploy_s,performance.retract_s,packed['required_motion_s'])
            if required<=base.deploy_s*(1+1e-4):break
            base=replace(base,deploy_s=required*1.0001,retract_s=required*1.0001)
            r=calculate(base,n=n,process_targets=process,flow_solver=solver,mixing=mixing,compressor=compressor,racks=racks,ammonia=ammonia)
            out=evaluate(r,r['inputs']['front_length_m'],d.rear_depth_m,hardware,rear_diameter_m=d.rear_diameter_m)
            if ammonia.enabled:install_ammonia(out,r,ammonia,hardware,performance)
        else:raise ValueError('Deployment/area fixed point did not converge')
        packed=allocation(out,r,d,hardware,performance,compressor,packaging)
        old=out['masses_kg']['shell_TPS_allowance']
        new=math.pi*base.outside_diameter_m*packed['total_length_m']*hardware.shell_TPS_kg_m2
        delta=new-old
        out['masses_kg']['shell_TPS_allowance']=new
        out['masses_kg']['design_margin']+=delta*hardware.design_margin
        out['total_dry_kg']+=delta*(1+hardware.design_margin)
        out['total_with_loop_fluid_kg']+=delta*(1+hardware.design_margin)
        out['overall_length_allowance_m']=packed['total_length_m']
        out['packaging']=packed
    out['racks']=r.get('racks')
    out['initial_gas_seed_kg']=r['initial_gas_seed_kg']
    out['compressor_analysis']=r.get('compressor_analysis')
    out['mixing']=r['mixing']
    out['compressor_inlet_K']=r['max_pumping_temperature_K'] if racks.enabled else r['inputs']['gas_K']
    out['metal_hot_K']=max(x['max_metal_K'] for x in r['racks']) if racks.enabled else base.metal_hot_K
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
    out['oxygen_used_as_propellant_kg']=min(out['propellant_kg'],out['oxygen_available_kg'])
    out['nitrogen_used_as_propellant_kg']=max(0.,out['propellant_kg']-out['oxygen_available_kg']) if scenario.allow_nitrogen_propellant else 0.
    if scenario.allow_nitrogen_propellant:
        margins.pop('oxygen_kg')
        margins['nitrogen_propellant_margin_kg']=r['mixing']['nitrogen_available_kg']-out['nitrogen_used_as_propellant_kg']
    margins['cutoff_Pa']=controls.cutoff_Pa-r['final_front_Pa']
    margins['coolant_replacement_kg']=r['mixing']['nitrogen_available_kg']-r['mixing']['coolant_replacement_kg']
    if r.get('compressor_analysis'):
        banks=r['compressor_analysis']['dive']['banks']
        if not racks.enabled:margins['compressor_bay_depth_m']=d.machinery_depth_m-sum(b.get('bank_length_m',0.) for b in banks)
        margins['compressor_face_m2']=math.pi*d.front_diameter_m**2/4*.9-banks[0]['annulus_m2']/(1-compressor.hub_tip_ratio**2)
    if racks.enabled:
        margins['interstage_small_holdup_fraction']=.01-r['interstage_max_batch_fraction']
        margins['molecular_compressor_temperature_K']=2000-r['max_pumping_temperature_K']
        out['interstage_vent_kg']=r['interstage_vent_kg']
        out['interstage_max_batch_fraction']=r['interstage_max_batch_fraction']
        margins['metal_temperature_K']=1042.-out['metal_hot_K']
        pcm_racks=[x for x in r['racks'] if 'pcm_material' in x]
        if pcm_racks:
            margins['pcm_core_temperature_K']=min(x['core_max_allowed_K']-x['core_max_K'] for x in pcm_racks)
            margins['pcm_complete_refreeze']=1e-8-max(x['recovered_melt_fraction'] for x in pcm_racks)
            out['pcm_core_mass_kg']=sum(x['pcm_kg'] for x in pcm_racks)
            out['pcm_shell_and_fin_mass_kg']=sum(x['shell_and_fin_kg'] for x in pcm_racks)
        if packaging.enabled:
            margins['length_m']=packaging.max_length_over_diameter*packed['outside_diameter_m']-packed['total_length_m']
            margins['storage_pressure_Pa']=packaging.max_storage_pressure_Pa-out['rear_pressure_Pa']
        out['front_gas_volume_m3']=r['front_volume_m3']
        out['gas_temperature_range_K']=[min(r['gas_temperature_K']),max(r['gas_temperature_K'])]
    if ammonia.enabled:
        stages=out['ammonia']['stages']
        margins['ammonia_inventory_kg']=min(x['available_kg']-x['used_kg'] for x in stages)
        margins['ammonia_return_enthalpy_J_kg']=-max(x['enthalpy_over_target_J_kg'] for x in stages)
        margins['ammonia_boiling_K']=min(x['boiling_K']-x['peak_wall_K'] for x in stages)
        margins['ammonia_tube_stress_Pa']=min(150e6-(ammonia.pressure_Pa+x['peak_dp_Pa'])*ammonia.radius_m/ammonia.wall_m*1.5 for x in stages)
        out['payoff_including_ammonia_inventory_days']=((out['total_dry_kg']+out['ammonia']['total_inventory_kg'])/out['net_liquid_equivalent_kg_day'] if out['net_liquid_equivalent_kg_day']>0 else None)
    out['total_with_working_fluids_kg']=out['total_with_loop_fluid_kg']+r['mixing']['injected_kg']
    for key in ('capture_impulse','escape_impulse','uncollected_mouth_impulse','geometric_intercept_impulse'):
        out[key+'_Ns']=solver.last[key]
    out['effective_ultimate_Pa']=solver.last['ultimate_Pa']
    out['final_front_pressure_Pa']=r['final_front_Pa']
    result=dict(status='Conditional continuous-inlet cycle; no shock validation or circular-delivery payoff',
        inputs=dict(design=asdict(d),hardware=asdict(hardware),performance=asdict(performance),
            process=asdict(process),scenario=asdict(scenario),flow=asdict(flow),controls=asdict(controls),mixing=asdict(mixing),compressor=asdict(compressor),racks=asdict(racks),packaging=asdict(packaging),ammonia=asdict(ammonia)),
        outputs=out,constraints=dict(margins=margins,
            all_implemented_screens_pass=bool(all(v>=-1e-8 for v in margins.values()) and solver.last['stop_reason']=='cutoff_pressure'),
            unresolved=['Shock position/start margin and calibrated capture/leakage coefficients',
                'Rack correlation/rarefaction calibration and spatial gradients; lattice pressure loss intentionally omitted',
                'Intermediate gas storage dynamics (current racks use quasi-steady series flow)',
                'Compressor performance map, spin-up and installed mass capability',
                'Hull drag, structural/dynamic loads and deployable mechanisms',
                'Finite-thrust orbit restoration and circular-apogee export']),
        resolved_cycle_inputs=r['inputs'],numerics=dict(samples=n))
    if history:result['history']=solver.last['history']
    return result
