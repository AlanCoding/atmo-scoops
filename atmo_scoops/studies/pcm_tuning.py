"""Small matched search: tune front rack mass and suction for solid and PCM cells.

This is a discrete sensitivity search, not a global optimum. Stage masses and
geometry are recorded exactly in each result; full dynamic storage remains out
of scope.
"""
from pathlib import Path
from dataclasses import replace,asdict
import json
from ..system import inputs_from_dict,simulate

ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/pcm_racks/tuned'

def main():
 DEST.mkdir(parents=True,exist_ok=True)
 base=inputs_from_dict(json.loads((ROOT/'configs/finite_rack_reference.json').read_text()))
 base['design']=replace(base['design'],perigee_km=85.,rear_depth_m=16.)
 base['compressor']=replace(base['compressor'],thermodynamic_samples=201)
 cases=[]
 for f in (.5,.8,1.1,1.5):
  for suction in (.85,1.2,1.6):
   cases.append((f'solid_f{f:g}_s{suction:g}',replace(base['racks'],mass_factors=(f,1.5,1.5,1.5)),suction))
 for material in ('nitrate_eutectic','sodium_nitrate'):
  for f in (1.5,2.,3.):
   for suction in (1.2,1.6):
    cases.append((f'{material}_5mm_f{f:g}_s{suction:g}',replace(base['racks'],pcm_material=material,wire_radius_m=.005,mass_factors=(f,3.,3.,3.)),suction))
 for f in (3.,4.,6.):
  for suction in (1.2,1.6):
   cases.append((f'eutectic_10mm_front_f{f:g}_s{suction:g}',replace(base['racks'],pcm_material='nitrate_eutectic',wire_radii_m=(.01,.005,.005,.005),mass_factors=(f,3.,3.,3.)),suction))
 cases.append(('eutectic_10mm_front_f3_s1.6_fins',replace(base['racks'],pcm_material='nitrate_eutectic',wire_radii_m=(.01,.005,.005,.005),mass_factors=(3.,3.,3.,3.),pcm_fin_volume_fraction=.05),1.6))
 rows=[]
 for name,racks,suction in cases:
  try:
   args={**base,'racks':racks,'controls':replace(base['controls'],suction_scale=suction)}
   r=simulate(**args,n=201);o=r['outputs'];filename=name+'.json'
   (DEST/filename).write_text(json.dumps(r,indent=2)+'\n')
   row=dict(name=name,file=filename,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
    rack_t=sum(x['mass_kg'] for x in o['racks'])/1000,net_kg_pass=o['net_liquid_equivalent_kg'],
    max_inlet_K=o['compressor_inlet_K'],max_shell_K=o['metal_hot_K'],length_m=o['overall_length_allowance_m'],
    melt_max=[x.get('melt_fraction_max',0.) for x in o['racks']],
    screens=r['constraints']['all_implemented_screens_pass'],failed={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8})
  except ValueError as exc:row=dict(name=name,error=str(exc),racks=asdict(racks),suction_scale=suction,screens=False)
  rows.append(row);print(row,flush=True)
  (DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__':main()
