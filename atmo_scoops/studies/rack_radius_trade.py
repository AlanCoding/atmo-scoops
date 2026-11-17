"""Wire radius sensitivity at fixed orbit, lattice fraction and thermal mass rule."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
from ..racks import Racks

def main():
 root=Path(__file__).resolve().parents[2];dest=root/'results/finite_rack_limits/radius_trade';dest.mkdir(parents=True,exist_ok=True)
 base=inputs_from_dict(json.loads((root/'configs/limit_case_reference.json').read_text()))
 base['design']=replace(base['design'],front_depth_m=1.,machinery_depth_m=0.,rear_depth_m=16.,perigee_km=85.,apogee_km=2000.)
 base['performance']=replace(base['performance'],deploy_s=0.,retract_s=0.)
 base['compressor']=replace(base['compressor'],minimum_train_ratio=100.,thermodynamic_samples=401)
 rows=[]
 for radius in (.0001,.0003,.001,.003):
  try:
   r=simulate(**{**base,'racks':Racks(wire_radius_m=radius,radius_over_pitch=.1)},n=401)
   name=f'radius_{radius:g}.json';(dest/name).write_text(json.dumps(r,indent=2)+'\n')
   o=r['outputs'];row=dict(radius_m=radius,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,length_m=o['overall_length_allowance_m'],net_kg_pass=o['net_liquid_equivalent_kg'],gas_peak_K=o['compressor_inlet_K'],metal_peak_K=o['metal_hot_K'],screens=r['constraints']['all_implemented_screens_pass'],margins=r['constraints']['margins'],file=name)
  except ValueError as e:row=dict(radius_m=radius,error=str(e))
  rows.append(row);print(row,flush=True)
  (dest/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__':main()
