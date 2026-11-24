"""Small reproducibility/response probe, not an optimizer or replacement design."""
from pathlib import Path
import json,time,hashlib,argparse,signal
from atmo_scoops.transient.reduced_coordinates import rack_allocation,with_total_rack_mass
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.io import read_result,write_trajectory
from atmo_scoops.transient.plate_optimize import constraint_vector
ROOT=Path(__file__).resolve().parents[2]

def main():
 p=argparse.ArgumentParser();p.add_argument('--factor',type=float,default=1);a=p.parse_args()
 base=json.loads((ROOT/'results/transient/valve_restore/selected_refined_config.json').read_text())
 saved=read_result(ROOT/'results/transient/valve_restore/selected_refined.json.gz')
 allocation=rack_allocation(base);config=with_total_rack_mass(base,allocation['total_kg']*a.factor)
 out=ROOT/'results/transient/reduced_coordinates';out.mkdir(parents=True,exist_ok=True)
 label={1.:'baseline',.99:'rack_minus_1pct',1.01:'rack_plus_1pct'}[a.factor]
 provenance=dict(reference_sha256=hashlib.sha256((ROOT/'results/transient/valve_restore/selected_refined.json.gz').read_bytes()).hexdigest(),model_sha256=hashlib.sha256(b''.join(p.relative_to(ROOT).as_posix().encode()+p.read_bytes() for p in sorted((ROOT/'atmo_scoops').rglob('*.py')))).hexdigest())
 (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 (out/f'{label}_config.json').write_text(json.dumps(config,indent=2)+'\n')
 t=time.monotonic()
 def timeout(*args):raise TimeoutError('600-second evaluation budget; unresolved, not physically infeasible')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(600)
 try:
  r=simulate(config,samples=1001);signal.alarm(0)
  names,values=constraint_vector(r)
  row=dict(label=label,factor=a.factor,seconds=time.monotonic()-t,allocation=allocation,
   dry_kg=r['dry_kg'],net_liquid_kg=r['net_liquid_kg'],feasible=r['feasible'],
   diagnostic_payoff_days=r['diagnostic_payoff_days'],operating_payoff_days=r['operating_payoff_days'],
   closure=r['closure'],audits=r['audits'],margins=r['margins'],
   failed_constraints={n:float(v) for n,v in zip(names,values) if v<0},
   rack_kg=[g['mass_kg'] for g in r['hardware']['geometry']],
   rack_depth_m=[g['rack_depth_m'] for g in r['hardware']['geometry']],
   receiver_m3=r['hardware']['geometry'][4]['gas_m3'],
   baseline_difference=dict(dry_kg=r['dry_kg']-saved['dry_kg'],liquid_kg=r['net_liquid_kg']-saved['net_liquid_kg'],days=r['diagnostic_payoff_days']-saved['diagnostic_payoff_days']),
   input_sha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest())
  write_trajectory(out/f'{label}.json',r)
 except Exception as e:
  row=dict(label=label,error=repr(e),seconds=time.monotonic()-t)
 finally:signal.alarm(0)
 (out/f'{label}_summary.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if 'error' in row:raise SystemExit(1)
 if a.factor==1 and (not row['feasible'] or abs(row['baseline_difference']['days'])>.01):raise SystemExit('Baseline reproduction gate failed')
if __name__=='__main__':main()
