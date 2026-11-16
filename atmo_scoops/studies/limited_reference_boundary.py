"""Locate simultaneous storage/oxygen limits for the fixed L/D reference."""
from pathlib import Path
from dataclasses import replace
import json, math
from scipy.optimize import root
from ..system import simulate,inputs_from_dict
from ..orbit import Orbit


def main():
 folder=Path(__file__).resolve().parents[2]/'results/altitude_sensitivity/limited_reference'
 base=inputs_from_dict(json.loads((folder/'apogee_10000.json').read_text())['inputs'])
 trials=[];cache={}
 def evaluate(h,a,n=401):
  key=(float(h),float(a),n)
  if key not in cache:
   args={**base,'design':replace(base['design'],perigee_km=float(h),apogee_km=float(a))}
   args['controls']=replace(base['controls'],max_after_perigee_s=min(1200.,Orbit(h,a).time_at_altitude(999.)))
   if n>401:args['compressor']=replace(base['compressor'],thermodynamic_samples=n)
   r=simulate(**args,n=n);cache[key]=r;o=r['outputs']
   trials.append(dict(perigee_km=h,apogee_km=a,pressure_Pa=o['rear_pressure_Pa'],oxygen_margin_kg=o['oxygen_mass_margin_kg'],samples=n))
   print(trials[-1],flush=True)
  return cache[key]
 def residual(x):
  o=evaluate(x[0],x[1]*1000)['outputs']
  return [math.log(o['rear_pressure_Pa']/110000.),100*o['oxygen_mass_margin_kg']/o['retained_kg']]
 sol=root(residual,[63.,14.],options={'eps':1e-5,'xtol':1e-6})
 if not sol.success or max(abs(v) for v in residual(sol.x))>1e-4:raise ValueError(str(sol.message))
 # Move slightly inside both boundaries, then verify with finer sampling.
 h=float(sol.x[0]+.02);a=float(sol.x[1]*1000-10.)
 r=evaluate(h,a,1601);o=r['outputs'];d=r['inputs']['design'];outer=max(d['mouth_diameter_m'],d['front_diameter_m'],d['rear_diameter_m'])+2*d['radial_clearance_m']
 limits=dict(storage_pressure_Pa=110000.-o['rear_pressure_Pa'],length_m=10*outer-o['overall_length_allowance_m'])
 r['investigation_limits']=dict(max_length_over_diameter=10.,outside_diameter_m=outer,max_storage_pressure_Pa=110000.,margin=limits,passes=all(v>=0 for v in limits.values()) and r['constraints']['all_implemented_screens_pass'])
 if not r['investigation_limits']['passes']:raise ValueError('Refined interior point fails constraints')
 (folder/'joint_boundary.json').write_text(json.dumps(r,indent=2)+'\n')
 (folder/'joint_boundary_search.json').write_text(json.dumps(dict(boundary_perigee_km=float(sol.x[0]),boundary_apogee_km=float(sol.x[1]*1000),trials=trials),indent=2)+'\n')
 config=folder.parents[2]/'configs/limit_case_reference.json'
 config.write_text(json.dumps(r['inputs'],indent=2)+'\n')
 print('FINAL',h,a,o['operating_mass_payoff_days'],o['total_dry_kg']/1000,flush=True)

if __name__=='__main__':main()
