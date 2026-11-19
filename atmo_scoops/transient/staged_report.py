"""Summarize sequential stages without treating unresolved trajectories as optima."""
import json
from pathlib import Path
ROOT=Path('results/transient/staged')

def rows(name):
    p=ROOT/name/'evaluations.json';return json.loads(p.read_text()) if p.exists() else []

def main():
    text=['# Staged numerical results','',
          'This is the preserved zero-loss/full-loss staging study. The current active reference is the subsequent [1% resistance continuation](REDUCED_LOSS.md). This earlier study retained gaseous propellant bypass, finite cooling and all system budgets, but disabled rack losses in its accepted reference. The earlier joint lattice search remains experimental.','',
          'All payoffs below are **operating-orbit** dry-mass payoff. Circular-apogee export is not included. These are bounded local searches and declared coupled proposals, not proofs of a global optimum.','',
          '## Run status','', '| Study | Evaluations | Complete | Physically feasible | Numerical errors |','|---|---:|---:|---:|---:|']
    names=['bypass','bypass_search','bypass_reboost','bypass_verify','loss_fixed','loss_fixed_extended','loss_reboost','loss_search','loss_verify','pitch_search','pitch_verify','radius_search','radius_verify','segmentation_probe']
    for name in names:
        rs=rows(name)
        if rs:text += [f'| {name} | {len(rs)} | {sum("audits" in r for r in rs)} | {sum(r["feasible"] for r in rs)} | {sum(bool(r.get("error")) for r in rs)} |']
    text += ['', '## Physically feasible completed trajectories','', 'Passing the physical checks for one trajectory is not the numerical release gate. Only the bypass reference has passed paired resolution checks; head-loss figures below remain provisional.', '', '| Case | Dry mass, t | New liquid, kg/orbit | Payoff, days |','|---|---:|---:|---:|']
    for name in ['bypass','bypass_search','bypass_reboost','bypass_verify','loss_fixed','loss_fixed_extended','loss_reboost','loss_search','loss_verify','pitch_search','pitch_verify','radius_search','radius_verify','segmentation_probe']:
        accepted=[r for r in rows(name) if r['feasible']]
        if accepted:
            r=min(accepted,key=lambda r:r['operating_payoff_days'])
            text += [f'| {name}: {r["name"]} | {r["dry_kg"]/1000:.1f} | {r["net_liquid_kg"]:.2f} | {r["operating_payoff_days"]:.3f} |']
    text += ['', '## Numerical release gates','']
    for name in names:
        p=ROOT/name/'gate.json'
        if p.exists():
            g=json.loads(p.read_text());text += [f'- **{name}: {"PASS" if g["passed"] else "NOT PASSED"}** — '+', '.join(f'{k}: {v}' for k,v in g['checks'].items())+'.']
    progress=ROOT/'progress.json'
    if progress.exists():text += ['', '## Original study disposition (superseded by reduced-loss continuation)', '',json.loads(progress.read_text())['disposition'],'']
    text += ['## Gas bypass through the cycle','', '![Validated gas and liquid inventories](bypass_cycle.png)','', 'The shaded interval is the prescribed burn. Gas is stored for the next pass; no future capture is borrowed to pay the current burn. Reproduce with `python -m atmo_scoops.transient.staged_plot`.','', '## What was optimized','',
             'The fixed-geometry coordinate search changes Isp, burn duration, solar area, battery energy and power ratings, bus rating, warm-store mass, warm-radiator area, and plant flow/electrical ratings. It polls ±12%, then ±6%, testing any combined favorable directions in an additional full trajectory. No installed capacity changes during a forward evaluation. Radius, pitch, rack inventories, chamber clear depths, orbit, material assumptions and gas-feed component capabilities remain fixed in that local search.','',
             'Separate declared Isp proposals scale energy and peak-power capacities before integration, and preserve the ratio of gas reserve to required propellant. These provide coupled feasible directions that an independent coordinate poll can miss; they are not an inner hardware-sizing loop.','',
             'The initial gas-bypass baseline passed at 304.321 days and 304.319 days under tighter integration. The wider 2,100 s Isp proposal timed out; it is explicitly unresolved rather than assigned an infeasible physical interpretation or a payoff.','',
             '## Reproduction','', '```sh',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action baseline',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action optimize --output results/transient/staged/bypass_search --rounds 2',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action reboost --output results/transient/staged/bypass_reboost --isps 1500 2100 2600 --workers 3',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config configs/transient_staged_bypass.json --output results/transient/staged/bypass_verify',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action reboost --config configs/transient_staged_loss_refined.json --output results/transient/staged/loss_reboost --isps 2400 3200 4000 --workers 3 --seconds 900',
             'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config configs/transient_staged_loss_repaired.json --output results/transient/staged/loss_verify --workers 2 --seconds 900',
             '.venv/bin/python -m atmo_scoops.transient.staged_report', '```','',
             'Each result directory stores exact candidate input files and compressed histories for completed trajectories. Existing evaluations are cached: use a new output directory to repeat a run, especially after changing equations or numerical settings. Manually stopped stagnating trajectories have explicit unresolved records and no fabricated histories. `configs/transient_active.json` names the promoted reference; default `python -m atmo_scoops.transient` now reads it.','',
             'The [stage plan](README.md) defines what remains fixed and the pitch/radius release order. The [gas-feed dossier](../../modeling/propellant_feed/GAS_RESERVE.md) gives the propellant path, hardware and energy accounting.']
    Path('investigations/staged_refinement/RESULTS.md').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
