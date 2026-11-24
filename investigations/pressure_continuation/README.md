# Pressure continuation toward v1.0.2

This is an exploratory numerical investigation, not an accepted v1.0.2 release.
The frozen v1.0.1 model, inputs and payoff remain unchanged. No constraints or
physical equations are relaxed.

[Numerical results and termination](RESULTS.md) record the pressure seeds and the bounded restoration.

## Groups exposed by the first experiment

| Group | Current treatment | Possible subsystem optimization |
|---|---|---|
| Receiver working pressure | Test +5% and +10% targets | Outer design choice |
| Atmospheric batch/perigee | Match incident integrated supply to +5%/+10% using a bracketed scalar altitude root | Conditional sizing, then explicit fill/closure restoration |
| Rack allocation | Freeze five physical mass fractions; scale total mass with expected batch | Optimize allocation in a thermal/compressor-chain subproblem; allow total in outer solve |
| Sheet thickness/gaps/rows/materials | Frozen | Validated thermal/hydraulic subproblem, with shared downstream boundary histories |
| Compressor motors and plant throughput/electric rating | Scale with batch as an initial sizing rule | Stage-chain mass/work/head/flow capability response curves |
| Solar, battery energy, waste-heat buffer and radiator | Scale with batch as an initial sizing rule | Time-resolved power/thermal sizing, not an orbit-average energy fit |
| Thrusters | Keep Isp and burn duration; hardware recomputes from changed atmospheric impulse | Coupled Isp/duration/power scheduling subproblem |
| Reserve initial mass | Initially scales with pressure at fixed reserve geometry/temperature | Outer inventory/energy closure, later partition sizing |
| Initial reserve temperature and perigee | Initial temperature fixed; both released for three-coordinate restoration | Explicit closure coordinates, not independent technology improvements |
| Pressure ratings | All stage ratings scale with working-pressure factor | Structural sizing from actual operating envelopes; provisional constant relative margin here |

The two pressure factors also scale total rack mass and expected incident batch
by the same factor. It is an initial extensive scaling rule, not a claim that
constant pressure ratios or identical thermal states will result. Suction volume
capacity and head capacity stay fixed initially because increasing inlet density
can raise mass throughput at similar volumetric flow. This hypothesis is checked
by the transient, not imposed on it. Motor and plant limits may still bind.

Package volumes, rack dimensions, deployment times, receiver gas volume, shell
mass, propulsion and installed bus/discharge rating are recalculated **before**
each integration. An unchanged hull with more packed equipment has less gas
volume; fill mismatch is therefore expected from a naive linear batch seed.

## Numerical sequence

1. Retain the independently reproduced refined v1.0.1 baseline.
2. Generate each pressure/batch-scaled seed. A bracketed root over 80–100 km
   matches integrated atmospheric supply; this inexpensive algebraic step runs
   no transient cycles and does not establish capture or survival.
3. Integrate one refined cycle. Report capture, physical margins, all closure
   residuals and diagnostic payoff. A failed constraint is not hidden by that
   payoff number.
4. On the +5% case, attempt a deliberately small outer least-squares restoration
   of receiver fill error, reserve mass and reserve energy. Its only coordinates
   are perigee, initial reserve mass and initial reserve temperature. Thermal and
   electrical constraints are still checked afterward, not secretly restored.
5. Stop after four outer function evaluations (plus finite-difference probes),
   recording termination and the actual number of cycles. This is not a payoff
   optimizer, and exhausting the evaluation budget is not convergence.

Each cycle has a 600-second guard; numerical failure stops restoration. The
finite differences use 0.002 km altitude, 0.2 kg reserve inventory and 0.02 K
reserve temperature increments. Those steps are an explicit local probe choice,
not a claim of derivative accuracy over all regimes. Raw residuals and evaluated
inputs are retained. Named results are separate from ignored per-evaluation caches.

## Reproduction

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/pressure_continuation/run.py --factor 1.05
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/pressure_continuation/run.py --factor 1.10
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python investigations/pressure_continuation/run.py --factor 1.05 --restore
```

No new architecture or independent pressure history is inserted. Receiver target
is a design input; actual pressure remains an integrated-state consequence.

## Interpreting the first restored candidate

The +5% target reaches physical feasibility through three closure coordinates
with no change to the prescribed rack allocation. All 16 recorded configurations
complete their cycles; the four-iterate restoration budget expires before the
solver certifies its stricter mathematical termination criterion. That budget
status is explicit, not a timeout or unfinished forward evaluation. A tighter
independent replay checks the selected physically feasible point.

The first restoration targets zero fill error, while v1.0.1 uses part of its
allowed positive fill tolerance. This and the scaled-but-unoptimized hardware
prevent interpreting the payoff difference as an optimized marginal cost of
pressure. Higher pressure changes component packing as well as gas density.
The power/thermal and processing groups retain their +5% seed scale even though
restoration changes actual collection. Their sizing is a natural separate
subproblem, with the full transient still checking all shared boundary conditions.
