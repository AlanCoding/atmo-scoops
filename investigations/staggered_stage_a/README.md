# Staggered cooling plates: constrained checkpoint A

**Rejected architecture: v1.0.1-rejected-boosted.** These numerical results remain
reproducible but do not describe the agreed valve-connected reserve. See the
[frozen archive](../../docs/design_archive/v1.0.1_rejected_boosted/README.md) and
[replacement design](../../docs/publication/V1_0_1.md).

**COBYLA converged at 275.726 operating-orbit payoff days**, with 100 requested
forward evaluations, status 0, and maximum scaled constraint violation
1.8e-23. It terminated when the trust-region radius reached the configured
0.01 tolerance. This is local constrained convergence, not a global-optimality
certificate. All 100 requested cycles completed; 11 additional initialization
probes were unused by the solver and are separately identified in the replay audit.

The returned point is evaluation 61. The finer-resolution check is feasible at
**275.730 days**: **13,249.48 tonnes dry** and **3,538.13 kg useful liquid per
cycle**. The frozen case 72 remains 278.019 days; the corrected unoptimized seed
is 278.031 days. The endpoint is the operating orbit, not delivered liquid in a
circular apogee orbit. Orbit and hull remain fixed at 85 × 2,000 km, 30 m bore,
31.7 m outside diameter and 317 m length.

## What this checkpoint establishes

Four staggered rows use wider physical channels for friction and smaller
effective thermal spacing for heat transfer. The complete longer core consumes
real chamber volume. Metal mass and wetted area are not multiplied. The front
core is now **3.598 m**, versus 0.896 m in the frozen design. The optimizer keeps
roughly 1.0–1.4 mm sheets; no sheet reaches the 0.2 mm floor.

The geometry explicitly includes 10 m front empty space, actual compressor-bank
lengths and 1 m hatch-equipment buffers. Arbitrary shared front equipment bays
are removed. All other hardware retains its volume charge against the receiver.
The separate 125 m propellant section and five-cycle product storage are later
checkpoints, not credited here.

The payoff change is modest: propulsion and its power system still dominate.
The returned Isp is **1,810.30 s**, with a **1,234.28 s** burn. Useful liquid grows
while total dry mass stays close to the frozen reference. See the full mass table
and exact coordinate values below rather than attributing the payoff gain solely
to plate friction.

## Review assets

- [Rack masses, dimensions, temperatures, pressure losses, full mass budget and closure](OPTIMIZED_REVIEW.md)
- [All 33 independent coordinates, selected values and bounds](VARIABLES.md)
- [Archived scale drawing SVG](../../docs/design_archive/v1.0.1_rejected_boosted/scale.svg) / [PNG](../../docs/design_archive/v1.0.1_rejected_boosted/scale.png)
- [Exact axial length table](../v1_layout/DRAWING_LENGTHS.md)
- [Aft receiver coast draw-down and liquefaction audit](RECEIVER_COAST.md)
- [Cycle P/T/inventory chart](optimized_cycle.png)
- [Pressure-loss / inlet-pressure histories](optimized_pressure.png)
- [Numerical review, including the refined burn-start issue](NUMERICAL_REVIEW.md)
- [Equations and thermal-spacing assumption](../../modeling/metal_coolers/INTERRUPTED_REDUCED_MODEL.md)
- [Offset-row schematic](../../docs/images/staggered_plate_cooler.svg)
- [Grouped implementation plan](../../local-issue-drafts/specifications/docs/SCALE_REVIEW_IMPLEMENTATION_PLAN.md)
- [Optimizer termination](../../results/transient/staggered/thermal_equivalence/optimization/termination.json), [search manifest](../../results/transient/staggered/thermal_equivalence/optimization/search.json), [selected inputs](../../results/transient/staggered/thermal_equivalence/optimization/selected_config.json), [validation gate](../../results/transient/staggered/thermal_equivalence/selected_validation/gate.json)

## Engineering interpretation

At peak flow, the front rack's modeled drop is about **18% of inlet pressure**;
downstream ratios are far smaller. During low-pressure tails, the front drop
exceeds inlet pressure for about **7.4% of processed throughput**. This prevents
calling the point hydraulically established. The agreed power-only surcharge
remains in use; it does not enforce physically attainable suction flow.

The search fixes all rack frontal areas at the full bore and fixes four rows.
Those choices help impose shallow, wide downstream racks. The review includes a
separate smaller-area packaging screen, with its increased velocity/loss, but
makes no new simulated payoff claim for that arrangement. Low-pressure cutoff,
active area, row count, ducting and deployment deserve a subsequent controlled
study. Thermal-spacing equivalence and offset-entry losses remain reduced-model
assumptions requiring paired validation.

## Numerical checks

The selected point passes conservation and closure at both retained resolutions;
liquid production differs by 0.0017%. Default automatic initialization at refined
tolerance failed exactly at burn start. Explicit initial attempted steps of 1 ms
and 0.1 ms both complete and remain feasible (275.721 and 275.730 days). BDF still
adapts its steps with unchanged error tolerances. The selected fine trajectory
uses 0.1 ms and records that numerical override. No physics or closure criterion
was changed to pass the gate. See the numerical review for the failure evidence.

Repository validation: **158 tests passed**; the audit passed all eight cycle
resolution/conservation checks and the Kepler energy/angular-momentum check.

## Reproduction

Run from the repository root using its local venv. The optimizer command replays
its exact cache when present; use a fresh output directory for a new forward run.

```sh
.venv/bin/python -m atmo_scoops.transient.plate_optimize \
  --config configs/transient_staggered_thermal_seed.json \
  --output results/transient/staggered/thermal_equivalence/optimization \
  --maxiter 300 --tol .01 --rhobeg .03 --seconds 300
PYTHONPATH=. .venv/bin/python investigations/staggered_stage_a/select_terminal.py \
  results/transient/staggered/thermal_equivalence/optimization
PYTHONPATH=. .venv/bin/python investigations/staggered_stage_a/validate_start_step.py \
  --config results/transient/staggered/thermal_equivalence/optimization/selected_config.json \
  --output /tmp/staggered-check.json --first-step-s 0
PYTHONPATH=. .venv/bin/python investigations/staggered_stage_a/validate_start_step.py \
  --config results/transient/staggered/thermal_equivalence/optimization/selected_config.json \
  --output /tmp/staggered-check-refined.json --first-step-s .0001 --refine
PYTHONPATH=. .venv/bin/python investigations/staggered_stage_a/report.py \
  results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz \
  --output investigations/staggered_stage_a/OPTIMIZED_REVIEW.md
PYTHONPATH=. .venv/bin/python investigations/staggered_stage_a/draw_checkpoint.py \
  results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz \
  --output /tmp/rejected-staggered-scale.svg
```

Earlier `checkpoint_a/` searches used the superseded wide-channel thermal
approximation. They are retained as provenance, not candidate results for this
question. The frozen v1.0 numerical reference is unchanged. Parent checkpoint:
`da7a790`.
