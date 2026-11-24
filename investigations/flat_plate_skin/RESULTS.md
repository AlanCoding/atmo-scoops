# Flat-plate side friction and the lower-altitude question

[Equations, sources and applicability](../../modeling/aerodynamics/FLAT_PLATE_SHEAR.md). This is a conditional shear estimate, not a new cycle optimum or release. Geometry, apogee and atmosphere follow the widened-bounds candidate. No integrated cycle was rerun for these compiler comparisons.

## Current candidate

At 85.09807 km and a 600 K exterior wall, the full-pass effective Cf is **0.0009292** and skin impulse is **2.075%** of incident-mouth impulse. The selected candidate already used Cf=0.002, equivalent to 4.466%; do not add these penalties together.

| Compiler quantity | Existing constant Cf | Optional laminar plate |
|---|---:|---:|
| Skin impulse, MN s | 2.458 | 1.142 |
| Reference propellant, kg | 3504.506 | 3424.296 |
| Installed thrust electrical power, MW | 746.586 | 729.499 |

The compiler derives thrust-related hardware from required impulse; other capacity inputs remain unchanged. This is not a closed replacement cycle. The roughly 80 kg propellant reduction and 17 MW rating reduction are conditional compiler consequences, not a validated payoff improvement.

Wall-temperature sensitivity at the current perigee:

| Assumed wall K | Skin / mouth impulse % |
|---|---:|
| 300 | 2.086 |
| 600 | 2.075 |
| 1000 | 2.059 |

## Altitude scaling, same geometry and 2,000 km apogee

| Perigee km | Peak Re_L | Peak q Pa | Skin / incident-mouth impulse % |
|---|---:|---:|---:|
| 50.000 | 1.54e+08 | 32338.04 | 0.182 |
| 60.000 | 4.89e+07 | 9590.36 | 0.318 |
| 70.000 | 1.48e+07 | 2587.21 | 0.588 |
| 80.000 | 3.41e+06 | 546.20 | 1.298 |
| 85.098 | 1.41e+06 | 225.80 | 2.075 |
| 90.000 | 5.83e+05 | 95.71 | 3.273 |
| 100.000 | 1.22e+05 | 19.16 | 8.104 |

These rows assume laminar flow at every altitude; they are not validated transition predictions. The saved 120/150 km extrapolations are excluded from this table because continuum applicability is particularly poor. The 100 km full-pass result already has major rarefaction/curvature limitations.

## Does lower altitude eventually become worse?

Not established by the current optimizations. At fixed velocity and temperature profile, capture and its momentum/thermal burden scale approximately as density. If hardware scales proportionally with batch mass, dry-mass payoff can approach a floor without developing an interior optimum. Fixed overhead can make deeper dives look progressively better.

For this laminar equation Fskin ∝ D sqrt(L) sqrt(ρ μ) U^(3/2) sqrt(C*). Collection momentum scales as ρ U² D_mouth². Thus their ratio scales approximately as ρ^(−1/2), not as increasing density. A conventional turbulent one-fifth-power scaling would give ρ^(−1/5) instead; this scaling observation is not a turbulent coefficient estimate. Transition can cause a finite change, but side friction alone supplies no theorem of an ultimate altitude penalty.

Real restrictions include maximum local heat flux and reusable lip temperature/erosion, side heating and catalysis, peak force/bending/buckling, qualified tank pressure, compressor throughput/head, finite thermal storage and heat transfer, finite electric power and available coast time. The model includes some capacity constraints but not qualified limits for all of these. Fixed total gas volume with a genuinely fixed pressure rating and minimum temperature also bounds batch inventory through m≈pV/(RT). If pressure rating and installed hardware are allowed to grow, that particular bound changes.

The numerical package itself currently rejects perigees outside 75–110 km as a molecular-air study scope. That is another artificial domain boundary, distinct from the local 85.098 km optimization floor and not a survivability claim. The offline shear screen can show equations below this domain without declaring those trajectories feasible collection designs.

Consequently: expand altitude only with explicit complete-capture/pressure/thermal/power constraints and documented capabilities. Do not expect this new side-shear law by itself to stop the optimizer from descending. Keep the published design and the constant-Cf comparison intact while the boundary-layer assumptions are reviewed.

## Reproduction

```sh
PYTHONPATH=. .venv/bin/python investigations/flat_plate_skin/run.py
PYTHONPATH=. .venv/bin/python investigations/flat_plate_skin/report.py
```

- [Numerical screen and compiler comparison](../../results/transient/flat_plate_skin/screen.json).
- [Optional candidate inputs, not a closed optimized cycle](../../results/transient/flat_plate_skin/candidate_config.json).
