from dataclasses import replace
import math
import pytest
from atmo_scoops.ammonia import AmmoniaCooling,geometry,exchange
from atmo_scoops.system import defaults,inputs_from_dict


def test_configuration_and_displaced_volume():
 s=AmmoniaCooling(enabled=True);s.validate();g=geometry(s,700)[0]
 assert g['solid_m3']+g['gas_m3']==pytest.approx(g['envelope_m3'])
 assert g['mass_kg']<g['solid_m3']*7870
 assert g['deployed_physical_m2']==0
 assert g['liquid']['hold_up_kg']>0
 assert inputs_from_dict(defaults())['ammonia']==AmmoniaCooling()


def test_control_flow_energy_and_finite_capacity():
 g=geometry(AmmoniaCooling(enabled=True),700)[0];a=g['liquid']
 UA,d=exchange(1e6,900,g)
 heat=UA*(900-a['cold_K'])
 assert heat==pytest.approx(d['liquid_flow_kg_s']*a['cp']*(d['liquid_out_K']-a['cold_K']))
 assert d['liquid_out_K']==pytest.approx(299.)
 _,limited=exchange(1e9,900,g)
 assert limited['liquid_flow_kg_s']==a['maximum_flow_kg_s']
 assert limited['liquid_out_K']>a['target_K']
 assert limited['liquid_pump_W']>0
 assert exchange(1e6,200,g)[0]==0


def test_wall_and_liquid_resistance_are_not_free():
 g=geometry(AmmoniaCooling(enabled=True),700)[0]
 UA,_=exchange(1e6,900,g)
 assert 0<UA<1e6
 thicker=geometry(replace(AmmoniaCooling(enabled=True),wall_m=.0003),700)[0]
 assert thicker['mass_kg']>g['mass_kg']
 with pytest.raises(ValueError):replace(AmmoniaCooling(enabled=True),cold_K=150).validate()


def test_integrated_energy_mass_packing_and_inventory():
 import json
 from pathlib import Path
 from atmo_scoops.system import simulate
 base=inputs_from_dict(json.loads((Path(__file__).parents[1]/'configs/finite_rack_reference.json').read_text()))
 base['design']=replace(base['design'],perigee_km=85.,rear_depth_m=16.)
 base['controls']=replace(base['controls'],suction_scale=.85)
 base['compressor']=replace(base['compressor'],thermodynamic_samples=101)
 base['ammonia']=AmmoniaCooling(enabled=True,inventories_kg=(600000.,80000.,30000.,30000.))
 r=simulate(**base,n=101);o=r['outputs'];a=o['ammonia']
 assert r['constraints']['all_implemented_screens_pass']
 assert abs(o['thermal_energy_balance_residual_J'])<.01
 assert o['total_dry_kg']==pytest.approx(sum(o['masses_kg'].values()))
 assert o['metal_panel_m2']==0
 assert a['used_kg']<a['total_inventory_kg']
 assert a['rejected_J']==pytest.approx(a['regenerated_heat_J']+a['refrigeration_J']+a['coast_pump_J']+a['electrical_loss_J'])
 assert o['packaging']['component_package_m3']['ammonia_inventory_tank']==a['tank_m3']
 assert o['payoff_including_ammonia_inventory_days']>o['operating_mass_payoff_days']
 assert len(a['stages'])==4
 # Inventory is an explicit feasibility limit, not an infinite cold bath.
 base['ammonia']=replace(base['ammonia'],inventories_kg=(1.,1.,1.,1.))
 rejected=simulate(**base,n=101)
 assert rejected['constraints']['margins']['ammonia_inventory_kg']<0
 assert not rejected['constraints']['all_implemented_screens_pass']
