"""Replay actual COBYLA requests and batch its remaining axial initialization.

Predicted future probes may go unused if the anchor shifts. Only points actually
requested by unchanged scipy COBYLA participate in its optimization.
"""
import argparse,json,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import minimize,Bounds
from atmo_scoops.transient.plate_optimize import encode
from investigations.valve_reserve.optimize import isolated_trial
class Missing(Exception):pass

def main():
 p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--workers',type=int,default=8);a=p.parse_args();out=Path(a.output);m=json.load(open(out/'manifest.json'));base=m['base'];spec=m['coordinates'];n=len(spec);rho=m['options']['rhobeg']
 for batch in range(12):
  rows=[json.load(open(p)) for p in out.glob('eval_*.json')];cache={tuple(r['x']):r for r in rows};used=[];nxt=[]
  def evaluate(x):
   key=tuple(x)
   if key not in cache:nxt.extend(x.tolist());raise Missing()
   if key not in used:used.append(key)
   if 'error' in cache[key]:raise RuntimeError(cache[key]['error'])
   return cache[key]
  try:minimize(lambda x:evaluate(x)['diagnostic_payoff_days']/300,encode(base,spec),method='COBYLA',bounds=Bounds(np.zeros(n),np.ones(n)),constraints=[dict(type='ineq',fun=lambda x:np.array(evaluate(x)['constraints']))],options=m['options'])
  except Missing:pass
  audit=dict(used=len(used),cached=len(cache),next_x=nxt)
  (out/'replay.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit),flush=True)
  if not nxt or len(used)>=n+1:break
  anchors=[]
  for x in used:
   dx=np.array(nxt)-x;changed=np.flatnonzero(abs(dx)>1e-12)
   if len(changed)==1 and abs(abs(dx[changed[0]])-rho)<1e-12:anchors.append((np.array(x),int(changed[0])))
  if not anchors:break
  anchor,start=anchors[-1];xs=[]
  for i in range(start,min(n,start+a.workers)):
   x=anchor.copy();x[i]+=rho if x[i]+rho<=1 else -rho
   if tuple(x) not in cache:xs.append(x)
  if not xs:break
  with ThreadPoolExecutor(max_workers=a.workers) as pool:
   for r in pool.map(isolated_trial,[(list(x),base,spec,str(out)) for x in xs]):
    if 'error' in r:raise RuntimeError(r['error'])
    print(json.dumps(dict(seconds=r['seconds'],days=r['diagnostic_payoff_days'],feasible=r['feasible'])),flush=True)
if __name__=='__main__':main()
