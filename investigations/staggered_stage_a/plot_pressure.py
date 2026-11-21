"""Pressure-loss applicability, from saved states only."""
import argparse,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-mpl')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.transient.io import read_result
p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=read_result(a.result);h=r['history'];t=np.array(r['time_s'])/60
flow=np.column_stack([h['pump_kg_s'],h['coast_kg_s']]);press=np.array(h['pressure_Pa']);drop=np.array(h['rack_drop_Pa'])
fig,axes=plt.subplots(5,2,figsize=(13,13),layout='constrained')
for i in range(5):
 mask=flow[:,i]>.01*flow[:,i].max();ratio=drop[:,i]/np.maximum(press[:,i],1e-30)
 axes[i,0].plot(t,np.where(mask,press[:,i],np.nan),label='Rack inlet / chamber pressure',color='#126e8b')
 axes[i,0].plot(t,np.where(mask,drop[:,i],np.nan),label='Modeled pressure drop',color='#b67c12')
 axes[i,0].set_yscale('log');axes[i,0].set_ylabel(f'Rack {i+1}\nPa')
 axes[i,1].plot(t,np.where(mask,ratio,np.nan),color='#126e8b');axes[i,1].axhline(1,color='#b03a43',ls='--',label='Drop = inlet pressure')
 axes[i,1].fill_between(t,1,np.maximum(1,ratio),where=mask&(ratio>1),color='#d98e96',alpha=.4)
 axes[i,1].set_yscale('log');axes[i,1].set_ylabel('Drop / inlet pressure')
 for ax in axes[i]:
  ax.set_xlim((-8,12) if i<4 else (10,73));ax.grid(alpha=.2);ax.set_xlabel('Minutes from perigee')
axes[0,0].legend(fontsize=8);axes[0,1].legend(fontsize=8)
fig.suptitle('Rack pressure-loss surrogate — only flow above 1% of each stage peak shown\nRed regions cannot be read as a physically realized pressure drop',fontsize=14)
a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=140);fig.savefig(a.output.with_suffix('.svg'));plt.close(fig)

svg=a.output.with_suffix('.svg')
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
