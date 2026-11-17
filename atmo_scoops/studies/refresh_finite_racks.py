"""Re-evaluate saved boundary points with the current numerical model.

Search histories remain evidence of how points were located. This refresh checks
feasibility at those inputs; it does not claim to reoptimize their boundaries.
"""
from pathlib import Path
from dataclasses import replace
import json,hashlib
from ..system import inputs_from_dict,simulate

ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/finite_rack_limits'

def summary(r,name):
 o=r['outputs'];return dict(apogee_km=r['inputs']['design']['apogee_km'],perigee_km=r['inputs']['design']['perigee_km'],
  rear_depth_m=o['rear_depth_m'],pressure_Pa=o['rear_pressure_Pa'],length_m=o['overall_length_allowance_m'],
  dry_t=o['total_dry_kg']/1000,compressor_t=o['compressor_mass_kg']/1000,net_kg_pass=o['net_liquid_equivalent_kg'],
  payoff_days=o['operating_mass_payoff_days'],period_h=o['cycle']['orbit_s']/3600,screens=r['constraints']['all_implemented_screens_pass'],file=name)

def main():
 for folder in (DEST,DEST/'reference_1mm'):
  rows=[]
  for path in sorted(folder.glob('apogee_*.json')):
   old=json.loads(path.read_text());args=inputs_from_dict(old['inputs'])
   args['compressor']=replace(args['compressor'],thermodynamic_samples=801)
   r=simulate(**args,n=801)
   path.write_text(json.dumps(r,indent=2)+'\n');row=summary(r,path.name);rows.append(row);print(row,flush=True)
  (folder/'summary.json').write_text(json.dumps(sorted(rows,key=lambda x:x['apogee_km']),indent=2)+'\n')
 # Fix orbit and hardware when isolating provisional envelope-density effects.
 path=DEST/'reference_1mm/apogee_2000.json';ref=json.loads(path.read_text());args=inputs_from_dict(ref['inputs'])
 args['compressor']=replace(args['compressor'],thermodynamic_samples=401)
 sensitivities=[]
 for density in (100.,250.,1000.):
  r=simulate(**{**args,'packaging':replace(args['packaging'],machinery_bulk_kg_m3=density)},n=401)
  name=f'package_density_{density:.0f}.json';(DEST/name).write_text(json.dumps(r,indent=2)+'\n')
  o=r['outputs'];sensitivities.append(dict(density_kg_m3=density,length_m=o['overall_length_allowance_m'],payoff_days=o['operating_mass_payoff_days'],file=name))
 (DEST/'packaging_sensitivity.json').write_text(json.dumps(sensitivities,indent=2)+'\n')
 (ROOT/'configs/finite_rack_reference.json').write_text(json.dumps(ref['inputs'],indent=2)+'\n')
 (DEST/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'atmo_scoops').rglob('*.py')},indent=2)+'\n')

if __name__=='__main__':main()
