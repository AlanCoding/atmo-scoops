"""Integrated fixed-orbit ammonia exchanger/control sensitivity."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
from ..ammonia import AmmoniaCooling
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/ammonia_integrated'

def main():
 DEST.mkdir(exist_ok=True)
 base=inputs_from_dict(json.loads((ROOT/'results/pcm_racks/refined/solid_tuned_1601.json').read_text())['inputs'])
 base['compressor']=replace(base['compressor'],thermodynamic_samples=201)
 rows=[]
 cases=[('solid_reference',None,1.2)]
 for scale in (.5,1.,1.5):
  for suction in (.6,.85,1.1):
   a=AmmoniaCooling(enabled=True,areas_m2=tuple(scale*x for x in (170000.,6000.,6000.,6000.)),inventories_kg=(600000.,80000.,30000.,30000.))
   cases.append((f'cold200_area{scale:g}_s{suction:g}',a,suction))
 for cold in (240.,280.):
  for suction in (.6,.85):
   a=AmmoniaCooling(enabled=True,cold_K=cold,hot_target_K=340.,pressure_Pa=5e6,
       inventories_kg=(1000000.,100000.,50000.,50000.))
   cases.append((f'cold{cold:g}_hot340_s{suction:g}',a,suction))
 for name,a,suction in cases:
  args={**base,'controls':replace(base['controls'],suction_scale=suction)}
  if a:args['ammonia']=a
  try:
   r=simulate(**args,n=201);o=r['outputs'];(DEST/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
   row=dict(name=name,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
       net_kg=o['net_liquid_equivalent_kg'],compressor_t=o['compressor_mass_kg']/1000,
       compressor_peak_MW=o['compressor_peak_MW'],inlet_peak_K=o['compressor_inlet_K'],length_m=o['overall_length_allowance_m'],
       screens=r['constraints']['all_implemented_screens_pass'],failed={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8})
  except ValueError as exc:row=dict(name=name,error=str(exc),screens=False)
  rows.append(row);print(row,flush=True);(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
