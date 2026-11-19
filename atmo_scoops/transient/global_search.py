"""Bounded differential evolution with feasibility-first selection.

Each trial compiles hardware and runs one forward cycle; no shooting, resizing,
or surrogate payoff. Numerical failures are explicitly unresolved candidates.
"""
import argparse,copy,json,math,multiprocessing,signal,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from .cycle import simulate,ConstraintViolation
from .search import summary
from .io import write_trajectory


def coordinates(base,pitch_max=2.,isp_max=3000.):
    d=base['design'];spec=[]
    def add(name,lo,hi,log=True):spec.append(dict(name=name,low=lo,high=hi,log=log))
    for i in range(5):add(f'radius:{i}',.0002,.01)
    for i in range(5):add(f'pitch_diameter:{i}',1.25,pitch_max,False)
    for i,z in enumerate([5.42,.4,.18,.2,.32]):add(f'solid_depth:{i}',z*math.pi*.01*.4,z*math.pi*.01*2.5)
    for i in range(4):add(f'clear_depth_m:{i}',0.,5.,False)
    for field in ['suction_m3_s','head_J_kg','motor_MW']:
        for i,v in enumerate(d[field]):add(f'{field}:{i}',v*.6,v*1.8)
    for field in ['solar_area_m2','battery_MWh','battery_MW','bus_MW','warm_radiator_m2','warm_store_kg']:add(field,d[field]*.7,d[field]*1.7)
    for field,lo,hi in [('coast_suction_m3_s',250,1500),('coast_head_J_kg',2.5e6,8e6),('coast_motor_MW',15,60),('plant_flow_kg_s',1,4),('plant_electric_MW',10,40),('isp_s',1200,3000),('burn_s',800,2000),('apogee_km',1800,6000),('gas_reserve_kg',3500,9000),('gas_volume_m3',300,1500),('cutoff_Pa',1,20),('pump_stop_s',120,600),('vent_duration_s',10,60)]:add(field,lo,hi)
    next(s for s in spec if s['name']=='isp_s')['high']=isp_max
    for i in range(5):add(f'rack_initial_K:{i}',300,400,False)
    return spec

def decode(x,base,spec):
    c=copy.deepcopy(base);d=c['design'];r=[0.]*5;a=[0.]*5;v=[0.]*5
    for u,s in zip(x,spec):
        lo,hi=s['low'],s['high'];value=math.exp(math.log(lo)+u*math.log(hi/lo)) if s['log'] else lo+u*(hi-lo)
        key=s['name']
        if ':' in key:
            key,j=key.split(':');j=int(j)
            if key=='radius':r[j]=value
            elif key=='pitch_diameter':a[j]=value
            elif key=='solid_depth':v[j]=value
            else:d[key][j]=value
        else:d[key]=value
    d['stage_radius_m']=r;d['stage_pitch_m']=[2*rr*aa for rr,aa in zip(r,a)]
    d['rack_depth_m']=[vv*4*aa*aa/math.pi for vv,aa in zip(v,a)]
    return c

def encode(c,spec):
    d=c['design'];x=[]
    for s in spec:
        key=s['name']
        if ':' in key:
            key,j=key.split(':');j=int(j)
            if key=='radius':v=d['stage_radius_m'][j]
            elif key=='pitch_diameter':v=d['stage_pitch_m'][j]/(2*d['stage_radius_m'][j])
            elif key=='solid_depth':v=d['rack_depth_m'][j]*math.pi*(d['stage_radius_m'][j]/d['stage_pitch_m'][j])**2
            else:v=d[key][j]
        else:v=d[key]
        x.append((math.log(v/s['low'])/math.log(s['high']/s['low'])) if s['log'] else (v-s['low'])/(s['high']-s['low']))
    return np.clip(x,0,1)

SCALES=dict(reserve_kg=100.,material_K=100.,pressure_Pa=1000.,warm_K=100.,SOC=.1,liquid_kg=1.,tank_m3=10.,Bi=.1,gas_K=1000.,unmet_MJ=1000.,product_kg=1000.,periodic=100.,gas_buffer_Pa=1e6,gas_buffer_K=100.,gas_buffer_inventory_kg=100.,rack_Mach=.1,rack_Re=75.,rack_rows=5.)

def evaluate(item):
    idx,x,base,spec,seconds=item;t=time.monotonic()
    def expired(*_):raise TimeoutError('Candidate wall-time budget exhausted; unresolved')
    signal.signal(signal.SIGALRM,expired);signal.alarm(seconds)
    try:
        config=decode(x,base,spec);r=simulate(config,samples=101)
        violation=sum(max(0.,-v)/SCALES.get(k,1.) for k,v in r['margins'].items())
        if not r['feasible'] and violation==0:violation=1.
        row=dict(case=idx,x=list(x),seconds=time.monotonic()-t,violation=violation,**summary(r))
        return row,r
    except ConstraintViolation as exc:
        return dict(case=idx,x=list(x),seconds=time.monotonic()-t,feasible=False,violation=1000.,error=str(exc),status='physical_path_rejection',inputs=decode(x,base,spec)),None
    except (ValueError,RuntimeError,TimeoutError,FloatingPointError) as exc:
        return dict(case=idx,x=list(x),seconds=time.monotonic()-t,feasible=False,violation=1e9,error=str(exc),inputs=decode(x,base,spec)),None
    finally:signal.alarm(0)

def rank(row):
    return (0,row['operating_payoff_days']) if row.get('feasible') else (1,row['violation'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=Path('configs/transient_low_re_search.json'));p.add_argument('--output',type=Path,default=Path('results/transient/global_racks'));p.add_argument('--population',type=int,default=16);p.add_argument('--generations',type=int,default=2);p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=int,default=240);p.add_argument('--seed',type=int,default=73);p.add_argument('--max-new',type=int,default=4);p.add_argument('--pitch-max',type=float,default=2.);p.add_argument('--isp-max',type=float,default=3000.);a=p.parse_args()
    base=json.loads(a.config.read_text());spec=coordinates(base,a.pitch_max,a.isp_max);rng=np.random.default_rng(a.seed);a.output.mkdir(parents=True,exist_ok=True)
    manifest=dict(base=base,coordinates=spec,algorithm='DE/rand/1/bin with feasibility-first selection',population=a.population,generations=a.generations,seed=a.seed,wall_budget_s=a.seconds)
    manifest_path=a.output/'search.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text())!=manifest:
        raise ValueError('Search manifest changed; use a new output directory rather than mixing cached evaluations')
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    center=encode(base,spec);pop=np.clip(center+rng.normal(0,.12,(a.population,len(spec))),0,1);pop[0]=center
    # Wide global initial proposals, plus radius-bound probes at fixed solid inventory.
    pop[-2:]=rng.random((2,len(spec)))
    pop[1,:5]=0.;pop[2,:5]=1.
    log=a.output/'evaluations.json'
    rows=json.loads(log.read_text()) if log.exists() else []
    def key(x):return json.dumps(list(x))
    cache={key(row['x']):row for row in rows};best=min(rows,key=rank) if rows else None
    parents=None;serial=0;remaining=a.max_new
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for gen in range(a.generations+1):
            if gen:
                trial=pop.copy()
                for i in range(a.population):
                    ids=rng.choice(np.delete(np.arange(a.population),i),3,replace=False);mut=np.clip(pop[ids[0]]+.6*(pop[ids[1]]-pop[ids[2]]),0,1);mask=rng.random(len(spec))<.65;mask[rng.integers(len(spec))]=True;trial[i,mask]=mut[mask]
            else:trial=pop.copy()
            missing=[(serial+i,x.tolist(),base,spec,a.seconds) for i,x in enumerate(trial) if key(x) not in cache]
            tasks=missing[:remaining]
            futures=[pool.submit(evaluate,task) for task in tasks]
            for future in as_completed(futures):
                row,r=future.result()
                remaining-=1;row['generation']=gen;rows.append(row);cache[key(row['x'])]=row
                if best is None or rank(row)<rank(best):
                    best=row
                    if r is not None:write_trajectory(a.output/'best.json',r);(a.output/'best_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
                log.write_text(json.dumps(rows,indent=2)+'\n')
                print(json.dumps({k:row.get(k) for k in ['case','generation','feasible','operating_payoff_days','violation','seconds','error']}),flush=True)
            if any(key(x) not in cache for x in trial):return
            current=[cache[key(x)] for x in trial]
            if parents is None:parents=current
            else:
                for i,row in enumerate(current):
                    if rank(row)<rank(parents[i]):parents[i]=row;pop[i]=trial[i]
            serial+=a.population
            (a.output/'population.json').write_text(json.dumps(dict(population=pop.tolist(),parents=parents),indent=2)+'\n')
    (a.output/'done.json').write_text(json.dumps(dict(best=best,evaluations=len(rows)),indent=2)+'\n')
    print('Best:',rank(best),flush=True)
if __name__=='__main__':main()
