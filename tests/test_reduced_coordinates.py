import copy
import json
from pathlib import Path
import pytest
from atmo_scoops.transient.reduced_coordinates import rack_allocation, with_total_rack_mass
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config

@pytest.fixture
def reference():
    return json.loads(Path('configs/transient_v1_0_1_valve.json').read_text())

def test_identity_and_no_mutation(reference):
    original = copy.deepcopy(reference)
    mapped = with_total_rack_mass(reference, rack_allocation(reference)['total_kg'])
    assert mapped == original
    mapped['design']['rack_depth_m'][0] *= 2
    assert reference == original

@pytest.mark.parametrize('factor', [.99, 1.01])
def test_physical_allocation_and_packing_change(reference, factor):
    base = rack_allocation(reference)
    candidate = with_total_rack_mass(reference, base['total_kg'] * factor)
    after = rack_allocation(candidate)
    assert after['total_kg'] == pytest.approx(base['total_kg'] * factor)
    assert after['fractions'] == pytest.approx(base['fractions'])
    h0 = compile_hardware(*read_config(reference))
    h1 = compile_hardware(*read_config(candidate))
    assert h1['geometry'][4]['gas_m3'] != h0['geometry'][4]['gas_m3']
    assert h1['masses_kg']['rack_mechanisms'] == pytest.approx(h0['masses_kg']['rack_mechanisms'] * factor)
    for key in ['plate_gap_m', 'plate_thickness_m', 'rack_initial_K', 'materials', 'suction_m3_s', 'motor_MW']:
        assert candidate['design'][key] == reference['design'][key]

@pytest.mark.parametrize('total', [0, -1, float('nan'), float('inf')])
def test_invalid_mass(reference, total):
    with pytest.raises(ValueError):
        with_total_rack_mass(reference, total)
