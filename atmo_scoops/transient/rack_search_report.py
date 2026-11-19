"""Report the constrained search without converting failed closure into payoff."""
import argparse,json
from pathlib import Path
from .io import read_result
from .global_search import rank

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('results/transient/rack_wide_optimization'));args=parser.parse_args();root=args.root
    manifest=json.loads((root/'search.json').read_text())
    pitch_max=next(s['high'] for s in manifest['coordinates'] if s['name']=='pitch_diameter:0')
    rows=json.loads((root/'evaluations.json').read_text())
    complete=[r for r in rows if 'dry_kg' in r]
    feasible=[r for r in complete if r['feasible']]
    preflight=[r for r in rows if 'five physical rows' in r.get('error','')]
    unresolved=[r for r in rows if r.get('error') and r.get('status')!='physical_path_rejection' and r not in preflight]
    out=Path('investigations/rack_radius');out.mkdir(exist_ok=True)
    text=['# Rod radius and pitch: coupled constrained search','',
          'This is a finite global-search attempt with the low-Re inline-bank model, not a converged optimum. Each candidate compiles hardware and runs one forward orbit. No inner cycle iteration or automatic capacity resizing is used.','',
          f'Evaluations: **{len(rows)}**; complete trajectories: **{len(complete)}**; feasible: **{len(feasible)}**; unresolved numerical evaluations: **{len(unresolved)}**; fewer-than-five-row geometry exclusions: **{len(preflight)}**.','',
          'The search varies 55 scalar coordinates, including five radii, five common pitches, five solid inventories, four clear depths, compressor capacities, propulsion, power and thermal hardware, gas reserve, initial rack temperatures and cutoff/vent timing. Perigee remains 85 km; bore is 30 m and hull L/D is 10. All bounds and inputs are in [the manifest](../../'+str(root)+'/search.json).','',
          f'Radius bounds are 0.2–10 mm. Pitch/diameter is 1.25–{pitch_max:g}. Values above 2 extend beyond the illustrated low-Re square-bank anchors: this is explicitly a geometry-extrapolation search, pending sensitivity and additional evidence. See [equations and evidence](../../modeling/metal_coolers/LOW_RE_BANK.md).','']
    if feasible:
        best=min(feasible,key=rank)
        text += [f'Lowest accepted operating-orbit payoff in this run: **{best["operating_payoff_days"]:.1f} days**. This is not circular-apogee delivery payoff.','']
        text += ['The earlier approximately 304-day result used a different rack heat-transfer treatment and omitted rack resistance. Geometry and installed capacities also differ; the ratio of these payoffs is not a controlled estimate of the pressure-loss penalty alone.','']
    else:
        text += ['**No accepted revised payoff was found.** Positive liquid production in a trial does not establish a recurring cycle if it consumes the starting gas propellant reserve or fails another closure/path constraint. The earlier approximately 304-day no-rack-loss result is not validated by this search. A numerical timeout is not evidence of physical infeasibility.','']
    text += ['## Completed candidates','', '| Case | Dry mass, t | Liquid, kg/orbit | Gas-reserve change, kg | Feasible |','|---|---:|---:|---:|---|']
    for r in sorted(complete,key=lambda x:x['case']):
        deficit=sum(r['closure']['gas_reserve_species_kg'])
        text += [f'| {r["case"]} | {r["dry_kg"]/1000:.1f} | {r["net_liquid_kg"]:.1f} | {deficit:.1f} | {r["feasible"]} |']
    if complete:
        best=min(complete,key=rank);d=best['inputs']['design']
        if best['case']==0:
            text += ['', 'The declared reference seed remains the best candidate in this finite run. The mutation generation did not establish a better allocation; these dimensions must not be described as a converged optimum.','']
        text += ['',f'## Lowest-violation completed candidate ({best["case"]})','',
                 'This table describes a search candidate; it is an accepted numerical reference only if the feasibility column above is true.','',
                 '| Rack | Radius, mm | Common pitch, mm | Requested rack depth, m |','|---|---:|---:|---:|']
        for i,(r,p,l) in enumerate(zip(d['stage_radius_m'],d['stage_pitch_m'],d['rack_depth_m'])):
            text += [f'| {i+1} | {r*1000:.4f} | {p*1000:.4f} | {l:.4f} |']
        hits=[str(i+1) for i,r in enumerate(d['stage_radius_m']) if r<=.000200001]
        text += ['',f'Racks at the 0.2 mm floor: {", ".join(hits) or "none"}. This bound hit is in the tested reference; it does not establish an optimized radius.','',
                 'Path/closure margins outside tolerance: '+(', '.join(f'{k}={v:.5g}' for k,v in best['margins'].items() if v < -1e-6) or 'none')+'.','']
        text += ['Largest installed mass contributions (before margin except the margin entry):','', '| Component | Mass, t |','|---|---:|']
        for k,v in sorted(best['masses_kg'].items(),key=lambda kv:-kv[1])[:10]:
            text += [f'| {k.replace("_"," ")} | {v/1000:.1f} |']
        text += ['']
    text += ['## Why radius and pitch compete','',
             '![Frozen-state geometry trade](fixed_state_trade.png)','',
             'This calculation holds front-rack solid inventory and a representative completed-trial state fixed: 458 Pa, 1,339 K gas, 436 K metal. The left panel evaluates exchange at 18 kg/s; it does not assert that every geometry can pass that flow. The right panel finds flow for a 20% pressure drop, omitting points above Re=75. Dashed curves extrapolate geometry beyond the illustrated low-Re anchors. Integer row rounding causes small ripples. Reproduce with `python -m atmo_scoops.transient.rack_trade_plot`.','']
    ref=Path('results/transient/high_isp_rack_refined.json')
    if not ref.exists():ref=Path('results/transient/high_isp_rack.json.gz')
    if ref.exists():
        r=read_result(ref)
        text += ['## Independent compact-bank 4,000 s reference','',
                 f'Dry mass {r["dry_kg"]/1000:.1f} t; liquid {r["net_liquid_kg"]:.2f} kg/orbit; diagnostic mass/production ratio {r["diagnostic_payoff_days"]:.1f} days. Full acceptance: **{r["feasible"]}**. This is a separate declared reference, not a search optimum.', '',
                 f'Minimum numerical gas inventory: {r["audits"]["min_gas_kg"]:.8g} kg (required >−0.0001 kg). Gas-reserve change: {sum(r["closure"]["gas_reserve_species_kg"]):.6g} kg. A diagnostic ratio is not an accepted payoff when any audit fails.', '',
                 f'[Trajectory](../../{ref}) and embedded inputs preserve the exact numerical settings.', '']
    text += ['## Resolution and resistance checks','']
    for label,path in [('Tighter integration','results/transient/wide_rack_refined.json.gz'),('Double hydraulic resistance, unchanged hardware','results/transient/wide_rack_double_loss.json.gz'),('Extended inlet tail (170/150 km)','results/transient/wide_rack_inlet_check.json.gz')]:
        if Path(path).exists():
            rr=read_result(path)
            text += [f'- {label}: dry {rr["dry_kg"]/1000:.1f} t; product {rr["net_liquid_kg"]:.3f} kg/orbit; accepted={rr["feasible"]}; accepted payoff={rr["operating_payoff_days"]}; minimum gas={rr["audits"]["min_gas_kg"]:.6g} kg. [Exact trajectory](../../{path}).']
    text += ['', 'The tighter check uses the corrected interior one-sided control value at both integration event boundaries. This prevents using the pre-burn derivative to start the burn segment. It changes no finite-duration control schedule. Doubling resistance alone leaves thermal conductance unchanged; it is an uncertainty probe, not a calibration of coupled heat/drag behavior.', '', '## Reproduction and limits','',
             '```sh','OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.property_table',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.global_search --config configs/transient_low_re_wide_search.json --output results/transient/rack_wide_optimization --population 8 --generations 1 --workers 4 --seconds 480 --max-new 16 --pitch-max 8 --isp-max 6000',
             '.venv/bin/python -m atmo_scoops.transient.rack_search_report','```','',
             'The search resumes from exact encoded candidates. Use a fresh output directory after changing equations. `done.json` records completion of the declared generations, not mathematical convergence. Numerical limits are 480 s and 160,000 RHS evaluations per trial.','',
             'Unresolved priorities are robust trace-inventory integration, more effective exploration around feasible seeds, broader sparse-bank evidence, and thermal uncertainty. The radius floor was tested, but no claim of a global optimum follows from a small population in 55 dimensions. The tighter check passes; the extended-inlet check changes production by only about 0.002%, but fails the 0.1 g nonnegative-inventory tolerance. That numerical defect remains unresolved and is not silently accepted.','',
             'The pressure/heat law is a reduced continuum array model with an existing molecular heat-transfer resistance; hydraulic slip is not validated. Compressor maps, support structure, repeated deployment and circular-apogee export remain separate physical uncertainties.']
    (out/'RESULTS.md').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
