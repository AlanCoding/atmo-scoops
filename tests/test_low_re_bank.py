import copy,json,math
import numpy as np
import pytest
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.porous import laminar_bank_coefficient,suction_pressure
from atmo_scoops.transient.global_search import coordinates,encode,decode,rank
from atmo_scoops.racks import conductance,Racks

def config():return json.load(open('configs/transient_low_re_search.json'))

def test_primary_equation_and_viscous_scaling():
    assert laminar_bank_coefficient(10,2,2)==pytest.approx(3.18858204485377)
    assert laminar_bank_coefficient(20,2,2)==pytest.approx(3.18858204485377/2)
    h=compile_hardware(*read_config(config()));g=h['geometry'][0]
    p1,_=suction_pressure(1,1000,500,287,g)
    p2,_=suction_pressure(2,1000,500,287,g)
    # Viscous term scales with mass flow; small exit loss adds a positive quadratic term.
    assert 2<(1e6-p2*p2)/(1e6-p1*p1)<2.01

def test_radius_and_pitch_propagate_to_geometry_and_exchange():
    x=config();h=compile_hardware(*read_config(x));g=h['geometry'][0]
    assert g['plane_open_fraction']==pytest.approx(.5)
    x['design']['stage_radius_m'][0]/=2;x['design']['stage_pitch_m'][0]/=2
    g2=compile_hardware(*read_config(x))['geometry'][0]
    assert g2['mass_kg']==pytest.approx(g['mass_kg'],rel=.03) # integer rows
    assert g2['wetted_m2']/g['wetted_m2']==pytest.approx(2,rel=.03)
    a,_=conductance(500,500,10,g['frontal_m2'],g,Racks())
    b,_=conductance(500,500,10,g2['frontal_m2'],g2,Racks())
    assert b>a
    p1,_=suction_pressure(1,1000,500,287,g)
    p2,_=suction_pressure(1,1000,500,287,g2)
    assert p2<p1

def test_bound_and_55_variable_roundtrip():
    c=config();spec=coordinates(c);assert len(spec)==55
    x=encode(c,spec);rebuilt=decode(x,c,spec)
    assert rebuilt['design']['stage_radius_m']==pytest.approx(c['design']['stage_radius_m'])
    low=x.copy();low[:5]=0
    assert decode(low,c,spec)['design']['stage_radius_m']==pytest.approx([.0002]*5)
    read_config(decode(low,c,spec))
    c['design']['stage_radius_m'][0]=.000199
    with pytest.raises(ValueError,match='0.2 mm'):read_config(c)

def test_feasibility_dominates_apparent_payoff():
    assert rank(dict(feasible=True,operating_payoff_days=1000))<rank(dict(feasible=False,violation=.001))
    assert rank(dict(feasible=False,violation=1))<rank(dict(feasible=False,violation=100))


def test_heos_table_preserves_real_gas_isentropic_work():
    from atmo_scoops.transient.thermo import properties,Y
    th=properties()
    try:
        for T,p1,p2 in [(300.,30.,3000.),(500.,500.,10000.),(340.,6000.,1500000.)]:
            th.table_enabled=False
            exact=th.compression(T,p1,p2,Y,.75)
            th.table_enabled=True
            interpolated=th.compression(T,p1,p2,Y,.75)
            assert interpolated==pytest.approx(exact,rel=1e-5)
    finally:th.table_enabled=False
