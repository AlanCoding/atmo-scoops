import math
from dataclasses import replace
import numpy as np
import pytest
import CoolProp.CoolProp as CP
from atmo_scoops.compressor import RealAir,Compressor,bank_mass,evaluate_train_history


def test_isentropic_entropy_and_actual_efficiency():
    gas=RealAir()
    ideal=gas.compress(30.,1000.,300.,1.)
    actual=gas.compress(30.,1000.,300.,.75)
    assert ideal['outlet']['s_J_kg_K']==pytest.approx(ideal['inlet']['s_J_kg_K'],abs=1e-6)
    assert actual['outlet']['s_J_kg_K']>actual['inlet']['s_J_kg_K']
    assert actual['shaft_J_kg']==pytest.approx(ideal['shaft_J_kg']/.75,rel=1e-9)
    assert actual['outlet']['T_K']>ideal['outlet']['T_K']
    # Independently use CoolProp's entropy and enthalpy flash, not our PT root.
    f=gas.fluid;f.update(CP.PSmass_INPUTS,300.,actual['inlet']['s_J_kg_K'])
    assert f.hmass()==pytest.approx(actual['isentropic_h_J_kg'],rel=1e-9)


def test_property_domain_nonideality_and_bypass():
    gas=RealAir()
    assert abs(gas.state(5e6,300.)['Z']-1)>1e-3
    assert gas.compress(30,1000,20,.75)['shaft_J_kg']==0
    with pytest.raises(ValueError,match='domain'):gas.compress(30,1000,1e7,.5)
    with pytest.raises(ValueError):Compressor(blocks=2.5).validate()


def test_row_volume_is_total_not_per_blade_and_motor_counted_once():
    s=Compressor();state=RealAir().state(30.,1000.)
    b=bank_mass(10.,10000.,1000.,s,state)
    height=b['module_diameter_m']*(1-s.hub_tip_ratio)/2
    row_volume=s.blade_volume_factor*height**3/s.blade_aspect_ratio**2
    assert b['rotor_and_stator_kg']==pytest.approx(2*row_volume*s.material_density_kg_m3*b['rows']*b['modules'])
    assert b['total_kg']==pytest.approx(b['structural_kg']+1.)
    heavy=bank_mass(10.,10000.,1000.,replace(s,mass_multiplier=2),state)
    assert heavy['structural_kg']==pytest.approx(2*b['structural_kg'])
    with pytest.raises(ValueError,match='stress'):
        bank_mass(10.,10000.,1000.,replace(s,tip_speed_m_s=1000),state)


def test_train_energy_contains_spinup_and_idle_exactly_once():
    gas=RealAir();s=Compressor()
    times=np.linspace(0,60,5)
    r=evaluate_train_history(gas,s,np.full(5,30.),1000,np.full(5,3000.),
                            np.ones(5),times,4,600,.95,rated_suction=10000,idle_fraction=.05)
    shaft_electric=float(np.trapezoid(r['bank_power_W'].sum(axis=1),times))
    assert r['electricity_J']==pytest.approx(shaft_electric+r['spinup_electric_J']+60*r['idle_electric_W'])
    assert len(r['banks'])==4
