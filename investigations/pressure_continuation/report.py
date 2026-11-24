"""Report pressure seeds/restoration without treating diagnostic payoffs as optima."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[2];folder=ROOT/'results/transient/pressure_continuation'
lines=['# Pressure continuation: numerical results','','This is an exploratory v1.0.2 study, not a new version release. See [input groups and method](README.md). v1.0.1 remains the accepted 306.398724-day reference.','', '| Case | Perigee km | Target kPa | Rack mass t | Dry mass t | Liquid kg/orbit | Diagnostic days | Feasible |','|---|---:|---:|---:|---:|---:|---:|---|']
rows=[]
for name in ['p105','p110']:
 for kind in ['seed','selected']:
  f=folder/name/f'{kind}_summary.json'
  if f.exists():rows.append((name,kind,json.loads(f.read_text())))
for name,kind,r in rows:
 d=r['inputs']['design'];lines.append(f'| {name} {kind} | {d["perigee_km"]:.6f} | {d["receiver_fill_Pa"]/1000:.6f} | {sum(r["rack_kg"])/1000:.3f} | {r["dry_kg"]/1000:.3f} | {r["liquid_kg"]:.4f} | {r["diagnostic_days"]:.6f} | {r["feasible"]} |')
lines+=['','The seed hardware scales with the intended larger atmospheric batch. During restoration, hardware scale stays fixed while perigee and initial reserve state vary; actual admitted mass need not retain the exact seed scaling. These points are **not payoff-optimized**, and a failed seed does not disprove a pressure target. Structural ratings scale too, so higher pressure is not free tank capacity.','', '## Collection and closure','', '| Case | Capture % | Fill error Pa | Reserve mass error kg | Reserve energy error MJ | Battery error MJ |','|---|---:|---:|---:|---:|---:|']
for name,kind,r in rows:
 cl=r['closure'];fraction=r['admitted_kg']/(r['admitted_kg']+cl['missed_capture_kg']);lines.append(f'| {name} {kind} | {100*fraction:.6f} | {cl["receiver_fill_Pa"]:.6f} | {sum(cl["gas_reserve_species_kg"]):.6f} | {cl["gas_reserve_MJ"]:.6f} | {cl["battery_MJ"]:.6f} |')
lines+=['','Original constraints remain: 99.9% collection minimum, ±50 Pa fill error, 0.1 kg per reserve species, ±1 MJ reserve energy, plus all thermal, electrical, structural and conservation checks. Collection fraction is admission from the modeled incident supply, not delivered-liquid yield.','', '## Local coupling diagnostic','']
evals=json.loads((folder/'p105/evaluations.json').read_text());seed=evals[0];f=np.array(seed['residual']);first=[]
for x in [[.002,0,0],[0,.0002,0],[0,0,.0002]]:first.append(next(r for r in evals if r['x']==x))
j=np.array([(np.array(r['residual'])-f)/max(r['x']) for r in first]).T
lines+=['Initial finite-difference Jacobian for the +5% seed:', '', '| Scaled residual | Perigee / 1 km | Reserve mass / 1,000 kg | Reserve temperature / 100 K |','|---|---:|---:|---:|']
for name,row in zip(['Fill error / 100 Pa','Reserve mass error / 100 kg','Reserve energy error / 10 MJ'],j):lines.append('| '+name+' | '+' | '.join(f'{x:.5f}' for x in row)+' |')
lines += ['',f'The two-norm condition number is **{np.linalg.cond(j):.3f} under these explicitly chosen scales**. This indicates a locally distinguishable three-coordinate restoration direction, not universal numerical robustness; different units/scales change the condition number.','']
term=folder/'p105/termination.json'
if term.exists():
 t=json.loads(term.read_text());lines+=['## Restoration termination','',f'Least-squares success flag: **{t["success"]}**. Message: {t["message"]}. Outer function evaluations: **{t["nfev"]}**; total recorded forward configurations including derivative probes: **{t["cycle_evaluations"]}**. Feasibility of the selected point: **{t["feasible"]}**. This is a closure restoration, not constrained payoff optimization.','']
 # Preserve named selected trajectory rather than relying on an ignored cache.
 selected=json.loads((folder/'p105/selected_summary.json').read_text());key=hashlib.sha256(json.dumps(selected['inputs'],sort_keys=True).encode()).hexdigest();src=folder/'p105'/f'trajectory_{key}.json.gz'
 if src.exists():shutil.copyfile(src,folder/'p105/selected.json.gz')
replay=folder/'p105/replay_summary.json'
if replay.exists():
 q=json.loads(replay.read_text());s0=json.loads((folder/'p105/selected_summary.json').read_text())
 lines+=['## Independent tighter replay','', f'Halving relative tolerance and maximum integration step gives **{q["diagnostic_days"]:.6f} days**, a difference of **{q["diagnostic_days"]-s0["diagnostic_days"]:+.6f} days**. Feasible: **{q["feasible"]}**. [Replay summary](../../results/transient/pressure_continuation/p105/replay_summary.json) and [inputs](../../results/transient/pressure_continuation/p105/replay_config.json).','']
lines+=['## Scope and numerical evidence','','The initial process-pool launcher failed because the sandbox disallowed its forkserver socket. No derivative cycle was run by that launcher. The replacement uses subprocess workers; this infrastructure failure is not a numerical instability or rejected physical design. Each completed cycle and input is logged.','', 'The seed trials isolate a practical partition: rack/material allocation can remain fixed while total thermal inventory scales; fill and reserve restoration use three dedicated outer coordinates. Compressor-chain and power/thermal groups are promising independent sizing subproblems, but still exchange boundary histories and physical package volume. No claim of independent subsystem optima is made.','', '### Artifacts','']
for name,kind,r in rows:lines.append(f'- [{name} {kind} summary](../../results/transient/pressure_continuation/{name}/{kind}_summary.json).')
lines.append('- [Restoration evaluations](../../results/transient/pressure_continuation/p105/evaluations.json).')
Path(__file__).with_name('RESULTS.md').write_text('\n'.join(lines)+'\n')
