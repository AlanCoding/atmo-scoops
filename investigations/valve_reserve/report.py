import sys,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.transient.io import read_result
r=read_result(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
t=np.asarray(r['time_s'])/60;h=r['history'];p=np.array(h['pressure_Pa']);gm=np.array(r['gas_species_kg']).sum(axis=2);rm=np.array(r['gas_reserve_species_kg']).sum(axis=1)
fig,axs=plt.subplots(3,1,figsize=(11,10),sharex=True)
axs[0].plot(t,p[:,-1]/1000,label='Main receiver');axs[0].plot(t,np.array(h['buffer_Pa'])/1000,label='Isolated reserve');axs[0].set_ylabel('Pressure (kPa)')
axs[1].plot(t,gm[:,-1]/1000,label='Main receiver');axs[1].plot(t,rm/1000,label='Reserve');axs[1].plot(t,np.array(r['liquid_species_kg']).sum(axis=1)/1000,label='Liquid product');axs[1].set_ylabel('Inventory (tonnes)')
axs[2].plot(t,h['valve_transfer_kg_s'],label='Valve transfer (+ to reserve)');axs[2].plot(t,h['liquefaction_kg_s'],label='Liquefaction');axs[2].set_ylabel('Flow (kg/s)');axs[2].set_xlabel('Minutes from perigee')
for ax in axs:
 ax.grid(alpha=.2);ax.axvline(max(r['inputs']['design']['pump_stop_s'],r['inputs']['design']['burn_s']/2)/60,color='gray',ls='--',label='Reserve isolated');ax.legend()
fig.suptitle('Valve reserve: collection, shared feed, isolation and product drawdown');fig.tight_layout()
for ext in ['svg','png']:fig.savefig(out/f'cycle.{ext}',dpi=170)
# Concise machine-readable physical dimensions and state extrema for publication.
hw=r['hardware'];tables=[]
for i,g in enumerate(hw['geometry']):
 tables.append(dict(stage=i+1,material=r['inputs']['design']['materials'][i],metal_t=g['mass_kg']/1000,frontal_area_m2=g['frontal_m2'],core_depth_m=g['rack_depth_m'],thickness_mm=g['thickness_m']*1000,clearance_mm=g['gap_m']*1000,initial_K=h['rack_K'][0][i],final_K=h['rack_K'][-1][i],max_K=max(x[i] for x in h['rack_K'])))
(out/'rack_dimensions.json').write_text(json.dumps(tables,indent=2)+'\n')
(out/'mass_breakdown.json').write_text(json.dumps(hw['masses_kg'],indent=2)+'\n')
print(json.dumps(dict(payoff=r['operating_payoff_days'],diagnostic=r['diagnostic_payoff_days'],dry_t=r['dry_kg']/1000,product_t=r['net_liquid_kg']/1000,perigee=r['inputs']['design']['perigee_km'],closure=r['closure'],events=r.get('reserve_events')),indent=2))
