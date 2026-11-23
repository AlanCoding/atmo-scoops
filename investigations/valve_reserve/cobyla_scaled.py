"""Established constrained COBYLA, with parallel exact initialization caching."""
import argparse,json,time,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import minimize,Bounds
from atmo_scoops.transient.plate_optimize import encode
from investigations.valve_reserve.optimize import isolated_trial

def scaled_constraints(r):
 v=np.array(r['constraints'],dtype=float)
 factors=dict(gas_reserve_species_kg=1e-4,gas_reserve_MJ=.01,receiver_fill_Pa=.01,
              unmet_MJ=1e-4,rack_enthalpy_J_kg=.005,battery_MJ=.001,warm_MJ=.001,
              gas_kg=1e-4,gas_MJ=1e-4,rotor_MJ=1e-4,thrust_relative=1e-4)
 for i,name in enumerate(r['names']):v[i]*=factors.get(name.split(':')[0],1.)
 return v

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--output',required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--maxiter',type=int,default=240);p.add_argument('--rhobeg',type=float,default=.03);p.add_argument('--tol',type=float,default=.01);a=p.parse_args()
 old=json.load(open(a.manifest));base=old['base'];spec=old['coordinates'];out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 manifest=dict(base=base,coordinates=spec,algorithm='scipy COBYLA with characteristic-magnitude constraint scaling',options=dict(maxiter=a.maxiter,rhobeg=a.rhobeg,tol=a.tol,catol=1e-9),source_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path('atmo_scoops/transient').glob('*.py')))+Path(__file__).read_bytes()+Path('investigations/valve_reserve/optimize.py').read_bytes()).hexdigest())
 mp=out/'manifest.json'
 if mp.exists() and json.loads(mp.read_text())!=manifest:raise ValueError('Changed implementation/search manifest')
 mp.write_text(json.dumps(manifest,indent=2)+'\n');cache={};count=[0];best=[None]
 def evaluate(x):
  key=tuple(x)
  if key in cache:return cache[key]
  return accept(isolated_trial((list(x),base,spec,str(out))))
 def accept(r):
  if 'error' in r:raise RuntimeError(r['error'])
  cache[tuple(r['x'])]=r;count[0]+=1
  if r['feasible'] and min(r['constraints'])>=-1e-7 and (best[0] is None or r['operating_payoff_days']<best[0]['operating_payoff_days']):
   best[0]=r
   (out/'best_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n');(out/'best_summary.json').write_text(json.dumps(r,indent=2)+'\n')
  print(json.dumps(dict(evaluation=count[0],seconds=round(r['seconds'],1),days=r['diagnostic_payoff_days'],feasible=r['feasible'],constraint_min=min(r['constraints']),best_days=best[0]['operating_payoff_days'] if best[0] else None)),flush=True)
  return r
 x=encode(base,spec)
 try:
  evaluate(x)
  xs=[x+np.eye(len(x))[i]*(a.rhobeg if x[i]+a.rhobeg<=1 else -a.rhobeg) for i in range(len(x))]
  with ThreadPoolExecutor(max_workers=a.workers) as pool:
   for r in pool.map(isolated_trial,[(list(z),base,spec,str(out)) for z in xs]):accept(r)
  sol=minimize(lambda x:evaluate(x)['diagnostic_payoff_days']/300,x,method='COBYLA',bounds=Bounds(np.zeros(len(x)),np.ones(len(x))),constraints=[dict(type='ineq',fun=lambda x:scaled_constraints(evaluate(x)))],options=manifest['options'])
  r=evaluate(sol.x)
  (out/'selected_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n');(out/'selected_summary.json').write_text(json.dumps(r,indent=2)+'\n')
  done=dict(success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),maxcv=float(sol.maxcv),feasible=r['feasible'],days=r['operating_payoff_days'],best_feasible_days=best[0]['operating_payoff_days'] if best[0] else None,evaluations=count[0])
 except Exception as e:done=dict(success=False,error=str(e),evaluations=count[0])
 (out/'termination.json').write_text(json.dumps(done,indent=2)+'\n');print(json.dumps(done),flush=True)
if __name__=='__main__':main()
