"""Independent tighter acceptance gate for each incremental optimization stage."""
from pathlib import Path
import argparse,json,time,signal
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.io import write_trajectory
from atmo_scoops.transient.plate_optimize import constraint_vector

def propellant_inventory_metrics(result):
 totals=[sum(species) for species in result['gas_reserve_species_kg']]
 index=min(range(len(totals)),key=totals.__getitem__)
 return dict(minimum_reserve_total_kg=totals[index],minimum_reserve_time_s=result['time_s'][index])

def main():
 p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();out=a.folder
 termination=json.loads((out/'termination.json').read_text())
 if not termination['success']:raise RuntimeError('Optimization did not terminate successfully')
 c=json.loads((out/'selected_config.json').read_text());c['design'].update(rtol=min(1e-8,c['design']['rtol']*.1),max_step_s=2.5)
 (out/'replay_config.json').write_text(json.dumps(c,indent=2)+'\n')
 def timeout(*_):raise TimeoutError('600-second independent replay limit')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(600);start=time.monotonic()
 r=simulate(c,samples=1501);signal.alarm(0);names,cv=constraint_vector(r)
 row=dict(**propellant_inventory_metrics(r),seconds=time.monotonic()-start,feasible=r['feasible'],days=r['diagnostic_payoff_days'],dry_kg=r['dry_kg'],liquid_kg=r['net_liquid_kg'],closure=r['closure'],margins=r['margins'],audits=r['audits'],failed={n:float(v) for n,v in zip(names,cv) if v < -1e-7})
 write_trajectory(out/'replay.json',r);(out/'replay_summary.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
 if not r['feasible'] or row['failed']:raise SystemExit('Tighter replay failed: do not advance to next variable')
if __name__=='__main__':main()
