"""Independent tighter replay of a selected pressure-continuation candidate."""
from pathlib import Path
import json,signal,time
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.io import write_trajectory
from atmo_scoops.transient.plate_optimize import constraint_vector
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'results/transient/pressure_continuation/p105'
c=json.loads((out/'candidate_config.json').read_text());d=c['design']
d['rtol']/=2;d['max_step_s']/=2
(out/'replay_config.json').write_text(json.dumps(c,indent=2)+'\n')
def timeout(*args):raise TimeoutError('600-second tighter replay budget')
signal.signal(signal.SIGALRM,timeout);signal.alarm(600);started=time.monotonic()
r=simulate(c,samples=1501);signal.alarm(0);names,v=constraint_vector(r)
write_trajectory(out/'replay.json',r)
row=dict(seconds=time.monotonic()-started,feasible=r['feasible'],days=r['operating_payoff_days'],diagnostic_days=r['diagnostic_payoff_days'],dry_kg=r['dry_kg'],liquid_kg=r['net_liquid_kg'],closure=r['closure'],margins=r['margins'],audits=r['audits'],failed={n:float(x) for n,x in zip(names,v) if x < -1e-7})
(out/'replay_summary.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row))
