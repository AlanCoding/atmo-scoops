"""Audit fill-while-thrusting from the frozen v1.0.1 trajectory; no new solve."""
from pathlib import Path
import json,gzip
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
r=json.load(gzip.open(ROOT/'results/transient/valve_restore/selected_refined.json.gz','rt'))
t=np.array(r['time_s']);h=r['history'];d=r['inputs']['design'];m=np.array(h['buffer_kg']);p=np.array(h['buffer_Pa']);prop=sum(np.array(r['ledger']['prop_'+s]) for s in ('N2','O2','Ar'))
# Reserve has valve exchange and thruster outflow only. This gives net cumulative
# transfer independently of quadrature across the discontinuous opening event.
transfer=m-m[0]+prop
start=-d['burn_s']/2;end=d['burn_s']/2;opening=r['reserve_events'][0]['time_s']
def row(name,when):
 at=lambda a:float(np.interp(when,t,a))
 return dict(event=name,time_s=when,reserve_kg=at(m),reserve_Pa=at(p),main_receiver_Pa=at(np.array(h['pressure_Pa'])[:,4]),consumed_kg=at(prop),net_valve_in_kg=at(transfer))
rows=[row('Burn starts',start),row('Valve opens',opening),row('Minimum reserve',float(t[np.argmin(m)])),row('Perigee',0),row('Maximum reserve',float(t[np.argmax(m)])),row('Burn ends / reserve isolates',end)]
assert abs(transfer[0])<1e-8
assert np.max(abs(transfer[t<opening-1e-6]))<1e-5
out=dict(events=rows,initial_inventory_kg=float(m[0]),total_consumed_kg=float(prop[-1]),net_refill_kg=float(transfer[-1]),closure_kg=float(m[-1]-m[0]),initial_over_total_consumption=float(m[0]/prop[-1]),consumed_before_open_kg=rows[1]['consumed_kg'],remaining_burn_consumption_kg=float(prop[-1]-rows[1]['consumed_kg']),minimum_inventory_fraction=float(min(m)/m[0]),note='Net transfer inferred conservatively from inventory plus cumulative thruster outflow; bidirectional exchange is allowed.')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
plt.rcParams['svg.fonttype']='none'
fig,axs=plt.subplots(3,1,figsize=(11,9),sharex=True,layout='constrained')
axs[0].plot(t/60,np.array(h['pressure_Pa'])[:,4]/1000,label='Main receiver');axs[0].plot(t/60,p/1000,label='Thruster reserve');axs[0].set_ylabel('Pressure (kPa)')
axs[1].plot(t/60,m/1000,label='Reserve inventory');axs[1].plot(t/60,prop/1000,label='Cumulative propellant consumed');axs[1].plot(t/60,transfer/1000,label='Cumulative net valve refill');axs[1].set_ylabel('Mass (tonnes)')
axs[2].plot(t/60,h['valve_transfer_kg_s'],label='Valve flow (+ into reserve)');consumption=np.array(h['thrust_MW'])*1e6*2*r['inputs']['capabilities']['eta_thruster']/(d['isp_s']*9.80665)**2
axs[2].plot(t/60,consumption,label='Thruster flow');axs[2].set(xlabel='Minutes from perigee',ylabel='kg/s',xlim=(-11,11))
for ax in axs:
 ax.axvline(opening/60,color='gray',ls='--',label=f'Valve opens: {opening:.2f} s');ax.axvline(0,color='gray',ls=':');ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.suptitle('v1.0.1: the reserve refills while the thrusters are running')
for ext in ['svg','png']:
 path=Path(__file__).with_suffix('.'+ext);fig.savefig(path,dpi=160)
 if ext=='svg':path.write_text('\n'.join(x.rstrip() for x in path.read_text().splitlines())+'\n')
print(json.dumps(out,indent=2))
