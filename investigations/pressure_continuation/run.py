"""Small pressure continuation with grouped hardware and explicit outer restoration.

One cycle per evaluation. No cycle-equation, constraint or tolerance changes.
"""
from pathlib import Path
import argparse,copy,json,hashlib,time,signal,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.optimize import brentq,least_squares
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.reduced_coordinates import rack_allocation,with_total_rack_mass
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.plate_optimize import constraint_vector
from atmo_scoops.transient.io import write_trajectory
ROOT=Path(__file__).resolve().parents[2]
BASE=json.loads((ROOT/'results/transient/valve_restore/selected_refined_config.json').read_text())

def installed(c):
 c=copy.deepcopy(c);d=c['design'];h=compile_hardware(*read_config(c))
 peak=h['thrust_W']/1e6+sum(d['motor_MW'])+d['coast_motor_MW']+d['plant_electric_MW']+1.
 d['bus_MW']=peak;d['battery_MW']=peak
 return c

def supply(c):
 h=compile_hardware(*read_config(c));f=h['forcing']
 return float(np.trapezoid(f['supply'],f['time']))

def seed(factor):
 c=with_total_rack_mass(BASE,rack_allocation(BASE)['total_kg']*factor);d=c['design'];b=BASE['design']
 # Keep geometric/thermal allocation fixed, scale extensive capacities as a seed.
 for k in ['solar_area_m2','battery_MWh','warm_store_kg','warm_radiator_m2',
           'plant_flow_kg_s','plant_electric_MW','coast_motor_MW','gas_reserve_kg']:
  d[k]=b[k]*factor
 d['motor_MW']=[v*factor for v in b['motor_MW']]
 d['rated_pressure_Pa']=[v*factor for v in b['rated_pressure_Pa']]
 d['receiver_fill_Pa']=b['receiver_fill_Pa']*factor
 target=supply(BASE)*factor
 def fun(alt):
  d['perigee_km']=alt
  return supply(c)-target
 alt=brentq(fun,80.,100.,xtol=1e-9);d['perigee_km']=alt
 return installed(c)

def candidate(base,x):
 c=copy.deepcopy(base);d=c['design']
 d['perigee_km']=base['design']['perigee_km']+float(x[0])
 d['gas_reserve_kg']=base['design']['gas_reserve_kg']+1000*float(x[1])
 d['gas_initial_K']=base['design']['gas_initial_K']+100*float(x[2])
 return installed(c)

def evaluate(task):
 base,x,folder=task;c=candidate(base,x);folder=Path(folder)
 key=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest();path=folder/f'eval_{key}.json'
 if path.exists():return json.loads(path.read_text())
 started=time.monotonic()
 def timeout(*args):raise TimeoutError('600-second forward limit: unresolved numerical evaluation')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(600)
 try:
  r=simulate(c,samples=1001);names,cv=constraint_vector(r);cl=r['closure']
  row=dict(x=list(x),seconds=time.monotonic()-started,inputs=c,feasible=r['feasible'],
   diagnostic_days=r['diagnostic_payoff_days'],operating_days=r['operating_payoff_days'],
   dry_kg=r['dry_kg'],liquid_kg=r['net_liquid_kg'],closure=cl,margins=r['margins'],audits=r['audits'],
   failed={n:float(v) for n,v in zip(names,cv) if v < -1e-7},
   residual=[cl['receiver_fill_Pa']/100.,sum(cl['gas_reserve_species_kg'])/100.,cl['gas_reserve_MJ']/10.],
   admitted_kg=sum(r['ledger'][k][-1] for k in ['in_N2','in_O2','in_Ar']),
   capture=r['margins'].get('full_capture'),
   rack_kg=[g['mass_kg'] for g in r['hardware']['geometry']],receiver_m3=r['hardware']['geometry'][4]['gas_m3'])
  if np.allclose(x,0,rtol=0,atol=0):write_trajectory(folder/'seed.json',r)
  if r['feasible']:write_trajectory(folder/f'trajectory_{key}.json',r)
 except Exception as e:row=dict(x=list(x),error=repr(e),seconds=time.monotonic()-started)
 finally:signal.alarm(0)
 path.write_text(json.dumps(row,indent=2)+'\n');return row

def isolated(task):
 base,x,folder=task
 key=hashlib.sha256(json.dumps(x).encode()).hexdigest()
 path=Path(folder)/f'task_{key}.json';path.write_text(json.dumps(task))
 process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker-task',str(path)],capture_output=True,text=True)
 if process.returncode:raise RuntimeError(process.stderr[-2000:])
 return json.loads(process.stdout)

def main():
 p=argparse.ArgumentParser();p.add_argument('--factor',type=float,required=True);p.add_argument('--restore',action='store_true');a=p.parse_args()
 folder=ROOT/f'results/transient/pressure_continuation/p{round(a.factor*100):03}'
 folder.mkdir(parents=True,exist_ok=True);base=seed(a.factor)
 manifest=dict(pressure_factor=a.factor,base=base,model_sha256=hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+p.read_bytes() for p in sorted((ROOT/'atmo_scoops').rglob('*.py')))).hexdigest())
 mp=folder/'manifest.json'
 if mp.exists() and json.loads(mp.read_text())!=manifest:raise RuntimeError('Changed source or input; choose a fresh output directory')
 mp.write_text(json.dumps(manifest,indent=2)+'\n')
 rows=[];cache={}
 def accept(r):
  if 'error' in r:raise RuntimeError(r['error'])
  cache[tuple(r['x'])]=r;rows.append(r)
  (folder/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(json.dumps({k:r[k] for k in ['x','seconds','feasible','diagnostic_days','residual','failed']}),flush=True)
  return r
 def get(x):
  key=tuple(float(v) for v in x)
  return cache[key] if key in cache else accept(evaluate((base,list(key),str(folder))))
 initial=get(np.zeros(3));(folder/'seed_summary.json').write_text(json.dumps(initial,indent=2)+'\n')
 if not a.restore:return
 with ThreadPoolExecutor(max_workers=3) as pool:
  def jac(x):
   f=np.array(get(x)['residual']);steps=np.array([.002,.0002,.0002])
   points=[x+np.eye(3)[i]*steps[i] for i in range(3)]
   for r in pool.map(isolated,[(base,z.tolist(),str(folder)) for z in points]):
    if tuple(r['x']) not in cache:accept(r)
   return np.array([(np.array(get(z)['residual'])-f)/step for z,step in zip(points,steps)]).T
  sol=least_squares(lambda x:np.array(get(x)['residual']),np.zeros(3),jac=jac,
   bounds=([-1.,-.5,-.5],[1.,.5,.5]),max_nfev=4,ftol=1e-6,xtol=1e-6,gtol=1e-6)
  selected=get(sol.x)
  (folder/'selected_summary.json').write_text(json.dumps(selected,indent=2)+'\n')
  (folder/'selected_config.json').write_text(json.dumps(selected['inputs'],indent=2)+'\n')
  (folder/'termination.json').write_text(json.dumps(dict(success=bool(sol.success),message=sol.message,nfev=int(sol.nfev),cycle_evaluations=len(rows),feasible=selected['feasible']),indent=2)+'\n')
if __name__=='__main__':
 if '--worker-task' in sys.argv:
  task=json.loads(Path(sys.argv[sys.argv.index('--worker-task')+1]).read_text())
  print(json.dumps(evaluate(task)))
 else:main()
