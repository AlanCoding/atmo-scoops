"""Inventory reserve and time-resolution checks for integrated ammonia cases."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/ammonia_integrated/refined'

def main():
 DEST.mkdir(exist_ok=True);rows=[]
 for label,name in [('solid','solid_reference'),('cold200','cold200_area1_s0.85'),('cold200_small','cold200_area0.5_s1.1'),('warm280','cold280_hot340_s0.85')]:
  source=json.loads((DEST.parent/(name+'.json')).read_text());base=inputs_from_dict(source['inputs'])
  if base['ammonia'].enabled:base['ammonia']=replace(base['ammonia'],inventories_kg=tuple(1.1*x['used_kg'] for x in source['outputs']['ammonia']['stages']))
  if label=='cold200_small':base['ammonia']=replace(base['ammonia'],pressure_Pa=2.5e6)
  for n in (801,1601):
   args={**base,'compressor':replace(base['compressor'],thermodynamic_samples=n)}
   r=simulate(**args,n=n);o=r['outputs'];(DEST/f'{label}_{n}.json').write_text(json.dumps(r,indent=2)+'\n')
   row=dict(name=label,n=n,payoff_days=o['operating_mass_payoff_days'],inventory_payoff_days=o.get('payoff_including_ammonia_inventory_days'),
      dry_t=o['total_dry_kg']/1000,net_kg=o['net_liquid_equivalent_kg'],compressor_t=o['compressor_mass_kg']/1000,
      length_m=o['overall_length_allowance_m'],screens=r['constraints']['all_implemented_screens_pass'],
      failed={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8})
   rows.append(row);print(row,flush=True);(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
  if base['ammonia'].enabled:(ROOT/'configs'/f'ammonia_{label}_reference.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
if __name__=='__main__':main()
