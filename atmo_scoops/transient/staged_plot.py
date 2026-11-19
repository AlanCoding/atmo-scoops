"""Plot the validated active gas bypass; no new simulation."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .io import read_result

def main():
 r=read_result('results/transient/staged/bypass_verify/check_refined.json')
 t=np.array(r['time_s'])/60;idx=np.unique(np.linspace(0,len(t)-1,1000,dtype=int))
 gas=np.array(r['gas_reserve_species_kg']).sum(axis=1)/1000
 liquid=np.array(r['liquid_species_kg']).sum(axis=1)/1000
 fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
 ax[0].plot(t[idx],gas[idx],label='Gaseous thruster reserve')
 ax[0].plot(t[idx],liquid[idx],label='New liquid product')
 ax[0].set_ylabel('Inventory (tonnes)');ax[0].legend()
 ax[1].plot(t[idx],np.array(r['history']['gas_fill_kg_s'])[idx],label='Gas reserve refill')
 ax[1].plot(t[idx],np.array(r['history']['liquefaction_kg_s'])[idx],label='Liquefaction feed')
 ax[1].set_ylabel('Flow (kg/s)');ax[1].set_xlabel('Minutes from perigee');ax[1].legend()
 for a in ax:
  a.axvspan(-r['inputs']['design']['burn_s']/120,r['inputs']['design']['burn_s']/120,alpha=.08,color='gray')
  a.grid(alpha=.2)
 fig.suptitle(f'Validated bypass-only reference: {r["operating_payoff_days"]:.2f} days\nGas propellant returns to its starting inventory; only product is liquefied')
 out=Path('investigations/staged_refinement/bypass_cycle.png');fig.savefig(out,dpi=160)
if __name__=='__main__':main()
