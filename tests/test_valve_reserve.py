"""Geometry and conservative port contracts for the valve-reserve restoration."""
import json,math,copy
from pathlib import Path
import pytest
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.gas_feed import valve_flow,state
from atmo_scoops.transient.thermo import properties,Y

def config():return json.loads(Path('configs/transient_valve_seed.json').read_text())

def test_volume_partition_packages_and_rack_fit():
 d,c=read_config(config());h=compile_hardware(d,c);g=h['geometry'][-1];p=h['stage_packing'];v=h['gas_system']
 assert p['reserve_start_m']==192 and v['depth_m']==125
 assert p['receiver_end_m']==p['reserve_start_m']
 assert sum(x['depth_m'] for x in h['geometry'])+h['bay_m']+v['depth_m']==pytest.approx(317)
 A=math.pi*15**2;hd=c.head_depth_m
 full=A*(g['depth_m']-hd)+math.pi*hd**3/3
 assert g['gross_m3']+p['aft_displacement_m3']==pytest.approx(full)
 assert g['frontal_m2']==pytest.approx(math.pi*p['receiver_radius_m']**2)
 assert g['rack_depth_m']*g['frontal_m2']==pytest.approx(g['envelope_m3'])
 assert v['fill_bank']['total_kg']==v['fill_bank']['spin_energy_J']==0
 assert h['masses_kg']['gas_reserve_system']==2500
 more=config();more['design']['solar_area_m2']*=1.1
 h2=compile_hardware(*read_config(more))
 assert h2['gas_system']['usable_internal_m3']==v['usable_internal_m3']
 assert h2['geometry'][-1]['gas_m3']<g['gas_m3']
 assert h2['geometry'][-1]['mass_kg']==g['mass_kg']

def test_valve_pressure_direction_and_equalization_energy():
 th=properties();m1=100*Y;m2=50*Y
 h,cp,R=th.at(400);U1=100*(Y@h-R*400);U2=50*(Y@h-R*400)
 a=state(th,m1,U1/1e6,1000);b=state(th,m2,U2/1e6,1000)
 f=valve_flow(a['p'],b['p'],a['T'],.1,R,cp)
 assert f>0 and valve_flow(b['p'],a['p'],b['T'],.1,R,cp)==0
 assert valve_flow(a['p'],a['p'],a['T'],.1,R,cp)==0
 dt=.001;transfer=f*dt*Y;Q=f*dt*a['h']
 assert sum(m1-transfer)+sum(m2+transfer)==pytest.approx(150)
 assert (U1-Q)+(U2+Q)==pytest.approx(U1+U2)
 assert valve_flow(a['p'],0,a['T'],.2,R,cp)==pytest.approx(2*valve_flow(a['p'],0,a['T'],.1,R,cp))

def test_valve_rejects_hidden_thermal_conditioning():
 c=config();c['design']['gas_thermal_UA_W_K']=50000
 with pytest.raises(ValueError,match='adiabatic'):read_config(c)

def test_external_thruster_mass_does_not_displace_receiver():
 c=config();a=compile_hardware(*read_config(c));c['design']['isp_s']*=1.1
 b=compile_hardware(*read_config(c))
 assert b['masses_kg']['thrusters']>a['masses_kg']['thrusters']
 assert b['packages_m3']['machines']==pytest.approx(a['packages_m3']['machines'])
 assert b['geometry'][-1]['gas_m3']==pytest.approx(a['geometry'][-1]['gas_m3'])
