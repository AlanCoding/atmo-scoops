"""Direct-solar boost-window / Isp optimization, separate first-order study."""
from pathlib import Path
from dataclasses import replace
import json
from scipy.optimize import differential_evolution
from ..system import inputs_from_dict
from ..two_volume import Reference,calculate
from ..inlet import ContinuousEncounter
from ..reboost import rebudget
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/reboost'
def main(architectures=None):
 rows=json.loads((DEST/'solar_screen.json').read_text()) if architectures and (DEST/'solar_screen.json').exists() else []
 best=json.loads((DEST/'solar_optima.json').read_text()) if architectures and (DEST/'solar_optima.json').exists() else []
 for label,path in [('solid','results/ammonia_integrated/refined/solid_1601.json'),('ammonia','results/ammonia_integrated/refined/cold200_1601.json'),('warm_ammonia','results/ammonia_integrated/refined/warm280_1601.json')]:
  if architectures and label not in architectures:continue
  source=json.loads((ROOT/path).read_text());a=inputs_from_dict(source['inputs'])
  cache=DEST/f'{label}_raw.json'
  if cache.exists():raw=json.loads(cache.read_text())
  else:
   raw=calculate(Reference(**source['resolved_cycle_inputs']),n=1601,process_targets=a['process'],flow_solver=ContinuousEncounter(a['flow'],a['controls']),
       mixing=a['mixing'],compressor=a['compressor'],racks=a['racks'],ammonia=a['ammonia'])
   cache.write_text(json.dumps(raw,indent=2)+'\n')
  for window in (120.,300.,600.,900.,1100.):
   for isp in (2000.,3000.,4000.):
    name=f'{label}_direct_w{window:g}_isp{isp:g}'
    try:
     r=rebudget(source,raw,isp,window);(DEST/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
     row=dict(name=name,architecture=label,isp_s=isp,window_s=window,payoff_days=r['payoff_days'],dry_t=r['dry_kg']/1000,net_kg=r['net_kg'],
       impulse_multiplier=r['arc']['impulse_multiplier'],solar_MW=r['solar_W']/1e6,screens=r['screens'])
    except ValueError as exc:row=dict(name=name,error=str(exc),screens=False)
    rows.append(row);print(row,flush=True);(DEST/'solar_screen.json').write_text(json.dumps(rows,indent=2)+'\n')
  for only_energy,buffered in ((False,False),(True,False),(False,True)) if source['outputs'].get('ammonia') else ((False,False),(True,False)):
   def objective(x):
    try:
     r=rebudget(source,raw,float(x[0]),float(x[1]),energy_only=only_energy,buffer_ammonia_rejection=buffered)
     return r['payoff_days'] if r['screens'] else 1e7+sum(max(0.,-v) for v in r['margins'].values())
    except ValueError:return 1e9
   opt=differential_evolution(objective,[(1000.,7000.),(60.,1600.)],seed=42,popsize=8,maxiter=35,tol=2e-5,polish=True)
   r=rebudget(source,raw,float(opt.x[0]),float(opt.x[1]),energy_only=only_energy,buffer_ammonia_rejection=buffered)
   name=f'{label}_direct_{"energy_only" if only_energy else "closed_orbit"}{"_buffered" if buffered else ""}_best'
   (DEST/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
   row=dict(name=name,architecture=label,isp_s=r['isp_s'],window_s=r['window_each_s'],payoff_days=r['payoff_days'],dry_t=r['dry_kg']/1000,
       net_kg=r['net_kg'],impulse_multiplier=r['arc']['impulse_multiplier'],solar_MW=r['solar_W']/1e6,screens=r['screens'])
   best.append(row);print(row,flush=True);(DEST/'solar_optima.json').write_text(json.dumps(best,indent=2)+'\n')
if __name__=='__main__':main()
