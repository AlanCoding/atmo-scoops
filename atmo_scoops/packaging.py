"""Explicit folded envelopes and deployment travel, with serialized capabilities."""
from dataclasses import dataclass, asdict
import math

@dataclass(frozen=True)
class Packaging:
    enabled: bool = True
    deployment_speed_m_s: float = 10.
    travel_over_sqrt_area: float = 1.
    solar_W_m3: float = 40000.  # ROSA approximate published package figure.
    warm_radiator_stack_pitch_m: float = .02  # Engineering sensitivity, not qualified hardware.
    machinery_bulk_kg_m3: float = 250.  # Installed plant/drive envelope; sensitivity assumption.
    battery_Wh_m3: float = 280000.  # Manufacturer module-scale range, external integration extra.
    battery_bulk_kg_m3: float = 1800.
    buffer_bulk_kg_m3: float = 800.
    module_packing_fraction: float = .75
    equipment_bay_fill_fraction: float = .7
    max_length_over_diameter: float = 10.
    max_storage_pressure_Pa: float = 110000.

    def validate(self):
        if not isinstance(self.enabled,bool):raise ValueError('packaging.enabled must be boolean')
        for k,v in asdict(self).items():
            if k=='enabled':continue
            if not math.isfinite(v) or v<=0:raise ValueError(f'packaging.{k} must be positive')
        if max(self.module_packing_fraction,self.equipment_bay_fill_fraction)>1:raise ValueError('Packing fractions cannot exceed 1')


def allocation(o,r,d,hw,perf,comp,spec):
    A=math.pi*d.front_diameter_m**2/4
    banks=r['compressor_analysis']['dive']['banks']+r['compressor_analysis']['coast']['banks']
    bank_volume=sum(b.get('modules',0)*math.pi*b.get('module_diameter_m',0)**2/4*b.get('bank_length_m',0)/spec.module_packing_fraction for b in banks)
    motor_volume=sum(b.get('motor_kg',0) for b in banks)/spec.machinery_bulk_kg_m3
    m=o['masses_kg']
    plant=sum(m[k] for k in ('refrigerator','product_heat_exchangers','separator','warm_aftercooler'))/spec.machinery_bulk_kg_m3
    battery=max(o['masses_kg']['battery']*perf.battery_Wh_kg/spec.battery_Wh_m3,
                o['masses_kg']['battery']/spec.battery_bulk_kg_m3)
    pieces=dict(solar=o['solar_MW']*1e6/spec.solar_W_m3,
        warm_radiator=o['warm_radiator_panel_m2']*spec.warm_radiator_stack_pitch_m,
        liquefaction_and_heat_exchangers=plant,compressor_cases=bank_volume,compressor_motors=motor_volume,
        battery=battery,warm_heat_buffer=m['warm_buffer']/spec.buffer_bulk_kg_m3,
        propulsion_and_distribution=(m['propulsion_hardware']+m['power_distribution'])/spec.machinery_bulk_kg_m3,
        liquid_tanks=o['retained_kg']/800*1.2,
        rack_deployment_hardware=m['hot_sheet_deployment']/spec.machinery_bulk_kg_m3,
        other_fixed_hardware=(m['avionics_attitude']+m['liquid_storage_valves_plumbing'])/spec.machinery_bulk_kg_m3)
    if 'ammonia' in o:
        a=o['ammonia']
        pieces.update(ammonia_inventory_tank=a['tank_m3'],
            ammonia_radiator=a['radiator_m2']*spec.warm_radiator_stack_pitch_m,
            ammonia_machinery=(m['ammonia_refrigerator']+m['ammonia_pump']+m['ammonia_tank']+m['ammonia_power_distribution'])/spec.machinery_bulk_kg_m3)
    # Racks are in their working envelopes during the pass, never packed as solid metal.
    rack_volumes=[x['envelope_m3'] for x in r['racks']]
    interstage=sum(rack_volumes[1:])/A
    front=r['inputs']['front_length_m']
    hardware=sum(pieces.values())/spec.equipment_bay_fill_fraction/A
    length=front+d.rear_depth_m+interstage+hardware
    outside=max(d.front_diameter_m,d.rear_diameter_m,d.mouth_diameter_m)+2*d.radial_clearance_m
    travel={k:spec.travel_over_sqrt_area*math.sqrt(v)/spec.deployment_speed_m_s for k,v in
        [('solar',o['solar_area_m2']),('warm_radiator',o['warm_radiator_panel_m2']),('metal_racks',o['metal_panel_m2'])]}
    if 'ammonia' in o:travel['ammonia_radiator']=spec.travel_over_sqrt_area*math.sqrt(o['ammonia']['radiator_m2'])/spec.deployment_speed_m_s
    return dict(component_package_m3=pieces,equipment_bay_m3=hardware*A,
        rack_envelopes_m3=rack_volumes,rack_gas_m3=[x['gas_m3'] for x in r['racks']],
        front_depth_m=front,rear_depth_m=d.rear_depth_m,interstage_rack_depth_m=interstage,
        equipment_equivalent_depth_m=hardware,total_length_m=length,outside_diameter_m=outside,
        length_over_diameter=length/outside,deployment_travel_s=travel,
        required_motion_s=max(travel.values()),assumptions=asdict(spec))
