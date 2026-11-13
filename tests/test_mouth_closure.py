from dataclasses import replace
import math
import numpy as np
import pytest

from atmo_scoops.open_mouth import port_flow, recover_open
from atmo_scoops.system import Design, Hardware, Performance, Scenario, simulate


def test_port_pressure_direction_and_choked_limit():
    g=1.4;R=287.;T=700.;A=2.;cd=.8;p=100.
    expected=cd*A*p/math.sqrt(R*T)*math.sqrt(g)*(2/(g+1))**((g+1)/(2*(g-1)))
    assert port_flow(p,0,T,A,R,g,cd)==pytest.approx(expected)
    assert port_flow(p,20,T,A,R,g,cd)==pytest.approx(expected)
    assert 0<port_flow(p,99,T,A,R,g,cd)<expected
    assert port_flow(p,p,T,A,R,g,cd)==0
    assert port_flow(p,2*p,T,A,R,g,cd)==0


def test_open_recovery_matches_vacuum_leak_and_pump_analytic_solution():
    t=np.linspace(0,20,401);zero=np.zeros_like(t);R=287.;T=700.;V=100.;S=5.
    leak_rate_per_kg=port_flow(R*T/V,0,T,.1,R,1.4,.8)
    k=S/V+leak_rate_per_kg
    r=recover_open(t,zero,zero,zero,zero,1.,0.,S,V,.1,R,T,1.4,.8,1e-12,
                   np.full_like(t,.23),.23)
    expected=np.exp(-k*r['time'])
    assert np.allclose(r['front'],expected,rtol=2e-7,atol=1e-9)
    assert r['rear'][-1]==pytest.approx(S/V/k*(1-expected[-1]),rel=2e-7)
    assert r['leaked'][-1]==pytest.approx(leak_rate_per_kg/k*(1-expected[-1]),rel=2e-7)
    assert r['retained_oxygen']==pytest.approx(.23*r['rear'][-1])


def test_door_is_optional_but_bulkhead_remains_and_mass_sensitivity_is_exact():
    closed=simulate(n=401)['outputs']
    heavier=simulate(hardware=replace(Hardware(),mouth_closure_kg_m2=100),n=401)['outputs']
    expected=math.pi*Design().mouth_diameter_m**2/4*90
    assert heavier['total_dry_kg']-closed['total_dry_kg']==pytest.approx(expected*1.25)
    opened=simulate(replace(Design(),mouth_closure=False),n=401)['outputs']
    assert opened['masses_kg']['mouth_closure']==0
    assert opened['masses_kg']['compressor_bulkhead']==closed['masses_kg']['compressor_bulkhead']
    assert opened['outbound_admitted_kg']>0
    assert opened['pump_stop_reason']=='inlet_pressure_floor'
    assert opened['front_pressure_at_pump_stop_Pa']==pytest.approx(.1)


@pytest.mark.parametrize('support',[1.,.3])
def test_open_cycle_conservation_and_resolution_with_and_without_reverse_flow(support):
    d=replace(Design(),mouth_closure=False)
    a=simulate(d,scenario=Scenario(open_mouth_support_over_ram=support),n=801)['outputs']
    b=simulate(d,scenario=Scenario(open_mouth_support_over_ram=support),n=3201)['outputs']
    for key in ('captured_kg','retained_kg','total_dry_kg','compressor_kWh','hot_absorbed_GJ'):
        assert a[key]==pytest.approx(b[key],rel=3e-4)
    assert b['captured_kg']==pytest.approx(b['retained_kg']+b['vent_kg'],abs=1e-7)
    assert b['vent_kg']==pytest.approx(b['mouth_leakage_kg']+b['final_front_vent_kg'])
    assert abs(b['thermal_energy_balance_residual_J'])<.01
    if support==.3:assert b['mouth_leakage_kg']>0


def test_pressure_floor_and_run_time_limit_are_distinct():
    closed=simulate(performance=replace(Performance(),compressor_min_inlet_Pa=10),n=401)['outputs']
    assert closed['cycle']['recovery_s']<450
    assert closed['front_pressure_at_pump_stop_Pa']==pytest.approx(10)
    r=simulate(replace(Design(),mouth_closure=False,recovery_s=10),n=401)
    assert r['outputs']['pump_stop_reason']=='recovery_time_limit'
    assert r['constraints']['margins']['open_pump_pressure_floor_Pa']<0


def test_boolean_and_coefficient_validation():
    with pytest.raises(ValueError,match='boolean'):simulate(replace(Design(),mouth_closure=0),n=101)
    with pytest.raises(ValueError,match='open_mouth'):simulate(scenario=Scenario(open_mouth_support_over_ram=0),n=101)
