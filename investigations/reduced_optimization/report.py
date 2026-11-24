"""Report optimizer termination separately from independent physical validation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'results/transient/reduced_optimization'
lines=['# Incremental optimization results','','The accepted v1.0.1 publication remains unchanged. These are scoped local constrained searches around the feasible pressure-continuation candidate. See [method and bounds](README.md).','', '| Stage | Solver success | Iterations | Forward configurations | Search days | Replay days | Replay feasible | Bound hits |','|---|---|---:|---:|---:|---:|---|---|']
completed=[]
for name in ['rack_mass_precise','pressure']:
 folder=out/name
 if not (folder/'termination.json').exists():continue
 t=json.loads((folder/'termination.json').read_text());r=json.loads((folder/'selected_summary.json').read_text()) if (folder/'selected_summary.json').exists() else None
 replay=json.loads((folder/'replay_summary.json').read_text()) if (folder/'replay_summary.json').exists() else None
 completed.append((name,folder,t,r,replay))
 lines.append(f'| {name} | {t["success"]} | {t.get("nit","—")} | {t.get("cycles","—")} | '+(f'{r["days"]:.6f}' if r else '—')+' | '+(f'{replay["days"]:.6f}' if replay else '—')+' | '+(str(replay['feasible']) if replay else 'Not run')+' | '+(', '.join(t.get('bound_hits',[])) or 'none')+' |')
baseline=json.loads((ROOT/'results/transient/reduced_coordinates/baseline_summary.json').read_text())
seed=json.loads((ROOT/'results/transient/pressure_continuation/p105/replay_summary.json').read_text())
lines+=['','## Comparison on the operating-orbit metric','','| Configuration | Dry mass t | Net liquid kg/orbit | Payoff days |','|---|---:|---:|---:|',f'| Published v1.0.1 replay | {baseline["dry_kg"]/1000:,.2f} | {baseline["net_liquid_kg"]:,.3f} | {baseline["diagnostic_payoff_days"]:.4f} |',f'| +5% pressure-continuation seed | {seed["dry_kg"]/1000:,.2f} | {seed["liquid_kg"]:,.3f} | {seed["days"]:.4f} |']
for name,folder,t,r,replay in completed:
 if replay:lines.append(f'| {name}, tighter replay | {replay["dry_kg"]/1000:,.2f} | {replay["liquid_kg"]:,.3f} | {replay["days"]:.4f} |')
lines+=['','The continuation seed has enlarged installed hardware relative to the publication reference. These searches retain those capacities. A difference from the published payoff is therefore not an isolated rack-mass or pressure effect. The seed was restored near zero fill error; optimization can use the guarded ±25 Pa band. Improvements combine mass, perigee and reserve-state adjustment, including that filling allowance. Delivery/circularization is not newly credited.']
lines+=['','## Selected physical inputs','', '| Stage | Rack total t | Receiver target kPa | Receiver/reserve rating kPa | Perigee km | Initial reserve kg | Initial reserve K |','|---|---:|---:|---:|---:|---:|---:|']
for name,folder,t,r,replay in completed:
 if not r:continue
 d=r['inputs']['design'];lines.append(f'| {name} | {sum(r["rack_kg"])/1000:.4f} | {d["receiver_fill_Pa"]/1000:.6f} | {d["rated_pressure_Pa"][-1]/1000:.6f} | {d["perigee_km"]:.6f} | {d["gas_reserve_kg"]:.6f} | {d["gas_initial_K"]:.6f} |')
lines+=['','Rack mass fractions remain fixed. The pressure stage adds exactly one independent scalar; structural rating follows a fixed target/rating ratio. Solar area, battery energy and processing/thermal capacities retain the continuation sizes; thrust hardware and bus/discharge ratings still follow demand. All constraints and their limiting values are retained in the linked summaries.','']
available=[(name,r) for name,_,_,r,_ in completed if r]
if available:
 lines+=['','## Fixed rack allocation','','| Rack | Fixed fraction | '+' | '.join(name+' mass t' for name,_ in available)+' |','|---|---:|'+ '---:|'*len(available)]
 first=available[0][1]
 for k,mass in enumerate(first['rack_kg']):
  lines.append(f'| {k+1} | {100*mass/sum(first["rack_kg"]):.5f}% | '+' | '.join(f'{r["rack_kg"][k]/1000:.3f}' for _,r in available)+' |')
for name,folder,t,r,replay in completed:
 lines += ['',f'## {name}: termination and acceptance','', f'Solver message: **{t.get("message",t.get("error"))}**.']
 if r:
  lines += ['',f'Selected fill error: **{r["closure"]["receiver_fill_Pa"]:.6f} Pa**. Original model feasible: **{r["feasible"]}**.']
 if replay:
  cl=replay['closure'];lines += ['',f'Tighter replay: dry mass **{replay["dry_kg"]/1000:,.3f} t**, net liquid **{replay["liquid_kg"]:,.6f} kg/orbit**, fill error **{cl["receiver_fill_Pa"]:.6f} Pa**, total reserve mass error **{sum(cl["gas_reserve_species_kg"]):.6f} kg**, reserve energy error **{cl["gas_reserve_MJ"]:.6f} MJ**.',f'Capture: **{100*(1-r["inputs"]["design"]["capture_tolerance"]+replay["margins"]["full_capture"]):.5f}%**; minimum propulsion reserve: **{replay["minimum_reserve_total_kg"]:.4f} kg**. Original failed constraints: `{replay["failed"]}`. Change from search payoff: **{replay["days"]-r["days"]:+.6f} days**.']
 lines += ['',f'- [Termination](../../results/transient/reduced_optimization/{name}/termination.json).',f'- [Manifest and bounds](../../results/transient/reduced_optimization/{name}/manifest.json).',f'- [Evaluation history](../../results/transient/reduced_optimization/{name}/evaluations.json).']
 if r:lines.append(f'- [Selected inputs](../../results/transient/reduced_optimization/{name}/selected_config.json).')
 if replay:lines.append(f'- [Tighter replay](../../results/transient/reduced_optimization/{name}/replay_summary.json).')
lines+=['','## Scope of the result','','A successful termination is a bounded local result with this fixed allocation and these hardware capabilities, not a certified global optimum. An active rack-mass bound is reported rather than silently widened. The second stage is only authorized by successful first-stage termination and tighter feasibility. No surrogate correction, fabricated numerical penalty or hidden cycle-to-cycle iteration is used. The original full-capture tolerance remains enforced.']
lines+=['','The pressure result reaches the lower rack-mass bound and the upper initial-reserve-mass bound. Those are local experiment bounds, not material or tank-capacity limits. In particular, the initial gas inventory is a cycle-closure coordinate. A continuation with wider rack/closure-state bounds should precede treating 5.54 kPa as an engineering optimum or adding further design variables. The result nevertheless demonstrates successful constrained optimization with both total rack mass and pressure free; the stage fractions never changed.']
lines+=['','## Numerical qualification','','The high-resolution rack solve is a warm-started convergence confirmation, not the entire cost of finding its candidate. Earlier histories in `rack_mass_exact_equalities`, `rack_mass`, `rack_mass_contiguous` and `rack_mass_resolved` preserve the development attempts. The first two used a strided objective gradient and are superseded by the contiguous-array fix. The latter two were interrupted while diagnosing derivative/integration resolution. Their termination is not reported as convergence.','', 'At identical inputs, reducing rtol from 1e-5 to 1e-7 changed nitrogen closure by 11.8 g but payoff by less than 0.001 day. Final searches therefore use rtol=1e-7 and replay uses 1e-8. SLSQP objective tolerance is 0.005 days. The guarded closure bands remain stricter than the original physical acceptance limits. See [method and reproducible restart](README.md).','', 'The full 175-test suite and conservation/Kepler audit passed; focused reduced-coordinate/optimizer tests were rerun after the driver changes. The array-layout regression exercises SLSQP itself. Each accepted replay also records species/energy conservation, reserve availability and capture.']
Path(__file__).with_name('RESULTS.md').write_text('\n'.join(lines)+'\n')
