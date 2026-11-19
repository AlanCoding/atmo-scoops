"""Report finite-budget power-only searches and their resolution gates."""
import gzip
import json
from pathlib import Path
import numpy as np

ROOT=Path('results/transient/power_only')

def main():
    text=['# Power-only resistance: pitch and radius searches','',
          'The owner requested 10% and 100% resistance as an added compressor electricity charge, releasing pitch first and radius second. These runs use the [power-only cycle implementation](../../modeling/metal_coolers/POWER_ONLY.md); they do not lower suction pressure or solve a hydraulic root. Each candidate is a single forward cycle with finite installed hardware, energy/species conservation and periodic constraints.','',
          'These are bounded pattern searches, **not certified global optima or stationarity proofs**. Search completion, numerical resolution, and physical feasibility are separate results. All payoffs are operating-orbit production; circular-apogee delivery remains unmodeled.','',
          '## Results','',
          '| Stage | Completed / evaluated | Feasible | Best payoff, days | Loss / all compression energy | Loss / first-stage compression energy |','|---|---:|---:|---:|---:|---:|']
    selected=[]
    for name in ('seed_0.1','seed_1','seed_1_repaired','pitch_0.1','pitch_1','radius_0.1','radius_1'):
        folder=ROOT/name;p=folder/'evaluations.json'
        if not p.exists():continue
        rows=json.loads(p.read_text());good=[r for r in rows if r.get('feasible')]
        if good:
            best=min(good,key=lambda r:r['operating_payoff_days']);m=best['loss_power_audit']
            text.append(f'| {name} | {sum("audits" in r for r in rows)} / {len(rows)} | {len(good)} | {best["operating_payoff_days"]:.3f} | {100*m["energy_ratio"]:.1f}% | {100*m["stage_energy_ratios"][0]:.1f}% |')
            if name.startswith(('pitch_','radius_')):selected.append((name,best))
        else:text.append(f'| {name} | {sum("audits" in r for r in rows)} / {len(rows)} | 0 | — | — | — |')
    text+=['','A loss/base ratio of 200% means the loss charge alone is twice ordinary compression electricity. It is not the fraction of total including loss. Ordinary compression excludes refrigeration, rotor spin-up and idle draw.','',
           '## Selected geometry and loss power','']
    for name,r in selected:
        d=r['inputs']['design'];m=r['loss_power_audit'];text += [f'### {name}', '',f'Candidate `{r["name"]}`; dry mass {r["dry_kg"]/1000:.1f} t; net liquid {r["net_liquid_kg"]:.1f} kg/orbit. Loss {m["loss_electric_MWh"]:.4f} MWh/orbit; ordinary compression {m["base_compression_MWh"]:.4f} MWh/orbit; peak combined loss power {m["peak_loss_MW"]:.3f} MW.','',
            '| Rack, front to rear | Radius, mm | Pitch, mm | Loss / stage compression energy |','|---|---:|---:|---:|']
        rr=d.get('stage_radius_m') or [d['rod_radius_m']]*5;pp=d.get('stage_pitch_m') or [d['rod_pitch_m']]*5
        for i,(rad,pit,ratio) in enumerate(zip(rr,pp,m['stage_energy_ratios'])):text.append(f'| {i+1} | {rad*1000:.3f} | {pit*1000:.3f} | {100*ratio:.2f}% |')
        p=Path(r['trajectory'])
        with gzip.open(p,'rt') as f:traj=json.load(f)
        loss=np.array(traj['history']['rack_loss_MW']);base=np.array(traj['history']['stage_compression_base_MW']);mask=base.sum(axis=1)>1.
        peak=float((loss.sum(axis=1)[mask]/base.sum(axis=1)[mask]).max()) if mask.any() else 0.
        text+=['',f'Instantaneous peak loss/base for the complete train, requiring ordinary compression above **1 MW**, is **{100*peak:.1f}%**. Very large ratios at nearly zero ordinary head are excluded from this statistic; all energy remains in the cycle totals.','']
        if min(rr)<=.0002*(1+1e-8):text+=['**The 0.2 mm radius floor is reached in this candidate.**','']
        else:text+=['The 0.2 mm radius floor is not reached in this candidate.','']
        if max(rr)>=.005*(1-1e-8):text+=['**The 5 mm search ceiling is reached; this is a bound, not a demonstrated material optimum.**','']
    text+=['## Large-loss cases among feasible completed trials','',
           '| Search | Largest train loss/base energy | Payoff of that case, days | Selected best? |','|---|---:|---:|---|']
    for name,best in selected:
        rows=json.loads((ROOT/name/'evaluations.json').read_text());good=[r for r in rows if r.get('feasible')]
        extreme=max(good,key=lambda r:r['loss_power_audit']['energy_ratio'])
        text.append(f'| {name} | {100*extreme["loss_power_audit"]["energy_ratio"]:.1f}% | {extreme["operating_payoff_days"]:.3f} | {"yes" if extreme["name"]==best["name"] else "no"} |')
    text+=['## Unresolved evaluations and geometry rejections','', '| Search | Forward timeouts | Geometry/input rejections |', '|---|---:|---:|']
    for name,_ in selected:
        rows=json.loads((ROOT/name/'evaluations.json').read_text())
        text.append(f'| {name} | {sum("exceeded" in r.get("error","") for r in rows)} | {sum(bool(r.get("error")) and "exceeded" not in r["error"] for r in rows)} |')
    text+=['', 'Row-count rejections enforce the existing minimum of five physical rows for the bank correlation. They are not integration failures. Timeout cases remain unresolved and prevent claims of an exhaustive local poll.', '', '## Resolution gates','']
    for p in sorted(ROOT.glob('verify_*/gate.json')):
        g=json.loads(p.read_text());text += [f'- `{p.parent.name}`: **{"PASS" if g["passed"] else "NOT PASSED"}**. `{json.dumps(g)}`']
    p=ROOT/'disposition.json'
    if p.exists():text+=['',json.loads(p.read_text())['text'],'']
    text+=['## Search definition and reproduction','',
           'The pitch stage releases five independent pitch/radius ratios at fixed 1 mm radius. The radius stage keeps pitch free and adds five radii, 0.2–5 mm. Pitch/radius bounds are 4.01–40. Nominal solid inventory is preserved; integer-row rounding is charged. Geometry changes therefore affect actual rack mass, envelope, gas volume, heat transfer and deployed area. Materials, hull dimensions, orbit, initial rack temperatures, and nominal metal inventory remain fixed.','',
           'Each geometry poll includes single-coordinate moves and common-geometry probes. A subsequent hardware poll varies ten propulsion/electrical/thermal/plant settings and five motor ratings. Individually favorable hardware moves are tested together in another full cycle. One broad geometry/hardware round is a bounded experiment, not evidence of final optimizer convergence. The radius studies additionally test combined favorable geometry moves and dense/thin geometry with increased supporting hardware. The larger allowance increases front motor 50%, warm store 25%, radiator 15%, solar and battery energy 2%, and bus 5%; the lean allowance increases front motor 15%, store 12%, and radiator 6%. These are declared trial directions, not automatic sizing inside a cycle. Exact inputs and all completed/error records are saved with each study.','',
           '```sh',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage pitch --config configs/transient_power_only_0.1.json --output results/transient/power_only/pitch_0.1 --workers 4 --seconds 180',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage pitch --config configs/transient_power_only_1_seed.json --output results/transient/power_only/pitch_1 --workers 3 --seconds 240',
           '# For each factor, release radius using the completed pitch best_config.json:',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_0.1/best_config.json --output results/transient/power_only/radius_0.1 --workers 4 --seconds 240',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_1/best_config.json --output results/transient/power_only/radius_1 --workers 3 --seconds 240',
           '# Full-strength radius hardware poll resumed with --workers 6 --seconds 300; cached geometry trials retained.',
           '# Also test combined favorable geometry moves and supporting-hardware allowances:',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_0.1/best_config.json --output results/transient/power_only/radius_0.1 --workers 4 --seconds 300 --finish-combination',
           'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_1/best_config.json --output results/transient/power_only/radius_1 --workers 4 --seconds 300 --finish-combination',
           '.venv/bin/python -m atmo_scoops.transient.power_geometry_report','```','',
           'Existing evaluations are cached. Use a new directory after changing equations or to repeat the experiment. Selected candidates require paired resolution checks before being accepted. The pressure-coupled active reference is not silently replaced by these power-only experiments.','']
    Path('investigations/staged_refinement/POWER_OPTIMIZATION.md').write_text('\n'.join(text))

if __name__=='__main__':main()
