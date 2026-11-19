"""Report hydraulic continuation without treating timeouts as physics results."""
import json
from pathlib import Path

ROOT=Path('results/transient/loss_continuation')

def main():
    lines=['# Reduced head-loss continuation','',
           'This investigation keeps 1 mm rod radius, 10 mm pitch, rack inventories, geometry and the historical heat-transfer treatment fixed. Gaseous propellant bypass remains enabled. It reduces only the hydraulic resistance coefficient; this is a numerical continuation experiment, not evidence that physical rack resistance is smaller.','',
           '## Equation','',
           '`p_suction² = max(0, p_chamber² − α K_full G² R T)`', '',
           '`G` is mass flux through frontal area. The multiplier α scales the resistance coefficient, including the finite-row exit term. It does not multiply an already-solved pressure drop or the compressor work. Flow and suction pressure are still solved together. As α tends to zero the original zero-loss model is recovered. The optimizer cannot vary α.','',
           '## Results','',
           '| Study / candidate | Complete | Feasible | Operating-orbit payoff, days |',
           '|---|---|---|---:|']
    for name in ('scan','verify_seed','search','verify_best'):
        p=ROOT/name/'evaluations.json'
        if not p.exists():continue
        rows=json.loads(p.read_text())
        shown=rows
        if name=='search':
            good=[r for r in rows if r.get('feasible')]
            shown=[min(good,key=lambda r:r['operating_payoff_days'])] if good else []
        for r in shown:
            payoff=r.get('operating_payoff_days')
            value=f'{payoff:.6f}' if payoff is not None else '—'
            lines.append(f'| {name} / {r["name"]} | {"yes" if "audits" in r else "unresolved"} | {"yes" if r.get("feasible") else "no / unresolved"} | {value} |')
        if name=='search':
            lines+=['',f'Search: {len(rows)} evaluations; {sum("audits" in r for r in rows)} complete, {sum(r.get("feasible",False) for r in rows)} physically feasible, {sum(bool(r.get("error")) for r in rows)} unresolved.', '']
    lines+=['','## Numerical gates','']
    for name in ('verify_seed','verify_best'):
        p=ROOT/name/'gate.json'
        if p.exists():lines.append(f'- {name}: `{json.dumps(json.loads(p.read_text()))}`')
    p=ROOT/'disposition.json'
    if p.exists():lines+=['',json.loads(p.read_text())['text'],'']
    lines+=['## Search scope and reproduction','',
            'A fixed-geometry feasible coordinate poll varies Isp, burn duration, solar area, battery energy and power, bus rating, warm-store mass, radiator area, and plant flow/power. A candidate compiles hardware first and integrates once; no internal resizing or cycle iteration. Jointly favorable coordinate moves require a separate forward evaluation. Conservation, closure and numerical gates are unchanged. Results are local candidates, not global optima. Payoff excludes circular-apogee export.','',
            'Exact inputs, summaries and completed histories are stored under `results/transient/loss_continuation/`. Existing evaluations are cached; use a new output directory for a fresh repetition.','',
            '```sh',
            'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.loss_continuation',
            'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config results/transient/loss_continuation/scan/loss_0.01.inputs.json --output results/transient/loss_continuation/verify_seed --workers 2 --seconds 600',
            'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action optimize --config results/transient/loss_continuation/scan/loss_0.01.inputs.json --output results/transient/loss_continuation/search --workers 4 --seconds 600 --rounds 1 --initial-step .03',
            'OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config configs/transient_loss_continuation.json --output results/transient/loss_continuation/repeat_verification --workers 2 --seconds 600',
            '.venv/bin/python -m atmo_scoops.transient.loss_continuation_report',
            '```','',
            'The saved `verify_best` gate compares the completed search winner with the separately run tighter trajectory in `refined_best`, avoiding a duplicate coarse simulation. The verification command above reproduces both settings from the accepted config.','']
    Path('investigations/staged_refinement/REDUCED_LOSS.md').write_text('\n'.join(lines))

if __name__=='__main__':main()
