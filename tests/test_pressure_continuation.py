"""Verify the reduced experiment's physical input contract without running orbits."""
import copy
import pytest
from investigations.pressure_continuation.run import BASE, seed, supply, candidate
from atmo_scoops.transient.reduced_coordinates import rack_allocation
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config

@pytest.mark.parametrize('factor',[1.05,1.10])
def test_batch_scaling_preserves_allocation_and_charges_hardware(factor):
    original=copy.deepcopy(BASE)
    c=seed(factor);base=rack_allocation(BASE);after=rack_allocation(c)
    assert BASE==original
    assert after['fractions']==pytest.approx(base['fractions'])
    assert after['total_kg']==pytest.approx(base['total_kg']*factor)
    assert supply(c)/supply(BASE)==pytest.approx(factor,rel=1e-8)
    h0=compile_hardware(*read_config(BASE));h1=compile_hardware(*read_config(c))
    assert h1['masses_kg']['pressure_vessels']>h0['masses_kg']['pressure_vessels']
    assert h1['geometry'][4]['gas_m3']<h0['geometry'][4]['gas_m3']
    for key in ['receiver_fill_tolerance_Pa','plate_gap_m','plate_thickness_m','suction_m3_s','head_J_kg','rack_initial_K']:
        assert c['design'][key]==BASE['design'][key]


def test_restoration_coordinates_do_not_resize_other_groups():
    c=seed(1.05);r=candidate(c,[.01,.001,.001])
    changed={k for k in c['design'] if c['design'][k]!=r['design'][k]}
    assert changed <= {'perigee_km','gas_reserve_kg','gas_initial_K','bus_MW','battery_MW'}
    assert r['design']['gas_reserve_kg']==pytest.approx(c['design']['gas_reserve_kg']+1)
