"""Generate the plate investigation from exact solver records."""
import json
from pathlib import Path

def main():
    root=Path('results/transient/plates');folder=root/'cobyla_stable'
    text=['# Parallel plates and the nonlinear constrained optimizer','',
    'The preceding rod/pitch study used a finite pattern search. It was not evidence that a nonlinear constrained optimizer had converged, nor that the power-only approximation cured the forward solver. The minimum-five-row rejections concerned thick rods and combined geometries, not a selected 0.2 mm radius.','',
    'This investigation uses [parallel-plate coolers](../../modeling/metal_coolers/PLATES.md) and `scipy.optimize.minimize(method="COBYLA")`, with a separate vector of forward-cycle inequality constraints. All resistance is at 100% of the plane-Poiseuille formula, charged as extra compressor electricity; suction pressure is unchanged.','',
    '## Solver result','', 'The original run stopped on evaluation 14 with a HEOS pressure-flash error at about 0.008 Pa. A density-based HEOS update fixed that exact case without replacing real-gas caloric properties; it passed the paired resolution check. A second failure involved exactly zero species in a three-species HEOS backend during a near-vacuum implicit-solver trial. Routing to the actual nonzero-species backend fixed it; both resolutions completed with consistent physical infeasibility. This report uses `cobyla_stable`, whose requested vertices were recomputed under both fixes, and preserves both interrupted runs separately.','']
    p=folder/'termination.json'
    text += ['```json',json.dumps({k:v for k,v in json.loads(p.read_text()).items() if k!='x'},indent=2) if p.exists() else '{"status": "running"}','```','']
    rows=json.loads((folder/'evaluations.json').read_text()) if (folder/'evaluations.json').exists() else []
    good=[r for r in rows if r.get('feasible')]
    text += [f'Logged evaluations: {len(rows)}. Complete forward cycles: {sum("audits" in r for r in rows)}. Feasible cycles: {len(good)}. Numerical or input failures: {sum(bool(r.get("error")) for r in rows)}.','']
    if good:
        selection=json.loads((root/'reference_selection.json').read_text()); b=selection['nominal'];d=b['inputs']['design'];m=b['loss_power_audit']
        text += [f'Validated working reference (actual optimizer-history evaluation): {b["index"]}; **{b["operating_payoff_days"]:.3f} days** operating-orbit payoff; dry mass **{b["dry_kg"]/1000:.1f} t**, product **{b["net_liquid_kg"]:.1f} kg/orbit**. This is not delivered circular-apogee payoff.','',f'Added friction electricity: {m["loss_electric_MWh"]:.4f} MWh/orbit; ordinary compressor electricity: {m["base_compression_MWh"]:.4f} MWh/orbit. Ratio: **{100*m["energy_ratio"]:.1f}%** across the train, **{100*m["stage_energy_ratios"][0]:.1f}%** for the front stage.','', '| Stage | Full thickness, mm | Clear gap, mm | Center pitch, mm | Axial stack depth, m | Initial K |','|---|---:|---:|---:|---:|---:|']
        for i,(t,g,z,T) in enumerate(zip(d['plate_thickness_m'],d['plate_gap_m'],d['rack_depth_m'],d['rack_initial_K'])):text.append(f'| {i+1} | {1000*t:.4f} | {1000*g:.4f} | {1000*(t+g):.4f} | {z:.4f} | {T:.3f} |')
        text += ['', f'Optimized controls/capacities: Isp {d["isp_s"]:.2f} s; burn {d["burn_s"]:.2f} s; solar {d["solar_area_m2"]:.0f} m²; battery {d["battery_MWh"]:.3f} MWh; warm store {d["warm_store_kg"]/1000:.2f} t; warm radiator {d["warm_radiator_m2"]:.0f} m² physical panel area. Dive motor ratings {d["motor_MW"]} MW; coast motor {d["coast_motor_MW"]:.3f} MW.', '']
        manifest=json.loads((folder/'search.json').read_text())
        hits=[q['key'] for q,x in zip(manifest['coordinates'],b['x']) if x<1e-5 or x>1-1e-5]
        text += ['Coordinates at a declared search bound (within 1e-5 in unit coordinates; initial rack temperatures are near the 300 K lower bounds): '+(', '.join(hits) if hits else 'none')+'.', '']
        text += ['', 'Closure residuals (limits: rack 500 J/kg; battery/warm store 100 MJ; chamber gas 0.1 kg / 0.01 MJ; rotors 0.01 MJ; impulse relative 1e-4; gas reserve 0.1 kg/species and 1 MJ):','', '```json',json.dumps(b['closure'],indent=2),'```','',f'Minimum scaled constraint margin: {min(b["constraints"]):.8g}.','']
    if (root/'reference_selection.json').exists():
        sel=json.loads((root/'reference_selection.json').read_text())
        text += ['## Reference selection and resolution check', '', 'COBYLA returned evaluation 98 at 277.6608 days. Its refined simulation completed, but battery closure was -103.286 MJ against the unchanged 100 MJ limit (nominal -97.509 MJ). It is therefore not the released reference. We selected the lowest-payoff feasible point from the actual optimizer history with at least 20 MJ nominal reserve inside that limit, without adjusting any inputs. This is a nearby validated feasible design, not the exact returned local optimum. All three resolutions must pass the same physical, closure and conservation gates. The rule is implemented in `plate_reference.py`.', '', '```json', json.dumps(sel['validation'],indent=2), '```', '']
    text += ['## Reproduction and scope','',
    'The 33 scalar coordinates are five gaps, five full thicknesses, five metal inventories, five initial metal temperatures, solar area, battery energy, warm-store mass, warm-radiator area, plant flow and electrical ratings, four dive motor ratings, coast motor rating, thruster Isp and burn duration. Diameter, length, orbit, suction capacities, compressor head capability, vessel ratings and processing schedule stay fixed. Fixed-thickness mode is also available.','',
    'Coordinates are logarithmically scaled to unit bounds. The initial trust-region radius is 0.03 and terminal radius 0.01; the latter is a few percent in some physical dimensions, not a high-precision optimum. Constraint tolerance is 1e-7 in scaled coordinates. The 300-evaluation maximum is an emergency budget, not a success condition. Numerical failures terminate the run explicitly. Each candidate runs once; paired resolution checks are separate validation, not inner closure iterations.','',
    '```sh',
    'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action baseline --config configs/transient_plates_seed.json --output results/transient/plates/seed --workers 2 --seconds 300',
    'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.plate_optimize --config configs/transient_plates_optimization_seed.json --output results/transient/plates/cobyla_stable --maxiter 300 --tol 0.01 --rhobeg 0.03 --seconds 240',
    'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.plate_reference',
    '.venv/bin/python -m atmo_scoops.transient.plate_report',
    '```','']
    for p in root.glob('*/gate.json'):text += [f'Numerical gate `{p.parent.name}`:', '```json',p.read_text().strip(),'```','']
    out=Path('investigations/plates');out.mkdir(exist_ok=True);(out/'README.md').write_text('\n'.join(text))

if __name__=='__main__':main()
