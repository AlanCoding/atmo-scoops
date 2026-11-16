"""Find pressure-limited perigees with L/D<=10 and fixed low-pressure storage."""
from pathlib import Path
from dataclasses import replace
import json,hashlib
from scipy.optimize import brentq
from ..system import simulate,inputs_from_dict
from ..orbit import Orbit


def main():
 root=Path(__file__).resolve().parents[2];dest=root/'results/altitude_sensitivity/limited_reference';dest.mkdir(exist_ok=True)
 base=inputs_from_dict(json.loads((root/'results/altitude_sensitivity/90km.json').read_text())['inputs'])
 d=base['design'];bore=30.;outer=bore+2*d.radial_clearance_m
 design=replace(d,front_diameter_m=bore,rear_diameter_m=bore,rear_depth_m=10*outer-d.front_depth_m-d.machinery_depth_m)
 base={**base,'design':design,'compressor':replace(base['compressor'],minimum_train_ratio=1.)}
 cap=110000.;rows=[]
 for apogee in (937.1912423634607,2000.,10000.,15000.):
  evaluations=[];cache={}
  def evaluate(h,n=401):
   key=(round(h,9),n)
   if key not in cache:
    inputs={**base,'design':replace(design,perigee_km=h,apogee_km=apogee)}
    if apogee>1000:
     inputs['controls']=replace(base['controls'],max_after_perigee_s=min(base['controls'].max_after_perigee_s,Orbit(h,apogee).time_at_altitude(999.)))
    if n>401:inputs['compressor']=replace(inputs['compressor'],thermodynamic_samples=n)
    r=simulate(**inputs,n=n);cache[key]=r
    evaluations.append(dict(perigee_km=h,rear_pressure_Pa=r['outputs']['rear_pressure_Pa'],screens_pass=r['constraints']['all_implemented_screens_pass']))
    print('trial',apogee,h,r['outputs']['rear_pressure_Pa'],flush=True)
   return cache[key]
  # Root is approached from the feasible side after the solver converges.
  h=brentq(lambda h:evaluate(h)['outputs']['rear_pressure_Pa']-cap,60.,90.,xtol=.003)
  h+=.01
  r=evaluate(h,n=1601);o=r['outputs'];ld=o['overall_length_allowance_m']/outer
  margins={'storage_pressure_Pa':cap-o['rear_pressure_Pa'],'length_m':10*outer-o['overall_length_allowance_m']}
  r['investigation_limits']=dict(max_length_over_diameter=10.,outside_diameter_m=outer,max_storage_pressure_Pa=cap,margin=margins,
   passes=all(x>=0 for x in margins.values()) and r['constraints']['all_implemented_screens_pass'])
  name=f'apogee_{apogee:.0f}.json';(dest/name).write_text(json.dumps(r,indent=2)+'\n')
  row=dict(apogee_km=apogee,perigee_km=h,storage_Pa=o['rear_pressure_Pa'],dry_t=o['total_dry_kg']/1000,compressor_t=o['compressor_mass_kg']/1000,net_kg_pass=o['net_liquid_equivalent_kg'],payoff_days=o['operating_mass_payoff_days'],period_h=o['cycle']['orbit_s']/3600,passes=r['investigation_limits']['passes'],failed_margins={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8},file=name,evaluations=evaluations)
  rows.append(row);print('RESULT',row,flush=True)
  (dest/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
 sources=list((root/'atmo_scoops').rglob('*.py'))
 (dest/'manifest.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')

if __name__=='__main__':main()
