import math
from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import quad

from atmo_scoops.atmosphere import make_profile
from atmo_scoops.encounter import pressure_window,orbit_state
from atmo_scoops.orbit import Orbit,MU
from atmo_scoops.process import liquefaction_train,coast_compressor,ProcessTargets


def test_orbit_invariants_and_pressure_window():
    o=Orbit(100,2000);_,dt,r,_,vr,vt=o.eccentric_grid(1001)
    assert sum(dt)==pytest.approx(o.period)
    assert np.allclose((vr*vr+vt*vt)/2-MU/r,-MU/(2*o.a),rtol=1e-12)
    assert np.allclose(r*vt,o.h,rtol=1e-12)
    atm=make_profile();edge,peak=pressure_window(o,atm,.5)
    assert float(orbit_state(o,-edge,atm)['ram_Pa'])==pytest.approx(.5*peak)
    assert np.allclose(atm.fractions.sum(axis=1),1)


def test_product_refrigeration_energy_and_scaling():
    a=liquefaction_train(1/3600)
    assert a['liquid_out_kg_s']==a['new_air_kg_s']
    assert a['radiator_heat_W']==pytest.approx(a['electricity_W']+a['actual_cold_duty_W'])
    assert a['actual_cold_duty_W']==pytest.approx(a['sensible_cooling_W']+a['condensation_W'])
    b=liquefaction_train(2/3600)
    assert b['electricity_W']==pytest.approx(2*a['electricity_W'])
    c=liquefaction_train(1/3600,targets=replace(ProcessTargets(),carnot_fraction=.3))
    assert c['electricity_W']==pytest.approx(a['electricity_W']/2)


def test_coast_evacuator_matches_integrated_pressure_work():
    m,V,T,time=84.,5700.,340.,4900.
    d=coast_compressor(m,V,T,time)
    S=d['pumping_speed_m3_s'];p0=d['input_pressure_start_Pa'];R=296.8
    def power(t):
        remaining=m*math.exp(-S*t/V)
        p=remaining*R*T/V
        return remaining*S/V*R*T*math.log(1e5/p)/.5
    assert quad(power,0,time)[0]==pytest.approx(d['electricity_J'],rel=1e-8)
    assert m*math.exp(-S*time/V)==pytest.approx(d['residual_kg'])


@pytest.mark.parametrize("initial_pressure", [2e5, 2e9])
def test_coast_feed_regulates_above_delivery_pressure(initial_pressure):
    R,T,V,duration=296.8,340.,100.,4900.
    m=initial_pressure*V/(R*T)
    d=coast_compressor(m,V,T,duration)
    S=d['pumping_speed_m3_s']
    def power(t):
        remaining=m*math.exp(-S*t/V)
        return remaining*S/V*R*T*max(0.,math.log(1e5/(remaining*R*T/V)))/.5
    transition=V/S*math.log(initial_pressure/1e5)
    points=[transition] if 0<transition<duration else None
    assert quad(power,0,duration,points=points)[0]==pytest.approx(d['electricity_J'],rel=1e-8,abs=1e-6)
    assert d['peak_power_W']>=0
