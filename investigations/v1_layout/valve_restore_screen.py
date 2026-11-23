"""Algebraic planning screen only: no cycle integration or optimization."""
import json,math
from pathlib import Path
import numpy as np
from atmo_scoops.transient.io import read_result
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.thermo import properties,Y
from atmo_scoops.atmosphere import make_profile
ROOT=Path(__file__).resolve().parents[2]
r=read_result(ROOT/'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz');h=r['hardware'];d=r['inputs']['design'];cap=r['inputs']['capabilities']
A=math.pi*d['bore_m']**2/4;rad=d['bore_m']/2;hd=cap['head_depth_m'];head=lambda radius:math.pi*hd*(3*radius**2+hd**2)/6
rs=h['stage_packing']['receiver_start_m'];reserve_length=125.;split=h['length_m']-reserve_length;L=split-rs
# Retain all non-reserve package estimates as a planning seed; future resized
# hardware/valve and bulkhead allowances must be recomputed in the real model.
packages=h['stage_packing']['aft_displacement_m3']-h['gas_system']['package_m3']/cap['fill_fraction']
gross=lambda radius,length:math.pi*radius**2*(length-2*hd)+2*head(radius)
main_radius=math.sqrt((gross(rad,L)-packages-math.pi*hd**3/3)/(math.pi*(L-hd)))
Vm=gross(main_radius,L)-h['geometry'][4]['solid_m3'];Vr=gross(rad,reserve_length)
old=compile_hardware(*read_config(r['inputs']));C0=float(np.trapezoid(old['forcing']['supply'],old['forcing']['time']));B0=old['propellant_reference_kg'];beta=B0/C0
hist=np.array(r['history']['pressure_Pa'])[:,4];ip=int(np.argmax(hist));P0=float(hist[ip]);T0=r['history']['gas_K'][ip][4];R=float(Y@properties().R)
atm=make_profile();hm=d['perigee_km'];rho1=float(atm.at(hm-.25)[0]);rho2=float(atm.at(hm+.25)[0]);H=.5/math.log(rho1/rho2)
cases=[]
for name,P in [('preserve_previous_working_pressure',P0),('inherited_rating_divided_by_1.1',6500/1.1),('inherited_rating_no_margin',6500)]:
 main_mass=P*Vm/(R*T0);C=main_mass/(1-beta);B=beta*C;reserve=P*Vr/(R*T0);factor=C/C0;alt=hm-H*math.log(factor)
 cases.append(dict(name=name,target_pressure_Pa=P,temperature_K=T0,fresh_capture_kg=C,propellant_kg=B,main_mass_kg=main_mass,reserve_mass_kg=reserve,fresh_capture_scale=factor,perigee_km=alt,preentry_halfburn_remaining_kg=reserve-B/2))
out=dict(status='algebraic planning estimate, not a new simulation',base_perigee_km=hm,apogee_km=d['apogee_km'],main_start_m=rs,split_m=split,hull_end_m=h['length_m'],main_length_m=L,reserve_length_m=reserve_length,main_radius_m=main_radius,reserve_radius_m=rad,main_gas_m3=Vm,reserve_gas_m3=Vr,retained_package_displacement_m3=packages,head_depth_m=hd,receiver_rack_core_m=h['geometry'][4]['rack_depth_m']*(rad/main_radius)**2,reference_incident_kg=C0,reference_propellant_kg=B0,beta=beta,local_density_scale_height_km=H,cases=cases)
assert Vm>0 and Vr>0 and 0<beta<1
for z in cases:assert abs(z['fresh_capture_kg']-z['propellant_kg']-z['main_mass_kg'])<1e-8
Path(__file__).with_name('VALVE_ALGEBRA.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
