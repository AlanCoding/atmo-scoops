"""Small, gated coordinate searches. One forward cycle per declared candidate."""
import argparse,copy,json,multiprocessing,signal,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from .cycle import simulate
from .search import summary
from .io import write_trajectory
from .hardware import compile_hardware
from .inputs import read_config

ROOT=Path('results/transient/staged')

def evaluate(task):
    name,config,folder,*budget=task;seconds=budget[0] if budget else 300;t=time.monotonic()
    def expired(*_):raise TimeoutError(f'Forward evaluation exceeded {seconds} s; unresolved, not a physical rejection')
    signal.signal(signal.SIGALRM,expired);signal.alarm(seconds)
    try:
        r=simulate(config,samples=101)
        path=write_trajectory(Path(folder)/(name+'.json'),r)
        return dict(name=name,seconds=time.monotonic()-t,trajectory=str(path),**summary(r))
    except (ValueError,RuntimeError,TimeoutError) as exc:
        return dict(name=name,inputs=config,seconds=time.monotonic()-t,error=str(exc),feasible=False)
    finally:signal.alarm(0)

def batch(cases,folder,workers=4,seconds=300):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    rows=json.loads((folder/'evaluations.json').read_text()) if (folder/'evaluations.json').exists() else []
    byname={r['name']:r for r in rows};todo=[]
    for name,c in cases.items():
        c=json.loads(json.dumps(c))
        cp=folder/(name+'.inputs.json')
        if cp.exists() and json.loads(cp.read_text())!=c:raise ValueError(f'Changed candidate {name}; use a new folder')
        cp.write_text(json.dumps(c,indent=2)+'\n')
        if name not in byname:todo.append((name,c,str(folder),seconds))
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for f in as_completed([pool.submit(evaluate,t) for t in todo]):
            r=f.result();rows.append(r);byname[r['name']]=r
            (folder/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n')
            print(json.dumps({k:r.get(k) for k in ['name','seconds','feasible','operating_payoff_days','error']}),flush=True)
    return [byname[name] for name in cases]

def resolution(config):
    c=copy.deepcopy(config);d=c['design'];d.update(max_step_s=d.get('max_step_s',10.)/2,rtol=d.get('rtol',2e-5)/2,atol=d.get('atol',1e-7)/10)
    return c

def numerical_gate(rows,require_feasible=True):
    """Never confuse physical infeasibility with a converged numerical solution."""
    complete=len(rows)==2 and all('audits' in r and not r.get('error') for r in rows)
    checks={'two_complete_trajectories':complete}
    if complete:
        checks['conservation_and_nonnegative_inventory']=all(r['audits']['species_kg']<1e-4 and r['audits']['energy_MJ']<.01 and r['audits']['min_gas_kg']>-.0001 for r in rows)
        changes={k:abs(rows[1][k]-rows[0][k])/max(abs(rows[0][k]),1.) for k in ('net_liquid_kg','admitted_kg','lost_kg','propellant_kg')}
        checks['resolution_within_half_percent']=max(changes.values())<.005
        if require_feasible:checks['two_feasible_cycles']=all(r['feasible'] for r in rows)
    else:changes={}
    return dict(passed=all(checks.values()),checks=checks,relative_changes=changes)

def reboost_proposals(base,isps=(1500.,2100.,2600.)):
    """Declared correlated search directions, sized BEFORE the forward solve."""
    ref=compile_hardware(*read_config(base));out={}
    for isp in isps:
        c=copy.deepcopy(base);d=c['design'];d['isp_s']=isp
        h=compile_hardware(*read_config(c));power=h['thrust_W']/ref['thrust_W']
        energy=power*d['burn_s']/base['design']['burn_s']
        for k in ('solar_area_m2','battery_MWh','warm_store_kg','warm_radiator_m2'):d[k]*=energy
        for k in ('battery_MW','bus_MW'):d[k]*=power
        # Preserve the propellant reserve/required-burn ratio, not future capture.
        reserve_ratio=h['required_impulse_Ns']/ref['required_impulse_Ns']*base['design']['isp_s']/isp
        d['gas_reserve_kg']*=reserve_ratio;d['gas_volume_m3']*=reserve_ratio
        out[f'isp_{isp:g}']=c
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--action',choices=['baseline','optimize','verify','reboost'],required=True);p.add_argument('--config',type=Path,default=Path('configs/transient_gas_reduced_plant.json'));p.add_argument('--output',type=Path,default=ROOT/'bypass');p.add_argument('--workers',type=int,default=4);p.add_argument('--rounds',type=int,default=2);p.add_argument('--isps',nargs='+',type=float,default=[1500.,2100.,2600.]);p.add_argument('--seconds',type=int,default=300);p.add_argument('--initial-step',type=float,default=.12);a=p.parse_args()
    if not 0<a.initial_step<1:p.error('--initial-step must lie between zero and one')
    base=json.loads(a.config.read_text())
    if a.action=='reboost':
        batch(reboost_proposals(base,a.isps),a.output,a.workers,a.seconds);return
    if a.action=='baseline':
        rows=batch({'baseline':base,'baseline_refined':resolution(base)},a.output,a.workers,a.seconds)
        (a.output/'gate.json').write_text(json.dumps(numerical_gate(rows),indent=2)+'\n');return
    if a.action=='verify':
        rows=batch({'check':base,'check_refined':resolution(base)},a.output,a.workers,a.seconds)
        (a.output/'gate.json').write_text(json.dumps(numerical_gate(rows),indent=2)+'\n');return
    # Independent installed capacities and controls; geometry is fixed here.
    bounds=dict(isp_s=(1200.,5000.),burn_s=(800.,1800.),solar_area_m2=(1e6,5e6),battery_MWh=(180.,800.),battery_MW=(450.,2000.),bus_MW=(450.,2000.),warm_store_kg=(200000.,1000000.),warm_radiator_m2=(20000.,100000.),plant_flow_kg_s=(.5,4.),plant_electric_MW=(5.,40.))
    a.output.mkdir(parents=True,exist_ok=True)
    manifest=dict(base=base,bounds=bounds,algorithm='feasible coordinate poll, fixed geometry',rounds=a.rounds)
    if a.initial_step!=.12:manifest['initial_step']=a.initial_step
    mp=a.output/'search.json'
    if mp.exists() and json.loads(mp.read_text())!=json.loads(json.dumps(manifest)):raise ValueError('Changed search manifest')
    mp.write_text(json.dumps(manifest,indent=2)+'\n')
    center=copy.deepcopy(base);best=batch({'seed':center},a.output,a.workers,a.seconds)[0]
    if not best['feasible']:raise RuntimeError('Seed is not feasible; validate the stage before optimizing')
    for round_id in range(a.rounds):
        step=a.initial_step/(2**round_id);cases={}
        for key,(lo,hi) in bounds.items():
            for sign in (-1,1):
                c=copy.deepcopy(center);c['design'][key]=min(hi,max(lo,c['design'][key]*(1+sign*step)))
                cases[f'r{round_id}_{key}_{sign}']=c
        rows=batch(cases,a.output,a.workers,a.seconds)
        # Test the combined individually favorable directions as a NEW forward
        # candidate. Individual feasibility does not imply joint feasibility.
        combined=copy.deepcopy(center)
        for key in bounds:
            improving=[r for r in rows if r['name'].startswith(f'r{round_id}_{key}_') and r['feasible'] and r['operating_payoff_days']<best['operating_payoff_days']]
            if improving:combined['design'][key]=min(improving,key=lambda r:r['operating_payoff_days'])['inputs']['design'][key]
        if combined!=center:
            rows+=batch({f'r{round_id}_combined':combined},a.output,a.workers,a.seconds)
        accepted=[r for r in rows if r['feasible']]+[best]
        new=min(accepted,key=lambda r:r['operating_payoff_days'])
        if new['operating_payoff_days']<best['operating_payoff_days']:
            best=new;center=copy.deepcopy(new['inputs'])
        (a.output/'best_config.json').write_text(json.dumps(center,indent=2)+'\n')
        (a.output/'best_summary.json').write_text(json.dumps(best,indent=2)+'\n')
    (a.output/'done.json').write_text(json.dumps(dict(best=best['name'],payoff_days=best['operating_payoff_days']),indent=2)+'\n')
if __name__=='__main__':main()
