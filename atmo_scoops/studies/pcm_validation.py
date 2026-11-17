"""Resolution checks and latent-heat ablation at identical cell masses."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'results/pcm_racks/refined'

def main():
 DEST.mkdir(exist_ok=True)
 cases=[('solid_reference','solid_0.001.json'),
 ('solid_tuned','tuned/solid_f0.5_s1.2.json'),
 ('pcm_best','tuned/sodium_nitrate_5mm_f2_s1.2.json'),
 ('pcm_melting','tuned/nitrate_eutectic_5mm_f1.5_s1.2.json'),
 ('pcm_10mm','tuned/eutectic_10mm_front_f4_s1.2.json')]
 rows=[]
 for name,source in cases:
  original=json.loads((ROOT/'results/pcm_racks'/source).read_text())
  for n in (801,1601):
   args=inputs_from_dict(original['inputs']);args['compressor']=replace(args['compressor'],thermodynamic_samples=n)
   r=simulate(**args,n=n);path=DEST/f'{name}_{n}.json';path.write_text(json.dumps(r,indent=2)+'\n')
   o=r['outputs'];row=dict(name=name,n=n,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,rack_t=sum(x['mass_kg'] for x in o['racks'])/1000,net_kg=o['net_liquid_equivalent_kg'],screens=r['constraints']['all_implemented_screens_pass'],cooldown_s=o['ideal_metal_cooldown_s'])
   rows.append(row);print(row,flush=True);(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
  if name=='pcm_melting':
   args['racks']=replace(args['racks'],masses_kg=tuple(x['mass_kg'] for x in r['outputs']['racks']),pcm_latent_fraction=0.)
   z=simulate(**args,n=n);(DEST/'pcm_melting_no_latent.json').write_text(json.dumps(z,indent=2)+'\n');print('latent disabled',z['outputs']['operating_mass_payoff_days'],z['constraints'],flush=True)

if __name__=='__main__':main()
