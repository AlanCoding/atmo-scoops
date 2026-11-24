"""One explicit Newton correction for a feasible optimization seed.

Uses already measured sensitivities; no inner cycle-to-cycle iteration.
The correction is verified by one new forward cycle and all existing constraints.
"""
from pathlib import Path
import json,shutil
import numpy as np
from investigations.reduced_optimization.run import evaluate,solver_jacobian,checked_bounds
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'results/transient/reduced_optimization/pressure_wide_refined'
out=ROOT/'results/transient/reduced_optimization/pressure_wide_closed'
out.mkdir(exist_ok=True)
m=json.loads((source/'manifest.json').read_text());rows=json.loads((source/'evaluations.json').read_text())
x=np.array(rows[0]['x']);f=np.array(rows[0]['eq']);steps=m['steps']
J=solver_jacobian([(np.array(r['eq'])-f)/h for r,h in zip(rows[1:6],steps)])
controls=[2,3,4];target=np.array([.2,0.,0.]);change=np.linalg.solve(J[:,controls],target-f)
new=x.copy();new[controls]+=change;checked_bounds(m['bounds'],new)
meta=dict(method='one measured-Jacobian Newton seed correction, then one-cycle verification',source=str(source.relative_to(ROOT)),before_x=x.tolist(),after_x=new.tolist(),before_scaled_residual=f.tolist(),target_scaled_residual=target.tolist(),closure_coordinates=[m['coordinates'][i] for i in controls],scaled_jacobian=J[:,controls].tolist(),condition=float(np.linalg.cond(J[:,controls])),bounds=m['bounds'])
(out/'seed_restoration.json').write_text(json.dumps(meta,indent=2)+'\n')
row=evaluate((m['base'],new.tolist(),str(out)))
(out/'seed_summary.json').write_text(json.dumps(row,indent=2)+'\n')
if 'error' in row:raise RuntimeError(row['error'])
(out/'seed_config.json').write_text(json.dumps(row['inputs'],indent=2)+'\n')
(out/'start_x.json').write_text(json.dumps(new.tolist())+'\n')
shutil.copyfile(out/f'trajectory_{row["key"]}.json.gz',out/'seed.json.gz')
print(json.dumps(dict(x=row['x'],days=row['days'],feasible=row['feasible'],scaled_residual=row['eq'],minimum_guarded_margin=min(row['ineq']))),flush=True)
if not row['feasible'] or min(row['ineq']) < -1e-6:raise SystemExit('Seed correction did not pass; do not claim a restored seed')
