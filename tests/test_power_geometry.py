import copy
import json
import math
import pytest
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.power_geometry_search import geometry,geometry_proposals

def base():return json.load(open('configs/transient_power_only_0.1.json'))

def test_geometry_coordinates_preserve_nominal_solid_and_bound_radius():
    c=base();d=c['design']
    old=[z*math.pi*(d['rod_radius_m']/d['rod_pitch_m'])**2 for z in d['rack_depth_m']]
    for altered in [geometry(c,ratios=[6.]*5),geometry(c,radii=[.00001]*5)]:
        q=altered['design'];assert min(q['stage_radius_m'])>=.0002
        new=[z*math.pi*(r/p)**2 for z,r,p in zip(q['rack_depth_m'],q['stage_radius_m'],q['stage_pitch_m'])]
        assert new==pytest.approx(old)
        compile_hardware(*read_config(altered))
    assert not c['design']['stage_radius_m']

def test_pitch_stage_never_changes_radius_and_radius_stage_keeps_pitch_free():
    c=base()
    assert all(x['design']['stage_radius_m']==[.001]*5 for x in geometry_proposals(c,'pitch',0).values())
    names=geometry_proposals(c,'radius',0)
    assert any(n.startswith('pitch_') for n in names)
    assert any(n.startswith('radius_') for n in names)
    c['design']['rack_loss_mode']='invalid'
    with pytest.raises(ValueError):read_config(c)

def test_power_only_saved_cycle_conserves_and_does_not_lower_suction_pressure():
    import gzip
    import numpy as np
    with gzip.open('results/transient/power_only/seed_0.1/baseline_refined.json.gz','rt') as f:r=json.load(f)
    assert r['feasible']
    assert r['audits']['species_kg']<1e-4
    assert r['audits']['energy_MJ']<.01
    assert np.asarray(r['history']['compressor_suction_Pa'])==pytest.approx(np.asarray(r['history']['pressure_Pa'])[:,:4])
    assert r['loss_power_audit']['loss_electric_MWh']>0
    assert r['loss_power_audit']['energy_ratio']==pytest.approx(.06926,rel=.002)
    assert max(abs(v) for v in r['closure']['gas_reserve_species_kg'])<.1

def test_geometry_combination_keeps_stage_moves_and_selected_hardware():
    from atmo_scoops.transient.power_geometry_search import combine_geometry
    c=base();seed=dict(inputs=c,operating_payoff_days=300.)
    pitch=geometry(c,ratios=[7.,10.,10.,10.,10.])
    radius=geometry(c,radii=[.001,.002,.001,.001,.001])
    rows=[dict(name='r0_pitch_0_0.7',inputs=pitch,feasible=True,operating_payoff_days=290.),dict(name='r0_radius_1_2',inputs=radius,feasible=True,operating_payoff_days=295.)]
    best=copy.deepcopy(seed);best['inputs']['design']['bus_MW']=1000.
    combined=combine_geometry(seed,best,rows)['design']
    assert combined['stage_radius_m'][1]==.002
    assert combined['stage_pitch_m'][0]==pytest.approx(.007)
    assert combined['stage_pitch_m'][1]==pytest.approx(.02)
    assert combined['bus_MW']==1000.
