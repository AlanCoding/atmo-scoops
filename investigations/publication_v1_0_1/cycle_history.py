"""Publication tank histories from the accepted valve-only v1.0.1 cycle."""
from pathlib import Path
import gzip,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
r=json.load(gzip.open(ROOT/'results/transient/valve_restore/selected_refined.json.gz','rt'))
t=np.array(r['time_s'])/60;h=r['history'];d=r['inputs']['design']
opened=next(e['time_s'] for e in r['reserve_events'] if e['event']=='reserve_pressure_catch')/60
closed=max(d['pump_stop_s'],d['burn_s']/2)/60
fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True,layout='constrained')
for i,col in enumerate(['#d59b24','#6e71b2','#4c9f78','#7486ad']):
 axes[0].plot(t,np.array(h['pressure_Pa'])[:,i]/1000,label=f'Chamber {i+1} (before compressor {i+1})',color=col,lw=1.4)
axes[0].plot(t,np.array(h['pressure_Pa'])[:,-1]/1000,label='Main receiver',color='#247c8c')
axes[0].plot(t,np.array(h['buffer_Pa'])/1000,label='Thruster reserve',color='#b34a32')
axes[0].set(ylabel='Tank pressure (kPa)',title='v1.0.1 cycle — valve-only reserve; no reserve-filling compressor')
axes[1].plot(t,np.array(r['gas_species_kg']).sum(axis=2)[:,-1]/1000,label='Gas in main receiver',color='#247c8c')
axes[1].plot(t,np.array(r['gas_reserve_species_kg']).sum(axis=1)/1000,label='Gas in thruster reserve',color='#b34a32')
axes[1].plot(t,np.array(r['liquid_species_kg']).sum(axis=1)/1000,label='Liquid product',color='#6e71b2')
axes[1].set(ylabel='Inventory (tonnes)',xlabel='Minutes from perigee')
for ax in axes:
 ax.axvspan(opened,closed,color='#c6d8b8',alpha=.3)
 ax.axvline(opened,color='#657b4e',ls=':',lw=1)
 ax.axvline(closed,color='#657b4e',ls='--',lw=1)
 ax.set_xlim(-12,86);ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=9)
axes[0].text(.43,.40,'Shaded: valve enabled (−0.73 to +10.29 min)\nThen reserve isolated; receiver drains to liquefaction',transform=axes[0].transAxes,va='top',fontsize=10,bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
plt.rcParams['svg.fonttype']='none'
for stem in ['v1_cycle_history','v1_0_1_cycle_history']:
 for ext in ['svg','png']:
  out=ROOT/f'docs/images/{stem}.{ext}';fig.savefig(out,dpi=160)
  if ext=='svg':out.write_text('\n'.join(x.rstrip() for x in out.read_text().splitlines())+'\n')
