"""Audit existing reserve-refill power from saved states, without rerunning cycle."""
import os,json
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.transient.io import read_result
from atmo_scoops.transient.thermo import properties
ROOT=Path(__file__).resolve().parents[2]
r=read_result(ROOT/'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz');h=r['history'];d=r['inputs']['design'];c=r['inputs']['capabilities'];th=properties()
t=np.array(r['time_s']);minute=t/60;start=d['plant_start_s'];fill=np.array(h['gas_fill_kg_s']);flow=np.array(h['coast_kg_s']);p=np.array(h['pressure_Pa'])[:,4];T=np.array(h['gas_K'])[:,4];Tw=np.array(h['warm_K']);bp=np.array(h['buffer_Pa'])
reserve=np.array(r['gas_reserve_species_kg']).sum(1);refill=np.where(t>=start,reserve-np.interp(start,t,reserve),0);needed=refill[-1]
booster=np.zeros(len(t));shared=np.zeros(len(t));refrigerator=np.zeros(len(t));product=np.zeros(len(t));liquid=np.array(h['liquefaction_kg_s'])
for i in np.flatnonzero(flow>1e-9):
 species=np.array(r['gas_species_kg'][i][4]);y=species/species.sum();pin=max(p[i],.001);temp=T[i];ratio=max(1.,1e5/pin)**(1/3);wtotal=0.
 for j in range(3):
  w=th.compression(temp,pin,pin*ratio,y,c['eta_compressor']);wtotal+=w
  temp=min(temp+w/max(th.at(temp,y)[1],1),Tw[i]+20);pin*=ratio
 fw=th.compression(temp,1e5,max(bp[i],1e5),y,c['eta_compressor'])
 booster[i]=fill[i]*fw/c['eta_motor']/1e6
 shared[i]=fill[i]*wtotal/c['eta_motor']/1e6
 pw,_=th.liquid_duty(temp,y,Tw[i],c['carnot_fraction']);refrigerator[i]=liquid[i]*pw/1e6
 product[i]=liquid[i]*(wtotal/c['eta_motor']+pw+c['separation_J_kg'])/1e6+np.array(h['rack_loss_MW'])[i,4]*liquid[i]/flow[i]
gasP=np.array(h['gas_fill_MW']);loss=np.array(h['rack_loss_MW']);expected=booster+shared+loss[:,4]*np.divide(fill,flow,out=np.zeros_like(fill),where=flow>0)
assert np.max(abs(expected-gasP))<1e-5
assert abs(np.trapezoid(product,t)/r['ledger']['plant_MJ'][-1]-1)<.001
milestones=[]
for fraction in [.5,.9,.99,.999,.9999]:
 tm=float(np.interp(fraction*needed,refill,t));milestones.append(dict(fraction=fraction,minutes=tm/60,minutes_since_plant_start=(tm-start)/60,source_Pa=float(np.interp(tm,t,p)),reserve_bar=float(np.interp(tm,t,bp))/1e5))
dive=np.array(h['stage_compression_base_MW'])[:,:4].sum(1)+loss[:,:4].sum(1)
powers={}
for name,values in [('booster_only',booster),('shared_compression_for_reserve',shared),('reserve_branch',gasP),('refrigerator_only',refrigerator),('liquid_product_branch',product),('dive_compression_and_rack_loss',dive),('thrusters',np.array(h['thrust_MW']))]:
 powers[name]=dict(peak_MW=float(max(values)),energy_MWh=float(np.trapezoid(values,t)/3600))
quarter=t[-1]-t[0];quarter/=4
q=dict(minutes=quarter/60,fraction_refilled=float(np.interp(quarter,t,refill)/needed),source_Pa=float(np.interp(quarter,t,p)))
result=dict(source='selected_validation/check_refined.json.gz',refill_kg=needed,plant_start_minutes=start/60,milestones=milestones,quarter_orbit_after_perigee=q,powers=powers,installed_MW=dict(booster=d['gas_fill_motor_MW'],dive_blocks=d['motor_MW'],coast_compressors=d['coast_motor_MW'],refrigerator=d['plant_electric_MW']),max_power_reconstruction_error_MW=float(max(abs(expected-gasP))))
base=Path(__file__).with_name('reserve_refill');base.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
fig,axs=plt.subplots(3,1,figsize=(11,10),layout='constrained',sharex=True)
axs[0].plot(minute,refill/needed*100,color='#39834c',label='Reserve replenished');axs[0].set(ylabel='Refill complete (%)',ylim=(-2,108));ax=axs[0].twinx();ax.plot(minute,p/1000,color='#176b8b',label='Receiver pressure');ax.set(ylabel='Receiver pressure (kPa)',ylim=(0,5.3));axs[0].legend(loc='upper left');ax.legend(loc='upper right')
for m in milestones[2:3]:axs[0].annotate(f"99% at {m['minutes']:.1f} min\nReceiver still {m['source_Pa']/1000:.2f} kPa",xy=(m['minutes'],99),xytext=(44,65),arrowprops=dict(arrowstyle='->',color='#555'))
axs[1].plot(minute,gasP,label='Reserve branch: shared compression + booster + rack loss',color='#176b8b');axs[1].plot(minute,booster,label='Booster alone',color='#39834c');axs[1].plot(minute,refrigerator,label='Refrigerator alone',color='#a36b1a');axs[1].plot(minute,product,label='Full liquid-product branch',color='#8d5798',ls='--');axs[1].set(ylabel='Electrical load (MW)',ylim=(0,None));axs[1].legend(fontsize=9)
axs[2].plot(minute,fill,color='#39834c',label='Gas to reserve');axs[2].plot(minute,liquid,color='#a36b1a',label='Gas to liquid products');axs[2].set(ylabel='Flow (kg/s)',xlabel='Minutes after perigee',ylim=(0,None));axs[2].legend()
for a in axs:a.axvline(start/60,color='gray',ls=':',lw=1);a.set_xlim(0,72);a.grid(alpha=.2)
fig.suptitle('Existing boosted reserve — timing and power audit\nSaved 275.7-day simulation; architecture acceptance pending',fontsize=14)
fig.savefig(base.with_suffix('.png'),dpi=140);fig.savefig(base.with_suffix('.svg'));plt.close(fig)
pth=base.with_suffix('.svg');pth.write_text('\n'.join(x.rstrip() for x in pth.read_text().splitlines())+'\n')
