"""Parallel positive-coordinate sensitivity probes with exact cache reuse.

Not a different optimizer: the ordinary search must replay these exact x keys.
Run only while plate_optimize is stopped. No approximate/rounded cache matching.
"""
import argparse,hashlib,json,multiprocessing,signal,time,tempfile
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
from atmo_scoops.transient.plate_optimize import encode,decode,constraint_vector
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.search import summary
from atmo_scoops.transient.io import write_trajectory,read_result

def trial(task):
 x,manifest,tmp,index=task;start=time.monotonic();config=decode(x,manifest['base'],manifest['coordinates'])
 def expired(*_):raise TimeoutError('Forward wall-time budget exhausted')
 signal.signal(signal.SIGALRM,expired);signal.alarm(manifest['seconds'])
 try:
  r=simulate(config,samples=101);names,cv=constraint_vector(r)
  row=dict(x=x,seconds=time.monotonic()-start,constraint_names=names,constraints=cv.tolist(),precomputed_initialization=True,**summary(r))
  path=str(write_trajectory(Path(tmp)/f'{index}.json',r)) if r['feasible'] else None
 except (RuntimeError,ValueError,TimeoutError,FloatingPointError) as exc:
  row=dict(x=x,inputs=config,seconds=time.monotonic()-start,error=str(exc),feasible=False,precomputed_initialization=True);path=None
 finally:signal.alarm(0)
 return row,path

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=4);p.add_argument('--from-replay',action='store_true');p.add_argument('--count',type=int,default=4);a=p.parse_args();out=a.output
 manifest=json.loads((out/'search.json').read_text())
 sources=[Path(__file__).resolve().parents[2]/'atmo_scoops'/'transient'/n for n in ('plate_optimize.py','plates.py','hardware.py','inputs.py','cycle.py','thermo.py','porous.py')]
 if manifest.get('implementation_sha256')!=hashlib.sha256(b''.join(p.read_bytes() for p in sources)).hexdigest():raise ValueError('Numerical implementation changed')
 ep=out/'evaluations.json';rows=json.loads(ep.read_text());keys={tuple(r['x']) for r in rows};x0=encode(manifest['base'],manifest['coordinates']);xs=[]
 start_coordinate=0
 if a.from_replay:
  audit=json.loads((out/'replay_audit.json').read_text());nxt=np.array(audit['next_x']);rho=manifest['options']['rhobeg'];anchors=[]
  for row in rows:
   if row['index'] not in audit['requested_evaluation_indices']:continue
   delta=nxt-np.array(row['x']);changed=np.flatnonzero(abs(delta)>1e-12)
   if len(changed)==1 and abs(delta[changed[0]]-rho)<1e-12:anchors.append((row, int(changed[0])))
  if not anchors:
   print('Initialization prefill ended: the next requested point requires the ordinary optimizer.',flush=True)
   raise SystemExit(2)
  anchor,start_coordinate=anchors[-1];x0=np.array(anchor['x'])
 for i in range(start_coordinate,min(len(x0),start_coordinate+a.count)):
  x=x0.copy();x[i]+=manifest['options']['rhobeg']
  if x[i]<=1 and tuple(x) not in keys:xs.append(x.tolist())
 best=min((r for r in rows if r.get('feasible')),key=lambda r:r['operating_payoff_days'],default=None)
 (out/'prefill.json').write_text(json.dumps(dict(method='Exact positive-coordinate initialization cache; ordinary COBYLA replay still required',workers=a.workers,requested=len(xs),start_coordinate=start_coordinate,anchor_x=x0.tolist()),indent=2)+'\n')
 with tempfile.TemporaryDirectory(prefix='atmo-prefill-') as tmp,ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
  jobs=[pool.submit(trial,(x,manifest,tmp,i)) for i,x in enumerate(xs)]
  for job in as_completed(jobs):
   row,path=job.result();row['index']=len(rows);rows.append(row)
   temp=ep.with_suffix('.tmp');temp.write_text(json.dumps(rows,indent=2)+'\n');temp.replace(ep)
   if row.get('feasible') and (best is None or row['operating_payoff_days']<best['operating_payoff_days']):
    best=row;r=read_result(Path(path));write_trajectory(out/'best.json',r);(out/'best_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n');(out/'best_summary.json').write_text(json.dumps(row,indent=2)+'\n')
   print(json.dumps({k:row.get(k) for k in ('index','seconds','feasible','diagnostic_payoff_days','error')}),flush=True)
 print('Sensitivity cache ready; resume unchanged plate_optimize command.',flush=True)
if __name__=='__main__':main()
