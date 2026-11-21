import math
import pytest
from atmo_scoops.transient.plates import geometry,diagnostics,charge,conductance
from atmo_scoops.transient.porous import viscosity
from atmo_scoops.racks import Racks


def test_plate_inventory_and_two_faces():
    g=geometry(10.,2.,.001,.004,2700.)
    assert g['solid_m3']==pytest.approx(4.)
    assert g['wetted_m2']==pytest.approx(8000.)
    assert g['deployed_physical_m2']==pytest.approx(4000.)
    assert g['gas_m3']+g['solid_m3']==pytest.approx(20.)


def test_poiseuille_darcy_and_power_scaling():
    g=geometry(10.,2.,.001,.004,2700.)
    p,T,rho,flow=1000.,300.,.01,.1
    a=diagnostics(flow,p,T,rho,g);u=flow/(rho*10*g['porosity']);dh=.008
    expected=96/a['Re']*2/dh*rho*u*u/2
    assert a['drop_Pa']==pytest.approx(expected)
    power,_=charge(flow,p,T,rho,g,.75)
    assert power==pytest.approx(a['drop_Pa']*flow/rho/.75)
    assert charge(2*flow,p,T,rho,g,.75)[0]==pytest.approx(4*power)
    assert charge(0,0,T,0,g,.75)==(0.,0.)


def test_conductance_rarefaction_and_thickness():
    g=geometry(10.,2.,.001,.004,2700.)
    ua,info=conductance(1e6,300.,.1,10,g,Racks())
    continuum=7.54*viscosity(300)*1100/.71/.008
    assert info['h_W_m2_K']==pytest.approx(continuum,rel=1e-3)
    assert info['Bi']==pytest.approx(info['h_W_m2_K']*.001/(2*40))
    assert conductance(1e-8,300.,0,10,g,Racks())[0]<ua*1e-6


def test_optimizer_roundtrip_and_independent_inventory():
    import json
    from pathlib import Path
    from atmo_scoops.transient.plate_optimize import specs,encode,decode
    c=json.loads(Path('configs/transient_plates_seed.json').read_text());s=specs(c);x=encode(c,s)
    decoded=decode(x,c,s)
    assert decoded['design']['rack_depth_m']==pytest.approx(c['design']['rack_depth_m'])
    solid=lambda d:[z*t/(t+g) for z,t,g in zip(d['rack_depth_m'],d['plate_thickness_m'],d['plate_gap_m'])]
    x[0]+=.01
    changed=decode(x,c,s)
    assert solid(changed['design'])==pytest.approx(solid(c['design']))
    assert changed['design']['plate_gap_m'][0]>c['design']['plate_gap_m'][0]
    assert changed['design']['plate_thickness_m']==pytest.approx(c['design']['plate_thickness_m'])


def test_signed_closure_constraints():
    from atmo_scoops.transient.plate_optimize import constraint_vector
    r=dict(margins={'product_kg':1.,'periodic':0.},closure=dict(rack_enthalpy_J_kg=[0.]*5,battery_MJ=100.,warm_MJ=0.,gas_kg=0.,gas_MJ=0.,rotor_MJ=0.,thrust_relative=0.,gas_reserve_species_kg=[0.]*3,gas_reserve_MJ=0.),audits=dict(species_kg=0.,energy_MJ=0.,min_gas_kg=0.),feasible=True)
    names,v=constraint_vector(r)
    assert v[names.index('battery_MJ:0:upper')]==0
    assert v[names.index('battery_MJ:0:lower')]==2
    r['closure']['battery_MJ']=-101.;r['feasible']=False
    names,v=constraint_vector(r)
    assert v[names.index('battery_MJ:0:lower')]==pytest.approx(-.01)


def test_small_scaled_path_violation_does_not_become_discrete_rejection():
    from atmo_scoops.transient.plate_optimize import constraint_vector
    r=dict(margins={'warm_K':-1e-5},closure=dict(rack_enthalpy_J_kg=[0.]*5,battery_MJ=0.,warm_MJ=0.,gas_kg=0.,gas_MJ=0.,rotor_MJ=0.,thrust_relative=0.,gas_reserve_species_kg=[0.]*3,gas_reserve_MJ=0.),audits=dict(species_kg=0.,energy_MJ=0.,min_gas_kg=0.),feasible=False)
    names,v=constraint_vector(r)
    assert v[names.index('warm_K')]==pytest.approx(-1e-7)
    assert v[names.index('other_validity')]==1.


def test_serial_wider_pitch_preserves_material_and_faces():
    g=geometry(700.,.9,.0014,.0062,3210.)
    wide=geometry(700.,3.6,.0014,4*(.0014+.0062)-.0014,3210.)
    for key in ('solid_m3','mass_kg','wetted_m2'):
        assert wide[key]==pytest.approx(g[key])
    assert wide['gas_m3']>g['gas_m3']
    expected=(wide['pitch_m']/g['pitch_m'])**2*(g['gap_m']/wide['gap_m'])**3
    assert diagnostics(40,400,900,.0017,wide)['drop_Pa']/diagnostics(40,400,900,.0017,g)['drop_Pa']==pytest.approx(expected)


def test_interrupted_rows_have_no_free_heat_or_pressure_credit():
    g=geometry(700.,3.6,.0014,.029,3210.)
    base=conductance(400.,800.,40.,700.,g,Racks())[0]
    original_dp=diagnostics(40.,400.,800.,.002,g)['drop_Pa']
    offset=dict(g,row_count=4,offset_fraction=.5,restart_loss_K=.674,entrance_credit=1.)
    assert conductance(400.,800.,40.,700.,offset,Racks())[0]>base
    assert diagnostics(40.,400.,800.,.002,offset)['drop_Pa']>original_dp
    aligned=dict(offset,offset_fraction=0.)
    assert conductance(400.,800.,40.,700.,aligned,Racks())[0]==pytest.approx(base)
    assert diagnostics(40.,400.,800.,.002,aligned)['drop_Pa']==pytest.approx(original_dp)
    assert charge(0,400,800,.002,offset,.75)==(0.,0.)
    assert conductance(400,800,0,700,offset,Racks())[0]>0


def test_explicit_stages_keep_other_hardware_and_gas_displacement():
    import json
    from pathlib import Path
    from atmo_scoops.transient.inputs import read_config
    from atmo_scoops.transient.hardware import compile_hardware
    c=json.loads(Path('configs/transient_staggered_seed.json').read_text())
    d,cap=read_config(c);h=compile_hardware(d,cap);p=h['stage_packing']
    assert p['stages'][0]['rack_start_m']==10.
    for stage,bank in zip(p['stages'],h['banks']):
        assert stage['hatch_end_m']-stage['hatch_start_m']==pytest.approx(1.)
        assert stage['compressor_end_m']-stage['compressor_start_m']==pytest.approx(bank['bank_length_m'])
    allocated=sum(p['aft_packages_m3'].values())+h['masses_kg']['dive_compressors']/cap.machinery_kg_m3+sum(p['front_mechanisms_m3'])
    assert allocated==pytest.approx(sum(h['packages_m3'].values()))
    g=h['geometry'][-1]
    assert g['gas_m3']+g['solid_m3']+p['aft_displacement_m3']==pytest.approx(g['gross_m3'])
    assert p['stages'][-1]['hatch_end_m']+g['depth_m']==pytest.approx(317.)
    original=c['design']['plate_row_clearance_m'];c['design']['plate_row_clearance_m']=original+.01
    changed=compile_hardware(*read_config(c))
    # Four front racks each gain 3 gaps, while the receiver surrenders the length.
    assert changed['geometry'][-1]['depth_m']==pytest.approx(g['depth_m']-.12)


def test_offset_equivalence_preserves_heat_at_paid_volume_and_lower_loss():
    narrow=geometry(700.,.9,.0014,.0062,3210.)
    wide=geometry(700.,3.6,.0014,4*narrow['pitch_m']-.0014,3210.)
    wide.update(row_count=4,thermal_model='offset_equivalent',restart_loss_K=.674)
    for p in (0.,.01,400.,1e6):
        a,_=conductance(p,800.,40.,700.,narrow,Racks())
        b,info=conductance(p,800.,40.,700.,wide,Racks())
        assert b==pytest.approx(a)
        assert info['thermal_gap_m']==pytest.approx(narrow['gap_m'])
    assert wide['envelope_m3']==pytest.approx(4*narrow['envelope_m3'])
    assert wide['mass_kg']==pytest.approx(narrow['mass_kg'])
    assert wide['wetted_m2']==pytest.approx(narrow['wetted_m2'])
    assert diagnostics(40,400,800,.002,wide)['drop_Pa']<diagnostics(40,400,800,.002,narrow)['drop_Pa']
    single=dict(narrow,row_count=1,thermal_model='offset_equivalent')
    assert conductance(400,800,40,700,single,Racks())[0]==pytest.approx(conductance(400,800,40,700,narrow,Racks())[0])


def test_thermal_optimizer_coordinates_pay_in_actual_volume():
    import json
    from pathlib import Path
    from atmo_scoops.transient.plate_optimize import specs,encode,decode
    from atmo_scoops.transient.hardware import compile_hardware
    from atmo_scoops.transient.inputs import read_config
    c=json.loads(Path('configs/transient_staggered_thermal_seed.json').read_text());s=specs(c);x=encode(c,s)
    assert s[0]['key']=='thermal_gap_m:0'
    assert decode(x,c,s)['design']['plate_gap_m']==pytest.approx(c['design']['plate_gap_m'])
    a=compile_hardware(*read_config(c));x[0]+=.02;changed=decode(x,c,s);b=compile_hardware(*read_config(changed))
    assert b['geometry'][0]['mass_kg']==pytest.approx(a['geometry'][0]['mass_kg'])
    assert b['geometry'][0]['thermal_gap_m']>a['geometry'][0]['thermal_gap_m']
    assert b['geometry'][0]['gap_m']>a['geometry'][0]['gap_m']
    assert b['geometry'][0]['depth_m']>a['geometry'][0]['depth_m']
    assert b['geometry'][4]['depth_m']<a['geometry'][4]['depth_m']
    # Thickness changes cannot produce a negative effective gap.
    x[5]=1.;d=decode(x,c,s);read_config(d)
