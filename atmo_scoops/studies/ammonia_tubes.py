"""Fixed-area ammonia tube size/pitch sensitivity, with matched wall/radius."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/ammonia_tubes'
def run(label,radius_mm,ratio,n=201,wall_mm=None):
 base=inputs_from_dict(json.loads((ROOT/f'configs/reboost_{label}_isp_optimum.json').read_text()))
 base['compressor']=replace(base['compressor'],thermodynamic_samples=n)
 base['ammonia']=replace(base['ammonia'],radius_m=radius_mm/1000,wall_m=(radius_mm/10 if wall_mm is None else wall_mm)/1000,radius_over_pitch=ratio)
 result=simulate(**base,n=n)
 name=f'{label}_r{radius_mm:g}_q{ratio:g}_{n}'+(f'_wall{wall_mm:g}' if wall_mm is not None else '')
 (DEST/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
 o=result['outputs'];a=o['ammonia'];racks=o['racks']
 row=dict(name=name,architecture=label,radius_mm=radius_mm,pitch_mm=radius_mm/ratio,ratio=ratio,n=n,wall_mm=base['ammonia'].wall_m*1000,
  payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,net_kg=o['net_liquid_equivalent_kg'],
  compressor_t=o['compressor_mass_kg']/1000,peak_inlet_K=o['compressor_inlet_K'],tube_t=a['tube_metal_kg']/1000,
  line_fill_t=sum(s['line_fill_kg'] for s in a['stages'])/1000,used_t=a['used_kg']/1000,regen_GJ=a['refrigeration_J']/1e9,
  pump_MJ=a['pass_pump_J']/1e6,peak_dp_kPa=max(s['peak_dp_Pa'] for s in a['stages'])/1000,
  front_depth_m=o['front_depth_m'],length_m=o['overall_length_allowance_m'],
  front_paths=racks[0]['liquid']['parallel_paths'],front_path_length_m=racks[0]['liquid']['length_m'],
  screens=result['constraints']['all_implemented_screens_pass'],
  failed={k:v for k,v in result['constraints']['margins'].items() if v< -1e-8})
 print(row,flush=True);return row

def main():
 DEST.mkdir(exist_ok=True);rows=[]
 for label in ('warm_ammonia','ammonia'):
  for radius in (.25,.5,1.,2.,5.,10.):
   rows.append(run(label,radius,.1));(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
 for ratio in (.05,.2):
  rows.append(run('warm_ammonia',1.,ratio));(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
def checks():
 DEST.mkdir(exist_ok=True)
 rows=[run('warm_ammonia',.25,.1,801),run('warm_ammonia',.25,.1,201,wall_mm=.1),run('warm_ammonia',.5,.1,201,wall_mm=.1)]
 (DEST/'checks.json').write_text(json.dumps(rows,indent=2)+'\n')

if __name__=='__main__':
 import sys
 checks() if '--checks' in sys.argv else main()
