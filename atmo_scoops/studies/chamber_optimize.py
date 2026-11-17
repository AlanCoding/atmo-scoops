"""Bounded multivariable pattern search for transient rack/empty-depth allocation."""
from pathlib import Path
import json,copy,os,multiprocessing,signal,time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from ..chambers.__main__ import run
from ..chambers.proxy import evaluate
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/chamber_optimization'
# Five rack depths and five additional empty depths (m). Fixed 30 m bore.
BOUNDS=np.array([(2.,7.),(.015,.8),(.015,.8),(.015,.8),(.015,1.),(0.,12.),(0.,12.),(0.,12.),(0.,12.),(2.,100.)])

def build(x,base):
 c=copy.deepcopy(base)
 for i,v in enumerate(c['chambers']):v.update(rack_depth_m=float(x[i]),depth_m=float(x[i]+x[i+5]))
 return c

def worker(job):
 idx,x,base,anchor,ref=job
 started=time.monotonic()
 def timeout(signum,frame):raise RuntimeError('Numerical timeout after 35 seconds; not a physical rejection')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(35)
 try:
  r=run(build(x,base));p=evaluate(r,anchor,ref)
  # Penalize real constraint breaches; retain failed cases and reasons.
  penalty=sum(max(0.,-p['margins'][k])/scale for k,scale in [('length_m',30),('pressure_Pa',1e4),('metal_K',100),('gas_K',1000),('net_product_kg',1000),('reset_time_s',1000)])
  score=p['proxy_days'] if p['feasible'] else 1e5+1e4*penalty
  record=dict(id=idx,x=list(map(float,x)),score=score,**p)
  if p['feasible']:(DEST/f'candidate_{idx:04d}.json').write_text(json.dumps(r)+'\n')
 except (ValueError,RuntimeError,OverflowError) as e:record=dict(id=idx,x=list(map(float,x)),score=1e9,feasible=False,error=str(e))
 signal.alarm(0);record['elapsed_s']=time.monotonic()-started
 return record

def main():
 DEST.mkdir(exist_ok=True);anchor=json.loads((ROOT/'results/reboost/solid_isp_optimum_1601.json').read_text())
 base=json.loads((ROOT/'configs/chamber_transient_reference.json').read_text());base['schedule'].update(start_s=-600.,max_step_s=8.,rtol=1e-4,withdrawal_kg_s=2.);base['samples']=501
 baseline=run(base);ref=baseline['ledger']['shaft_work_MJ'][-1]
 (DEST/'baseline.json').write_text(json.dumps(baseline)+'\n');(DEST/'baseline_proxy.json').write_text(json.dumps(evaluate(baseline,anchor,ref),indent=2)+'\n')
 (DEST/'settings.json').write_text(json.dumps(dict(bounds_m=BOUNDS.tolist(),reference_shaft_MJ=ref,base_config=base,anchor='results/reboost/solid_isp_optimum_1601.json',processing_kg_MJ=10.,method='bounded coordinate pattern search, two starts, three step scales'),indent=2)+'\n')
 x0=np.array([c['rack_depth_m'] for c in base['chambers']]+[c['depth_m']-c['rack_depth_m'] for c in base['chambers']]);x0=np.clip(x0,BOUNDS[:,0],BOUNDS[:,1])
 rows=[];seen={};counter=0
 def batch(vectors,pool):
  nonlocal counter
  jobs=[]
  for x in vectors:
   x=np.clip(x,BOUNDS[:,0],BOUNDS[:,1]);key=tuple(np.round(x,7))
   if key not in seen:seen[key]=None;jobs.append((counter,x,base,anchor,ref));counter+=1
  for row in pool.map(worker,jobs):
   rows.append(row);seen[tuple(np.round(row['x'],7))]=row
   print('eval',row['id'],'days',round(row.get('proxy_days',1e9),2),'feasible',row['feasible'],'seconds',round(row['elapsed_s'],1),row.get('error',''),flush=True)
   (DEST/'search.json').write_text(json.dumps(rows,indent=2)+'\n')
  (DEST/'search.json').write_text(json.dumps(rows,indent=2)+'\n')
  return [seen[tuple(np.round(np.clip(x,BOUNDS[:,0],BOUNDS[:,1]),7))] for x in vectors]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('fork')) as pool:
  seeds=batch([x0,np.r_[4.,.3,.15,.08,.12,1.,1.,1.,1.,25.]],pool)
  best=min(seeds,key=lambda r:r['score'])
  for step in (.65,.35,.15):
   for sweep in range(2):
    x=np.array(best['x']);vectors=[]
    for i in range(10):
     for sign in (-1,1):
      xx=x.copy();delta=step*max(x[i],.1 if i<5 else 2.);xx[i]+=sign*delta;vectors.append(xx)
    trial=min(batch(vectors,pool),key=lambda r:r['score'])
    if trial['score']<best['score']:best=trial
    else:break
    print('BEST',best['id'],best['score'],flush=True)
 (DEST/'best_search.json').write_text(json.dumps(best,indent=2)+'\n')
 if not best['feasible']:raise RuntimeError('No feasible candidate')
 config=build(best['x'],base);config['schedule'].update(max_step_s=2.,rtol=2e-6);config['samples']=1801
 (ROOT/'configs/chamber_transient_optimized.json').write_text(json.dumps(config,indent=2)+'\n')
 for name,cfg in [('best',config),('baseline_refined',{**base,'schedule':{**base['schedule'],'max_step_s':2.,'rtol':2e-6},'samples':1801})]:
  r=run(cfg);p=evaluate(r,anchor,ref);(DEST/f'{name}.json').write_text(json.dumps(r)+'\n');(DEST/f'{name}_proxy.json').write_text(json.dumps(p,indent=2)+'\n');print(name,p,flush=True)
if __name__=='__main__':main()
