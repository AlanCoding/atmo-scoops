"""Paired solid / encapsulated PCM radius and mass-allocation investigation."""
from pathlib import Path
from dataclasses import replace
import json,hashlib
from ..system import inputs_from_dict,simulate

ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/pcm_racks'

def main():
 DEST.mkdir(exist_ok=True)
 base=inputs_from_dict(json.loads((ROOT/'configs/finite_rack_reference.json').read_text()))
 base['design']=replace(base['design'],perigee_km=85.,rear_depth_m=16.)
 base['compressor']=replace(base['compressor'],thermodynamic_samples=201)
 cases=[]
 for radius in (.001,.003,.01):
  cases.append((f'solid_{radius:g}',replace(base['racks'],wire_radius_m=radius)))
 for material in ('nitrate_eutectic','sodium_nitrate','tin'):
  for factor in (1.5,3.,6.,12.):
   cases.append((f'{material}_10mm_f{factor:g}',replace(base['racks'],pcm_material=material,wire_radius_m=.01,mass_factors=(factor,)*4)))
 for factor in (1.5,3.,6.):
  cases.append((f'eutectic_5mm_f{factor:g}',replace(base['racks'],pcm_material='nitrate_eutectic',wire_radius_m=.005,mass_factors=(factor,)*4)))
 for factor in (1.5,3.,6.):
  cases.append((f'hybrid_interstage_f{factor:g}',replace(base['racks'],pcm_materials=('none','nitrate_eutectic','nitrate_eutectic','nitrate_eutectic'),wire_radii_m=(.001,.01,.01,.01),mass_factors=(1.5,factor,factor,factor))))
 rows=[]
 for name,racks in cases:
  path=DEST/f'{name}.json'
  try:
   r=simulate(**{**base,'racks':racks},n=201)
   o=r['outputs'];row=dict(name=name,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
    rack_t=sum(x['mass_kg'] for x in o['racks'])/1000,net_kg_pass=o['net_liquid_equivalent_kg'],
    length_m=o['overall_length_allowance_m'],max_inlet_K=o['compressor_inlet_K'],max_shell_K=o['metal_hot_K'],
    max_cooldown_s=o['ideal_metal_cooldown_s'],coast_s=o['cycle']['deployed_s'],
    melt_max=[x.get('melt_fraction_max',0.) for x in o['racks']],
    core_max_K=[x.get('core_max_K') for x in o['racks']],
    screens=r['constraints']['all_implemented_screens_pass'],
    failed={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8},file=path.name)
   path.write_text(json.dumps(r,indent=2)+'\n')
  except ValueError as exc:
   row=dict(name=name,error=str(exc),screens=False)
  rows.append(row);print(row,flush=True)
  (DEST/'screen.json').write_text(json.dumps(rows,indent=2)+'\n')
 (DEST/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'atmo_scoops').rglob('*.py')},indent=2)+'\n')

if __name__=='__main__':main()
