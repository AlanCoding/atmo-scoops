"""Repeatable resolution and optional-LN2 conservation experiments."""
import argparse,copy,json
from pathlib import Path
from .cycle import simulate
from .search import summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',nargs='+',choices=['reference','best','mixing'],default=['reference','best','mixing']);a=p.parse_args()
    root=Path('results/transient')
    for name in a.cases:
        baseline=json.loads((root/('reference.json' if name=='reference' else 'best.json')).read_text())
        config=copy.deepcopy(baseline['inputs']);config['design'].update(max_step_s=5.,rtol=1e-5);config['capabilities']['vacuum_regularization_kg']=.0005
        if name=='mixing':config['design']['mixing_ratio']=.02
        r=simulate(config,samples=401 if name!='mixing' else 301);row=summary(r);row['thermodynamic_audit']=r['thermodynamic_audit']
        if name=='mixing':row['injected_N2_kg']=r['ledger']['mix_kg'][-1];filename='mixing_check.json'
        else:
            row['relative_net_liquid_change']=r['net_liquid_kg']/baseline['net_liquid_kg']-1
            row['relative_payoff_change']=r['diagnostic_payoff_days']/baseline['diagnostic_payoff_days']-1
            filename='resolution.json' if name=='reference' else 'best_resolution.json'
        (root/filename).write_text(json.dumps(row,indent=2)+'\n')
        print(name,row['feasible'],row['operating_payoff_days'],flush=True)
        if not row['feasible']:raise RuntimeError(f'{name}: closure/constraint verification failed; inspect {filename}')

if __name__=='__main__':main()
