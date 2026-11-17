# External skin-friction impulse sensitivity

**Implemented:** an effective skin-friction coefficient adds hull drag impulse to the coupled model. These are coefficient scenarios, not a calibrated aerodynamic prediction or reoptimized vehicle. The 285-day comparison has zero external skin friction.

## Impulse calculation

For axial flight and a cylindrical external envelope:

```text
q(t) = 0.5 rho(t) v_relative(t)^2
S_wetted = pi D_out L × area_multiplier
J_skin = integral Cf_effective q(t) S_wetted dt
J_total = J_incident_mouth + J_skin
```

The existing prescribed Kepler/atmosphere history supplies the integral; no additional trajectory iteration is introduced. Total impulse feeds the same finite-burn steering penalty, installed thruster rating, propellant expenditure, electrical load and thermal cycle. It cannot create captured gas.

At 30 m mouth diameter, 31.7 m outside diameter and 317 m length, the ratio is `J_skin/J_mouth = Cf × S_wetted/(2 A_mouth) = 22.3309 Cf`. The factor of one-half belongs to dynamic pressure; the incident-air capture impulse uses `rho v² A_mouth`.

The capability inputs are `skin_friction_coefficient` and `skin_area_multiplier`. They are scenario assumptions, **not optimizer variables allowed to drift to zero**. Zero remains the backwards-compatible value for saved historical inputs. The new `configs/transient_skin_reference.json` explicitly uses 0.002.

## Coupled results

| Effective Cf | Added impulse | Electrical/thermal capacity proposal | Dry mass (t) | Net liquid (kg/orbit) | Accepted payoff (days) |
|---:|---:|---|---:|---:|---:|
| 0 | 0% | Historical comparison | 14,017 | 3,617.4 | 285.32 |
| 0.002 | 4.47% | Unchanged capacities | 14,098 | 3,461.7 | Rejected |
| 0.001 | 2.23% | Energy-scaled proposal | 14,256 | 3,539.6 | 296.54 |
| 0.002 | 4.47% | Energy-scaled proposal | 14,494 | 3,461.9 | 308.27 |
| 0.005 | 11.17% | Energy-scaled proposal | 15,208 | 3,228.5 | 346.84 |

The unchanged-capacity Cf=0.002 case exceeds the 450 K warm-store limit by about 0.37 K and finishes with a 216 MJ (0.060 MWh) battery deficit, beyond the declared 100 MJ closure tolerance. Its diagnostic payoff is not an accepted repeatable-cycle result. Thruster rating/mass still derives from the increased required impulse even when the other capacities are held fixed.

For the capacity proposals, solar area, battery energy/power, bus rating, warm-store mass and warm-radiator area are each multiplied by the drag-impulse ratio **before integration**. Other stage and plant capacities remain fixed. This restores closure in the tested cases but is not a minimum-mass resizing or a fresh optimum.

## Meaning and limits of Cf

Cf is the wetted-area mean shear coefficient referenced to freestream dynamic pressure. It is not the usual whole-vehicle frontal-area drag coefficient. The multiplier can represent extra exposed area, but cannot by itself model fin pressure drag.

At reference perigee, the free-stream length-based Reynolds number is approximately 1.43 million using Sutherland viscosity. Classical incompressible flat-plate averages would be about 0.0011 (laminar) or 0.0043 (turbulent); these are scale checks, **not hypersonic predictions**. Compressibility, actual boundary-layer-edge state, wall temperature, transition, roughness, rarefaction and shape must be resolved before choosing an aerodynamic coefficient.

[NASA TN D-3969](https://ntrs.nasa.gov/citations/19670016466) develops skin-friction/heat-transfer charts for compressible turbulent flat plates. It establishes the need for Mach, Reynolds and wall-temperature dependence; it does not validate our constant coefficient, a 317 m scoop geometry, or extrapolation beyond its stated chart domain.

The current cases therefore span Cf=0.001–0.005 as **illustrative sensitivity scenarios**, not confidence bounds. Offline aerothermal calculations should produce an impulse-weighted coefficient or a time-dependent shear table for the optimizer. Keep L/D fixed until that calibration is sufficiently defensible.

This change includes skin drag only. It does not yet include inlet/spillage pressure drag beyond the existing mouth-incident momentum allowance, skirt/fin pressure drag, base drag, attitude error or wall heating/TPS mass. `mechanical_work_J` is drag work, not heat deposited into the wall; do not assign all of it to a coolant loop. Local convective heat flux requires a separate aerothermal calculation.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.skin_study --workers 2
.venv/bin/python -m atmo_scoops.transient.skin_report
.venv/bin/python -m atmo_scoops.transient --config configs/transient_skin_reference.json --output results/transient/skin_example.json
```

Inputs and all four trajectories are retained in `results/transient/skin_friction/`. The frozen zero-skin comparison is preserved; do not silently relabel it as including external drag.
