"""Gas-feed inventory and rack hydraulic/geometry contracts."""
import json
import numpy as np
import pytest
from atmo_scoops.transient import defaults
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.porous import suction_pressure,pump_flow
from atmo_scoops.transient.thermo import properties,Y

def geometry():
    x=defaults();x['design'].update(rack_flow_layout='outlet_planes',stage_pitch_m=[.02]*5)
    return compile_hardware(*read_config(x))['geometry'][0]

def test_transverse_planes_have_consistent_material_and_open_area():
    g=geometry();r=g['wire_radius_m'];p=g['pitch_m']
    assert g['row_count']==pytest.approx(round(g['row_count']))
    assert g['solid_m3']==pytest.approx(g['row_count']*g['frontal_m2']/p*np.pi*r*r)
    assert g['plane_open_fraction']==pytest.approx(1-2*r/p)

def test_resistance_limits_and_monotonicity():
    g=geometry();args=(500.,500.,287.,g)
    assert suction_pressure(10.,*args,0.)[0]==500.
    p1,info=suction_pressure(1.,*args)
    p2,_=suction_pressure(2.,*args)
    assert 0<=p2<p1<500.
    assert info['Re']>0 and info['Kn']>0
    assert suction_pressure(1e8,*args)[0]==0.

def test_pump_and_rack_solve_same_mass_flow():
    th=properties();g=geometry();p,T,pout,R=500.,500.,2000.,float(Y@th.R)
    args=(p,T,pout,R,Y,g,2000.,2e6,1e8,.95,.75,th,.1)
    f0,*_=pump_flow(*args,0.)
    f,ps,w,info=pump_flow(*args,1.)
    assert 0<f<f0 and ps<p
    assert w==pytest.approx(th.compression(T,ps,pout,Y,.75))
    expected=2000.*(ps-.03)/(R*T)*max(0,1-(w/2e6)**2)
    assert f==pytest.approx(expected,rel=2e-6)

def test_gas_tanks_displace_receiver_and_charge_mass():
    x=defaults();h0=compile_hardware(*read_config(x))
    x['design']['propellant_storage']='gas';h=compile_hardware(*read_config(x))
    assert h['geometry'][-1]['depth_m']<h0['geometry'][-1]['depth_m']
    assert h['dry_kg']>h0['dry_kg']
    assert h['gas_system']['tank_count']==4
    assert h['gas_system']['outer_diameter_m']<h['outside_m']
    x['design']['rack_flow_layout']='legacy_mixed';x['capabilities']['rack_loss_multiplier']=1
    with pytest.raises(ValueError,match='outlet-plane'):read_config(x)

def test_saved_gas_cycle_refills_before_next_burn_without_liquid_propellant():
    from atmo_scoops.transient.io import read_result
    r=read_result('results/transient/gas_trial.json')
    assert r['feasible'] and r['audits']['forward_integrations']==1
    assert r['audits']['species_kg']<1e-4 and r['audits']['energy_MJ']<.01
    assert max(abs(z) for z in r['closure']['gas_reserve_species_kg'])<.1
    assert abs(r['closure']['gas_reserve_MJ'])<1
    liquid=np.array(r['liquid_species_kg']);gas=np.array(r['gas_reserve_species_kg'])
    assert liquid[0].sum()==0 and gas[0].sum()==pytest.approx(4500.)
    assert gas.sum(axis=1).min()>0
    assert r['net_liquid_kg']==pytest.approx(sum(r['ledger']['made_'+s][-1] for s in ('N2','O2','Ar')))
    assert r['delivered_payoff_days'] is None

def test_saved_resistance_cycle_conserves_and_reduces_capture():
    from atmo_scoops.transient.io import read_result
    loss=read_result('results/transient/rack_trial.json')
    zero=read_result('results/transient/feed_pitch/cycle_layout_only.json')
    assert loss['audits']['species_kg']<1e-4 and loss['audits']['energy_MJ']<.01
    assert loss['audits']['forward_integrations']==1
    assert np.max(np.array(loss['history']['pump_kg_s'])[:,0])<np.max(np.array(zero['history']['pump_kg_s'])[:,0])
    assert np.max(np.array(loss['history']['rack_drop_Pa'])[:,0])>100
    assert not loss['feasible'] and loss['operating_payoff_days'] is None

def test_combined_cycle_cannot_count_product_while_depleting_gas_reserve():
    from atmo_scoops.transient.io import read_result
    r=read_result('results/transient/feed_pitch/cycle_joint_dense.json')
    assert r['net_liquid_kg']>0
    deficit=-sum(r['closure']['gas_reserve_species_kg'])
    assert deficit>r['net_liquid_kg']
    assert r['margins']['periodic']<0
    assert not r['feasible'] and r['operating_payoff_days'] is None
    assert r['audits']['species_kg']<1e-4 and r['audits']['energy_MJ']<.01
