import argparse,json
from pathlib import Path
from . import defaults,simulate

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path);p.add_argument('--output',type=Path,default=Path('results/transient/reference.json'));p.add_argument('--samples',type=int,default=1001);p.add_argument('--write-config',type=Path);a=p.parse_args()
 if a.write_config:a.write_config.write_text(json.dumps(defaults(),indent=2)+'\n');return
 r=simulate(json.loads(a.config.read_text()) if a.config else defaults(),a.samples);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,allow_nan=False)+'\n')
 print(json.dumps({k:r[k] for k in ['dry_kg','net_liquid_kg','diagnostic_payoff_days','operating_payoff_days','feasible','closure','margins','audits']},indent=2))
if __name__=='__main__':main()
