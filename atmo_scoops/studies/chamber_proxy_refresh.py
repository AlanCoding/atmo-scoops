"""Recompute saved proxy ledgers without changing the dynamic trajectories."""
from pathlib import Path
import json
from ..chambers.proxy import evaluate
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'results/chamber_optimization'
def main():
 settings=json.loads((D/'settings.json').read_text());a=json.loads((ROOT/settings['anchor']).read_text());ref=settings['reference_shaft_MJ'];rows=json.loads((D/'search.json').read_text())
 for row in rows:
  f=D/f"candidate_{row['id']:04d}.json"
  if f.exists() and row['feasible']:
   p=evaluate(json.loads(f.read_text()),a,ref);row.update(p);row['score']=p['proxy_days'] if p['feasible'] else 1e5
 (D/'search.json').write_text(json.dumps(rows,indent=2)+'\n')
 best=min((r for r in rows if r['feasible']),key=lambda r:r['proxy_days']);previous=json.loads((D/'best_search.json').read_text());assert best['id']==previous['id'],'Updated proxy changes selection; rerun refinement'
 (D/'best_search.json').write_text(json.dumps(best,indent=2)+'\n')
 for name in ('baseline','baseline_refined','best'):
  p=evaluate(json.loads((D/f'{name}.json').read_text()),a,ref);(D/f'{name}_proxy.json').write_text(json.dumps(p,indent=2)+'\n');print(name,p['proxy_days'],'motor kg',p['motor_uprating_kg'],flush=True)
 v=json.loads((D/'verification.json').read_text());v['proxy']=evaluate(json.loads((D/'best_verified.json').read_text()),a,ref)
 for r in v['retried']:
  if 'error' not in r:r.update(evaluate(json.loads((D/f"retry_{r['id']}.json").read_text()),a,ref))
 (D/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
if __name__=='__main__':main()
