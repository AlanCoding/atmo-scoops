from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from atmo_scoops.inlet import FlowCapabilities,EncounterControls,net_pump_rate
from atmo_scoops.open_mouth import port_flow
from atmo_scoops.system import simulate,Design


def test_pump_backflow_and_analytic_isolated_inventory():
    V=100.;S=10.;RT=287000.;p0=20.;pu=.3;cutoff=.5
    time=V/S*np.log((p0-pu)/(cutoff-pu))
    sol=solve_ivp(lambda t,p:[-RT/V*net_pump_rate(p[0],S,pu,RT)],(0,time),[p0],rtol=1e-10,atol=1e-11)
    assert sol.y[0,-1]==pytest.approx(cutoff,rel=1e-8)
    assert net_pump_rate(pu,S,pu,RT)==0
    assert net_pump_rate(pu/2,S,pu,RT)==0


def test_port_sonic_limit_and_zero_pressure_difference():
    R=287.;T=1000.;g=1.4;A=2.;Cd=.8;p=20.
    expected=Cd*A*p/np.sqrt(R*T)*np.sqrt(g)*(2/(g+1))**((g+1)/(2*(g-1)))
    assert port_flow(p,0,T,A,R,g,Cd)==pytest.approx(expected)
    assert port_flow(p,p,T,A,R,g,Cd)==0
    assert port_flow(p,1,T,A,R,g,Cd)==pytest.approx(expected)


def test_leakage_cutoff_and_projected_momentum_ledger():
    r=simulate(replace(Design(),front_depth_m=450),flow=FlowCapabilities(ultimate_inlet_Pa=1),
        controls=EncounterControls(suction_scale=.5,cutoff_Pa=1.05),n=801,history=True)
    o=r['outputs'];h=r['history']
    assert o['mouth_leakage_kg']>0
    assert o['captured_kg']==pytest.approx(o['retained_kg']+o['vent_kg'],abs=1e-6)
    assert o['final_front_pressure_Pa']==pytest.approx(1.05)
    assert np.trapezoid(h['leakage_kg_s'],h['time_s'])==pytest.approx(o['mouth_leakage_kg'],rel=.02)
    assert o['capture_impulse_Ns']+o['uncollected_mouth_impulse_Ns']==pytest.approx(o['geometric_intercept_impulse_Ns'],rel=2e-6)
    assert o['propellant_kg']==pytest.approx((o['geometric_intercept_impulse_Ns']+o['escape_impulse_Ns'])/(4000*9.80665))


def test_unreachable_cutoff_and_timeout_are_not_success():
    with pytest.raises(ValueError,match='Cutoff must exceed'):
        simulate(flow=FlowCapabilities(ultimate_inlet_Pa=1),n=101)
    r=simulate(controls=EncounterControls(max_after_perigee_s=10),n=101)
    assert not r['constraints']['all_implemented_screens_pass']
    assert r['outputs']['pump_stop_reason']=='time_limit'
