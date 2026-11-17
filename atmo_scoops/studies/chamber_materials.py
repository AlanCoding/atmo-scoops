"""Reproducible material/allocation comparison; isolated proxy, not mission payoff."""
from pathlib import Path
import copy,json,multiprocessing
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from . import chamber_optimize as opt
from ..chambers.__main__ import run
from ..chambers.proxy import evaluate
from ..chambers.materials import material
ROOT=opt.ROOT;DEST=ROOT/'results/chamber_materials'
BOUNDS=opt.BOUNDS.copy();BOUNDS[0]=[2,12]

def main():
 DEST.mkdir(exist_ok=True)
 anchor=json.loads((ROOT/'results/reboost/solid_isp_optimum_1601.json').read_text())
 ref=json.loads((ROOT/'results/chamber_optimization/settings.json').read_text())['reference_shaft_MJ']
 original=json.loads((ROOT/'configs/chamber_transient_optimized.json').read_text())
 summary={}
 for front in ('iron','fecral','sic'):
  folder=DEST/front;folder.mkdir(exist_ok=True);opt.DEST=folder
  base=copy.deepcopy(original)
  for i,c in enumerate(base['chambers']):c['material']=front if i==0 or front=='iron' else 'aluminum'
  base['schedule'].update(max_step_s=8.,rtol=1e-4);base['samples']=501
  x0=np.array([c['rack_depth_m'] for c in base['chambers']]+[c['depth_m']-c['rack_depth_m'] for c in base['chambers']])
  scaled=x0.copy()
  for i,c in enumerate(base['chambers']):
   hot=813 if i==0 else 480
   a=material('iron');b=material(c['material'])
   scaled[i]*=a.density*(a.energy(hot)-a.energy(298))/(b.density*(b.energy(hot)-b.energy(298)))
  rows=[];seen={}
  def batch(vectors,pool):
   jobs=[]
   for x in vectors:
    x=np.clip(x,BOUNDS[:,0],BOUNDS[:,1]);key=tuple(np.round(x,7))
    if key not in seen:seen[key]=None;jobs.append((len(seen)-1,x,base,anchor,ref))
   for row in pool.map(opt.worker,jobs):
    rows.append(row);seen[tuple(np.round(row['x'],7))]=row
    print(front,row['id'],round(row.get('proxy_days',1e9),2),row['feasible'],row.get('error',''),flush=True)
   (folder/'search.json').write_text(json.dumps(rows,indent=2)+'\n')
   return [seen[tuple(np.round(np.clip(x,BOUNDS[:,0],BOUNDS[:,1]),7))] for x in vectors]
  with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
   best=min(batch([x0,scaled],pool),key=lambda r:r['score'])
   for step in (.5,.25,.1):
    for sweep in range(2):
     x=np.array(best['x']);vectors=[]
     for i in range(10):
      for sign in (-1,1):
       xx=x.copy();xx[i]+=sign*step*max(x[i],.1 if i<5 else 2.);vectors.append(xx)
     trial=min(batch(vectors,pool),key=lambda r:r['score'])
     if trial['score']<best['score']:best=trial
     else:break
  if not best['feasible']:raise RuntimeError(f'No feasible {front} case')
  cfg=opt.build(best['x'],base);cfg['schedule'].update(max_step_s=2.,rtol=2e-6);cfg['samples']=1801
  (folder/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
  r=run(cfg);p=evaluate(r,anchor,ref)
  if not p["feasible"]:raise RuntimeError(f"Refined {front} candidate violates constraints: {p['margins']}")
  (folder/'best.json').write_text(json.dumps(r)+'\n');(folder/'proxy.json').write_text(json.dumps(p,indent=2)+'\n')
  verify=copy.deepcopy(cfg);verify['schedule'].update(max_step_s=1.,rtol=5e-7)
  rr=run(verify);pp=evaluate(rr,anchor,ref)
  if not pp["feasible"]:raise RuntimeError(f"Verification of {front} violates constraints: {pp['margins']}")
  (folder/'verified.json').write_text(json.dumps(rr)+'\n')
  summary[front]=dict(proxy=p,verified_proxy=pp,search_count=len(rows),feasible_count=sum(row['feasible'] for row in rows),numerical_failures=sum('error' in row for row in rows),best_id=best['id'])
  (DEST/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (DEST/'settings.json').write_text(json.dumps(dict(bounds_m=BOUNDS.tolist(),reference_shaft_MJ=ref,anchor='results/reboost/solid_isp_optimum_1601.json',method='two seeds; coordinate pattern search; steps .5,.25,.1; at most two sweeps each'),indent=2)+'\n')
if __name__=='__main__':main()
