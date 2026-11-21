"""SciPy COBYLA with explicit forward-cycle nonlinear constraints.

Every objective/constraint pair shares ONE cached cycle. Numerical failures stop
optimization rather than masquerading as physical rejection or objective noise.
"""
import argparse,copy,json,math,signal,time,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,Bounds
from .cycle import simulate
from .search import summary
from .io import write_trajectory

SCALES=dict(reserve_kg=100.,material_K=100.,pressure_Pa=1000.,warm_K=100.,SOC=.1,liquid_kg=100.,tank_m3=10.,Bi=.1,gas_K=1000.,unmet_MJ=1.,product_kg=1000.,gas_buffer_Pa=1e6,gas_buffer_K=100.,gas_buffer_inventory_kg=100.,plate_Re=1000.)


def specs(base,thickness=True):
    d=base['design'];s=[]
    def add(key,lo,hi):s.append(dict(key=key,low=lo,high=hi))
    thermal=d.get('plate_thermal_model')=='offset_equivalent'
    for i in range(5):add(f"{'thermal_gap_m' if thermal else 'plate_gap_m'}:{i}",.0005,.03 if thermal else .12 if max(d.get('plate_rows',[1]))>1 else .03)
    if thickness:
        for i in range(5):add(f'plate_thickness_m:{i}',.0002,.005)
    for i in range(5):
        v=d['rack_depth_m'][i]*d['plate_thickness_m'][i]/(d['plate_thickness_m'][i]+d['plate_gap_m'][i])
        add(f'solid_depth:{i}',v*.5,v*2.)
    for i in range(5):add(f'rack_initial_K:{i}',300.,400.)
    for k in ('solar_area_m2','battery_MWh','warm_store_kg','warm_radiator_m2','plant_flow_kg_s','plant_electric_MW'):
        add(k,d[k]*.75,d[k]*1.5)
    for i in range(4):add(f'motor_MW:{i}',d['motor_MW'][i]*.6,d['motor_MW'][i]*1.6)
    add('coast_motor_MW',d['coast_motor_MW']*.6,d['coast_motor_MW']*1.6)
    add('isp_s',1200.,3000.);add('burn_s',800.,2000.)
    return s


def encode(c,spec):
    d=c['design'];out=[]
    for s in spec:
        k=s['key']
        if ':' in k:
            k,i=k.split(':');i=int(i)
            if k=='thermal_gap_m':v=(d['plate_gap_m'][i]+d['plate_thickness_m'][i])/d['plate_rows'][i]-d['plate_thickness_m'][i]
            else:v=d[k][i] if k!='solid_depth' else d['rack_depth_m'][i]*d['plate_thickness_m'][i]/(d['plate_thickness_m'][i]+d['plate_gap_m'][i])
        else:v=d[k]
        out.append(math.log(v/s['low'])/math.log(s['high']/s['low']))
    return np.array(out)


def decode(x,base,spec):
    c=copy.deepcopy(base);d=c['design'];solid=[z*t/(t+g) for z,t,g in zip(d['rack_depth_m'],d['plate_thickness_m'],d['plate_gap_m'])]
    thermal=[(g+t)/n-t for g,t,n in zip(d['plate_gap_m'],d['plate_thickness_m'],d.get('plate_rows',[1]*5))]
    for u,s in zip(x,spec):
        v=s['low']*math.exp(float(u)*math.log(s['high']/s['low']));k=s['key']
        if ':' in k:
            k,i=k.split(':');i=int(i)
            if k=='thermal_gap_m':thermal[i]=v
            elif k=='solid_depth':solid[i]=v
            else:d[k][i]=v
        else:d[k]=v
    if d.get('plate_thermal_model')=='offset_equivalent':
        d['plate_gap_m']=[n*(g+t)-t for n,g,t in zip(d['plate_rows'],thermal,d['plate_thickness_m'])]
    d['rack_depth_m']=[v*(t+g)/t for v,t,g in zip(solid,d['plate_thickness_m'],d['plate_gap_m'])]
    return c


def constraint_vector(r):
    # Signed constraints, individually visible; no aggregate penalty objective.
    names=[];v=[]
    for k in sorted(r['margins']):
        if k=='periodic':continue
        names.append(k);v.append(r['margins'][k]/SCALES.get(k,1.))
    limits=dict(rack_enthalpy_J_kg=500.,battery_MJ=100.,warm_MJ=100.,gas_kg=.1,gas_MJ=.01,rotor_MJ=.01,thrust_relative=1e-4,gas_reserve_species_kg=.1,gas_reserve_MJ=1.)
    for k,lim in limits.items():
        for j,z in enumerate(np.atleast_1d(r['closure'][k])):
            names.extend([f'{k}:{j}:upper',f'{k}:{j}:lower']);v.extend([1-z/lim,1+z/lim])
    for key,lim in [('species_kg',1e-4),('energy_MJ',.01)]:names.append('audit:'+key);v.append(1-r['audits'][key]/lim)
    names.append('audit:inventory');v.append(1+r['audits']['min_gas_kg']/.0001)
    # Existing feasibility covers hatch and real-gas audit as well. Keep their
    # discrete validity guard explicit, never silently discard it.
    unexplained=not r['feasible'] and min(v)>=-1e-6 and all(z>=-1e-6 for z in r['margins'].values())
    names.append('other_validity');v.append(-1. if unexplained else 1.)
    return names,np.array(v)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--fixed-thickness',action='store_true');p.add_argument('--maxiter',type=int,default=300);p.add_argument('--tol',type=float,default=.01);p.add_argument('--rhobeg',type=float,default=.03);p.add_argument('--seconds',type=int,default=300);a=p.parse_args()
    base=json.loads(a.config.read_text());spec=specs(base,not a.fixed_thickness);a.output.mkdir(parents=True,exist_ok=True)
    manifest=dict(base=base,coordinates=spec,algorithm='scipy.optimize.minimize COBYLA',options=dict(maxiter=a.maxiter,tol=a.tol,rhobeg=a.rhobeg,catol=1e-7),seconds=a.seconds)
    if max(base['design'].get('plate_rows',[1]))>1:
        sources=[Path(__file__).with_name(name) for name in ('plate_optimize.py','plates.py','hardware.py','inputs.py','cycle.py','thermo.py','porous.py')]
        manifest['implementation_sha256']=hashlib.sha256(b''.join(p.read_bytes() for p in sources)).hexdigest()
    mp=a.output/'search.json'
    if mp.exists() and json.loads(mp.read_text())!=manifest:raise ValueError('Changed search manifest')
    mp.write_text(json.dumps(manifest,indent=2)+'\n');ep=a.output/'evaluations.json'
    rows=json.loads(ep.read_text()) if ep.exists() else [];cache={tuple(r['x']):r for r in rows};best=None
    for r in rows:
        if r.get('feasible') and (best is None or r['operating_payoff_days']<best['operating_payoff_days']):best=r
    def evaluate(x):
        nonlocal best
        key=tuple(float(z) for z in x)
        if key in cache:
            if cache[key].get('error'):raise RuntimeError('Previously unresolved forward solve; see evaluation log')
            return cache[key]
        config=decode(x,base,spec);start=time.monotonic()
        def expired(*_):raise TimeoutError('Forward wall-time budget exhausted')
        signal.signal(signal.SIGALRM,expired);signal.alarm(a.seconds)
        try:
            result=simulate(config,samples=101);names,cv=constraint_vector(result)
            row=dict(x=list(key),index=len(rows),seconds=time.monotonic()-start,constraint_names=names,constraints=cv.tolist(),**summary(result))
            if result['diagnostic_payoff_days'] is None:raise RuntimeError('No positive product; objective undefined')
            if row['feasible'] and (best is None or row['operating_payoff_days']<best['operating_payoff_days']):
                best=row;write_trajectory(a.output/'best.json',result)
                (a.output/'best_config.json').write_text(json.dumps(result['inputs'],indent=2)+'\n')
                (a.output/'best_summary.json').write_text(json.dumps(row,indent=2)+'\n')
        except (RuntimeError,ValueError,TimeoutError,FloatingPointError) as exc:
            row=dict(x=list(key),inputs=config,index=len(rows),seconds=time.monotonic()-start,error=str(exc),feasible=False)
        finally:signal.alarm(0)
        rows.append(row);cache[key]=row;ep.write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps({k:row.get(k) for k in ('index','seconds','feasible','diagnostic_payoff_days','error')}),flush=True)
        if row.get('error'):raise RuntimeError(row['error'])
        return row
    try:
        result=minimize(lambda x:evaluate(x)['diagnostic_payoff_days']/300.,encode(base,spec),method='COBYLA',bounds=Bounds(np.zeros(len(spec)),np.ones(len(spec))),constraints=[dict(type='ineq',fun=lambda x:np.array(evaluate(x)['constraints']))],options=manifest['options'])
        done=dict(success=bool(result.success),status=int(result.status),message=str(result.message),nfev=int(result.nfev),maxcv=float(result.maxcv),x=result.x.tolist(),objective_days=float(result.fun*300),best_feasible_days=best['operating_payoff_days'] if best else None)
    except RuntimeError as exc:
        done=dict(success=False,termination='unresolved forward evaluation; optimizer stopped',error=str(exc),evaluations=len(rows),best_feasible_days=best['operating_payoff_days'] if best else None)
    (a.output/'termination.json').write_text(json.dumps(done,indent=2)+'\n');print(json.dumps(done),flush=True)

if __name__=='__main__':main()
