"""Validate valve-specific invariants from one saved forward trajectory."""
import sys,json
import numpy as np
from atmo_scoops.transient.io import read_result

def check(r):
 h=r['history'];t=np.array(r['time_s']);d=r['inputs']['design'];reserve=np.array(r['gas_reserve_species_kg']);transfer=np.array(h['valve_transfer_kg_s']);isolate=max(d['pump_stop_s'],d['burn_s']/2)
 after=t>isolate+1e-6;coast=reserve[after]
 checks=dict(no_booster_power=max(abs(np.array(h['gas_fill_MW'])))<1e-12,
             no_booster_mass=r['hardware']['gas_system']['fill_bank']['total_kg']==0,
             isolated_transfer_zero=max(abs(transfer[after]))<1e-12,
             coast_inventory_constant=float(np.max(np.ptp(coast,axis=0)))<1e-7,
             coast_temperature_constant=float(np.ptp(np.array(h['buffer_K'])[after]))<1e-7,
             opening_event=len(r['reserve_events'])==1,
             full_thrust=abs(r['closure']['thrust_relative'])<1e-4,
             captured_supply=r['margins']['full_capture']>=0,
             conservative_mass=r['audits']['species_kg']<1e-4,
             conservative_energy=r['audits']['energy_MJ']<.01)
 if r['reserve_events']:
  before=t<r['reserve_events'][0]['time_s']-1e-6
  checks['no_premature_transfer']=max(abs(transfer[before]))<1e-12
 checks={k:bool(v) for k,v in checks.items()}
 checks['pass']=all(checks.values())
 return checks
if __name__=='__main__':
 r=check(read_result(sys.argv[1]));print(json.dumps(r,indent=2));sys.exit(0 if r['pass'] else 1)
