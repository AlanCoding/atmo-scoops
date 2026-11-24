"""Summarize completed probes without presenting infeasible payoff as a design."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'results/transient/reduced_coordinates'
rows=[json.loads((out/f'{n}_summary.json').read_text()) for n in ['baseline','rack_minus_1pct','rack_plus_1pct']]
lines=['# Fixed rack-allocation probe results','','These are unchanged-hardware perturbations around the refined v1.0.1 cycle, not reoptimized designs. See [method](README.md).','', '| Case | Rack mass t | Dry mass t | Liquid kg/cycle | Diagnostic days | Feasible | Runtime s |','|---|---:|---:|---:|---:|---|---:|']
for r in rows:
 if 'error' in r:lines.append(f'| {r["label"]} | — | — | — | — | Unresolved: {r["error"]} | {r["seconds"]:.1f} |');continue
 lines.append(f'| {r["label"]} | {sum(r["rack_kg"])/1000:.3f} | {r["dry_kg"]/1000:.3f} | {r["net_liquid_kg"]:.6f} | {r["diagnostic_payoff_days"]:.6f} | {r["feasible"]} | {r["seconds"]:.1f} |')
lines+=['','A diagnostic payoff is arithmetic from this single cycle. All three probes pass the current model feasibility checks, but only the baseline remains the published reference; no optimization or new design release is claimed. Small negative constraint values within numerical roundoff are listed in raw summaries but are not engineering failures.','', '## Closure response','', '| Case | Battery MJ | Heat buffer MJ | Receiver fill error Pa | Reserve mass error kg | Reserve energy MJ | Max rack enthalpy error J/kg |','|---|---:|---:|---:|---:|---:|---:|']
for r in rows:
 if 'error' in r:continue
 c=r['closure'];lines.append(f'| {r["label"]} | {c["battery_MJ"]:.4f} | {c["warm_MJ"]:.4f} | {c["receiver_fill_Pa"]:.4f} | {sum(c["gas_reserve_species_kg"]):.6f} | {c["gas_reserve_MJ"]:.6f} | {max(abs(x) for x in c["rack_enthalpy_J_kg"]):.3f} |')
lines+=['','## Full constraint and provenance records','']
for r in rows:
 label=r['label'];lines.append(f'- [{label} summary](../../results/transient/reduced_coordinates/{label}_summary.json), [exact inputs](../../results/transient/reduced_coordinates/{label}_config.json).')
 if 'error' not in r:
  failed={k:v for k,v in r['failed_constraints'].items() if v < -1e-7}
  lines.append('  Materially negative normalized constraints: '+(', '.join(f'{k}={v:.5g}' for k,v in failed.items()) or 'none')+'.')
lines += ['', '## Interpretation', '',
 'The ±1% response is smooth at this tested scale: less total rack mass reduces dry mass and payoff slightly, while useful liquid changes by only about 0.12 kg/orbit. All three full integrations completed in 71–79 seconds. This is local evidence, not a guarantee across a broad design search.', '',
 'The −1% case has receiver fill error +49.632 Pa against a ±50 Pa requirement and reserve energy residual +0.935 MJ against a ±1 MJ requirement. Its summed reserve mass discrepancy is 0.109 kg; the implemented closure criterion applies separately to each species (0.1 kg each), which is why it passes. Do not interpret this as an exactly periodic solution or a comfortable engineering margin.', '',
 'A sensible next small outer solve can retain fixed rack fractions and add the already-existing fill/reserve closure coordinates (perigee, initial reserve mass and temperature), with explicit numerical reserve inside the original tolerances. This is a proposed experiment, not implemented here. Keep independent rack temperatures, geometry and hardware capacities fixed until measured residuals require otherwise. Thermal rack enthalpy residuals stayed below 0.14 J/kg versus the 500 J/kg criterion; battery and heat-buffer closure did not drive this local response.', '',
 'No forward-cycle equations or tolerances were changed. Existing original inputs, solver and publication figures remain untouched.']
Path(__file__).with_name('RESULTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
