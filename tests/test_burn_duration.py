import pytest
from atmo_scoops.orbit import Orbit,MU
from atmo_scoops.studies.burn_duration import penalty,orbit_check

def test_centered_burn_short_duration_limit_and_power_trade():
 o=Orbit(85,2000)
 k=penalty(o,30)['impulse_multiplier']
 assert (k-1)/(MU/o.rp**3*30**2/24)==pytest.approx(1,rel=.002)
 short=penalty(o,300);long=penalty(o,1200)
 assert 1<short['impulse_multiplier']<long['impulse_multiplier']
 assert long['impulse_multiplier']/1200<short['impulse_multiplier']/300
 assert abs(long['closure_residual'])<1e-10

def test_centered_burn_restores_independently_propagated_orbit():
 r=orbit_check(Orbit(85,2000),1200,dv=.1)
 assert abs(r['energy_residual_relative_drag'])<1e-3
 assert abs(r['angular_residual_relative_drag'])<1e-3
 assert abs(r['apsidal_change_deg'])<1e-4

def test_burn_cannot_span_more_than_one_orbit():
 o=Orbit(85,2000)
 with pytest.raises(ValueError):penalty(o,o.period)
