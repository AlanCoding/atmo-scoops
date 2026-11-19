"""Frozen-state rack trade; deliberately not an orbital payoff surrogate."""
import json,copy,math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .inputs import read_config
from .hardware import compile_hardware
from .porous import suction_pressure
from ..racks import conductance,Racks

def main():
    c=json.load(open('configs/transient_low_re_search.json'))
    radii=np.geomspace(.0002,.01,80);curves=[]
    fig,axes=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
    for a in (1.25,2.,5.,8.):
        ua=[];flows=[]
        for r in radii:
            x=copy.deepcopy(c);d=x['design'];d['stage_radius_m'][0]=r;d['stage_pitch_m'][0]=2*r*a
            d['rack_depth_m'][0]=5.42*(a/5)**2
            g=compile_hardware(*read_config(x))['geometry'][0]
            h,_=conductance(458.,(1339.+436.)/2,18.,g['frontal_m2'],g,Racks(metal_conductivity_W_m_K=100))
            m=brentq(lambda f:suction_pressure(f,458.,1339.,287.,g)[0]-.8*458,1e-9,1000)
            ua.append(h/1e6);flows.append(m if suction_pressure(m,458.,1339.,287.,g)[1]['Re']<=75 else None)
        style='-' if a<=2 else '--';label=f'pitch/diameter {a:g}'+(' (extrapolated)' if a>2 else '')
        axes[0].loglog(radii*1000,ua,style,label=label)
        axes[1].loglog(radii*1000,flows,style,label=label)
        curves.append(dict(pitch_diameter=a,radius_mm=(radii*1000).tolist(),UA_MW_K=ua,flow_at_20_percent_drop_kg_s=flows))
    for ax in axes:
        ax.set_xlabel('Rod radius (mm)');ax.grid(True,which='both',alpha=.2)
    axes[0].set_ylabel('Heat-transfer conductance (MW/K)');axes[0].set_title('Smaller rods increase heat exchange')
    axes[1].set_ylabel('Mass flow at 20% pressure loss (kg/s)');axes[1].set_title('Larger rods reduce hydraulic resistance')
    axes[1].axhline(18,color='gray',linewidth=.8);axes[0].legend(fontsize=8)
    fig.suptitle('Fixed front-rack metal inventory and gas state — not optimized cycle performance')
    out=Path('investigations/rack_radius');out.mkdir(exist_ok=True)
    fig.savefig(out/'fixed_state_trade.png',dpi=160)
    (out/'fixed_state_trade.json').write_text(json.dumps(dict(pressure_Pa=458,gas_K=1339,metal_K=436,heat_flow_kg_s=18,curves=curves),indent=2)+'\n')
if __name__=='__main__':main()
