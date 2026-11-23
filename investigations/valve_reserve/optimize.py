"""Outer constrained solve: one forward cycle per candidate, parallel derivatives.

No cycling/shooting inside simulate. Restoration solves only three outer state/
orbit coordinates; full SLSQP then exposes geometry, capacities and controls.
"""
import argparse,copy,json,time,hashlib,signal,os,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import minimize,least_squares,Bounds
from atmo_scoops.transient.plate_optimize import specs as plate_specs,encode,decode,constraint_vector
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.io import write_trajectory
from atmo_scoops.transient.search import summary

def derived(config):
 d=config['design']
 d['plant_start_s']=max(650.,d['burn_s']/2+30.,d['pump_stop_s']+30.)
 # Conservative installed power envelope, not a post-cycle resizing loop.
 h=compile_hardware(*read_config(config))
 peak=h['thrust_W']/1e6+sum(d['motor_MW'])+d['coast_motor_MW']+d['plant_electric_MW']+1.
 d.update(bus_MW=peak,battery_MW=peak)
 return config

def trial(task):
 x,base,spec,out=task;t=time.monotonic();key=hashlib.sha256(np.asarray(x,dtype=np.float64).tobytes()).hexdigest()
 path=Path(out)/('eval_'+key+'.json')
 if path.exists():return json.loads(path.read_text())
 c=derived(decode(x,base,spec))
 def timeout(*args):raise TimeoutError('forward solve exceeded 360 seconds')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(360)
 try:
  r=simulate(c,samples=101);names,cv=constraint_vector(r)
  # Scale new engineering constraints, without altering physical tolerances.
  for i,n in enumerate(names):
   if n=='full_capture':cv[i]/=.001
   elif n=='receiver_fill_Pa':cv[i]=cv[i]/50.-.1
   elif n.startswith(('gas_reserve_species_kg:', 'gas_reserve_MJ:')):cv[i]-=.5
  row=dict(x=list(x),seconds=time.monotonic()-t,names=names,constraints=cv.tolist(),**summary(r))
  if r['feasible']:write_trajectory(Path(out)/('trajectory_'+key+'.json'),r)
 except Exception as e:
  row=dict(x=list(x),error=str(e),seconds=time.monotonic()-t,inputs=c)
 finally:signal.alarm(0)
 path.write_text(json.dumps(row,indent=2)+'\n')
 return row

def isolated_trial(task):
 x,base,spec,out=task
 key=hashlib.sha256(np.asarray(x,dtype=np.float64).tobytes()).hexdigest()
 result=Path(out)/('eval_'+key+'.json')
 if result.exists():return json.loads(result.read_text())
 path=Path(out)/('task_'+key+'.json');path.write_text(json.dumps(task))
 p=subprocess.run([sys.executable,__file__,'--worker-task',str(path)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-2000:])
 return json.loads(result.read_text())

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);p.add_argument('--restore',action='store_true');p.add_argument('--workers',type=int,default=12);p.add_argument('--maxiter',type=int,default=30);a=p.parse_args()
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);base=json.load(open(a.config))
 added=[dict(key='perigee_km',low=80.,high=100.),dict(key='gas_reserve_kg',low=1500.,high=8000.),dict(key='gas_initial_K',low=200.,high=490.)]
 spec=added if a.restore else plate_specs(base)+added
 if not a.restore:
  for k in ('suction_m3_s','head_J_kg'):
   for i,v in enumerate(base['design'][k]):spec.append(dict(key=f'{k}:{i}',low=v*.4,high=v*2.5))
  for k in ('coast_suction_m3_s','coast_head_J_kg'):
   v=base['design'][k];spec.append(dict(key=k,low=v*.4,high=v*2.5))
 manifest=dict(base=base,coordinates=spec,method='outer least_squares restoration' if a.restore else 'SLSQP',maxiter=a.maxiter,derivative_step=.0002)
 manifest['source_sha256']=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path('atmo_scoops/transient').glob('*.py')))+Path(__file__).read_bytes()).hexdigest()
 if (out/'manifest.json').exists() and json.loads((out/'manifest.json').read_text())!=manifest:raise ValueError('Changed source or search manifest; use a new output directory')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cache={};counter=[0]
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  def rows(xs):
   keys=[tuple(x) for x in xs];missing=[x for x in xs if tuple(x) not in cache]
   for r in pool.map(isolated_trial,[(list(x),base,spec,str(out)) for x in missing]):
    if 'error' in r:raise RuntimeError(r['error'])
    cache[tuple(r['x'])]=r;counter[0]+=1
    print(json.dumps(dict(evaluation=counter[0],seconds=round(r['seconds'],1),days=r['diagnostic_payoff_days'],feasible=r['feasible'],min_constraint=min(r['constraints']),reserve_kg=sum(r['closure']['gas_reserve_species_kg']),reserve_MJ=r['closure']['gas_reserve_MJ'],fill_Pa=r['closure']['receiver_fill_Pa'])),flush=True)
   return [cache[k] for k in keys]
  def evaluate(x):return rows([x])[0]
  def output(r):
   (out/'selected_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
   (out/'selected_summary.json').write_text(json.dumps(r,indent=2)+'\n')
  def rootf(x):
   r=evaluate(x);c=r['closure'];return np.array([sum(c['gas_reserve_species_kg'])/1000,c['gas_reserve_MJ']/100,c['receiver_fill_Pa']/1000])
  def vector(x):
   r=evaluate(x);return np.r_[r['diagnostic_payoff_days']/300,r['constraints']]
  jcache={}
  def jacobian(x,fun):
   key=tuple(x)
   if key not in jcache:
    hs=np.where(x+.0002<=1,.0002,-.0002);xs=[x+np.eye(len(x))[i]*hs[i] for i in range(len(x))];rows(xs)
    f=fun(x);jcache.clear();jcache[key]=np.array([(fun(z)-f)/h for z,h in zip(xs,hs)]).T
   return jcache[key]
  x=encode(base,spec)
  try:
   if a.restore:
    sol=least_squares(rootf,x,jac=lambda x:jacobian(x,rootf),bounds=(np.zeros(len(x)),np.ones(len(x))),xtol=1e-7,ftol=1e-7,gtol=1e-7,max_nfev=a.maxiter)
   else:
    sol=minimize(lambda x:vector(x)[0],x,jac=lambda x:jacobian(x,vector)[0],method='SLSQP',bounds=Bounds(np.zeros(len(x)),np.ones(len(x))),constraints=[dict(type='ineq',fun=lambda x:vector(x)[1:],jac=lambda x:jacobian(x,vector)[1:])],options=dict(maxiter=a.maxiter,ftol=1e-5,disp=True),callback=lambda x:output(evaluate(x)))
   r=evaluate(sol.x);output(r)
   done=dict(success=bool(sol.success),message=str(sol.message),nfev=int(sol.nfev),feasible=r['feasible'],days=r['operating_payoff_days'],min_constraint=min(r['constraints']),evaluations=counter[0])
  except Exception as exc:done=dict(success=False,error=str(exc),evaluations=counter[0])
  (out/'termination.json').write_text(json.dumps(done,indent=2)+'\n');print(json.dumps(done),flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--worker-task':trial(json.loads(Path(sys.argv[2]).read_text()))
 else:main()
