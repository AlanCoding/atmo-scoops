"""One forward hybrid cycle, conservative port/energy ledgers, finite hardware."""
from dataclasses import asdict
from functools import lru_cache
import math
import os,sys
import numpy as np
from scipy.integrate import solve_ivp
from ..chambers.materials import material
from ..racks import conductance,Racks
from ..open_mouth import port_flow
from ..orbit import MU,R_EARTH
from ..reboost import state_at
from .inputs import read_config
from .hardware import compile_hardware
from .thermo import properties,Y
from .gas_feed import state as gas_state
from .porous import pump_flow,suction_pressure,viscosity
from .loss_power_screen import charge as rack_power_charge

LEDGERS=['in_N2','in_O2','in_Ar','lost_N2','lost_O2','lost_Ar','made_N2','made_O2','made_Ar','prop_N2','prop_O2','prop_Ar','mix_kg','solar_MJ','radiated_MJ','boundary_MJ','exhaust_MJ','unmet_MJ','thrust_Ns','shaft_MJ','plant_MJ']+[f'rack_loss_{i}_MJ' for i in range(5)]
class ConstraintViolation(RuntimeError):
 pass

PROP_Y=np.array([.755,.232,0.])/.987
LI={name:40+i for i,name in enumerate(LEDGERS)}

def simulate(config,samples=1001):
 d,c=read_config(config);power_only=d.rack_loss_mode=='power_only';hydraulic_loss=c.rack_loss_multiplier if not power_only else 0.;hw=compile_hardware(d,c);th=properties();geom=hw['geometry'];mats=[material(n) for n in d.materials]
 th.table_enabled=d.compression_model=='HEOS_table'
 V=np.array([g['gas_m3'] for g in geom]);M=np.array([g['mass_kg'] for g in geom]);start,end=hw['start_s'],hw['end_s'];o=hw['orbit']
 y0=np.zeros(40+len(LEDGERS));y0[20:25]=[m.energy(T)*mass/1e6 for m,T,mass in zip(mats,d.rack_initial_K,M)]
 # A declared trace residual avoids singular empty-vessel temperature states.
 for i in range(5):
  trace=.001*V[i]/(float(Y@th.R)*300.)
  y0[3*i:3*i+3]=trace*Y;y0[15+i]=trace*float(Y@th.at(300.)[0]-float(Y@th.R)*300.)/1e6
 capacity=d.battery_MWh*3600.;y0[25]=capacity*d.battery_initial_soc;y0[26]=d.warm_store_kg*c.buffer_cp_J_kg_K*d.warm_initial_K/1e6;y0[27:30]=d.reserve_kg*Y
 gas_mode=d.propellant_storage=='gas'
 if gas_mode:
  y0[35:38]=d.gas_reserve_kg*np.array(d.gas_initial_fractions)
  h0,_,R0=th.at(d.gas_initial_K,np.array(d.gas_initial_fractions));y0[38]=d.gas_reserve_kg*(np.array(d.gas_initial_fractions)@h0-R0*d.gas_initial_K)/1e6
 Emax=np.array([b['spin_energy_J'] for b in hw['banks']]+[sum(b['spin_energy_J'] for b in hw['coast_banks']),hw['gas_system']['fill_bank']['spin_energy_J']])
 masses_limit=np.array(list(d.motor_MW)+[d.coast_motor_MW,d.gas_fill_motor_MW if gas_mode else 0.])*1e6
 release=np.array([d.pump_stop_s+d.vent_duration_s]*4+[d.plant_stop_s+d.vent_duration_s]);vent_start=release-d.vent_duration_s
 purged=np.zeros(5,dtype=bool);safe_hatch=np.ones(5,dtype=bool)
 forcing=hw['forcing'];r,vr,vt=state_at(o,forcing['time']);f=np.arctan2(vr*o.h/(MU*o.e),(o.h**2/(MU*r)-1)/o.e)
 shadow=(r*np.cos(f)<0)&(abs(r*np.sin(f))<R_EARTH);sun=(~shadow).astype(float)
 initial_liquid_h=float(y0[27:30]@th.liquid_h)
 def decode(y):
  mass=np.maximum(y[:15].reshape(5,3),0);total=mass.sum(axis=1);fractions=np.array([mm/tt if tt>1e-30 else Y for mm,tt in zip(mass,total)])
  # Smooth trace-mass regularization only for the singular vacuum limit.
  trace=c.vacuum_regularization_kg;u300=float(Y@th.at(300.)[0]-float(Y@th.R)*300.)
  Tg=np.array([th.temperature(y[15+i]*1e6+trace*u300,mass[i]+trace*Y) for i in range(5)])
  Tm=np.array([m.temperature(y[20+i]*1e6/M[i]) for i,m in enumerate(mats)])
  P=total*np.array([yy@th.R for yy in fractions])*Tg/V
  return mass,total,fractions,Tg,Tm,P
 evaluations=[0]
 def rates(t,y,detail=False):
  if not detail:evaluations[0]+=1
  if evaluations[0]>d.max_rhs_evaluations:raise RuntimeError(f"Numerical evaluation budget exceeded at t={t:.6f} s; candidate unresolved, not physically ruled out")
  dy=np.zeros_like(y);mass,total,yy,T,Tm,p=decode(y);Tw=y[26]*1e6/(d.warm_store_kg*c.buffer_cp_J_kg_K)
  state=[th.at(T[i],yy[i]) for i in range(5)];hs=np.array([s[0] for s in state]);cp=np.array([s[1] for s in state]);R=np.array([s[2] for s in state])
  phase=t if t<=o.period/2 else t-o.period
  solar_exposure=float(np.clip((abs(phase)-hw['safe_s'])/hw['array_motion_s'],0,1));rad_exposure=float(np.clip((abs(phase)-hw['safe_s'])/hw['radiator_motion_s'],0,1))
  solar=d.solar_area_m2*c.solar_W_m2*solar_exposure*float(np.interp(t,forcing['time'],sun))
  S=float(np.interp(t,forcing['time'],forcing['supply']));support=float(np.interp(t,forcing['time'],forcing['pressure']));Tamb=float(np.interp(t,forcing['time'],forcing['temperature']));v=float(np.interp(t,forcing['time'],forcing['speed']))
  hin=th.at(Tamb)[0]+v*v/2
  def port(up,down):
   if up<=down:return 0.
   eps=.001;gamma=cp[0]/(cp[0]-R[0]);fraction=min(1.,(up-down)/(eps*up))
   return port_flow(up,min(down,up*(1-eps)),T[0],geom[0]['frontal_m2'],R[0],gamma,.8)*fraction
  admitted=min(S,port(support,p[0])) if not purged[0] or t<d.pump_stop_s else 0.
  # No inlet door: after withdrawal the front remains open; insignificant next-entry forcing can refill it.
  if purged[0]:admitted=min(S,port(support,p[0]))
  leak=min(port(p[0],support),total[0]*100)
  dy[:3]+=admitted*Y-leak*yy[0];dy[15]+=(admitted*(Y@hin)-leak*(yy[0]@hs[0]))/1e6
  dy[LI['in_N2']:LI['in_Ar']+1]+=admitted*Y;dy[LI['lost_N2']:LI['lost_Ar']+1]+=leak*yy[0]
  dy[LI['boundary_MJ']]+=(admitted*(Y@hin)-leak*(yy[0]@hs[0]))/1e6
  # Optional recycled LN2: transfer liquid mass/enthalpy internally, never fresh product.
  injection=admitted*d.mixing_ratio*float(np.clip(y[27]/10,0,1))
  dy[0]+=injection;dy[15]+=injection*th.liquid_h[0]/1e6;dy[27]-=injection;dy[LI['mix_kg']]=injection
  active=np.array([-500<=t<d.pump_stop_s]*4+[d.plant_start_s<=t<d.plant_stop_s,gas_mode and d.plant_start_s<=t<d.plant_stop_s])
  rotor=np.r_[y[30:35],y[39]]
  gs=gas_state(th,np.maximum(y[35:38],0),y[38],d.gas_volume_m3) if gas_mode else None
  spinfrac=np.clip(rotor*1e6/np.maximum(Emax,1),0,1);speed=np.sqrt(spinfrac)
  spin_request=np.where(active,np.minimum(masses_limit,np.maximum(Emax-rotor*1e6,0)/c.spin_s/c.eta_motor),0.)
  flows=np.zeros(4);work=np.zeros(4);pump_request=np.zeros(4);suction=p[:4].copy();rack_info=[dict(drop_Pa=0.,Re=0.,Kn=0.,pore_Mach=0.) for _ in range(5)]
  for i in range(4):
   if not active[i]:continue
   if hydraulic_loss:
    idle=c.idle_fraction*masses_limit[i]*speed[i]
    flows[i],suction[i],work[i],rack_info[i]=pump_flow(p[i],T[i],p[i+1],R[i],yy[i],geom[i],d.suction_m3_s[i]*speed[i],d.head_J_kg[i]*spinfrac[i],max(0.,masses_limit[i]-spin_request[i]-idle),c.eta_motor,c.eta_compressor,th,d.cutoff_Pa,c.rack_loss_multiplier)
    pump_request[i]=flows[i]*work[i]/c.eta_motor+idle
    continue
   work[i]=th.compression(T[i],p[i],p[i+1],yy[i],c.eta_compressor)
   cap=max(0.,1-(work[i]/max(d.head_J_kg[i]*spinfrac[i],1.))**2)
   flows[i]=d.suction_m3_s[i]*speed[i]*max(p[i]-.03,0)/(R[i]*T[i])*cap*np.clip((p[i]-d.cutoff_Pa)/d.cutoff_Pa,0,1)
   pump_request[i]=flows[i]*work[i]/c.eta_motor+c.idle_fraction*masses_limit[i]*speed[i]
   fac=min(1.,max(masses_limit[i]-spin_request[i],0)/max(pump_request[i],1e-30));flows[i]*=fac;pump_request[i]*=fac
  loss_request=np.zeros(5)
  if power_only and c.rack_loss_multiplier:
   for i in range(4):
    extra,_=rack_power_charge(flows[i],p[i],T[i],total[i]/V[i],geom[i],c.eta_motor*c.eta_compressor)
    extra*=c.rack_loss_multiplier
    fac=min(1.,max(masses_limit[i]-spin_request[i],0)/max(pump_request[i]+extra,1e-30))
    flows[i]*=fac;pump_request[i]*=fac
    loss_request[i]=c.rack_loss_multiplier*rack_power_charge(flows[i],p[i],T[i],total[i]/V[i],geom[i],c.eta_motor*c.eta_compressor)[0]
    pump_request[i]+=loss_request[i]
  # Receiver withdrawal crosses its outlet rack. The coast train then branches
  # into a mixed-gas booster/reserve and the existing liquefaction plant.
  coast_flow=0.;liquid_flow=0.;gas_fill=0.;coast_work=0.;plant_work=0.;fill_work=0.;fill_h=0.;coast_suction=p[4]
  def coast_at(flow):
   ps,info=suction_pressure(flow,p[4],T[4],R[4],geom[4],hydraulic_loss)
   if ps<=d.cutoff_Pa:return 0.,0.,T[4],ps,info
   capacity=float('inf');pin=max(ps,.001);temp=T[4];ratio=max(1.,1e5/pin)**(1/3);work_sum=0.
   for j in range(3):
    w=th.compression(temp,pin,pin*ratio,yy[4],c.eta_compressor);work_sum+=w
    block_head=d.coast_head_J_kg/3*spinfrac[4]
    capacity=min(capacity,d.coast_suction_m3_s*d.coast_suction_fractions[j]*speed[4]*pin/(R[4]*temp)*max(0.,1-(w/max(block_head,1.))**2),max(masses_limit[4]-spin_request[4],0)/3/max(w/c.eta_motor,1))
    temp=min(temp+w/max(th.at(temp,yy[4])[1],1),Tw+20);pin*=ratio
   capacity=min(capacity,d.coast_suction_m3_s*speed[4]*max(ps-.03,0)/(R[4]*T[4])*max(0.,1-(work_sum/max(d.coast_head_J_kg*spinfrac[4],1.))**2),max(masses_limit[4]-spin_request[4],0)/max(work_sum/c.eta_motor,1))
   capacity*=np.clip((ps-d.cutoff_Pa)/d.cutoff_Pa,0,1)
   return capacity,work_sum,temp,ps,info
  # Only identical trial flows in this RHS evaluation are cached. Nothing is
  # reused across state/time changes, so no physical/property approximation.
  @lru_cache(maxsize=64)
  def branches(flow):
   capacity,w,temp,ps,info=coast_at(flow)
   if not capacity:return 0.,0.,w,0.,0.,0.,ps,info
   pw,_=th.liquid_duty(temp,yy[4],Tw,c.carnot_fraction)
   preheat=max(0.,float(yy[4]@hs[4])+w-float(yy[4]@th.at(temp)[0]))
   capacity=min(capacity,d.precool_UA_W_K*20/max(preheat,1))
   fill=0.;fw=0.;fh=0.
   if gas_mode:
    fw=th.compression(temp,1e5,max(gs['p'],1e5),yy[4],c.eta_compressor)
    cap=max(0.,1-(fw/max(d.gas_fill_head_J_kg*spinfrac[5],1.))**2)
    fill=min(capacity,max(0.,d.gas_reserve_kg-gs['mass'])/20,d.gas_fill_suction_m3_s*speed[5]*1e5/(R[4]*temp)*cap,max(0.,masses_limit[5]-spin_request[5])/max(fw/c.eta_motor,1),d.gas_fill_UA_W_K*20/max(fw,1))
    fh=float(yy[4]@th.at(temp)[0])
   liquid=min(max(0.,capacity-fill),d.plant_flow_kg_s,d.plant_electric_MW*1e6/max(pw,1),d.condenser_UA_W_K*5/max(float(yy[4]@th.latent),1))
   return liquid,fill,w,pw,fw,fh,ps,info
  if active[4] and total[4]>1e-7:
   if hydraulic_loss:
    from scipy.optimize import brentq
    upper=sum(branches(0.)[:2])
    coast_flow=brentq(lambda f:sum(branches(f)[:2])-f,0.,upper,xtol=1e-12,rtol=1e-10) if upper>0 else 0.
   liquid_flow,gas_fill,coast_work,plant_work,fill_work,fill_h,coast_suction,rack_info[4]=branches(coast_flow)
   coast_flow=liquid_flow+gas_fill
  if power_only and c.rack_loss_multiplier:
   extra=c.rack_loss_multiplier*rack_power_charge(coast_flow,p[4],T[4],total[4]/V[4],geom[4],c.eta_motor*c.eta_compressor)[0]
   fac=min(1.,max(masses_limit[4]-spin_request[4],0)/max(coast_flow*coast_work/c.eta_motor+extra,1e-30))
   liquid_flow*=fac;gas_fill*=fac;coast_flow=liquid_flow+gas_fill
   loss_request[4]=c.rack_loss_multiplier*rack_power_charge(coast_flow,p[4],T[4],total[4]/V[4],geom[4],c.eta_motor*c.eta_compressor)[0]
  fill_loss=loss_request[4]*gas_fill/max(coast_flow,1e-30)
  liquid_loss=loss_request[4]-fill_loss
  gas_request=gas_fill*(coast_work+fill_work)/c.eta_motor+fill_loss
  coast_request=liquid_flow*(coast_work/c.eta_motor+plant_work+c.separation_J_kg)+liquid_loss
  holdP=c.tank_heat_W*max((Tw+20)/70-1,0)/c.carnot_fraction
  thrust_request=hw['thrust_W'] if abs(t)<d.burn_s/2 else 0.
  battery_available=d.battery_MW*1e6*np.clip((y[25]-capacity*(1-c.battery_usable))/(.01*capacity),0,1)
  available=min(d.bus_MW*1e6,solar+battery_available)
  def allocate(request):
   nonlocal available
   actual=min(max(available,0),request);available-=actual;return actual
  thrust_limit=thrust_request
  if gas_mode:thrust_limit=min(thrust_limit,d.gas_feed_max_kg_s*(d.isp_s*9.80665)**2/(2*c.eta_thruster)*np.clip((gs['p']-d.gas_feed_min_Pa)/(.1*d.gas_feed_min_Pa),0,1))
  thrust=allocate(thrust_limit);base=allocate(c.auxiliary_W+holdP)
  spins=np.array([allocate(z) for z in spin_request]);pumpP=np.array([allocate(z) for z in pump_request]);gasP=allocate(gas_request);coastP=allocate(coast_request)
  pump_fraction=np.divide(pumpP,pump_request,out=np.ones(4),where=pump_request>0)
  loss_paid=loss_request.copy();loss_paid[:4]*=pump_fraction
  loss_paid[4]=liquid_loss*coastP/max(coast_request,1e-30)+fill_loss*gasP/max(gas_request,1e-30)
  flows*=pump_fraction
  for i in range(5):dy[LI[f'rack_loss_{i}_MJ']]=loss_paid[i]/1e6
  liquid_flow*=coastP/max(coast_request,1e-30);gas_fill*=gasP/max(gas_request,1e-30);coast_flow=liquid_flow+gas_fill
  if power_only:
   for i,f in enumerate([*flows,coast_flow]):
    if f<=0:continue
    if d.rack_flow_layout=='parallel_plates':
     from .plates import diagnostics as plate_diagnostics
     rack_info[i]=plate_diagnostics(f,p[i],T[i],total[i]/V[i],geom[i],R[i]);rack_info[i]['drop_Pa']*=c.rack_loss_multiplier
    else:
     g=geom[i];beta=1-2*g['wire_radius_m']/g['pitch_m'];mu=viscosity(T[i]);rho=total[i]/V[i]
     _,chi=rack_power_charge(f,p[i],T[i],rho,g,c.eta_motor*c.eta_compressor)
     rack_info[i]=dict(drop_Pa=c.rack_loss_multiplier*chi*p[i]/2,Re=f/g['frontal_m2']*2*g['wire_radius_m']/(beta*mu),Kn=mu/p[i]*math.sqrt(math.pi*R[i]*T[i]/2)/(2*g['wire_radius_m']),pore_Mach=f/(rho*g['frontal_m2']*beta*math.sqrt(1.4*R[i]*T[i])))
  demand=thrust_request+c.auxiliary_W+holdP+sum(spin_request)+sum(pump_request)+coast_request+gas_request
  load=thrust+base+sum(spins)+sum(pumpP)+coastP+gasP
  dy[LI['unmet_MJ']]=max(0,demand-load)/1e6
  from_sun=min(solar,load);discharge=load-from_sun
  charge=min(max(solar-load,0),d.battery_MW*1e6,max(0,(capacity*d.battery_initial_soc-y[25])*1e6/20/c.charge_eta),max(0,d.bus_MW*1e6-load))
  dy[25]=(charge*c.charge_eta-discharge/c.discharge_eta)/1e6
  warm=charge*(1-c.charge_eta)+discharge*(1/c.discharge_eta-1)+base+c.tank_heat_W
  dy[LI['solar_MJ']]=(from_sun+charge)/1e6;dy[LI['boundary_MJ']]+=c.tank_heat_W/1e6
  rotor_loss=np.where(active,0.,np.minimum(masses_limit*c.eta_motor,np.maximum(rotor,0)*1e6/c.brake_s))
  dy[30:35]=(spins*c.eta_motor-rotor_loss)[:5]/1e6;dy[39]=(spins*c.eta_motor-rotor_loss)[5]/1e6;warm+=sum(spins)*(1-c.eta_motor)+sum(rotor_loss)
  for i in range(4):
   f=flows[i];species=f*yy[i];dy[3*i:3*i+3]-=species;dy[3*(i+1):3*(i+1)+3]+=species
   h=float(yy[i]@hs[i]);dy[15+i]-=f*h/1e6;dy[16+i]+=f*(h+work[i])/1e6;warm+=pumpP[i]-f*work[i]
  if coast_flow:
   dy[12:15]-=coast_flow*yy[4];dy[19]-=coast_flow*float(yy[4]@hs[4])/1e6
   dy[27:30]+=liquid_flow*yy[4];dy[LI['made_N2']:LI['made_Ar']+1]+=liquid_flow*yy[4]
   warm+=coastP+liquid_flow*float(yy[4]@(hs[4]-th.liquid_h))
   if gas_mode:
    dy[35:38]+=gas_fill*yy[4];dy[38]+=gas_fill*fill_h/1e6
    warm+=gasP+gas_fill*(float(yy[4]@hs[4])-fill_h)
  dy[LI['plant_MJ']]=coastP/1e6;dy[LI['shaft_MJ']]=float(flows@work+coast_flow*coast_work+gas_fill*fill_work)/1e6
  prop=2*c.eta_thruster*thrust/(d.isp_s*9.80665)**2
  prop_y=gs['fractions'] if gas_mode else PROP_Y;prop_h=gs['h'] if gas_mode else float(PROP_Y@th.liquid_h)
  if gas_mode:
   dy[35:38]-=prop*prop_y;dy[38]-=prop*prop_h/1e6
   buffer_heat=d.gas_thermal_UA_W_K*(Tw-gs['T']);dy[38]+=buffer_heat/1e6;warm-=buffer_heat
  else:dy[27:30]-=prop*prop_y
  dy[LI['prop_N2']:LI['prop_Ar']+1]=prop*prop_y;dy[LI['thrust_Ns']]=2*c.eta_thruster*thrust/(d.isp_s*9.80665)
  retained=(1-c.eta_thruster)*c.retained_thruster_loss;warm+=thrust*retained
  dy[LI['exhaust_MJ']]=(thrust*(1-retained)+prop*prop_h)/1e6
  heats=np.zeros(5);exposures=np.zeros(5);biots=np.zeros(5);rad=0.
  for i,g in enumerate(geom):
   vent=total[i]/10 if vent_start[i]<=t<release[i] and not purged[i] else 0.
   if vent:
    dy[3*i:3*i+3]-=vent*yy[i];qh=vent*float(yy[i]@hs[i]);dy[15+i]-=qh/1e6
    dy[LI['lost_N2']:LI['lost_Ar']+1]+=vent*yy[i];dy[LI['boundary_MJ']]-=qh/1e6
   if not purged[i]:
    flow=(flows[i] if i<4 else coast_flow) if d.rack_flow_layout in ('outlet_planes','inline_bank','parallel_plates') else max(flows[i-1] if i else admitted+leak,flows[i] if i<4 else coast_flow,vent)
    UA,info=conductance(p[i],(T[i]+Tm[i])/2,flow,g['frontal_m2'],g,Racks(metal_conductivity_W_m_K=mats[i].conductivity),R=R[i],cp=cp[i]);biots[i]=info['Bi'];heats[i]=UA*(T[i]-Tm[i])
    dy[15+i]-=heats[i]/1e6;dy[20+i]+=heats[i]/1e6
   elif safe_hatch[i]:
    motion=hw['rack_motion_s'][i];exposures[i]=min(np.clip((t-release[i])/motion,0,1),np.clip((end-10-t)/motion,0,1))
    q=exposures[i]*g['wetted_m2']*c.rack_view*max(0,mats[i].emissivity*5.670374419e-8*Tm[i]**4-c.environment_W_m2)*np.clip((Tm[i]-d.rack_initial_K[i])/.5,0,1)
    dy[20+i]-=q/1e6;rad+=q
  qr=rad_exposure*2*d.warm_radiator_m2*max(0,c.radiator_emissivity*c.radiator_view*5.670374419e-8*Tw**4-c.environment_W_m2)*np.clip((Tw-d.warm_initial_K)/.5,0,1)
  dy[26]=(warm-qr)/1e6;dy[LI['radiated_MJ']]=(rad+qr)/1e6
  return dy,dict(rack_loss_MW=(loss_paid/1e6).tolist(),compression_base_MW=float(flows@work+coast_flow*coast_work+gas_fill*fill_work)/c.eta_motor/1e6,stage_compression_base_MW=(np.r_[flows*work/c.eta_motor,(coast_flow*coast_work+gas_fill*fill_work)/c.eta_motor]/1e6).tolist(),buffer_Pa=gs['p'] if gas_mode else 0.,buffer_K=gs['T'] if gas_mode else 0.,buffer_kg=gs['mass'] if gas_mode else 0.,gas_fill_kg_s=gas_fill,gas_fill_MW=gasP/1e6,liquefaction_kg_s=liquid_flow,compressor_suction_Pa=suction.tolist(),coast_suction_Pa=coast_suction,rack_drop_Pa=[a['drop_Pa'] for a in rack_info],rack_Re=[a['Re'] for a in rack_info],rack_Kn=[a['Kn'] for a in rack_info],rack_pore_Mach=[a['pore_Mach'] for a in rack_info],pressure_Pa=p.tolist(),gas_K=T.tolist(),rack_K=Tm.tolist(),warm_K=float(Tw),SOC=float(y[25]/capacity),solar_MW=solar/1e6,load_MW=load/1e6,thrust_MW=thrust/1e6,coast_kg_s=coast_flow,pump_kg_s=flows.tolist(),heat_MW=(heats/1e6).tolist(),rack_exposure=exposures.tolist(),Bi=biots.tolist(),unmet_MW=max(0,demand-load)/1e6)
 # Event boundaries guarantee each hardware/control transition is visited once.
 breaks=sorted(set([start,end,-500.,d.pump_stop_s,*release,d.plant_start_s,d.plant_stop_s,-d.burn_s/2,d.burn_s/2]))
 # Optional numerical restarts carry the entire state/ledger forward unchanged.
 # They refresh BDF history/Jacobian; they are not repeated cycles or resets.
 if d.integration_segment_s:
  breaks=sorted(set(breaks+np.arange(start,end,d.integration_segment_s).tolist()))
 breaks=[t for t in breaks if start<=t<=end];times=np.unique(np.r_[np.linspace(start,end,samples),breaks]);ys=[];ts=[];diag=[];current=y0.copy();events=[]
 def total_energy(y):return float(sum(y[15:27])+sum(y[30:35])+y[38]+y[39]+y[27:30]@th.liquid_h/1e6)
 for left,right in zip(breaks[:-1],breaks[1:]):
  if os.environ.get("ATMO_PROGRESS"):print(f"Integrating {left:.1f} to {right:.1f}",file=sys.stderr,flush=True)
  counter=[0]
  def rhs(t,y):
   counter[0]+=1
   if os.environ.get("ATMO_PROGRESS") and counter[0]%10000==0:print(f"  rhs {counter[0]} t={t:.6f}",file=sys.stderr,flush=True)
   # Use the interior one-sided control value at BOTH event boundaries.
   # A burn is off at exact |t|=burn/2 but on immediately to its right at
   # burn start; feeding the left value to BDF's initial derivative can force
   # sub-ULP steps when tolerances are tightened.
   return rates(max(np.nextafter(left,right),min(t,np.nextafter(right,left))),y)[0]
  def jac(t,y):
   base=rhs(t,y);j=np.zeros((len(y),len(y)))
   for k in range(40):
    delta=max(d.jacobian_absolute_step,d.jacobian_relative_step*max(abs(y[k]),1e-5));z=y.copy();z[k]+=delta;j[:,k]=(rhs(t,z)-base)/delta
   return j
  def hard_path(t,y):
   _,mm,_,tg,tm,pp=decode(y)
   tw=y[26]*1e6/(d.warm_store_kg*c.buffer_cp_J_kg_K)
   return min(min((m.limit_K+100-tm[i])/100 for i,m in enumerate(mats)),
              min((1.5*d.rated_pressure_Pa[i-1]-pp[i])/1000 for i in range(1,5)),
              (d.warm_max_K+100-tw)/100,
              (y[25]/capacity-(1-c.battery_usable)+.05)/.1)
  hard_path.terminal=True;hard_path.direction=-1
  sol=solve_ivp(rhs,(left,right),current,events=hard_path if d.early_reject else None,method='BDF' if d.integrator=='BDF_auto' else d.integrator,jac=jac if d.integrator=='BDF' else None,rtol=d.rtol,atol=d.atol,max_step=d.max_step_s,dense_output=True)
  if sol.status==1:raise ConstraintViolation(f'Hard path rejection at {sol.t[-1]:.3f} s: material/warm temperature, pressure or battery exceeded broad rejection threshold')
  if not sol.success:raise RuntimeError(f'{sol.message}; t={sol.t[-1]}, state={sol.y[:40,-1].tolist()}')
  selected=np.unique(np.r_[times[(times>=left)&(times<right)],sol.t[:-1]]);states=sol.sol(selected).T
  for t,y in zip(selected,states):ts.append(float(t));ys.append(y);diag.append(rates(float(t),y,True)[1])
  current=sol.y[:,-1]
  for i in range(5):
   if right==release[i]:
    m,tot,frac,T,Tm,P=decode(current);safe_hatch[i]=P[i]<100.
    if safe_hatch[i]:
     lost=current[3*i:3*i+3].copy();U=current[15+i];current[LI['lost_N2']:LI['lost_Ar']+1]+=lost;current[LI['boundary_MJ']]-=U
     current[3*i:3*i+3]=0.;current[15+i]=0.;purged[i]=True
    events.append(dict(time_s=right,chamber=i,pressure_before_Pa=float(P[i]),final_purge_kg=float(tot[i]),hatch_allowed=bool(safe_hatch[i])))
 ts.append(end);ys.append(current.copy());diag.append(rates(end,current,True)[1]);states=np.array(ys);tt=np.array(ts)
 species=states[:,:15].reshape(-1,5,3).sum(axis=1)+states[:,27:30]+states[:,35:38]
 initial_species=y0[:15].reshape(5,3).sum(axis=0)+y0[27:30]+y0[35:38]
 mr=species-initial_species-states[:,LI['in_N2']:LI['in_Ar']+1]+states[:,LI['lost_N2']:LI['lost_Ar']+1]+states[:,LI['prop_N2']:LI['prop_Ar']+1]
 energy=np.array([total_energy(y) for y in states]);er=energy-total_energy(y0)-states[:,LI['boundary_MJ']]-states[:,LI['solar_MJ']]+states[:,LI['radiated_MJ']]+states[:,LI['exhaust_MJ']]
 liquid_surplus=current[27:30]-y0[27:30];net=float(sum(liquid_surplus));history={k:[z[k] for z in diag] for k in diag[0]}
 initial_h=np.array([m.energy(T) for m,T in zip(mats,d.rack_initial_K)]);final_h=current[20:25]*1e6/M
 residuals=dict(rack_enthalpy_J_kg=(final_h-initial_h).tolist(),battery_MJ=float(current[25]-y0[25]),warm_MJ=float(current[26]-y0[26]),gas_kg=float((current[:15]-y0[:15]).sum()),gas_MJ=float(sum(current[15:20]-y0[15:20])),rotor_MJ=float(sum(current[30:35])),thrust_relative=float(current[LI['thrust_Ns']]/hw['required_impulse_Ns']-1),reserve_deficit_kg=np.minimum(liquid_surplus,0).tolist())
 residuals['gas_reserve_species_kg']=(current[35:38]-y0[35:38]).tolist();residuals['gas_reserve_MJ']=float(current[38]-y0[38]);residuals['rotor_MJ']+=float(current[39])
 P=np.array(history['pressure_Pa']);Tm=np.array(history['rack_K']);Tgas=np.array(history['gas_K']);mass=states[:,:15].reshape(-1,5,3).sum(axis=2)
 closure=max(max(abs(np.array(residuals['rack_enthalpy_J_kg'])))/500.,abs(residuals['battery_MJ'])/100.,abs(residuals['warm_MJ'])/100.,abs(residuals['gas_kg'])/.1,abs(residuals['gas_MJ'])/.01,abs(residuals['rotor_MJ'])/.01,abs(residuals['thrust_relative'])/1e-4)
 if gas_mode:closure=max(closure,max(abs(current[35:38]-y0[35:38]))/.1,abs(current[38]-y0[38])/1.)
 margins=dict(reserve_kg=float(min(liquid_surplus)),material_K=min(m.limit_K-float(Tm[:,i].max()) for i,m in enumerate(mats)),pressure_Pa=min(d.rated_pressure_Pa[i-1]-float(P[:,i].max()) for i in range(1,5)),warm_K=d.warm_max_K-max(history['warm_K']),SOC=min(history['SOC'])-(1-c.battery_usable),liquid_kg=float(states[:,27:30].min()),tank_m3=d.liquid_tank_m3-float((states[:,27:30]/th.liquid_density).sum(axis=1).max()),Bi=.1-float(np.max(history['Bi'])),gas_K=c.upper_gas_K-float(np.max(np.where(mass>.01,Tgas,0))),unmet_MJ=1.-float(current[LI['unmet_MJ']]),product_kg=net,periodic=1.-closure)
 if gas_mode:margins.update(gas_buffer_Pa=d.gas_rated_Pa-max(history['buffer_Pa']),gas_buffer_K=500.-max(history['buffer_K']),gas_buffer_inventory_kg=float(states[:,35:38].min()))
 if hydraulic_loss:margins['rack_Mach']=.3-float(np.max(history['rack_pore_Mach']))
 if d.rack_flow_layout=='inline_bank' or d.rack_pressure_model=='inline_laminar':
  margins['rack_Re']=75.-float(np.max(history['rack_Re']))
  margins['rack_rows']=min(g['row_count'] for g in geom)-5.
 if d.rack_flow_layout=='parallel_plates':
  margins['plate_Re']=1000.-float(np.max(history['rack_Re']))
 audits=dict(species_kg=float(abs(mr).max()),energy_MJ=float(abs(er).max()),min_gas_kg=float(states[:,:15].min()),forward_integrations=1,rhs_evaluations=evaluations[0])
 feasible=all(z>=-1e-6 for z in margins.values()) and all(safe_hatch) and audits['species_kg']<1e-4 and audits['energy_MJ']<.01 and audits['min_gas_kg']>-.0001
 output_hw={k:v for k,v in hw.items() if k not in ('orbit','forcing','rack_motion_s')};output_hw['rack_motion_s']=hw['rack_motion_s'].tolist()
 result=dict(model='transient-v2',inputs=dict(design=asdict(d),capabilities=asdict(c)),hardware=output_hw,time_s=tt.tolist(),history=history,gas_species_kg=states[:,:15].reshape(-1,5,3).tolist(),liquid_species_kg=states[:,27:30].tolist(),gas_reserve_species_kg=states[:,35:38].tolist(),ledger={name:states[:,index].tolist() for name,index in LI.items()},events=events,audits=audits,closure=residuals,margins=margins,feasible=bool(feasible),dry_kg=hw['dry_kg'],net_liquid_kg=net,diagnostic_payoff_days=hw['dry_kg']/net*o.period/86400 if net>0 else None,operating_payoff_days=hw['dry_kg']/net*o.period/86400 if net>0 and feasible else None,delivered_payoff_days=None)

 # No extra trajectory: validate the realized property regime and report the
 # operating-orbit offload map explicitly after the pre-offload audit.
 from .validate import check
 result['thermodynamic_audit']=check(result)
 valid=result['thermodynamic_audit']['low_density_chamber_EOS_screen_passed'] and result['thermodynamic_audit']['max_compressor_work_relative_error']<1e-5
 result['feasible']=bool(result['feasible'] and valid)
 if not result['feasible']:result['operating_payoff_days']=None
 from .power_search_metrics import loss_metrics
 result['loss_power_audit']=loss_metrics(result)
 result['offload_species_kg']=np.maximum(liquid_surplus,0).tolist()
 result['offload_enthalpy_MJ']=float(np.maximum(liquid_surplus,0)@th.liquid_h/1e6)
 result['post_offload_liquid_species_kg']=(current[27:30]-np.maximum(liquid_surplus,0)).tolist()
 return result
