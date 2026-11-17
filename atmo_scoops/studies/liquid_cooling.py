"""Reference-duty liquid inventory / refrigeration sensitivity (not payoff)."""
from pathlib import Path
from dataclasses import replace
import json
import CoolProp
from ..liquid_cooling import LiquidCooling,size
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'results/liquid_cooling'

def main():
 DEST.mkdir(exist_ok=True)
 reference=json.loads((ROOT/'results/pcm_racks/refined/solid_tuned_1601.json').read_text())
 duties=[]
 for r in reference['outputs']['racks']:
  c=r['convection_at_peak_flow'];tg=c.get('gas_K',(c.get('inlet_K',0)+c.get('outlet_K',0))/2)
  duties.append(dict(heat_J=r['absorbed_J'],gas_K=tg,h_gas_W_m2_K=c['h_W_m2_K'],frontal_m2=r['frontal_m2']))
 cycle=reference['outputs']['cycle']
 cases=[('Water',280.,340.,1e6),('Ammonia',200.,300.,2e6),('Ammonia',240.,300.,2e6),('Propane',100.,300.,2e6),('Propane',150.,300.,2e6),('Propane',200.,300.,2e6),('Nitrogen',70.,110.,3e6)]
 rows=[]
 for fluid,cold,hot,pressure in cases:
  for radiator in (260.,300.,340.,380.):
   for mode in (True,False):
    s=LiquidCooling(fluid=fluid,cold_K=cold,hot_K=hot,pressure_Pa=pressure,radiator_K=radiator,heat_pump=mode,coast_s=cycle['deployed_s'],sunlight_s=cycle['sunlit_s'])
    name=f'{fluid}_{cold:g}_{hot:g}_rad{radiator:g}_{"HP" if mode else "passive"}'
    try:
     r=size(duties,s);(DEST/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
     row=dict(name=name,file=name+'.json',fluid=fluid,cold_K=cold,hot_K=hot,radiator_K=radiator,heat_pump=mode,
        inventory_t=r['total_coolant_kg']/1000,tank_depth_m=r['coolant_tank_equivalent_depth_m'],
        dry_t=r['dry_component_kg']/1000,wet_t=r['component_with_coolant_kg']/1000,solar_MW=r['solar_MW'],
        radiator_m2=r['radiator_m2'],electric_GJ=r['refrigerator_J']/1e9,screen_pass=r['screen_pass'])
    except ValueError as exc:row=dict(name=name,error=str(exc),screen_pass=False)
    rows.append(row)
 (DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
 (DEST/'boundary_conditions.json').write_text(json.dumps(dict(CoolProp_version=CoolProp.__version__,source='results/pcm_racks/refined/solid_tuned_1601.json',duties=duties,cycle=cycle),indent=2)+'\n')
 (ROOT/'configs/liquid_cooling_reference.json').write_text(json.dumps(dict(duties=duties,cooling=__import__('dataclasses').asdict(LiquidCooling(coast_s=cycle['deployed_s'],sunlight_s=cycle['sunlit_s']))),indent=2)+'\n')
 for case in cases:
  ok=[x for x in rows if x.get('fluid')==case[0] and x.get('cold_K')==case[1] and x['screen_pass']]
  print(min(ok,key=lambda x:x['wet_t']) if ok else {'fluid':case[0],'cold_K':case[1],'no_passing_case':True},flush=True)

if __name__=='__main__':main()
