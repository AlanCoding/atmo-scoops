# Widening the rack-mass and reserve-inventory bounds

These are continuations of the [previous constrained searches](RESULTS.md), using the same five fixed rack mass fractions and one forward cycle per candidate. The accepted v1.0.1 publication remains unchanged.

Only total rack mass and initial reserve gas inventory ranges are widened in the first continuation. Compressor, plant, solar, battery-energy and thermal-store capacities retain their existing sizes. Thrust hardware and bus/discharge ratings remain derived costs. Original physical constraints and closure tolerances remain enforced.

| Search | Solver success | Iterations | Configurations | Replay feasible | Payoff days | Artificial bounds reached |
|---|---|---:|---:|---|---:|---|
| pressure | True | 3 | 19 | True | 289.5714 | total_rack_mass_ratio, reserve_delta_1000kg |
| pressure_wide_mass_reserve | False | — | 35 | Not run | — | none |
| pressure_wide_refined | False | — | 9 | Not run | — | none |
| pressure_wide_closed | True | 1 | 9 | True | 286.7825 | perigee_delta_km |

## Result

The actual five-variable SLSQP search terminated successfully with the rack and initial-reserve bounds inactive. **Perigee reaches its artificial lower search bound, 85.09807 km.** Receiver pressure and initial reserve temperature also remain inside their search ranges. This therefore does not yet establish an altitude optimum limited by hardware or material physics.
The final restart took one SLSQP iteration and nine evaluated configurations, including derivative probes; this excludes the two interrupted attempts and explicit seed correction documented below. The unchanged stopping tolerance is 0.005 days. The result is a local solver-converged point on a fairly flat rack-mass trade, not a certification of global optimality or a uniquely determined rack mass.
The low-metal trial below reveals a cooling/suction-throughput limitation, but that capture constraint is not active at the final point. Installed compressor capabilities remain fixed, so changing those capabilities could move this trade. No physical constraint was relaxed to obtain convergence.
The independent replay uses rtol=1e-9 and a 2.5 s maximum time step, versus rtol=1e-8 and 5 s in the search. It passes all original constraints: **True**. Operating-orbit payoff is **286.783 days**, compared with **289.571 days** before widening these two bounds.

## pressure

Termination: **Optimization terminated successfully**.

### Artificial search bounds

| Coordinate | Lower | Selected | Upper | Unit | At bound? |
|---|---:|---:|---:|---|---|
| Total racks | 458.8617 | 458.8617 | 560.8309 | t | YES |
| Perigee | 85.0981 | 85.1609 | 86.0981 | km | no |
| Initial reserve gas | 3419.8674 | 4019.8674 | 4019.8674 | kg | YES |
| Initial reserve temperature | 325.3266 | 348.6569 | 355.3266 | K | no |
| Receiver target | 4.7668 | 5.5414 | 5.7202 | kPa | no |

These intervals are exploration safeguards, not material limits. Initial reserve gas mass and temperature are periodic-state coordinates; the reserve tank geometry is fixed. Receiver/reserve structural rating follows target pressure at a fixed ratio, with its mass charged.

### Independent tighter replay

Dry mass **13,561.341 t**; net liquid **3,448.364 kg/orbit**; operating-orbit payoff **289.57136 days**. Capture **99.97952%**. Minimum total propulsion-gas inventory **2404.075 kg** at **-41.598 s** from perigee.
Fill residual **24.997991 Pa**; reserve species residuals **[0.0505, 0.015518, 0.00087] kg**; reserve energy residual **-0.501212 MJ**. Failed original constraints: `{}`.
Payoff change from search: **+0.000195 days**.

| Modeled constraint | Remaining margin | Interpretation |
|---|---:|---|
| Rack material temperature | 69.435125 K | Smallest allowance below a material temperature limit |
| Chamber pressure rating | 1276.744142 Pa | Smallest pressure-rating allowance among compressed chambers |
| Warm-loop temperature | 19.269550 K | Allowance below configured warm-loop maximum |
| Battery usable-energy floor | 6.681178 percentage points | Minimum state of charge minus the usable-energy floor |
| Liquid tank capacity | 16.039420 m³ | Unused liquid-storage volume at peak inventory |
| Full-capture tolerance | 0.079521 percentage points | Allowance before the permitted lost fraction is exceeded |
| Plate Reynolds-number validity | 889.557804 | Allowance below the configured Re=1000 applicability limit |
| Gas temperature capability | 1076.396302 K | Allowance below the modeled gas-temperature ceiling |

- [Manifest and numerical settings](../../results/transient/reduced_optimization/pressure/manifest.json).
- [Exact selected inputs](../../results/transient/reduced_optimization/pressure/selected_config.json).
- [Termination](../../results/transient/reduced_optimization/pressure/termination.json).
- [Evaluation history](../../results/transient/reduced_optimization/pressure/evaluations.json).
- [Replay and audits](../../results/transient/reduced_optimization/pressure/replay_summary.json).

## pressure_wide_mass_reserve

Termination: **Stopped for gradient-resolution refinement: 2.55-tonne mass probe spans the capture transition; same bounds, finer probe and tighter integration used next.**.

## pressure_wide_refined

Termination: **Stopped backtracking from an infeasible seed; measured Jacobian reused for one explicit closure correction before restarting the same constrained problem.**.

## pressure_wide_closed

Termination: **Optimization terminated successfully**.

### Artificial search bounds

| Coordinate | Lower | Selected | Upper | Unit | At bound? |
|---|---:|---:|---:|---|---|
| Total racks | 127.4616 | 448.3417 | 764.7694 | t | no |
| Perigee | 85.0981 | 85.0981 | 86.0981 | km | YES |
| Initial reserve gas | 2219.8674 | 4065.8505 | 5719.8674 | kg | no |
| Initial reserve temperature | 325.3266 | 350.1554 | 355.3266 | K | no |
| Receiver target | 4.7668 | 5.6374 | 5.7202 | kPa | no |

These intervals are exploration safeguards, not material limits. Initial reserve gas mass and temperature are periodic-state coordinates; the reserve tank geometry is fixed. Receiver/reserve structural rating follows target pressure at a fixed ratio, with its mass charged.

### Independent tighter replay

Dry mass **13,577.136 t**; net liquid **3,485.931 kg/orbit**; operating-orbit payoff **286.78252 days**. Capture **99.97731%**. Minimum total propulsion-gas inventory **2431.940 kg** at **-41.452 s** from perigee.
Fill residual **20.052329 Pa**; reserve species residuals **[0.001626, 0.0005, 2.8e-05] kg**; reserve energy residual **0.004913 MJ**. Failed original constraints: `{}`.
Payoff change from search: **+0.000048 days**.

| Modeled constraint | Remaining margin | Interpretation |
|---|---:|---|
| Rack material temperature | 60.423388 K | Smallest allowance below a material temperature limit |
| Chamber pressure rating | 1254.975352 Pa | Smallest pressure-rating allowance among compressed chambers |
| Warm-loop temperature | 18.222939 K | Allowance below configured warm-loop maximum |
| Battery usable-energy floor | 5.830547 percentage points | Minimum state of charge minus the usable-energy floor |
| Liquid tank capacity | 15.996273 m³ | Unused liquid-storage volume at peak inventory |
| Full-capture tolerance | 0.077310 percentage points | Allowance before the permitted lost fraction is exceeded |
| Plate Reynolds-number validity | 888.993076 | Allowance below the configured Re=1000 applicability limit |
| Gas temperature capability | 1060.050485 K | Allowance below the modeled gas-temperature ceiling |

- [Manifest and numerical settings](../../results/transient/reduced_optimization/pressure_wide_closed/manifest.json).
- [Exact selected inputs](../../results/transient/reduced_optimization/pressure_wide_closed/selected_config.json).
- [Termination](../../results/transient/reduced_optimization/pressure_wide_closed/termination.json).
- [Evaluation history](../../results/transient/reduced_optimization/pressure_wide_closed/evaluations.json).
- [Replay and audits](../../results/transient/reduced_optimization/pressure_wide_closed/replay_summary.json).

## A rejected low-metal trial shows the throughput limit

A trial with **397.776 t** of racks admitted only **98.0176%** of the incident batch. It also failed reserve/fill closure and is not an alternative payoff result. Material-temperature margin remained **30.60 K**, and usable battery margin **5.838 percentage points**.

| Case near maximum intake deficit | Time s | Front gas K | Front pressure Pa | Arriving kg/s | Admitted kg/s | First pump kg/s |
|---|---:|---:|---:|---:|---:|---:|
| Prior accepted case | 51.515 | 922.191 | 324.681 | 30.069 | 30.069 | 30.196 |
| Rejected lower-metal trial | 51.527 | 988.429 | 337.421 | 30.399 | 28.753 | 28.879 |

At that point, the first compressor has nominal full-speed suction capacity **32.523 kg/s**, reduced to about **29.096 kg/s** by the modeled head-capability factor (actual flow **28.879 kg/s**). Estimated compression, friction and idle draw is **11.929 MW** against a **32.398 MW** motor. Thus this snapshot points to suction-density/head capability rather than instantaneous motor power saturation. The full-speed calculation is a diagnostic upper estimate; the integrated rotor state determines actual flow.

The maximum deficit occurs after perigee, while atmospheric support is declining. The model couples gas temperature to suction density and compression work, limits compressor volume/head/power, and reduces admission when front pressure approaches inlet support. This is a cooling/throughput limitation with the installed compressor capabilities, not evidence that the metal has reached its temperature limit. The two trials also differ in perigee and reserve state; this comparison is diagnostic, not an isolated rack-mass derivative.

- [Rejected trial inputs](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_trial_config.json).
- [Saved time history](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_trial.json.gz).
- [Extracted comparison](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_diagnostic.json).

## Numerical refinement at the same inputs

The first widened attempt was stopped during backtracking; its history contains completed configurations and some in-flight work was deliberately discarded. It is not reported as converged. The refinement uses the same ranges and physical constraints, with a smaller rack-mass derivative probe and tighter integration.

| Derivative calculation | Local payoff slope, days per +1% rack mass | Scaled closure-matrix condition |
|---|---:|---:|
| 2.55 t probe, rtol=1e-7 | +0.134419 | 12.397 |
| 0.255 t probe, rtol=1e-8 | -0.000552 | 12.385 |

These slopes eliminate the linearized fill/reserve mass/reserve energy residuals using initial reserve mass, initial reserve temperature and target pressure, while holding perigee fixed. They diagnose derivative resolution near the capture transition; they are not substitute simulation results or a new payoff model.

- [Derivative comparison](../../results/transient/reduced_optimization/pressure_wide_refined/derivative_comparison.json).

## Explicit feasible-seed construction

The fine-gradient run still backtracked from a slightly unclosed initial state and was stopped. Its already-measured Jacobian supplied one Newton correction to initial reserve mass, initial reserve temperature and receiver target. Rack mass and perigee were held fixed for this seed correction only. One fresh forward cycle verified it; the subsequent constrained optimizer again frees all five coordinates under the same widened bounds.
The seed is physically feasible: **True**. Fill residual **19.999418 Pa** (targeted 20 Pa within the guarded band), summed reserve mass residual **0.000358353 kg**, reserve energy residual **0.000206802 MJ**. Seed payoff **286.782734 days**. This is initialization, not a substitute for the subsequent optimizer termination.

- [Measured-Jacobian correction](../../results/transient/reduced_optimization/pressure_wide_closed/seed_restoration.json).
- [Verified seed](../../results/transient/reduced_optimization/pressure_wide_closed/seed_summary.json).
- [Reproduction script](restore_seed.py).

## Interpretation and scope

A model constraint is not necessarily a fundamental physical limit: installed power/processing capacities and material capabilities are fixed assumptions in this experiment. A search-bound hit is not a physical limit at all. Closure and receiver-fill tolerance boundaries are numerical acceptance conditions, not hardware failures.

The complete collection, propellant availability, thermal, electrical, geometric, pressure-rating, applicability and conservation checks remain active. Leading-edge lifetime, calibrated compressor maps and resolved inlet aerodynamics are not established by optimizer convergence. These payoffs end in the operating orbit; delivery/circularization has not been added.

## Reporting correction

The previous report labeled `margins.reserve_kg` as minimum propulsion inventory. That field is the smallest liquid-species surplus. This report and the corrected earlier report instead sum the three species in the saved propulsion-gas reservoir at every time and take the minimum. The earlier 289.57-day case had **2,404.075 kg** minimum total propulsion gas, not 44.8 kg. This correction changes neither the trajectory nor its constraints or payoff.

## Code validation

The complete test suite passes **181 tests**. The model audit passes eight cycle resolution/conservation cases and the Kepler energy/angular-momentum checks. The rack allocation fractions match the preceding selected case to floating-point roundoff. The forward physics implementation was unchanged in this bound-continuation experiment.
