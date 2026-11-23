"""Receiver draw-down audit from the committed trajectory; no simulation."""
import json, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.transient.io import read_result
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz'
r=read_result(source);h=r['history'];d=r['inputs']['design'];t=np.array(r['time_s']);minutes=t/60
p=np.array(h['pressure_Pa'])[:,4];mass=np.array(r['gas_species_kg'])[:,4].sum(1)
liquid=np.array(r['liquid_species_kg']).sum(1);reserve=np.array(r['gas_reserve_species_kg']).sum(1)
start=d['plant_start_s'];stop=d['plant_stop_s'];release=stop+d['vent_duration_s']
refill=np.where(t>=start,reserve-np.interp(start,t,reserve),0)
fig,axs=plt.subplots(2,2,figsize=(13,8.7),layout='constrained')
ax=axs[0,0];ax.plot(minutes,p/1000,color='#156c8a',lw=2)
ax.set(ylabel='Receiver pressure (kPa)',title='Pressure: full operating range',ylim=(-.1,5.3))
i=int(np.argmax(p));ax.annotate(f'Peak {p[i]/1000:.3f} kPa',xy=(minutes[i],p[i]/1000),xytext=(20,4.9),arrowprops=dict(arrowstyle='->',color='#666'))
ax=axs[0,1];ax.plot(minutes,p,color='#156c8a',lw=2);ax.set_yscale('symlog',linthresh=.001)
ax.set(ylabel='Receiver pressure (Pa; logarithmic above 0.001)',title='Pressure: late-coast draw-down',ylim=(0,1e4))
ax.annotate('2.78 Pa / 4.55 kg\nat plant shutdown',xy=(70,np.interp(stop,t,p)),xytext=(26,8),arrowprops=dict(arrowstyle='->',color='#666'),fontsize=10)
ax.annotate('Vented, then residual purged\nZero modeled inventory at 72 min',xy=(72,0),xytext=(18,.008),arrowprops=dict(arrowstyle='->',color='#666'),fontsize=10)
ax=axs[1,0];ax.plot(minutes,mass/1000,label='Gas remaining in receiver',lw=2,color='#156c8a');ax.plot(minutes,liquid/1000,label='Liquid product accumulated',lw=2,color='#986018');ax.plot(minutes,refill/1000,label='Gas returned to thruster reserve',lw=2,color='#47834a')
ax.set(ylabel='Mass (tonnes)',title='Where the collected gas goes',ylim=(-.15,7.8));ax.legend(fontsize=9)
ax=axs[1,1]
for k,label,color in [('coast_kg_s','Total receiver withdrawal','#156c8a'),('liquefaction_kg_s','Liquid product','#986018'),('gas_fill_kg_s','Gaseous thruster-reserve refill','#47834a')]:ax.plot(minutes,h[k],label=label,color=color,lw=1.7)
ax.axhline(d['plant_flow_kg_s'],ls=':',color='#986018',label='Installed liquid-flow ceiling')
ax.set(ylabel='Flow (kg/s)',title='Processing slows as suction pressure falls',ylim=(-.1,6.6));ax.legend(fontsize=8.5)
for ax in axs.flat:
 ax.set_xlim(-5,86.03);ax.set_xlabel('Minutes after perigee');ax.grid(alpha=.2)
 ax.axvline(start/60,color='#999',ls='--',lw=1);ax.axvspan(stop/60,release/60,color='#d98080',alpha=.18)
fig.suptitle('Aft receiver — current optimized cycle (275.7-day payoff)\nDashed line: coast plant starts at 10.83 min. Red band: scheduled venting, 70–72 min.',fontsize=14)
out=Path(__file__).with_name('receiver_coast.png');fig.savefig(out,dpi=150);fig.savefig(out.with_suffix('.svg'));plt.close(fig)
svg=out.with_suffix('.svg');svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')
rows=[]
for minute in [10.8333333333333,20,30,40,50,60,70,72,86.0282299478]:
 rows.append(dict(minutes=minute,pressure_Pa=float(np.interp(minute*60,t,p)),receiver_kg=float(np.interp(minute*60,t,mass)),liquid_kg=float(np.interp(minute*60,t,liquid)),gas_refilled_kg=float(np.interp(minute*60,t,refill)),liquid_kg_s=float(np.interp(minute*60,t,h['liquefaction_kg_s']))))
budget=dict(receiver_at_processing_start_kg=float(np.interp(start,t,mass)),liquid_kg=float(liquid[-1]),gas_refilled_kg=float(refill[-1]),receiver_at_shutdown_kg=float(np.interp(stop,t,mass)))
budget['balance_error_kg']=budget['receiver_at_processing_start_kg']-budget['liquid_kg']-budget['gas_refilled_kg']-budget['receiver_at_shutdown_kg']
assert abs(budget['balance_error_kg'])<.01
result=dict(source=str(source.relative_to(ROOT)),rows=rows,budget=budget,peak_liquid_kg_s=max(h['liquefaction_kg_s']),product_branch_kWh_per_kg=r['ledger']['plant_MJ'][-1]/3.6/r['net_liquid_kg'],receiver_release_event=r['events'][-1])
out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
