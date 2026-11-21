"""Saved-result review plots, no numerical integration."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.transient.io import read_result
p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=read_result(a.result);t=np.array(r['time_s'])/60;h=r['history'];colors=['#9c5500','#0e7490','#3f6e31','#79549b','#b23951']
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for i,color in enumerate(colors):
 axes[0,0].plot(t,np.array(h['pressure_Pa'])[:,i],color=color,label=f'Volume {i+1}')
 axes[0,1].plot(t,np.where(np.array(r['gas_species_kg'])[:,i].sum(axis=1)>.01,np.array(h['gas_K'])[:,i],np.nan),color=color)
 axes[1,0].plot(t,np.array(h['rack_K'])[:,i],color=color)
 axes[1,1].plot(t,np.array(r['gas_species_kg'])[:,i].sum(axis=1),color=color)
for ax,title,y in zip(axes.flat,['Gas pressure','Gas temperature','Solid temperature','Gas inventory'],['Pa','K','K','kg']):
 ax.set(title=title,xlabel='Minutes from perigee',ylabel=y);ax.grid(alpha=.2);ax.axvline(0,color='gray',lw=.7)
axes[0,0].set_yscale('symlog',linthresh=.1);axes[1,1].set_yscale('symlog',linthresh=.01);axes[0,0].legend(fontsize=8);axes[0,0].set_ylim(bottom=0);axes[1,1].set_ylim(bottom=0);axes[0,1].set_title('Gas temperature (inventory > 0.01 kg)')
fig.suptitle('Combined staggered-plate / explicit-packing candidate — one forward cycle')
a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=150);fig.savefig(a.output.with_suffix('.svg'));plt.close(fig)

svg=a.output.with_suffix('.svg')
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
