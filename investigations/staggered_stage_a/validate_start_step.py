"""Independent resolution check with an explicit BDF event-start step.

Only numerical initialization changes; equations, controls, tolerances and the
single-forward-cycle rule are untouched. The override is recorded in the result.
"""
import argparse
import json
from pathlib import Path

from scipy.integrate import solve_ivp
import atmo_scoops.transient.cycle as cycle
from atmo_scoops.transient.io import write_trajectory
from atmo_scoops.transient.search import summary
from atmo_scoops.transient.staged_search import resolution

p = argparse.ArgumentParser()
p.add_argument('--config', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--first-step-s', type=float, default=.001)
p.add_argument('--refine', action='store_true')
a = p.parse_args()
if a.first_step_s < 0:
    p.error('Initial step must be nonnegative (zero uses automatic selection)')
config = json.loads(a.config.read_text())
if a.refine:
    config = resolution(config)
segments = []

def integrate(fun, span, state, **kwargs):
    step = min(a.first_step_s, span[1] - span[0])
    segments.append(dict(start_s=float(span[0]), end_s=float(span[1]), first_step_s=step))
    if step:
        kwargs['first_step'] = step
    return solve_ivp(fun, span, state, **kwargs)

cycle.solve_ivp = integrate
r = cycle.simulate(config, samples=101)
r['numerical_validation'] = dict(first_step_s=a.first_step_s, refined=a.refine,
                                  segments=segments, source_config=str(a.config))
a.output.parent.mkdir(parents=True, exist_ok=True)
write_trajectory(a.output, r)
a.output.with_suffix('.summary.json').write_text(json.dumps(summary(r), indent=2) + '\n')
print(json.dumps(dict(feasible=r['feasible'], payoff_days=r['operating_payoff_days'],
                     audits=r['audits'], numerical_validation=r['numerical_validation'])))
