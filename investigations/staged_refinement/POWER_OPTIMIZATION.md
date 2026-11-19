# Power-only resistance: pitch and radius searches

The owner requested 10% and 100% resistance as an added compressor electricity charge, releasing pitch first and radius second. These runs use the [power-only cycle implementation](../../modeling/metal_coolers/POWER_ONLY.md); they do not lower suction pressure or solve a hydraulic root. Each candidate is a single forward cycle with finite installed hardware, energy/species conservation and periodic constraints.

These are bounded pattern searches, **not certified global optima or stationarity proofs**. Search completion, numerical resolution, and physical feasibility are separate results. All payoffs are operating-orbit production; circular-apogee delivery remains unmodeled.

## Results

| Stage | Completed / evaluated | Feasible | Best payoff, days | Loss / all compression energy | Loss / first-stage compression energy |
|---|---:|---:|---:|---:|---:|
| seed_0.1 | 2 / 2 | 2 | 289.747 | 6.9% | 40.9% |
| seed_1 | 2 / 2 | 0 | — | — | — |
| seed_1_repaired | 2 / 2 | 2 | 294.119 | 69.6% | 408.7% |
| pitch_0.1 | 42 / 47 | 38 | 283.883 | 19.7% | 117.9% |
| pitch_1 | 44 / 47 | 39 | 291.830 | 69.5% | 413.5% |
| radius_0.1 | 66 / 69 | 54 | 282.719 | 19.6% | 115.0% |
| radius_1 | 63 / 69 | 56 | 290.017 | 67.4% | 386.9% |

A loss/base ratio of 200% means the loss charge alone is twice ordinary compression electricity. It is not the fraction of total including loss. Ordinary compression excludes refrigeration, rotor spin-up and idle draw.

## Selected geometry and loss power

### pitch_0.1

Candidate `r0_combined`; dry mass 13344.2 t; net liquid 3461.1 kg/orbit. Loss 0.6924 MWh/orbit; ordinary compression 3.5067 MWh/orbit; peak combined loss power 5.200 MW.

| Rack, front to rear | Radius, mm | Pitch, mm | Loss / stage compression energy |
|---|---:|---:|---:|
| 1 | 1.000 | 6.000 | 117.86% |
| 2 | 1.000 | 6.000 | 0.42% |
| 3 | 1.000 | 6.000 | 0.02% |
| 4 | 1.000 | 6.000 | 0.03% |
| 5 | 1.000 | 6.000 | 0.00% |

Instantaneous peak loss/base for the complete train, requiring ordinary compression above **1 MW**, is **503.9%**. Very large ratios at nearly zero ordinary head are excluded from this statistic; all energy remains in the cycle totals.

The 0.2 mm radius floor is not reached in this candidate.

### pitch_1

Candidate `r0_combined`; dry mass 13720.5 t; net liquid 3461.8 kg/orbit. Loss 2.4238 MWh/orbit; ordinary compression 3.4854 MWh/orbit; peak combined loss power 18.272 MW.

| Rack, front to rear | Radius, mm | Pitch, mm | Loss / stage compression energy |
|---|---:|---:|---:|
| 1 | 1.000 | 10.000 | 413.54% |
| 2 | 1.000 | 7.000 | 2.98% |
| 3 | 1.000 | 10.000 | 0.08% |
| 4 | 1.000 | 10.000 | 0.09% |
| 5 | 1.000 | 10.000 | 0.01% |

Instantaneous peak loss/base for the complete train, requiring ordinary compression above **1 MW**, is **1781.2%**. Very large ratios at nearly zero ordinary head are excluded from this statistic; all energy remains in the cycle totals.

The 0.2 mm radius floor is not reached in this candidate.

### radius_0.1

Candidate `r0_combined`; dry mass 13282.6 t; net liquid 3459.3 kg/orbit. Loss 0.6893 MWh/orbit; ordinary compression 3.5198 MWh/orbit; peak combined loss power 5.194 MW.

| Rack, front to rear | Radius, mm | Pitch, mm | Loss / stage compression energy |
|---|---:|---:|---:|
| 1 | 1.000 | 6.000 | 114.97% |
| 2 | 1.000 | 6.000 | 0.43% |
| 3 | 1.000 | 6.000 | 0.02% |
| 4 | 1.000 | 6.000 | 0.03% |
| 5 | 2.000 | 12.000 | 0.00% |

Instantaneous peak loss/base for the complete train, requiring ordinary compression above **1 MW**, is **505.3%**. Very large ratios at nearly zero ordinary head are excluded from this statistic; all energy remains in the cycle totals.

The 0.2 mm radius floor is not reached in this candidate.

### radius_1

Candidate `geometry_combined`; dry mass 13628.8 t; net liquid 3460.2 kg/orbit. Loss 2.4106 MWh/orbit; ordinary compression 3.5778 MWh/orbit; peak combined loss power 18.413 MW.

| Rack, front to rear | Radius, mm | Pitch, mm | Loss / stage compression energy |
|---|---:|---:|---:|
| 1 | 1.000 | 10.000 | 386.94% |
| 2 | 1.000 | 4.900 | 6.78% |
| 3 | 2.000 | 14.000 | 0.04% |
| 4 | 2.000 | 14.000 | 0.05% |
| 5 | 2.000 | 14.000 | 0.00% |

Instantaneous peak loss/base for the complete train, requiring ordinary compression above **1 MW**, is **1789.5%**. Very large ratios at nearly zero ordinary head are excluded from this statistic; all energy remains in the cycle totals.

The 0.2 mm radius floor is not reached in this candidate.

## Large-loss cases among feasible completed trials

| Search | Largest train loss/base energy | Payoff of that case, days | Selected best? |
|---|---:|---:|---|
| pitch_0.1 | 19.9% | 285.550 | no |
| pitch_1 | 138.6% | 447.852 | no |
| radius_0.1 | 80.1% | 298.643 | no |
| radius_1 | 175.6% | 439.661 | no |
## Unresolved evaluations and geometry rejections

| Search | Forward timeouts | Geometry/input rejections |
|---|---:|---:|
| pitch_0.1 | 5 | 0 |
| pitch_1 | 3 | 0 |
| radius_0.1 | 1 | 2 |
| radius_1 | 5 | 1 |

Row-count rejections enforce the existing minimum of five physical rows for the bank correlation. They are not integration failures. Timeout cases remain unresolved and prevent claims of an exhaustive local poll.

## Resolution gates

- `verify_pitch_0.1`: **PASS**. `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 1.269074451384902e-07, "admitted_kg": 9.122345513867493e-09, "lost_kg": 6.480701281578086e-05, "propellant_kg": 1.7474031216174942e-15}}`
- `verify_pitch_1`: **PASS**. `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 1.128476848911117e-05, "admitted_kg": 5.690964159115856e-06, "lost_kg": 0.00020001015518564873, "propellant_kg": 3.120362717174082e-15}}`
- `verify_radius_0.1`: **PASS**. `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 2.940455112406364e-06, "admitted_kg": 1.4510203525179673e-06, "lost_kg": 1.551361028168504e-05, "propellant_kg": 6.240725434348181e-16}}`
- `verify_radius_1`: **PASS**. `{"passed": true, "checks": {"two_complete_trajectories": true, "conservation_and_nonnegative_inventory": true, "resolution_within_half_percent": true, "two_feasible_cycles": true}, "relative_changes": {"net_liquid_kg": 4.247820005759885e-05, "admitted_kg": 2.08516492982509e-05, "lost_kg": 0.00015372376763111688, "propellant_kg": 1.4977741042435663e-15}}`

## Interpretation and disposition

Both selected pitch candidates and both selected radius candidates pass paired time-resolution, conservation, inventory and physical-feasibility gates. The coarse trajectories are reused from their exact search inputs; only the finer-resolution trajectory is rerun. The final radius results are 282.719 → 282.718 days at 10%, and 290.017 → 290.004 days at 100%.

The selected 100% case pays about 67% of ordinary whole-train compression electricity in added rack losses, and approximately 387% of first-stage compression electricity. Thus the requested >200% behavior is present for the front stage, not the cycle-integrated train total. Instantaneous whole-train ratios can exceed 200%, particularly at low ordinary compression head; the separate peak statistics above use an explicit denominator floor.

The selected radius solutions do not hit the 0.2 mm lower bound. At 10%, front-to-rear radii are [1, 1, 1, 1, 2] mm and pitches [6, 6, 6, 6, 12] mm. At 100%, radii are [1, 1, 2, 2, 2] mm and pitches [10, 4.9, 14, 14, 14] mm. These are best found in the declared finite search, not proven optima. Nominal metal inventories, orbit and initial rack temperatures were held fixed; this was not a new global search over every design coordinate.

Time-limited forward solves remain unresolved. Changing one previously timed-out trial to LSODA also timed out at both requested resolutions; no numerical cure is claimed. The minimum-five-row correlation rejection is separately counted and must not be confused with integration failure. At 10%, independently favorable geometry changes could not all be combined without violating that row-count restriction.

The energy-only model deliberately omits hydraulic pressure feasibility. It retains motor/bus/thermal limits, but its explicit conservative motor-flow reduction can overpenalize high-loss geometry compared with an exact maximum-flow solve. Therefore these results establish useful sensitivity and feasible energy-budget candidates, not validated compressor/rack flow performance. They do not replace the active pressure-coupled reference or include delivery to circular apogee orbit.


## Search definition and reproduction

The pitch stage releases five independent pitch/radius ratios at fixed 1 mm radius. The radius stage keeps pitch free and adds five radii, 0.2–5 mm. Pitch/radius bounds are 4.01–40. Nominal solid inventory is preserved; integer-row rounding is charged. Geometry changes therefore affect actual rack mass, envelope, gas volume, heat transfer and deployed area. Materials, hull dimensions, orbit, initial rack temperatures, and nominal metal inventory remain fixed.

Each geometry poll includes single-coordinate moves and common-geometry probes. A subsequent hardware poll varies ten propulsion/electrical/thermal/plant settings and five motor ratings. Individually favorable hardware moves are tested together in another full cycle. One broad geometry/hardware round is a bounded experiment, not evidence of final optimizer convergence. The radius studies additionally test combined favorable geometry moves and dense/thin geometry with increased supporting hardware. The larger allowance increases front motor 50%, warm store 25%, radiator 15%, solar and battery energy 2%, and bus 5%; the lean allowance increases front motor 15%, store 12%, and radiator 6%. These are declared trial directions, not automatic sizing inside a cycle. Exact inputs and all completed/error records are saved with each study.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage pitch --config configs/transient_power_only_0.1.json --output results/transient/power_only/pitch_0.1 --workers 4 --seconds 180
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage pitch --config configs/transient_power_only_1_seed.json --output results/transient/power_only/pitch_1 --workers 3 --seconds 240
# For each factor, release radius using the completed pitch best_config.json:
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_0.1/best_config.json --output results/transient/power_only/radius_0.1 --workers 4 --seconds 240
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_1/best_config.json --output results/transient/power_only/radius_1 --workers 3 --seconds 240
# Full-strength radius hardware poll resumed with --workers 6 --seconds 300; cached geometry trials retained.
# Also test combined favorable geometry moves and supporting-hardware allowances:
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_0.1/best_config.json --output results/transient/power_only/radius_0.1 --workers 4 --seconds 300 --finish-combination
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.power_geometry_search --stage radius --config results/transient/power_only/pitch_1/best_config.json --output results/transient/power_only/radius_1 --workers 4 --seconds 300 --finish-combination
.venv/bin/python -m atmo_scoops.transient.power_geometry_report
```

Existing evaluations are cached. Use a new directory after changing equations or to repeat the experiment. Selected candidates require paired resolution checks before being accepted. The pressure-coupled active reference is not silently replaced by these power-only experiments.
