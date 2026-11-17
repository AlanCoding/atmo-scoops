"""Full-cycle Isp sensitivity with atmospheric O2/N2 propellant allowed."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/reboost'
def main(architectures=None):
 rows=json.loads((DEST/'isp_screen.json').read_text()) if architectures and (DEST/'isp_screen.json').exists() else []
 for label,path in [('solid','results/ammonia_integrated/refined/solid_1601.json'),('ammonia','results/ammonia_integrated/refined/cold200_1601.json'),('warm_ammonia','results/ammonia_integrated/refined/warm280_1601.json')]:
  if architectures and label not in architectures:continue
  cfg=json.loads((ROOT/path).read_text())['inputs'];base=inputs_from_dict(cfg)
  base['scenario']=replace(base['scenario'],allow_nitrogen_propellant=True)
  base['compressor']=replace(base['compressor'],thermodynamic_samples=201)
  for isp in (1200.,1500.,1800.,2100.,2400.,2800.,3200.,4000.,5000.):
   name=f'{label}_{isp:g}';args={**base,'design':replace(base['design'],isp_s=isp)}
   try:
    r=simulate(**args,n=201);o=r['outputs'];(DEST/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
    row=dict(name=name,architecture=label,isp_s=isp,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
        net_kg=o['net_liquid_equivalent_kg'],propellant_kg=o['propellant_kg'],nitrogen_kg=o['nitrogen_used_as_propellant_kg'],
        screens=r['constraints']['all_implemented_screens_pass'],failed={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8})
   except ValueError as exc:row=dict(name=name,error=str(exc),screens=False)
   rows.append(row);print(row,flush=True);(DEST/'isp_screen.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
