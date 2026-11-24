# Incremental constrained optimization around the pressure-raised candidate

This investigation adds design freedom in two gated steps. It does not change
v1.0.1 or claim a released v1.0.2 design.

## Stage A: total rack mass with fixed allocation

Starting point: the feasible +5% receiver-pressure candidate from
[pressure continuation](../pressure_continuation/RESULTS.md).

Four outer coordinates are exposed:

1. Total solid-rack mass, within ±10% of the starting candidate; all five physical
   mass fractions remain fixed. Sheet thickness, gaps, rows and materials remain
   fixed. Rack lengths, areas, mechanism masses and packing are derived again.
2. Perigee offset, within ±0.5 km.
3. Initial reserve mass offset, within ±300 kg.
4. Initial reserve temperature offset, within ±15 K.

The last three restore filling and periodic reserve state; they are not extra
physical equipment. Every candidate still compiles hardware and integrates one
forward orbit. All other hardware groups retain their pressure-continuation
sizes for compressor/plant capacities, solar area, battery energy and thermal
stores. Thruster power/mass still follows the orbit/drag calculation, and
bus/battery-discharge ratings follow that demand. Battery mass is still the
larger of its energy- and power-sizing requirements. These are derived costs,
not additional search coordinates.

## Stage B: add receiver working pressure

Only after Stage A successfully terminates and passes a tighter replay, add a
fifth coordinate: receiver target pressure, between the original v1.0.1 target
and 20% above it. Maintain the current ratio of receiver/reserve structural
rating to target pressure and charge the resulting shell mass. Other stage
ratings stay fixed; their actual operating pressures remain simulated states.

Re-center the local rack-mass bounds around Stage A's selected input. If a bound
is active, report it: this is a bounded local optimum, not proof of a global
preferred rack mass or pressure. Structural rating is not an independently
optimized technology improvement.

## Numerical contract

SLSQP minimizes diagnostic operating-orbit payoff with explicit constraints.
Receiver filling and reserve closure use guarded versions of the existing
physical tolerance bands: ±25 Pa fill error, ±0.05 kg per reserve species and
±0.5 MJ reserve energy. These leave room for the tighter independent replay
inside the model's original ±50 Pa, ±0.1 kg and ±1 MJ acceptance limits.
Other original inequalities are retained. The liquid-inventory constraint
exposes the cycle's existing 1e-6 kg numerical roundoff allowance.
Nothing can qualify by discarding incident supply or omitting
thrust/thermal/electrical closure.

An earlier attempt imposed exact-zero fill and reserve equalities. It was
interrupted after small backtracking steps despite physically feasible cycles;
its history is retained in `rack_mass_exact_equalities`. That is not a
converged result. A subsequent guarded-band attempt also backtracked. A small
reproducer then identified a driver bug: SLSQP received a strided objective
gradient from a transposed Jacobian. Identical values in contiguous memory give
the correct downhill direction. Both early attempts are superseded; their
behavior cannot establish a physical or closure limitation. The corrected
search uses contiguous Jacobian rows, covered by an optimizer regression test.
Signed upper/lower fill constraints also avoid differentiating an absolute-value
cusp at zero fill error. The guarded-band run can reuse its physical trajectories,
but recomputes all constraint values under the new contract.

Cached finite-difference objective/constraint Jacobians share the same forward
cycles. Probe steps are explicit: rack-mass ratio 0.005, perigee 0.005 km,
reserve mass 2 kg, reserve temperature 0.2 K, and (when enabled) target-pressure
ratio 0.002. Independent probes run as subprocesses. Any unresolved numerical
exception stops the optimizer; no fabricated penalty or infeasibility replaces it.

Final search resolution is rtol=1e-7 and max_step=5 s, with 501 requested history
samples plus the integrator/event histories. Each solve allows 20 SLSQP
iterations and uses ftol=0.005 days. Actual termination flags, function evaluations,
all forward configurations, bound hits and physical margins are recorded.
A tighter replay, not merely a success flag, gates the next stage.

The first corrected-layout search used smaller derivative probes and a
1e-4-day tolerance. It reached feasible points around 309.22 days but was
interrupted as changes approached the observed 0.001–0.003-day numerical
variation. Its full history remains in `rack_mass_contiguous`. The final
rack-mass solve restarts from a feasible point in that history with the same
original base and bounds, larger probes and a 0.005-day objective tolerance.
This changes search resolution, not the physical acceptance conditions.

A larger-probe run at the original integration resolution still encountered
closure noise. A same-input check at rtol=1e-7 changed nitrogen closure by
11.8 g, enough to move the candidate across the guarded band, while changing
payoff by only 0.00096 days. `rack_mass_resolved/resolution_check.json` retains
both results. That run was interrupted, and `rack_mass_precise` restarts from
the checked point at the higher resolution. Independent replay uses rtol=1e-8,
max_step=2.5 s. These resolution changes leave physical tolerances unchanged.
The named histories retain the unsuccessful attempts; they are not reported as
converged results.

## Reproduction

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/run.py --config results/transient/pressure_continuation/p105/selected_config.json --output results/transient/reduced_optimization/rack_mass_precise --start-x '[1.0714397223494045,-0.055723919145892045,0.04676802453144999,-0.02620039591967816]'
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/replay.py results/transient/reduced_optimization/rack_mass_precise
# Continue only if both commands succeeded:
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/run.py --config results/transient/reduced_optimization/rack_mass_precise/selected_config.json --output results/transient/reduced_optimization/pressure --pressure
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/replay.py results/transient/reduced_optimization/pressure
.venv/bin/python investigations/reduced_optimization/report.py
```

Named manifests, evaluation histories, selected configurations and trajectories
are retained. Per-evaluation cache/worker files follow the existing ignore rules.

## Widened-bound continuation

The [bound continuation report](WIDENED_BOUNDS.md) separates search boundaries
from physical path constraints. The first continuation changes only the rack
mass ratio range from 0.9–1.1 to 0.25–1.5, and the initial-reserve offset from
±300 kg to −1,500/+2,000 kg. Both use the same original coordinate reference;
all five rack mass fractions remain fixed. Other search bounds initially stay
unchanged so their influence can be identified explicitly.

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/run.py --config results/transient/reduced_optimization/rack_mass_precise/selected_config.json --output results/transient/reduced_optimization/pressure_wide_mass_reserve --pressure --bounds-file investigations/reduced_optimization/widened_bounds.json --start-x '[0.9,-0.43712642905763044,0.2999999999951246,0.08330281602113514,1.107143672435058]'
# After successful termination:
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/replay.py results/transient/reduced_optimization/pressure_wide_mass_reserve
.venv/bin/python investigations/reduced_optimization/report_widened.py
```

Use a fresh output directory for a new manifest/runner version. Cached physical
trajectories can be reused only with identical compiled inputs and model code.

The first widened run was stopped after it backtracked near the capture
transition. Its 2.55-tonne forward rack-mass probe was too broad for local
refinement. The continuation below keeps the same bounds and physical model,
uses a 0.255-tonne mass probe and rtol=1e-8, and starts from a saved point in
that run. The independent replay automatically uses a tenfold tighter rtol
(1e-9 for this continuation). The first attempt is retained as unconverged.

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/run.py --config results/transient/reduced_optimization/rack_mass_precise/selected_config.json --output results/transient/reduced_optimization/pressure_wide_refined --pressure --bounds-file investigations/reduced_optimization/widened_bounds.json --start-x '[0.8790314026790359,-0.49999999999653016,0.34812853070747946,0.09613379864315273,1.1256625856236222]' --rtol 1e-8 --rack-step .0005
# After successful termination:
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/replay.py results/transient/reduced_optimization/pressure_wide_refined
PYTHONPATH=. .venv/bin/python investigations/reduced_optimization/report_widened.py
```

The fine-gradient run was also interrupted while backtracking from an unclosed
seed. `restore_seed.py` uses its already-computed Jacobian for one Newton
correction of the three closure coordinates, verifies that seed with one
forward cycle, and records the complete correction. The final optimizer again
frees all five coordinates with exactly the same widened bounds.

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/restore_seed.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/run.py --config results/transient/reduced_optimization/rack_mass_precise/selected_config.json --output results/transient/reduced_optimization/pressure_wide_closed --pressure --bounds-file investigations/reduced_optimization/widened_bounds.json --start-x '[0.8790314026790359,-0.49999999999653016,0.3458612535183913,0.09850845881191195,1.1263710468790016]' --rtol 1e-8 --rack-step .0005
# After successful termination:
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/reduced_optimization/replay.py results/transient/reduced_optimization/pressure_wide_closed
PYTHONPATH=. .venv/bin/python investigations/reduced_optimization/report_widened.py
```
