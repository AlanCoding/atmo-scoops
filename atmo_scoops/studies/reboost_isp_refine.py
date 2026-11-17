"""Local primary-model Isp minimization and higher-resolution verification."""
from pathlib import Path
from dataclasses import replace
import json
from scipy.optimize import minimize_scalar
from ..system import inputs_from_dict,simulate
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/reboost'
def main(architectures=None):
 rows=json.loads((DEST/'isp_optima.json').read_text()) if architectures and (DEST/'isp_optima.json').exists() else []
 for label in ('solid','ammonia','warm_ammonia'):
  if architectures and label not in architectures:continue
  base=inputs_from_dict(json.loads((DEST/f'{label}_1800.json').read_text())['inputs'])
  cache={}
  def f(isp):
   args={**base,'design':replace(base['design'],isp_s=float(isp))}
   r=simulate(**args,n=201);cache[float(isp)]=r
   return r['outputs']['operating_mass_payoff_days'] if r['constraints']['all_implemented_screens_pass'] else 1e9
  opt=minimize_scalar(f,bounds=(1400.,2400.),method='bounded',options={'xatol':3.})
  for n in (801,1601):
   args={**base,'design':replace(base['design'],isp_s=float(opt.x)),'compressor':replace(base['compressor'],thermodynamic_samples=n)}
   r=simulate(**args,n=n);(DEST/f'{label}_isp_optimum_{n}.json').write_text(json.dumps(r,indent=2)+'\n')
   o=r['outputs'];row=dict(architecture=label,isp_s=float(opt.x),n=n,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
       net_kg=o['net_liquid_equivalent_kg'],propellant_kg=o['propellant_kg'],nitrogen_kg=o['nitrogen_used_as_propellant_kg'],screens=r['constraints']['all_implemented_screens_pass'])
   rows.append(row);print(row,flush=True);(DEST/'isp_optima.json').write_text(json.dumps(rows,indent=2)+'\n')
  (ROOT/'configs'/f'reboost_{label}_isp_optimum.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
if __name__=='__main__':main()
