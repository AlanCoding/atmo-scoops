"""Paired apogee diagnostics for the altitude investigation; not optimization."""
from pathlib import Path
from dataclasses import replace,asdict
import json
from ..system import simulate,inputs_from_dict
from ..orbit import Orbit

def main():
 root=Path(__file__).resolve().parents[2];dest=root/'results/altitude_sensitivity/apogee';dest.mkdir(exist_ok=True)
 rows=[]
 for h in (60,80,90):
  base=inputs_from_dict(json.loads((root/f'results/altitude_sensitivity/{h}km.json').read_text())['inputs'])
  for apogee in (2000,10000,35786):
   args={**base,'design':replace(base['design'],apogee_km=apogee)}
   # Limit the requested integration grid to the atmosphere domain. A valid
   # case must reach pressure cutoff before this horizon, not stop at the cap.
   if apogee>1000:
    horizon=min(base['controls'].max_after_perigee_s,Orbit(h,apogee).time_at_altitude(999.))
    args['controls']=replace(base['controls'],max_after_perigee_s=horizon)
   try:
    r=simulate(**args,n=401);(dest/f'{h}_{apogee}.json').write_text(json.dumps(r,indent=2)+'\n');o=r['outputs']
    row=dict(perigee_km=h,apogee_km=apogee,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,net_kg_pass=o['net_liquid_equivalent_kg'],period_h=o['cycle']['orbit_s']/3600,sunlight_h=o['cycle']['sunlit_s']/3600,solar_t=o['masses_kg']['solar']/1000,battery_t=o['masses_kg']['battery']/1000,propulsion_t=o['masses_kg']['propulsion_hardware']/1000,screens_pass=r['constraints']['all_implemented_screens_pass'],failed_margins={k:v for k,v in r['constraints']['margins'].items() if v< -1e-8})
   except ValueError as e:row=dict(perigee_km=h,apogee_km=apogee,error=str(e),inputs={k:asdict(v) for k,v in args.items()})
   rows.append(row);print({k:v for k,v in row.items() if k!='inputs'},flush=True);(dest/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
