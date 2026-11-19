"""Re-evaluate interrupted COBYLA vertices after a numerical implementation fix.

This is not a search: only previously requested coordinates are evaluated, in
parallel. COBYLA then replays these newly computed exact objective/constraint
values and resumes generating its own trial points. No old numerical results
are mixed into the new cache.
"""
import argparse,json,shutil
from pathlib import Path
from .staged_search import batch
from .plate_optimize import constraint_vector


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    src=json.loads((a.source/'evaluations.json').read_text());cases={f'vertex_{r["index"]}':r['inputs'] for r in src}
    fresh=batch(cases,a.output/'revalidated',a.workers,300)
    if any(r.get('error') for r in fresh):raise RuntimeError('Revalidation contains unresolved forward evaluations')
    rows=[]
    for old,new in zip(src,fresh):
        names,v=constraint_vector(new)
        rows.append(dict(index=old['index'],x=old['x'],constraint_names=names,constraints=v.tolist(),**new))
    a.output.mkdir(exist_ok=True);(a.output/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n')
    shutil.copyfile(a.source/'search.json',a.output/'search.json')
    good=[r for r in rows if r['feasible']]
    if good:
        best=min(good,key=lambda r:r['operating_payoff_days'])
        (a.output/'best_config.json').write_text(json.dumps(best['inputs'],indent=2)+'\n')
        (a.output/'best_summary.json').write_text(json.dumps(best,indent=2)+'\n')
        shutil.copyfile(best['trajectory'],a.output/'best.json.gz')
    (a.output/'revalidation.json').write_text(json.dumps(dict(source=str(a.source),vertices=len(rows),note='All numerical values recomputed after the dilute/pure-species HEOS fix; no old values reused'),indent=2)+'\n')

if __name__=='__main__':main()
