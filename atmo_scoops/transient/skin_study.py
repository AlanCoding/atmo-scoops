"""Frozen-hardware and explicit capacity-proposal skin-impulse sensitivity.

No drag coefficient is presented as a validated prediction. Each trajectory
compiles once; power capacity proposals are made before any integration.
"""
import argparse,copy,json,multiprocessing
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from .search import run_case


def main():
    p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=2);a=p.parse_args()
    base=json.loads(Path('results/transient/best_config.json').read_text())
    folder=Path('results/transient/skin_friction');folder.mkdir(parents=True,exist_ok=True)
    cases=[];labels=[]
    for cf,resize in ((.002,False),(.001,True),(.002,True),(.005,True)):
        x=copy.deepcopy(base);d=x['design'];x['capabilities']['skin_friction_coefficient']=cf
        multiplier=1+cf*2*(d['bore_m']+2*d['clearance_m'])**2*d['length_diameter']/d['bore_m']**2
        if resize:
            for k in ('solar_area_m2','battery_MWh','battery_MW','bus_MW','warm_store_kg','warm_radiator_m2'):d[k]*=multiplier
        cases.append(x);labels.append(dict(coefficient=cf,capacity_proposal=resize,impulse_multiplier=multiplier))
    (folder/'proposals.json').write_text(json.dumps(dict(cases=cases,labels=labels),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        for r,label in zip(pool.map(run_case,[(i,x,str(folder)) for i,x in enumerate(cases)]),labels):
            rows.append(dict(**r,**label));(folder/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
            print(json.dumps({k:rows[-1].get(k) for k in ('case','coefficient','capacity_proposal','feasible','operating_payoff_days','error')}),flush=True)

if __name__=='__main__':main()
