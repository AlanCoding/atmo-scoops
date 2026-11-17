"""Refine selected layout and retry two timed-out front-depth trials."""
import json,signal,copy
from pathlib import Path
from ..chambers.__main__ import run
from ..chambers.proxy import evaluate
from .chamber_optimize import build
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/chamber_optimization'
def main():
 settings=json.loads((DEST/'settings.json').read_text());anchor=json.loads((ROOT/settings['anchor']).read_text());ref=settings['reference_shaft_MJ']
 rows=json.loads((DEST/'search.json').read_text());config=json.loads((ROOT/'configs/chamber_transient_optimized.json').read_text());best=json.loads((DEST/'best.json').read_text())
 config['schedule'].update(max_step_s=1.,rtol=5e-7);r=run(config);p=evaluate(r,anchor,ref)
 assert p['feasible'];assert r['checks']['max_mass_residual_kg']<1e-5 and r['checks']['max_energy_residual_MJ']<1e-4
 (DEST/'best_verified.json').write_text(json.dumps(r)+'\n')
 checks=dict(proxy=p,relative_final_receiver_mass_change=r['gas_mass_kg'][-1][-1]/best['gas_mass_kg'][-1][-1]-1,final_receiver_temperature_change_K=r['gas_temperature_K'][-1][-1]-best['gas_temperature_K'][-1][-1],retried=[])
 def timeout(sig,frame):raise RuntimeError('Refined retry numerical timeout (90 s)')
 signal.signal(signal.SIGALRM,timeout)
 for idx in (3,67):
  row=next(x for x in rows if x['id']==idx);cfg=build(row['x'],settings['base_config']);cfg['schedule'].update(max_step_s=2.,rtol=2e-6);cfg['samples']=1801
  signal.alarm(90)
  try:
   rr=run(cfg);pp=evaluate(rr,anchor,ref);(DEST/f'retry_{idx}.json').write_text(json.dumps(rr)+'\n');checks['retried'].append(dict(id=idx,**pp));print('retry',idx,pp['proxy_days'],pp['feasible'],flush=True)
  except RuntimeError as e:checks['retried'].append(dict(id=idx,error=str(e)));print('retry',idx,str(e),flush=True)
  finally:signal.alarm(0)
 (DEST/'verification.json').write_text(json.dumps(checks,indent=2)+'\n');print('selected refined',checks['relative_final_receiver_mass_change'],checks['final_receiver_temperature_change_K'],flush=True)
if __name__=='__main__':main()
