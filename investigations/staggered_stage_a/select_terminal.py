"""Select COBYLA's actual terminal point, not an unused cached probe."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('folder', type=Path)
a = p.parse_args()
done = json.loads((a.folder / 'termination.json').read_text())
if not done.get('success'):
    raise SystemExit('Optimizer did not converge; no checkpoint selected.')
rows = json.loads((a.folder / 'evaluations.json').read_text())
row = next(r for r in rows if r['x'] == done['x'])
if not row['feasible'] or row.get('error'):
    raise SystemExit('Terminal point is not feasible; no checkpoint selected.')
for name, value in [('selected_config', row['inputs']), ('selected_summary', row)]:
    (a.folder / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
print(json.dumps(dict(index=row['index'], payoff_days=row['operating_payoff_days'],
                     nfev=done['nfev'], maxcv=done['maxcv'])))
