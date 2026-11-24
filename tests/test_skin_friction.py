import math
import numpy as np
import pytest
from atmo_scoops.transient.drag import skin_impulse
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config,defaults


def test_skin_uses_dynamic_pressure_and_wetted_area():
    t=np.array([0.,10.]);rho=np.array([1e-5,1e-5]);v=np.array([8000.,8000.])
    r=skin_impulse(t,rho,v,30.,300.,.002)
    assert r['impulse_Ns']==pytest.approx(.5e-5*8000**2*.002*math.pi*30*300*10)
    assert r['mechanical_work_J']==pytest.approx(r['impulse_Ns']*8000)
    assert skin_impulse(t,rho,v,30,300)['impulse_Ns']==0


def test_drag_increases_propulsion_without_manufacturing_captured_mass():
    x=defaults();a=compile_hardware(*read_config(x));x['capabilities']['skin_friction_coefficient']=.002
    b=compile_hardware(*read_config(x));fraction=.002*2*31.7*317/30**2
    assert b['skin_impulse_fraction']==pytest.approx(fraction)
    assert b['thrust_W']/a['thrust_W']==pytest.approx(1+fraction)
    assert b['propellant_reference_kg']/a['propellant_reference_kg']==pytest.approx(1+fraction)
    assert b['geometric_impulse_Ns']==a['geometric_impulse_Ns']
    np.testing.assert_array_equal(a['forcing']['supply'],b['forcing']['supply'])
    assert b['masses_kg']['thrusters']>a['masses_kg']['thrusters']
    assert b['geometry'][-1]['depth_m']<a['geometry'][-1]['depth_m']


def test_laminar_plate_density_length_and_area_scaling():
    from atmo_scoops.transient.drag import flat_plate_laminar
    def calc(rho=1e-5,L=317.,D=31.7):
        return flat_plate_laminar([0,10],[rho]*2,[8000]*2,[200]*2,D,L)
    a=calc();assert calc(rho=4e-5)['impulse_Ns']==pytest.approx(2*a['impulse_Ns'])
    assert calc(L=4*317.)['impulse_Ns']==pytest.approx(2*a['impulse_Ns'])
    assert calc(D=2*31.7)['impulse_Ns']==pytest.approx(2*a['impulse_Ns'])
    assert a['mechanical_work_J']==pytest.approx(a['impulse_Ns']*8000)
    assert a['peak_dynamic_state']['reference_K']>600


def test_laminar_option_replaces_constant_without_changing_capture():
    x=defaults();x['capabilities'].update(skin_model='flat_plate_laminar')
    a=compile_hardware(*read_config(x));x['capabilities']['skin_friction_coefficient']=.5
    b=compile_hardware(*read_config(x))
    assert a['total_drag_impulse_Ns']==b['total_drag_impulse_Ns']
    assert a['skin_friction']['model']=='flat_plate_laminar'
    x['capabilities'].update(skin_model='constant',skin_friction_coefficient=0.)
    c=compile_hardware(*read_config(x))
    assert a['geometric_impulse_Ns']==c['geometric_impulse_Ns']
    np.testing.assert_array_equal(a['forcing']['supply'],c['forcing']['supply'])
    assert a['thrust_W']>c['thrust_W']


def test_plate_rejects_nonphysical_states():
    from atmo_scoops.transient.drag import flat_plate_laminar
    with pytest.raises(ValueError):
        flat_plate_laminar([0,1],[0,1e-5],[8000]*2,[200]*2,30,300)
    with pytest.raises(ValueError):
        flat_plate_laminar([1,0],[1e-5]*2,[8000]*2,[200]*2,30,300)
