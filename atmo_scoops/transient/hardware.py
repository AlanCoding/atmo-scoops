"""Direct installed mass/packing compilation; never observes a simulated cycle."""
from dataclasses import asdict,replace
import math
import numpy as np
from ..compressor import Compressor,bank_mass
from ..chambers.materials import material
from ..chambers.model import Chamber
from ..orbit import Orbit
from ..atmosphere import make_profile
from ..encounter import orbit_state
from ..reboost import arc_restore
from .thermo import properties,Y
from .drag import skin_impulse,flat_plate_laminar
from .gas_feed import hardware as gas_hardware

def compile_hardware(d,c):
 o=Orbit(d.perigee_km,d.apogee_km);start=-max(1200.,d.burn_s/2+c.spin_s+10);end=start+o.period
 if end<d.plant_stop_s+300:raise ValueError('Orbit leaves insufficient post-processing recovery window')
 times=np.linspace(start,end,2401);phase=np.where(times>o.period/2,times-o.period,times)
 atm=make_profile('reference')
 # Truncate the negligible exosphere above the profile; never extrapolate dense air.
 atm=replace(atm,alt_km=np.r_[atm.alt_km,1000.01,max(1001.,d.apogee_km+1)],density=np.r_[atm.density,1e-100,1e-100],fractions=np.vstack([atm.fractions,atm.fractions[-1],atm.fractions[-1]]),temperature=np.r_[atm.temperature,atm.temperature[-1],atm.temperature[-1]])
 state=orbit_state(o,phase,atm);A=math.pi*d.bore_m**2/4
 supply=A*state['density_kg_m3']*state['speed_m_s'];inlet_window=np.clip((d.inlet_ceiling_km-state['altitude_km'])/d.inlet_taper_km,0.,1.);J=float(np.trapezoid(supply*state['speed_m_s'],times))
 inlet_impulse=J
 outside=d.bore_m+2*d.clearance_m;length=outside*d.length_diameter
 if c.skin_model=='constant':
  skin=skin_impulse(times,state['density_kg_m3'],state['speed_m_s'],outside,length,c.skin_friction_coefficient,c.skin_area_multiplier)
 elif c.skin_model=='flat_plate_laminar':
  skin=flat_plate_laminar(times,state['density_kg_m3'],state['speed_m_s'],state['temperature_K'],outside,length,c.skin_wall_K,c.skin_area_multiplier)
 else:raise ValueError('Unknown external skin model')
 J=inlet_impulse+skin['impulse_Ns']
 penalty=arc_restore(o,0,d.burn_s/2,samples=1001);power=J*penalty['impulse_multiplier']*d.isp_s*9.80665/(2*c.eta_thruster*d.burn_s)
 mats=[material(n) for n in d.materials]
 if any(not 298<=T<m.limit_K for T,m in zip(d.rack_initial_K,mats)):raise ValueError('Initial rack temperature outside material range')
 pitches=d.stage_pitch_m or [d.rod_pitch_m]*5
 radii=d.stage_radius_m or [d.rod_radius_m]*5
 if d.rack_flow_layout=='parallel_plates':
  from .plates import geometry as plate_geometry
  rack_depths=list(d.rack_depth_m)
  geom=[plate_geometry(A,z,t,g,m.density) for z,t,g,m in zip(rack_depths,d.plate_thickness_m,d.plate_gap_m,mats)]
  for i,g in enumerate(geom):
   g.update(row_count=d.plate_rows[i],offset_fraction=d.plate_offset_fraction,
            thermal_model=d.plate_thermal_model,
            row_clearance_m=d.plate_row_clearance_m,restart_loss_K=c.plate_restart_loss_K,
            entrance_credit=c.plate_entrance_credit,
            installed_rack_depth_m=rack_depths[i]+(d.plate_rows[i]-1)*d.plate_row_clearance_m)
  for g in geom:
   if d.plate_thermal_model=='offset_equivalent':
    g.update(thermal_gap_m=g['pitch_m']/g['row_count']-g['thickness_m'],
             row_offsets_m=[j*g['pitch_m']/g['row_count'] for j in range(g['row_count'])])
  rack_depths=[g['installed_rack_depth_m'] for g in geom]
 else:
  rack_depths=[math.ceil(z/p-1e-9)*p if d.rack_flow_layout in ('outlet_planes','inline_bank') or d.rack_pressure_model=='inline_laminar' else z for z,p in zip(d.rack_depth_m,pitches)]
  geom=[Chamber(str(i),d.bore_m,max(z,1),z,rod_radius_m=radii[i],rod_pitch_m=pitches[i],material=n).geometry(.5 if d.rack_flow_layout=='inline_bank' else .25) for i,(z,n) in enumerate(zip(rack_depths,d.materials))]
  for g,z,p,r in zip(geom,rack_depths,pitches,radii):g.update(row_count=z/p,rack_depth_m=z,plane_open_fraction=1-2*r/p,lattice='inline_square_bank' if d.rack_flow_layout=='inline_bank' else 'alternating_transverse_rod_planes')
  for g in geom:g['pressure_model']=d.rack_pressure_model
  if (d.rack_flow_layout=='inline_bank' or d.rack_pressure_model=='inline_laminar') and min(g['row_count'] for g in geom)<5-1e-9:raise ValueError('Bank correlation requires at least five physical rows')
 spec=Compressor(module_diameter_m=.5,tip_speed_m_s=350.,axial_velocity_m_s=100.)
 dummy=dict(rho_kg_m3=.001,mu_Pa_s=2e-5,sound_m_s=400.)
 banks=[]
 for S,H,P in zip(d.suction_m3_s,d.head_J_kg,d.motor_MW):
  b=bank_mass(S,H,P*1e6,spec,dummy);banks.append(b)
 coast=[]
 for i in range(3):coast.append(bank_mass(d.coast_suction_m3_s*d.coast_suction_fractions[i],d.coast_head_J_kg/3,d.coast_motor_MW*1e6/3,spec,dummy))
 gas_system=gas_hardware(d,c,spec,dummy)
 footprint=np.array([g['deployed_physical_m2'] if d.rack_flow_layout=='parallel_plates' else g['solid_m3']/(math.pi*g['wire_radius_m']**2/g['pitch_m']) for g in geom])
 reference_sink=380.;equiv=c.carnot_fraction*77.34/(reference_sink-77.34)
 masses=dict(racks=sum(g['mass_kg'] for g in geom),rack_mechanisms=float(sum(footprint))*c.rack_mechanism_kg_m2,
  dive_compressors=sum(b['total_kg'] for b in banks),coast_compressors=sum(b['total_kg'] for b in coast),
  refrigerator=d.plant_electric_MW*1e6*equiv*c.heat_pump_kg_W_equivalent,
  external_exchangers=(d.precool_UA_W_K+d.condenser_UA_W_K)/c.exchanger_UA_per_kg,
  separator=d.plant_flow_kg_s*c.separation_J_kg/1000*5,
  solar=d.solar_area_m2*c.solar_W_m2/c.solar_W_kg,
  battery=max(d.battery_MWh*1e6/c.battery_Wh_kg,d.battery_MW*1e6/c.battery_W_kg),
  bus=d.bus_MW*1000*c.bus_kg_kW,thrusters=power/1000*c.thruster_kg_kW,
  warm_store=d.warm_store_kg,warm_radiator=d.warm_radiator_m2*2*c.radiator_kg_m2,
  liquid_tanks=300*d.liquid_tank_m3,auxiliary=5000.)
 if gas_system['enabled']:masses['gas_reserve_system']=gas_system['mass_kg']
 packages=dict(solar=d.solar_area_m2*c.solar_W_m2/40000,warm_radiator=d.warm_radiator_m2*.02,
  battery=max(d.battery_MWh*1e6/280000,masses['battery']/1800),warm_store=d.warm_store_kg/800,
  machines=sum(masses[k] for k in ['dive_compressors','coast_compressors','refrigerator','external_exchangers','separator','bus','thrusters','rack_mechanisms','auxiliary'])/c.machinery_kg_m3,
  liquid_tanks=d.liquid_tank_m3*1.2)
 if d.propellant_storage=='valve':packages['machines']-=masses['thrusters']/c.machinery_kg_m3
 if gas_system['enabled']:packages['gas_reserve_system']=gas_system['package_m3']
 bay=sum(packages.values())/c.fill_fraction/A;outside=d.bore_m+2*d.clearance_m;length=outside*d.length_diameter
 hd=c.head_depth_m;rad=d.bore_m/2;headV=math.pi*hd*(3*rad**2+hd**2)/6
 depths=[rack_depths[i]+d.clear_depth_m[i]+(2*hd if i else 0) for i in range(4)]
 packing=None
 if d.explicit_stage_packing:
  # No arbitrary shared axial blocks: actual bank envelopes + dedicated hatch zones.
  bay=sum(b['bank_length_m']+d.stage_hatch_buffer_m for b in banks)
  x=0.;stages=[]
  for i,(L,b) in enumerate(zip(depths,banks)):
   rack_start=x+d.clear_depth_m[i]+(hd if i else 0.)
   stages.append(dict(stage=i+1,gas_start_m=x,gas_end_m=x+L,
      rack_start_m=rack_start,rack_end_m=rack_start+rack_depths[i],
      compressor_start_m=x+L,compressor_end_m=x+L+b['bank_length_m'],
      hatch_start_m=x+L+b['bank_length_m'],hatch_end_m=x+L+b['bank_length_m']+d.stage_hatch_buffer_m))
   x=stages[-1]['hatch_end_m']
  # All other existing hardware is still charged by volume in the aft region.
  # The next checkpoint assigns actual radial sectors and narrows the tank.
  other=dict(packages)
  front_mechanisms=footprint[:4]*c.rack_mechanism_kg_m2
  other['machines']-=(masses['dive_compressors']+float(sum(front_mechanisms)))/c.machinery_kg_m3
  if any(front_mechanisms/c.machinery_kg_m3 > d.stage_hatch_buffer_m*A*c.fill_fraction):
   raise ValueError('Rack mechanisms exceed dedicated hatch equipment buffers')
  packing=dict(stages=stages,receiver_start_m=x,receiver_end_m=length,
       front_mechanisms_m3=(front_mechanisms/c.machinery_kg_m3).tolist(),
       aft_packages_m3=other,aft_displacement_m3=sum(other.values())/c.fill_fraction,
       note='Aft package displacement preserves all hardware; radial layout pending')
 depths.append(length-bay-sum(depths)-(d.reserve_depth_m if d.propellant_storage=='valve' else 0.))
 receiver_rad=rad
 if d.propellant_storage=='valve':
  L=depths[-1];displacement=packing['aft_displacement_m3']
  # Rounded heads: V=pi*r²*(L-hd)+pi*hd³/3. Packages occupy annulus once.
  r2=rad**2-displacement/(math.pi*(L-hd))
  if r2<=0:raise ValueError('Packages exceed main receiver radial capacity')
  receiver_rad=math.sqrt(r2);area=math.pi*r2
  g=geom[-1];ratio=A/area
  g['rack_depth_m']*=ratio
  g['installed_rack_depth_m']=g['rack_depth_m']+(g['row_count']-1)*d.plate_row_clearance_m
  g['frontal_m2']=area;rack_depths[-1]=g['installed_rack_depth_m']
  reserve_volume=A*(d.reserve_depth_m-hd)+math.pi*hd**3/3
  gas_system.update(usable_internal_m3=reserve_volume,depth_m=d.reserve_depth_m,
                    start_m=length-d.reserve_depth_m,end_m=length,internal_radius_m=rad)
  packing.update(receiver_end_m=length-d.reserve_depth_m,receiver_radius_m=receiver_rad,
                 reserve_start_m=length-d.reserve_depth_m,reserve_end_m=length,
                 note='All aft packages ahead of reserve; annular displacement charged once')
 if depths[-1]<rack_depths[-1]+2*hd:raise ValueError('Installed hardware/racks exceed fixed hull length')
 vessel=0
 for i,(g,L) in enumerate(zip(geom,depths)):
  vr=receiver_rad if i==4 else rad;va=math.pi*vr**2
  gross=va*L if i==0 else va*(L-hd)+math.pi*hd**3/3
  displacement=packing['aft_displacement_m3'] if packing and i==4 else 0.
  gas_volume=gross-g['solid_m3']-(0. if d.propellant_storage=='valve' and i==4 else displacement)
  if gas_volume<=0 or (i==4 and gas_volume<g['envelope_m3']-g['solid_m3']):raise ValueError('Aft equipment/rack displacement exceeds receiver')
  g.update(gross_m3=gross,gas_m3=gas_volume,depth_m=L,deployed_physical_m2=float(footprint[i]))
  if packing:g['equipment_displacement_m3']=displacement
  if i:
   rating=d.rated_pressure_Pa[i-1];barrel=2*math.pi*vr*(L-2*hd);heads=2*math.pi*(vr**2+hd**2);R=(vr**2+hd**2)/(2*hd)
   vessel+=(barrel*max(.001,1.5*rating*vr/150e6)+heads*max(.001,1.5*rating*R/(2*150e6)))*2700*1.5+(barrel+heads)
 if d.propellant_storage=='valve':
  L=d.reserve_depth_m;rating=d.rated_pressure_Pa[-1]
  barrel=2*math.pi*rad*(L-2*hd);heads=2*math.pi*(rad**2+hd**2);R=(rad**2+hd**2)/(2*hd)
  shell=(barrel*max(.001,1.5*rating*rad/150e6)+heads*max(.001,1.5*rating*R/(2*150e6)))*2700*1.5+(barrel+heads)
  vessel+=shell;gas_system['shell_and_support_kg']=shell
 masses['pressure_vessels']=vessel;masses['hull']=math.pi*outside*length*4
 masses['margin']=sum(masses.values())*c.margin
 prop=J*penalty['impulse_multiplier']/(d.isp_s*9.80665)
 return dict(orbit=o,geometry=geom,stage_packing=packing,gas_system=gas_system,banks=banks,coast_banks=coast,masses_kg=masses,dry_kg=sum(masses.values()),packages_m3=packages,bay_m=bay,length_m=length,outside_m=outside,
  thrust_W=power,required_impulse_Ns=J*penalty['impulse_multiplier'],geometric_impulse_Ns=inlet_impulse,total_drag_impulse_Ns=J,skin_friction=skin,skin_impulse_fraction=skin['impulse_Ns']/inlet_impulse,unresolved_exospheric_incident_kg=float(np.trapezoid(supply*(1-inlet_window),times)),propellant_reference_kg=prop,arc=penalty,
  start_s=start,end_s=end,forcing=dict(time=times,phase=phase,supply=supply*inlet_window,pressure=state['ram_Pa']*inlet_window,temperature=state['temperature_K'],speed=state['speed_m_s']),
  array_motion_s=math.sqrt(d.solar_area_m2)/c.deployment_m_s,radiator_motion_s=math.sqrt(d.warm_radiator_m2)/c.deployment_m_s,
  rack_motion_s=np.sqrt(footprint)/c.deployment_m_s,safe_s=o.time_at_altitude(200.))
