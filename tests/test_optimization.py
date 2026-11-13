from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from atmo_scoops.two_volume import front_inventory
from atmo_scoops.system import defaults,inputs_from_dict,simulate,Design
from atmo_scoops.optimization.search import Problem,BOUNDS,payoff_days


@pytest.mark.parametrize('suction',[0.,1e-7,10.,1e5])
def test_exact_piecewise_inflow_matches_independent_ode(suction):
    t=np.linspace(0,10,81);q=.7+.3*np.sin(t)
    exact=front_inventory(t,q,suction,1000.)
    numerical=solve_ivp(lambda ti,y:[np.interp(ti,t,q)-suction/1000*y[0]],
        (0,10),[0.],t_eval=t,rtol=1e-10,atol=1e-11,max_step=.02)
    assert np.allclose(exact,numerical.y[0],rtol=2e-7,atol=1e-8)


def test_optimizer_coordinates_round_trip_and_capabilities_stay_fixed():
    inputs=inputs_from_dict(defaults());p=Problem(inputs,BOUNDS,list(BOUNDS))
    d=p.decode(p.encode(inputs['design']))
    for key in BOUNDS:assert getattr(d,key)==pytest.approx(getattr(inputs['design'],key))
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
