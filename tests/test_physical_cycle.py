import math
from dataclasses import replace

import pytest

from atmo_scoops.physical_cycle import Hardware, rear_geometry, reference, evaluate
from atmo_scoops.two_volume import calculate


@pytest.fixture(scope='module')
def raw():
    return calculate(reference(), n=801)


def test_rear_physical_depth_accounts_for_curved_heads():
    d=18.3;area=math.pi*d*d/4
    # At minimum depth, only the two ellipsoidal heads remain.
    assert rear_geometry(d/2)['volume_m3'] == pytest.approx(area*d/3)
    assert rear_geometry(25)['volume_m3']-rear_geometry(10)['volume_m3'] == pytest.approx(area*15)
    with pytest.raises(ValueError):rear_geometry(5)


def test_mass_ledger_and_two_sided_area_accounting(raw):
    r=evaluate(raw,250,25)
    assert r['total_dry_kg'] == pytest.approx(sum(r['masses_kg'].values()))
    assert r['masses_kg']['design_margin'] == pytest.approx(r['total_dry_kg']*.25/1.25)
    assert r['warm_radiator_emitting_m2'] == 2*r['warm_radiator_panel_m2']
    assert r['metal_emitting_m2'] == 2*r['metal_panel_m2']
    assert r['net_liquid_equivalent_kg']+r['propellant_kg'] == pytest.approx(raw['retained_kg']*.999)
    assert r['compressor_mass_kg'] == pytest.approx(sum(r['masses_kg'][x] for x in ('compressor_hot','compressor_warm','compressor_coast')))


def test_suction_is_bounded_by_access_and_mass_target(raw):
    base=evaluate(raw,250,25)
    restricted=evaluate(raw,250,25,replace(Hardware(),compressor_open_fraction=.1))
    assert base['access_bound_pass']
    assert not restricted['access_bound_pass']
    assert restricted['suction_choking_bound_m3_s'] == pytest.approx(base['suction_choking_bound_m3_s']/3)
    heavier=evaluate(raw,250,25,replace(Hardware(),compressor_kg_per_m3_s=100))
    assert heavier['compressor_mass_kg'] > base['compressor_mass_kg']
    assert heavier['total_dry_kg'] > base['total_dry_kg']
    assert heavier['captured_kg'] == base['captured_kg']
