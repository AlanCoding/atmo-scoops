# Incremental optimization results

The accepted v1.0.1 publication remains unchanged. These are scoped local constrained searches around the feasible pressure-continuation candidate. See [method and bounds](README.md).

| Stage | Solver success | Iterations | Forward configurations | Search days | Replay days | Replay feasible | Bound hits |
|---|---|---:|---:|---:|---:|---|---|
| rack_mass_precise | True | 1 | 5 | 309.214110 | 309.214393 | True | none |
| pressure | True | 3 | 19 | 289.571165 | 289.571360 | True | total_rack_mass_ratio, reserve_delta_1000kg |

## Comparison on the operating-orbit metric

| Configuration | Dry mass t | Net liquid kg/orbit | Payoff days |
|---|---:|---:|---:|
| Published v1.0.1 replay | 12,840.22 | 3,085.886 | 306.3987 |
| +5% pressure-continuation seed | 13,351.93 | 3,167.160 | 310.4285 |
| rack_mass_precise, tighter replay | 13,428.81 | 3,197.887 | 309.2144 |
| pressure, tighter replay | 13,561.34 | 3,448.364 | 289.5714 |

The continuation seed has enlarged installed hardware relative to the publication reference. These searches retain those capacities. A difference from the published payoff is therefore not an isolated rack-mass or pressure effect. The seed was restored near zero fill error; optimization can use the guarded ±25 Pa band. Improvements combine mass, perigee and reserve-state adjustment, including that filling allowance. Delivery/circularization is not newly credited.

## Selected physical inputs

| Stage | Rack total t | Receiver target kPa | Receiver/reserve rating kPa | Perigee km | Initial reserve kg | Initial reserve K |
|---|---:|---:|---:|---:|---:|---:|
| rack_mass_precise | 509.8463 | 5.005174 | 6.825000 | 85.598073 | 3719.867351 | 340.326647 |
| pressure | 458.8617 | 5.541447 | 7.556256 | 85.160946 | 4019.867351 | 348.656929 |

Rack mass fractions remain fixed. The pressure stage adds exactly one independent scalar; structural rating follows a fixed target/rating ratio. Solar area, battery energy and processing/thermal capacities retain the continuation sizes; thrust hardware and bus/discharge ratings still follow demand. All constraints and their limiting values are retained in the linked summaries.


## Fixed rack allocation

| Rack | Fixed fraction | rack_mass_precise mass t | pressure mass t |
|---|---:|---:|---:|
| 1 | 84.13614% | 428.965 | 386.069 |
| 2 | 5.87650% | 29.961 | 26.965 |
| 3 | 2.84967% | 14.529 | 13.076 |
| 4 | 2.60128% | 13.263 | 11.936 |
| 5 | 4.53641% | 23.129 | 20.816 |

## rack_mass_precise: termination and acceptance

Solver message: **Optimization terminated successfully**.

Selected fill error: **24.979216 Pa**. Original model feasible: **True**.

Tighter replay: dry mass **13,428.811 t**, net liquid **3,197.887252 kg/orbit**, fill error **24.978747 Pa**, total reserve mass error **-0.059692 kg**, reserve energy error **0.490899 MJ**.
Capture: **99.98013%**; minimum propulsion reserve: **2223.9900 kg**. Original failed constraints: `{}`. Change from search payoff: **+0.000283 days**.

- [Termination](../../results/transient/reduced_optimization/rack_mass_precise/termination.json).
- [Manifest and bounds](../../results/transient/reduced_optimization/rack_mass_precise/manifest.json).
- [Evaluation history](../../results/transient/reduced_optimization/rack_mass_precise/evaluations.json).
- [Selected inputs](../../results/transient/reduced_optimization/rack_mass_precise/selected_config.json).
- [Tighter replay](../../results/transient/reduced_optimization/rack_mass_precise/replay_summary.json).

## pressure: termination and acceptance

Solver message: **Optimization terminated successfully**.

Selected fill error: **24.998776 Pa**. Original model feasible: **True**.

Tighter replay: dry mass **13,561.341 t**, net liquid **3,448.364190 kg/orbit**, fill error **24.997991 Pa**, total reserve mass error **0.066888 kg**, reserve energy error **-0.501212 MJ**.
Capture: **99.97952%**; minimum propulsion reserve: **2404.0747 kg**. Original failed constraints: `{}`. Change from search payoff: **+0.000195 days**.

- [Termination](../../results/transient/reduced_optimization/pressure/termination.json).
- [Manifest and bounds](../../results/transient/reduced_optimization/pressure/manifest.json).
- [Evaluation history](../../results/transient/reduced_optimization/pressure/evaluations.json).
- [Selected inputs](../../results/transient/reduced_optimization/pressure/selected_config.json).
- [Tighter replay](../../results/transient/reduced_optimization/pressure/replay_summary.json).

## Scope of the result

A successful termination is a bounded local result with this fixed allocation and these hardware capabilities, not a certified global optimum. An active rack-mass bound is reported rather than silently widened. The second stage is only authorized by successful first-stage termination and tighter feasibility. No surrogate correction, fabricated numerical penalty or hidden cycle-to-cycle iteration is used. The original full-capture tolerance remains enforced.

The pressure result reaches the lower rack-mass bound and the upper initial-reserve-mass bound. Those are local experiment bounds, not material or tank-capacity limits. In particular, the initial gas inventory is a cycle-closure coordinate. A continuation with wider rack/closure-state bounds should precede treating 5.54 kPa as an engineering optimum or adding further design variables. The result nevertheless demonstrates successful constrained optimization with both total rack mass and pressure free; the stage fractions never changed.

## Numerical qualification

The high-resolution rack solve is a warm-started convergence confirmation, not the entire cost of finding its candidate. Earlier histories in `rack_mass_exact_equalities`, `rack_mass`, `rack_mass_contiguous` and `rack_mass_resolved` preserve the development attempts. The first two used a strided objective gradient and are superseded by the contiguous-array fix. The latter two were interrupted while diagnosing derivative/integration resolution. Their termination is not reported as convergence.

At identical inputs, reducing rtol from 1e-5 to 1e-7 changed nitrogen closure by 11.8 g but payoff by less than 0.001 day. Final searches therefore use rtol=1e-7 and replay uses 1e-8. SLSQP objective tolerance is 0.005 days. The guarded closure bands remain stricter than the original physical acceptance limits. See [method and reproducible restart](README.md).

The full 175-test suite and conservation/Kepler audit passed; focused reduced-coordinate/optimizer tests were rerun after the driver changes. The array-layout regression exercises SLSQP itself. Each accepted replay also records species/energy conservation, reserve availability and capture.
