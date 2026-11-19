import pytest
from atmo_scoops.transient.loss_power_screen import charge
from atmo_scoops.transient.porous import suction_pressure

def test_power_charge_is_first_order_pressure_work():
    g=dict(wire_radius_m=.001,pitch_m=.01,frontal_m2=700.,row_count=500.,pressure_model='inline_laminar')
    p,T,R,m,eta=1000.,500.,287.,1.,.75*.95
    rho=p/(R*T)
    W,chi=charge(m,p,T,rho,g,eta)
    ps,_=suction_pressure(m,p,T,R,g,1e-6)
    assert (p-ps)*m/rho/eta==pytest.approx(W*1e-6,rel=1e-5)
    assert chi==pytest.approx(2*(W*eta*rho/m)/p)
    assert charge(0,p,T,rho,g,eta)==(0.,0.)
    with pytest.raises(ValueError):charge(m,p,T,0,g,eta)
