# First reduced-coordinate experiment

This is a conservative extension around accepted v1.0.1, not a new design or
replacement optimizer. It adds a coordinate adapter to the existing forward
model; no physical equations, constraints or component capabilities change.

The [completed three-run results](RESULTS.md) reproduce the baseline exactly and show a smooth, feasible ±1% response. The lower-mass point approaches fill/reserve closure bounds, not thermal limits.

## Compartmentalize decisions, not the physical balances

| Category | Treatment in this experiment |
|---|---|
| Architecture and capability assumptions | Frozen to the refined v1.0.1 inputs |
| Rack mass distribution | Five actual **mass** fractions frozen, including different SiC/Al densities |
| Total rack mass | One exposed scalar; baseline and ±1% probes |
| Sheet thickness, gap, row count and materials | Frozen |
| Initial rack, reserve and electrical states | Frozen; endpoint mismatch is reported, not repaired |
| Compressor, propulsion, plant and power capacities | Frozen |
| Rack core depth, area, mechanism mass, packing and receiver volume | Derived again from the proposed total mass |
| Gas/thermal/electrical histories | Integrated through one orbit, as before |

For reference masses m_i, define f_i=m_i/sum(m_i). The reduced coordinate M gives
m_i=f_i M. With material, frontal area, gap and thickness fixed, core depth is
proportional to mass. The adapter therefore scales all five core depths by
M/M_reference. The ordinary hardware compiler handles the consequences. This
reduces five independent rack-inventory coordinates to one; it does **not** claim
that their physical effects are independent of other subsystems.

Keeping fractions fixed is a local scope choice, not evidence that the current
allocation remains optimal after major compressor, material or architecture
changes. Those allocations can be reconsidered in a separate subsystem study.

## Baseline gate and probe interpretation

The adapter must reproduce the exact baseline configuration at its original total
mass. Tests check this identity, immutability, mass fractions, geometry/packing
changes and unchanged non-rack inputs. A fresh refined forward replay is compared
with the frozen trajectory; perturbations are attempted only after that gate.

The ±1% probes deliberately do not restore closure. A lower diagnostic payoff
with an unrecovered battery or reserve is **not** an improved design. We retain
all closure residuals and failed constraints so the next small outer solve can
select genuinely necessary companion coordinates rather than releasing all 46.
No automatic inner resizing, periodic shooting or tolerance relaxation is added.

## Reproduction

Use the repository virtual environment:

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_coordinates/run.py --factor 1
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_coordinates/run.py --factor .99
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_coordinates/run.py --factor 1.01
```

Each run saves its exact config, named compressed trajectory and summary under
`results/transient/reduced_coordinates/`. A 600-second wall-time guard reports an
unresolved evaluation explicitly; it does not convert a timeout into physical
infeasibility. This probe does not yet constitute the full worksheet, correction
map or publication-asset audit from the issue drafts.
