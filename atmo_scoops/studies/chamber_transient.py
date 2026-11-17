"""Reference-inspired transient chambers, coast controls and numerical check."""
import json,copy
from pathlib import Path
from ..chambers.__main__ import run
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/chamber_transient'
def main():
 cfg=json.loads((ROOT/'configs/chamber_transient_reference.json').read_text());DEST.mkdir(exist_ok=True)
 cases={}
 for name in ('empty_receiver','no_withdrawal','contact_ends_180s','refined'):
  c=copy.deepcopy(cfg)
  if name=='empty_receiver':c['chambers'][-1]['rack_depth_m']=0.
  if name=='no_withdrawal':c['schedule']['withdrawal_kg_s']=0.
  if name=='contact_ends_180s':c['schedule']['contact_stop_s']=180.
  if name=='refined':c['schedule'].update(max_step_s=1.,rtol=5e-7)
  r=run(c);(DEST/f'{name}.json').write_text(json.dumps(r,indent=2)+'\n');cases[name]=r['checks'];print(name,r['checks'],flush=True)
 (DEST/'checks.json').write_text(json.dumps(cases,indent=2)+'\n')
if __name__=='__main__':main()
