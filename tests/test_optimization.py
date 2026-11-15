from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from atmo_scoops.system import defaults,inputs_from_dict,simulate,Design
from atmo_scoops.optimization.search import Problem,BOUNDS,payoff_days


def test_optimizer_coordinates_round_trip_and_capabilities_stay_fixed():
    inputs=inputs_from_dict(defaults());p=Problem(inputs,BOUNDS,list(BOUNDS))
    d=p.decode(p.encode(inputs['design']))
    for key in BOUNDS:
        group,field=key.split('.',1) if '.' in key else ('design',key)
        assert getattr(d[group],field)==pytest.approx(getattr(inputs[group],field))
    assert 'compressor_kg_per_m3_s' not in p.keys
    assert 'thruster_efficiency' not in p.keys
    r=p.evaluate(p.encode(d))
    assert r['inputs']['hardware']==defaults()['hardware']
    assert p(p.encode(d))==pytest.approx(np.log(payoff_days(r)))


def test_failed_constraint_is_not_a_good_optimization_score():
    inputs=inputs_from_dict(defaults());p=Problem(inputs,BOUNDS,list(BOUNDS))
    d=replace(Design(),isp_s=3200)
    r=p.evaluate(p.encode(d))
    assert r['constraints']['margins']['oxygen_kg']<0
    assert p(p.encode(d))>=10000
