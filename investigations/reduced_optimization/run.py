"""Incremental SLSQP: total rack mass, three closure coordinates, then pressure.

No changes to cycle physics. Closure restoration is explicit in the outer solve.
"""
from pathlib import Path
import argparse,copy,json,hashlib,os,signal,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import minimize
from atmo_scoops.transient.reduced_coordinates import with_total_rack_mass,rack_allocation
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.plate_optimize import constraint_vector
from atmo_scoops.transient.io import write_trajectory,read_result
ROOT=Path(__file__).resolve().parents[2]

def solver_jacobian(columns):
 """C-contiguous rows: SLSQP's gradient bridge must not see strided views."""
 return np.array(columns, dtype=float).T.copy(order='C')

def checked_bounds(bounds, x0):
 """Validate explicit search ranges without relaxing any cycle constraint."""
 b=np.asarray(bounds,dtype=float);x=np.asarray(x0,dtype=float)
 if b.shape!=(len(x),2) or not np.all(np.isfinite(b)) or not np.all(b[:,0]<b[:,1]):
  raise ValueError('Bounds must be finite ordered pairs, one per coordinate')
 if not np.all(np.isfinite(x)) or np.any(x<b[:,0]) or np.any(x>b[:,1]):
  raise ValueError('Initial coordinates must lie within every bound')
 if b[0,0]<=0 or (len(x)==5 and b[4,0]<=0):
  raise ValueError('Rack mass and pressure ratios must stay positive')
 return b.tolist()

def config_at(base,x):
 c=with_total_rack_mass(base,rack_allocation(base)['total_kg']*float(x[0]));d=c['design'];b=base['design']
 d['perigee_km']=b['perigee_km']+float(x[1])
 d['gas_reserve_kg']=b['gas_reserve_kg']+1000*float(x[2])
 d['gas_initial_K']=b['gas_initial_K']+100*float(x[3])
 if len(x)==5:
  d['receiver_fill_Pa']=b['receiver_fill_Pa']*float(x[4])
  d['rated_pressure_Pa'][-1]=b['rated_pressure_Pa'][-1]*float(x[4])
 h=compile_hardware(*read_config(c));peak=h['thrust_W']/1e6+sum(d['motor_MW'])+d['coast_motor_MW']+d['plant_electric_MW']+1.
 d['bus_MW']=peak;d['battery_MW']=peak
 return c

def evaluate(task):
 base,x,out=task;out=Path(out);c=config_at(base,x)
 key=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();path=out/f'eval_{key}.json'
 cached=json.loads(path.read_text()) if path.exists() else None
 if cached and cached.get('contract')=='guarded_bands_v2':return cached
 reused=bool(cached and (out/f'trajectory_{key}.json.gz').exists())
 def timeout(*_):raise TimeoutError('600-second numerical evaluation budget; not physical infeasibility')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(600);start=time.monotonic()
 try:
  r=read_result(out/f'trajectory_{key}.json.gz') if reused else simulate(c,samples=501)
  names,vals=constraint_vector(r);cl=r['closure'];ins=[];iv=[]
  for n,v in zip(names,vals):
   # Use guarded versions of existing finite tolerances, not exact closure.
   if n=='receiver_fill_Pa':
    ins.extend(['receiver_fill_upper','receiver_fill_lower']);iv.extend([1.-cl['receiver_fill_Pa']/25.,1.+cl['receiver_fill_Pa']/25.]);continue
   elif n.startswith(('gas_reserve_species_kg:', 'gas_reserve_MJ:')):v-=.5
   # The cycle itself accepts -1e-6 kg roundoff; expose that existing guard.
   elif n=='liquid_kg':v+=1e-6
   if n=='full_capture':v/=0.001
   ins.append(n);iv.append(float(v))
  row=dict(contract='guarded_bands_v2',reused_cycle=reused,x=list(x),inputs=c,key=key,seconds=time.monotonic()-start,
   days=r['diagnostic_payoff_days'],feasible=r['feasible'],dry_kg=r['dry_kg'],liquid_kg=r['net_liquid_kg'],
   eq=[cl['receiver_fill_Pa']/100,sum(cl['gas_reserve_species_kg'])/100,cl['gas_reserve_MJ']/10],
   inequality_names=ins,ineq=iv,closure=cl,margins=r['margins'],audits=r['audits'],
   original_failed={n:float(v) for n,v in zip(names,vals) if v < -1e-7},
   rack_kg=[g['mass_kg'] for g in r['hardware']['geometry']],receiver_m3=r['hardware']['geometry'][4]['gas_m3'])
  if not reused:write_trajectory(out/f'trajectory_{key}.json',r)
 except Exception as e:row=dict(x=list(x),inputs=c,key=key,error=repr(e),seconds=time.monotonic()-start)
 finally:signal.alarm(0)
 path.write_text(json.dumps(row,indent=2)+'\n');return row

def isolated(task):
 _,x,out=task;key=hashlib.sha256(json.dumps(x).encode()).hexdigest();path=Path(out)/f'task_{key}.json';path.write_text(json.dumps(task))
 p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker-task',str(path)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-2000:])
 return json.loads(p.stdout)

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);p.add_argument('--pressure',action='store_true');p.add_argument('--maxiter',type=int,default=20);p.add_argument('--start-x');p.add_argument('--bounds-file',type=Path);p.add_argument('--rtol',type=float,default=1e-7);p.add_argument('--rack-step',type=float,default=.005);a=p.parse_args()
 base=json.loads(Path(a.config).read_text());base['design'].update(rtol=a.rtol,max_step_s=5.)
 if not 0<a.rtol<1 or not np.isfinite(a.rack_step) or a.rack_step<=0:raise ValueError('Invalid numerical resolution')
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 x0=np.array([1.,0.,0.,0.]+([1.] if a.pressure else []));steps=np.array([a.rack_step,.005,.002,.002]+([.002] if a.pressure else []))
 if a.start_x:x0=np.array(json.loads(a.start_x),dtype=float)
 bounds=[(.9,1.1),(-.5,.5),(-.3,.3),(-.15,.15)]
 if a.pressure:
  p0=base['design']['receiver_fill_Pa'];bounds.append((4766.8327597/p0,1.2*4766.8327597/p0))
 if a.bounds_file:bounds=json.loads(a.bounds_file.read_text())
 bounds=checked_bounds(bounds,x0)
 manifest=dict(base=base,coordinates=['total_rack_mass_ratio','perigee_delta_km','reserve_delta_1000kg','reserve_temperature_delta_100K']+(['receiver_pressure_ratio'] if a.pressure else []),bounds=bounds,start_x=x0.tolist(),steps=steps.tolist(),method='SLSQP',options=dict(maxiter=a.maxiter,ftol=.005),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),model_sha256=hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+p.read_bytes() for p in sorted((ROOT/'atmo_scoops').rglob('*.py')))).hexdigest())
 # JSON normalizes tuples to lists.
 manifest=json.loads(json.dumps(manifest));mp=out/'manifest.json'
 if mp.exists() and json.loads(mp.read_text())!=manifest:raise ValueError('Changed search provenance: use another output directory')
 mp.write_text(json.dumps(manifest,indent=2)+'\n');cache={};rows=[];iterations=[]
 def accept(r):
  rows.append(r);(out/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n')
  if 'error' in r:raise RuntimeError(r['error'])
  cache[tuple(r['x'])]=r
  print(json.dumps(dict(evaluation=len(rows),x=r['x'],days=r['days'],eq=r['eq'],min_ineq=min(r['ineq']),feasible=r['feasible'],seconds=r['seconds'])),flush=True)
  return r
 def get(x):
  k=tuple(float(v) for v in x)
  return cache[k] if k in cache else accept(evaluate((base,list(k),str(out))))
 def vector(x):
  r=get(x);return np.r_[r['days'],r['eq'],r['ineq']]
 jac_cache={}
 try:
  with ThreadPoolExecutor(max_workers=len(x0)) as pool:
   def jac(x):
    k=tuple(x)
    if k not in jac_cache:
     f=vector(x);hs=np.array([h if z+h<=bound[1] else -h for z,h,bound in zip(x,steps,bounds)])
     points=[x+np.eye(len(x))[i]*hs[i] for i in range(len(x))]
     missing=[z for z in points if tuple(z) not in cache]
     for r in pool.map(isolated,[(base,z.tolist(),str(out)) for z in missing]):accept(r)
     jac_cache.clear();jac_cache[k]=solver_jacobian([(vector(z)-f)/h for z,h in zip(points,hs)])
    return jac_cache[k]
   def callback(x):
    r=get(x);iterations.append(dict(x=list(x),days=r['days'],eq=r['eq'],feasible=r['feasible']))
    (out/'iterations.json').write_text(json.dumps(iterations,indent=2)+'\n')
   sol=minimize(lambda x:get(x)['days'],x0,jac=lambda x:jac(x)[0],method='SLSQP',bounds=bounds,
    constraints=[dict(type='ineq',fun=lambda x:np.array(get(x)['ineq']),jac=lambda x:jac(x)[4:])],
    callback=callback,options=manifest['options'])
   selected=get(sol.x)
   (out/'selected_summary.json').write_text(json.dumps(selected,indent=2)+'\n');(out/'selected_config.json').write_text(json.dumps(selected['inputs'],indent=2)+'\n')
   import shutil
   shutil.copyfile(out/f'trajectory_{selected["key"]}.json.gz',out/'selected.json.gz')
   done=dict(success=bool(sol.success),status=int(sol.status),message=str(sol.message),nit=int(sol.nit),nfev=int(sol.nfev),cycles=len(rows),days=selected['days'],feasible=selected['feasible'],bound_hits=[n for n,v,b in zip(manifest['coordinates'],sol.x,bounds) if min(abs(v-b[0]),abs(v-b[1]))<1e-5])
 except Exception as e:done=dict(success=False,error=repr(e),cycles=len(rows))
 (out/'termination.json').write_text(json.dumps(done,indent=2)+'\n');print(json.dumps(done),flush=True)
 if not done['success']:raise SystemExit(1)
if __name__=='__main__':
 if '--worker-task' in sys.argv:print(json.dumps(evaluate(json.loads(Path(sys.argv[sys.argv.index('--worker-task')+1]).read_text()))))
 else:main()
