# Reduced head-loss continuation

This investigation keeps 1 mm rod radius, 10 mm pitch, rack inventories, geometry and the historical heat-transfer treatment fixed. Gaseous propellant bypass remains enabled. It reduces only the hydraulic resistance coefficient; this is a numerical continuation experiment, not evidence that physical rack resistance is smaller.

## Equation

`p_suction² = max(0, p_chamber² − α K_full G² R T)`

`G` is mass flux through frontal area. The multiplier α scales the resistance coefficient, including the finite-row exit term. It does not multiply an already-solved pressure drop or the compressor work. Flow and suction pressure are still solved together. As α tends to zero the original zero-loss model is recovered. The optimizer cannot vary α.

## Results

| Study / candidate | Complete | Feasible | Operating-orbit payoff, days |
|---|---|---|---:|
| scan / loss_0.01 | yes | yes | 294.251872 |
| scan / loss_0.1 | unresolved | no / unresolved | — |
| scan / loss_0.05 | unresolved | no / unresolved | — |
| verify_seed / check | yes | yes | 294.251872 |
| verify_seed / check_refined | yes | yes | 294.224045 |
| search / r0_combined | yes | yes | 292.846432 |

Search: 22 evaluations; 20 complete, 17 physically feasible, 2 unresolved.

| verify_best / r0_combined | yes | yes | 292.846432 |
| verify_best / loss_0.01 | yes | yes | 292.802384 |

## Numerical gates

- verify_seed: `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 9.457725965238819e-05, "admitted_kg": 4.584401782504484e-05, "lost_kg": 0.00018920756822227004, "propellant_kg": 5.7414673996002994e-15}}`
- verify_best: `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 0.00015043695394707996, "admitted_kg": 7.286296250875638e-05, "lost_kg": 0.00022975643107660525, "propellant_kg": 7.488870521217848e-16}}`

**Accepted numerical continuation reference: 1% resistance coefficient.** The seed gives 294.251872 days; tighter integration gives 294.224045 days. The local search produces **292.846432 days**, checked at **292.802384 days** with tighter integration (0.015% payoff difference). Dry mass is **13,558.2 tonnes**, with **3,409.0 kg new liquid per orbit** at standard resolution. Isp remains **1,765.95 s** and burn duration **1,200 s**. The combined candidate reduces bus rating, warm-store mass, warm-radiator area and plant electrical rating by 3% each. All physical feasibility, cycle closure and numerical audit checks pass at both resolutions.

The search evaluated 22 candidates: 20 completed and two timed out (shorter burn and larger radiator). It is a bounded local improvement, **not a proof of optimizer convergence or a globally reliable search domain**. The seed scan's 5% and 10% cases exceeded 300 s and remain unresolved; they were not shown physically infeasible. No equations were smoothed, no losses were silently removed, and no acceptance tolerances were weakened.

`configs/transient_active.json` and `configs/transient_loss_continuation.json` now select the verified 1% case. The zero-loss comparison remains reproducible from `configs/transient_staged_bypass.json` at 289.75 days. **The multiplier is a numerical stepping stone, not a validated physical drag reduction.** Full-loss hardware performance remains unresolved; pitch and radius are still fixed. A next continuation should step the prescribed multiplier upward from this saved solution, rechecking feasibility and resolution at every accepted level.

## Search scope and reproduction

A fixed-geometry feasible coordinate poll varies Isp, burn duration, solar area, battery energy and power, bus rating, warm-store mass, radiator area, and plant flow/power. A candidate compiles hardware first and integrates once; no internal resizing or cycle iteration. Jointly favorable coordinate moves require a separate forward evaluation. Conservation, closure and numerical gates are unchanged. Results are local candidates, not global optima. Payoff excludes circular-apogee export.

Exact inputs, summaries and completed histories are stored under `results/transient/loss_continuation/`. Existing evaluations are cached; use a new output directory for a fresh repetition.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.loss_continuation
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config results/transient/loss_continuation/scan/loss_0.01.inputs.json --output results/transient/loss_continuation/verify_seed --workers 2 --seconds 600
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action optimize --config results/transient/loss_continuation/scan/loss_0.01.inputs.json --output results/transient/loss_continuation/search --workers 4 --seconds 600 --rounds 1 --initial-step .03
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action verify --config configs/transient_loss_continuation.json --output results/transient/loss_continuation/repeat_verification --workers 2 --seconds 600
.venv/bin/python -m atmo_scoops.transient.loss_continuation_report
```

The saved `verify_best` gate compares the completed search winner with the separately run tighter trajectory in `refined_best`, avoiding a duplicate coarse simulation. The verification command above reproduces both settings from the accepted config.
