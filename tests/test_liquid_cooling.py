from dataclasses import replace
import pytest
from atmo_scoops.liquid_cooling import LiquidCooling,size
D=[dict(heat_J=1e9,gas_K=900.,h_gas_W_m2_K=30.,frontal_m2=100.)]

def test_once_through_energy_and_no_free_regeneration():
 r=size(D)
 stage=r['stages'][0]
 assert stage['coolant_batch_kg']*r['useful_capacity_J_kg']==pytest.approx(1e9+stage['pump_J'])
 assert r['rejected_J']==pytest.approx(r['regenerated_heat_J']+r['refrigerator_J']+r['regeneration_pump_J'])
 assert r['regenerated_heat_J']==pytest.approx(r['total_coolant_kg']*r['useful_capacity_J_kg'])
 assert r['component_with_coolant_kg']==pytest.approx(r['dry_component_kg']+r['total_coolant_kg'])
 assert r['refrigerator_J']>0

def test_longer_dive_reduces_surface_and_peak_power_not_batch_heat():
 a=size(D);b=size(D,replace(LiquidCooling(),pass_s=120.))
 assert b['stages'][0]['wetted_m2']==pytest.approx(a['stages'][0]['wetted_m2']/2)
 assert b['stages'][0]['coolant_batch_kg']==pytest.approx(a['stages'][0]['coolant_batch_kg'])
 assert b['stages'][0]['pump_W']==pytest.approx(a['stages'][0]['pump_W']/2)

def test_passive_cold_endpoint_and_environment_limits():
 with pytest.raises(ValueError,match='Passive radiator'):size(D,replace(LiquidCooling(),heat_pump=False))
 with pytest.raises(ValueError,match='environmental'):size(D,replace(LiquidCooling(),heat_pump=False,radiator_K=180.))
 r=size(D,replace(LiquidCooling(),fluid='Water',cold_K=280,hot_K=340,pressure_Pa=1e6,heat_pump=False,radiator_K=260.))
 assert r['refrigerator_J']==0

def test_property_phase_and_temperature_checks():
 with pytest.raises(ValueError,match='single-phase'):size(D,replace(LiquidCooling(),hot_K=400.))
 with pytest.raises(ValueError,match='triple'):size(D,replace(LiquidCooling(),cold_K=150.))
 with pytest.raises(ValueError):size(D,replace(LiquidCooling(),velocity_m_s=0))

def test_carnot_efficiency_and_sunlight_charge_power():
 a=size(D);b=size(D,replace(LiquidCooling(),carnot_fraction=.175))
 assert b['refrigerator_J']==pytest.approx(a['refrigerator_J']*2)
 c=size(D,replace(LiquidCooling(),sunlight_s=1392.5))
 assert c['solar_MW']==pytest.approx(a['solar_MW']*2)
 assert c['radiator_m2']==pytest.approx(a['radiator_m2']*2)
