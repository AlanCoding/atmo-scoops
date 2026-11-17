"""Refined-case time-resolution and port-regularization sensitivity."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate

def main():
 root=Path(__file__).resolve().parents[2];folder=root/'results/finite_rack_limits'
 base=inputs_from_dict(json.loads((folder/'reference_1mm/apogee_2000.json').read_text())['inputs'])
 def run(n,eps):
  return simulate(**{**base,'compressor':replace(base['compressor'],thermodynamic_samples=n),
   'flow':replace(base['flow'],port_linearization_fraction=eps)},n=n)
 coarse=run(801,.001);fine=run(1601,.001);smooth=run(801,.0001)
 keys=('captured_kg','retained_kg','total_dry_kg','compressor_kWh','hot_absorbed_GJ','operating_mass_payoff_days')
 errors={k:abs(coarse['outputs'][k]/fine['outputs'][k]-1) for k in keys}
 smoothing={k:abs(coarse['outputs'][k]/smooth['outputs'][k]-1) for k in keys}
 assert max(errors.values())<.002,errors
 assert max(smoothing.values())<.002,smoothing
 for r in (coarse,fine,smooth):
  o=r['outputs']
  assert abs(o['captured_kg']+o['initial_gas_seed_kg']+o['mixing']['injected_kg']-o['retained_kg']-o['vent_kg'])<1e-6
  assert abs(o['thermal_energy_balance_residual_J'])<1e-8*o['hot_absorbed_GJ']*1e9
  assert r['constraints']['all_implemented_screens_pass']
 report=dict(status='passed',samples=[801,1601],relative_resolution_errors=errors,
  relative_port_smoothing_errors=smoothing,thermal_residual_J=fine['outputs']['thermal_energy_balance_residual_J'],
  scope='Numerical convergence/conservation of reduced model; not heat-transfer, machinery or packaging validation')
 (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
