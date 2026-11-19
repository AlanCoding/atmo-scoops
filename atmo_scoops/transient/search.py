"""External constrained candidate search; each evaluation is one forward cycle.

The demonstration is a small propulsion/power co-design grid, not a global
optimization of the full input schema. No result resizes its own hardware.
"""
import argparse
import copy
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from .cycle import simulate
from .io import write_trajectory
from .inputs import read_config
from .hardware import compile_hardware


def summary(r):
    keys=['inputs','dry_kg','net_liquid_kg','diagnostic_payoff_days','operating_payoff_days','feasible','margins','closure','audits']
    s={k:r[k] for k in keys}
    if 'loss_power_audit' in r:s['loss_power_audit']=r['loss_power_audit']
    s['masses_kg']=r['hardware']['masses_kg']
    s['receiver_depth_m']=r['hardware']['geometry'][-1]['depth_m']
    s['gross_liquid_kg']=sum(r['ledger'][f'made_{k}'][-1] for k in ('N2','O2','Ar'))
    s['propellant_kg']=sum(r['ledger'][f'prop_{k}'][-1] for k in ('N2','O2','Ar'))
    s['admitted_kg']=sum(r['ledger'][f'in_{k}'][-1] for k in ('N2','O2','Ar'))
    s['lost_kg']=sum(r['ledger'][f'lost_{k}'][-1] for k in ('N2','O2','Ar'))
    return s


def run_case(item):
    index,config,folder=item
    try:
        r=simulate(config,samples=301)
        write_trajectory(Path(folder,f'cycle_{index}.json'),r)
        return dict(case=index,**summary(r))
    except (ValueError,RuntimeError) as exc:
        return dict(case=index,inputs=config,feasible=False,error=str(exc))


def proposals(config):
    """Declared search subset: installed powers/areas proposed BEFORE integration.

    Scale energy capacities with prescribed reboost work and peak capacities with
    its power. This is a search trajectory through independent inputs, not an
    assertion that all these capacities must be tied in the eventual optimizer.
    """
    reference=compile_hardware(*read_config(config));base=config['design']
    for isp in (1800.,2300.,2800.):
        for duration in (1000.,1400.):
            x=copy.deepcopy(config);d=x['design'];d.update(isp_s=isp,burn_s=duration)
            h=compile_hardware(*read_config(x))
            energy=h['thrust_W']*duration/(reference['thrust_W']*base['burn_s'])
            peak=h['thrust_W']/reference['thrust_W']
            d.update(battery_MWh=base['battery_MWh']*energy,
                     solar_area_m2=base['solar_area_m2']*energy,
                     warm_store_kg=base['warm_store_kg']*energy,
                     warm_radiator_m2=base['warm_radiator_m2']*energy,
                     bus_MW=100+900*peak,battery_MW=100+900*peak)
            # Recorded numerical setting for this stiff tail; physical inputs unchanged.
            if isp==2800. and duration==1400.:d["jacobian_relative_step"]=1e-4
            yield x


def sizing_proposals(config):
    """Small external feasibility search around the first repeatable cycle."""
    choices=[dict(solar_area_m2=1.85e6,battery_MWh=340.,battery_initial_soc=.95,
                  bus_MW=900.,battery_MW=900.,warm_store_kg=450000.),
             dict(solar_area_m2=1.95e6,battery_MWh=360.,battery_initial_soc=.95,
                  bus_MW=900.,battery_MW=900.,warm_store_kg=500000.),
             dict(solar_area_m2=1.85e6,battery_MWh=340.,battery_initial_soc=.95,
                  bus_MW=900.,battery_MW=900.,warm_store_kg=450000.,
                  rack_initial_K=[300.]*5)]
    for choice in choices:
        x=copy.deepcopy(config);x['design'].update(choice);yield x


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=Path('configs/transient_reference.json'))
    p.add_argument('--output',type=Path,default=Path('results/transient/search'));p.add_argument('--workers',type=int,default=2)
    p.add_argument('--study',choices=['propulsion','sizing'],default='propulsion')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    candidates=list((proposals if a.study=='propulsion' else sizing_proposals)(json.loads(a.config.read_text())))
    (a.output/'proposals.json').write_text(json.dumps(candidates,indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context("fork")) as pool:
        for row in pool.map(run_case,[(i,x,str(a.output)) for i,x in enumerate(candidates)]):
            rows.append(row);print(json.dumps({k:row.get(k) for k in ['case','feasible','operating_payoff_days','error']}),flush=True)
            (a.output/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
    feasible=[r for r in rows if r['feasible']]
    if feasible:
        best=min(feasible,key=lambda r:r['operating_payoff_days'])
        (a.output/'best_config.json').write_text(json.dumps(best['inputs'],indent=2)+'\n')
        print(f"Best tested case {best['case']}: {best['operating_payoff_days']:.2f} days")

if __name__=='__main__':main()
