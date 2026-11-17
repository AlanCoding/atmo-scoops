# Scalar search scope for the first coupled optimization

**Scope registry; first implementation available.** See [actual inputs and current search subset](TRANSIENT_IMPLEMENTATION.md). The two geometry locks below are the owner's instructions.
Other proposed locks are recommendations for the first search, not silently
accepted permanent design decisions. This narrows the broad variable registry
in [the mathematical specification](TRANSIENT_OPTIMIZATION_SPEC.md).

## Geometry locks and length convention

| Scalar | Fixed value | Status |
|---|---:|---|
| `mouth_diameter_m` | 30 | Owner: retain reference diameter |
| `chamber_bore_m` | 30 | Same common-bore reference |
| `radial_clearance_m` | 0.85 | Retain existing packaging allowance |
| `outside_diameter_m` | 31.7 | Derived: 30 + 2 × 0.85 |
| `overall_length_over_outside_diameter` | 10 | Owner: fixed ratio, not merely an upper bound |
| `overall_length_m` | 317 | Derived: 10 × 31.7 |

The 30 m dimension in the chamber studies is an internal bore/collection diameter,
not the outside diameter. Use outside diameter for physical spacecraft L/D, as
in the existing packaging model. Thus this plan uses 317 m overall, not 300 m.
If the owner instead chooses a nominal-bore length convention, it would be 300 m;
that would be a different explicitly recorded convention, not a numerical result.
These locks do not assert a universal monotonic diameter advantage.

The old selected craft was about 119 m long. Fixed L/D=10 therefore changes the
reference geometry substantially; it is not just removing two optimizer inputs
from an otherwise unchanged solution. The old 373-day number is not a prediction
for the longer craft.

### Allocate the length; do not invent an empty machinery allowance

Select front/intermediate rack and clear depths and the receiver rack depth.
Compute installed equipment package length from that candidate's hardware.
Allocate the remaining physical axial budget to the aft receiver:

```
receiver_total_length = 317 m - other_chamber_lengths
                            - equipment_length - other_counted_axial_allowances
receiver_clear_barrel_depth = receiver_total_length
                             - receiver_heads_length - receiver_rack_depth
```

Count shared structures/heads only once. Every package and rack must fit. A
negative receiver clear depth makes the candidate infeasible; never clip it to
zero or enlarge the craft. Receiver volume is then derived from its real shape
and solid displacement. The **receiver empty depth is no longer an independent
variable**. It gets the residual budget, consistent with the intended long aft
tank. Controls can choose how much of its capacity to use; volume does not imply
that a batch fills the tank or reaches its rated pressure.

The receiver cannot drive L/D to infinity: L_total stays 317 m for every candidate,
not a quantity recomputed from desired pressure. Even an impossible all-receiver
cylinder has only pi*(30 m)^2/4*317 m, about 224,000 m³; real heads, racks and
hardware reduce that bound. For specified gas inventory and temperature,
`p ~ m*R*T/V_free` therefore cannot approach zero through unbounded volume.
Pressure is an integrated state, not a freely chosen tank-filling pressure.
Lowering a vessel's rated pressure must still satisfy its actual pressure history;
it does not authorize lengthening the hull. Saving equipment length can buy only
a finite increase in receiver volume within the same outer geometry.

## Other scalars recommended fixed for the first search

| Scalar(s) | Proposed fixed value | Why not optimize yet? |
|---|---:|---|
| `perigee_km` | 85 | Current comparison point. Without a reusable actively cooled leading-edge model, diving lower can exploit an absent survivability constraint. This is not a certified safe altitude. |
| `dive_compressor_block_count` | 4 | Avoid architecture/discrete-search expansion before the coupled cycle works. This is not four aerodynamic rows. |
| `front_rack_material` | SiC | Selected reference architecture; FeCrAl remains a separate comparison run. |
| `downstream_rack_material` | Aluminum, all four racks | Keep the material allocation topology fixed. |
| `rod_radius_m`, each rack | 0.001 | Without lattice pressure drop/support/lifetime limits, arbitrarily thin rods can look artificially attractive. |
| `rod_radius_over_pitch`, each rack | 0.1 for now | Owner accepts deferring pitch search until lattice pressure loss is modeled. Radius remains 1 mm. Later vary pitch itself; derive radius/pitch. |
| `deployment_speed_m_s` | 10 | Capability assumption, not a performance knob to increase for free. |
| `thrust_center_s` | 0 relative to perigee | Start with symmetric centered constant-magnitude burns with in-plane steering that restores energy and angular momentum; duration is free. Do not require purely prograde thrust over an extended arc. |
| `dive_pump_cutoff_Pa`, each block | 0.1 | Retain the laboratory cutoff while sizing machinery; optimize cutoff/control after off-design behavior is made credible. |
| `latest_dive_pump_stop_s` | +600 | Retain current maximum recovery window; actual flow may stop earlier at cutoff/interlocks. |
| `coast_feed_pressure_target_Pa` | 100000 | Initial pressurized-feed process benchmark. Not a universal pressure required for liquefaction. Do not optimize pressure while retaining a one-bar-only plant correlation. |
| `maximum_receiver_pressure_Pa` | 110000 | Retain the study cap. Actual tank pressure is a state, not a setpoint forced to this value. |
| `LN2_mixing_ratio` | 0 | Keep mixing code and ports; defer another architecture trade while closing the dry-rack cycle. |
| `front_material_limit_K`, `aluminum_limit_K` | 1000, 550 | Existing provisional study/property limits; optimizer cannot raise them. |
| `emissivity_SiC`, `emissivity_Al` | 0.8, 0.8 | Existing surface assumptions; change only in capability sensitivity, not as free variables. Aluminum requires a suitable emissive surface. |

Also freeze the compressor mechanical family for this first search: 0.5 m nominal
module diameter, 0.5 hub/tip ratio, 350 m/s tip-speed ceiling, and 100 m/s design
axial velocity. These are inherited conditional sizing assumptions, not validated
pump properties. Hardware capacities can still vary through installed module/row
sizing. Do not simultaneously optimize tip speed, arbitrary efficiency and a
mass coefficient without a credible map/stress model.

Keep atmosphere, solar orientation/eclipse scenario, radiator view factors,
structural allowables, packing coefficients, and specific masses/efficiencies
fixed in each run. For example, 60% thrust efficiency, 2 kg/kW thruster hardware,
1 kg/kW bus and 75% compressor isentropic efficiency remain explicit inherited
capability assumptions. Run separate sensitivity cases; do not let the optimizer
invent better technology.

## Specific scalars to keep free

Values below are **starting guesses from earlier cases**, not fixed answers or a
claim that the longer craft is already feasible. No new payoff has been run.

### Operating point and system capacities

| Free scalar | Starting guess | What supplies the opposing trade? |
|---|---:|---|
| `thrust_burst_s` | About 1200 s; 300 s comparison | Peak-power hardware versus finite-arc impulse, energy and propellant penalty |
| `thruster_isp_s` | 1765.95 s | Propellant consumption versus electric energy and power-system mass |
| `apogee_km` | 2000 km | Longer recovery/recharge versus fewer productive passes; actual eclipse, orbital speed and deployment remain coupled |
| `solar_physical_area_m2` | 1,346,403 m² | Generation versus array mass, folded volume and deployment time |
| `battery_rated_energy_MWh` | About 310 MWh | SOC closure versus installed mass/volume |
| `battery_power_rating_MW` | About 2748 MW | Simultaneous load capability versus pack power-density mass requirement |
| `bus_rating_MW` | About 2748 MW | Delivered power versus installed electrical mass/volume |
| `thruster_electrical_rating_MW` | About 2693 MW | Required orbital restoration versus installed thrust hardware, energy and propellant |
| `warm_radiator_physical_area_m2` | About 38,722 m² | Heat rejection versus radiator mass, packing and motion |
| `warm_buffer_inventory_kg` | About 576,445 kg | Heat storage/closure versus mass and volume; energy capacity follows material |

Do not fix apogee merely to stabilize the first published optimization: it is an
important energy/duty-cycle trade in this concept. It can be held at 2000 km in
a debugging comparison, then released in the first substantive design search.
Set explicit orbit/model-validity bounds and report active bounds; do not pretend
the old reference altitude or an arbitrary search boundary is a physical optimum.

### Each rack and its adjacent space

Each cell in the three numerical columns below is a separate scalar coordinate.
The receiver's clear depth is derived, not free.

| Rack | `rack_depth_m` seed | `extra_clear_depth_m` seed | `initial_rack_temperature_K` seed |
|---|---:|---:|---:|
| Front | 5.41905 | 0 | 298 |
| Interstage 1 | 0.35723 | 0 | 298 |
| Interstage 2 | 0.14804 | 0 | 298 |
| Interstage 3 | 0.17159 | 0 | 298 |
| Receiver | 0.26916 | Derived from remaining length | 298 |

This gives **14 free rack/allocation scalars**: five rack depths, four clear depths,
and five initial temperatures. The last five have five periodic enthalpy-closure
equalities; their values are not assumed to remain 298 K. No old 2–12 m front
search bound should silently become a new physical limit; use declared numerical
bounds within the fixed overall length and diagnose any active bounds.

### Dive compressor installed ratings

Each row supplies three scalar coordinates. The rating compiler must derive one
consistent mechanical bank from them; its dynamics cannot retain unrelated
reference capacity. Report hardware rounding and any sizing infeasibility.

| Block | `suction_rating_m3_s` seed | `head_rating_kJ_kg` seed | `motor_rating_MW` seed |
|---|---:|---:|---:|
| 1 | 27463.88 | 941.48 | 34.82 |
| 2 | 6207.44 | 1213.00 | 13.87 |
| 3 | 1723.19 | 933.92 | 10.53 |
| 4 | 687.08 | 823.74 | 16.96 |

The motor seeds retain anchor spin-up capacity and the selected final-stage
uprating. They are not inferred from cold inlet temperature alone. Capacity and
head must be allowed to move: freezing them would repeat the mass-audit problem.

### Remaining necessary coordinates

These are scalar inputs too, but the replacement component interface must establish
consistent initial ratings before quoting defensible numerical guesses:

- Each coast bank's `suction_rating_m3_s`, `head_rating_kJ_kg` and `motor_rating_MW`.
- `refrigerator_reference_lift_W`, `precooler_UA_W_K`, `condenser_UA_W_K`, and
  `separator_capacity_kg_s`. Freeze internal plant topology/pressure and tune these
  finite capacities, rather than prescribing unlimited 2 kg/s withdrawal.
- `product_tank_usable_m3`, species reserve tank volumes and required rated pressure
  or a declared fixed tank family. Capacity must cover actual batch/reserve history.
- Initial `battery_SOC`, `warm_store_temperature_K`, each gas node's independent
  species inventories and internal energy, and working-reserve species/energy
  states. Their closure equations remain mandatory; do not add redundant P/T/rho
  variables or remove closure to reduce the coordinate count.

Use simple fixed control laws and bounded scalar setpoints first. Add detailed
throttle knots, bank-specific deployment timing and variable pressure targets only
when they answer a demonstrated deficiency. Once hardware is coupled, control
refinement should not be confused with a free efficiency improvement.

## What this changes in the plan

The optimizer selects **how to use and equip a fixed-size craft**, not an unlimited
outer geometry. The previous L/D inequality becomes a design equality eliminated
by deriving receiver clear depth. Diameter and length cannot grow to improve the
objective. This still leaves the important physical trades in Isp, apogee, rack
allocation/starting temperatures, compressor capacity, electricity and heat rejection.
No claim of a global bounded optimum follows solely from fixing these two scalars;
remaining variables still need declared domains, physical constraints and
boundary/sensitivity checks.

The payoff and periodic closure equations remain those in the mathematical
specification. This scope document changes neither saved simulation inputs nor
reported payoff numbers. Recommendations above await adoption; the two owner
geometry locks govern the next coupled-model reference.

## Final disposition after duration/geometry review

- Keep diameter and overall L/D fixed. Receiver clear depth is the bounded
  remaining axial budget, never obtained by growing the hull to meet a desired
  pressure. Its P/T/inventory are solved states.
- Perigee is ultimately a constrained outer variable. Reusable leading-edge,
  heat-flux/material-temperature, pressure and machinery constraints may select
  its optimum at an active limit. Do not assume one particular constraint binds
  or eliminate altitude via an arbitrary pressure equation. Until reusable-entry
  limits exist, 85 km is a comparison scenario, not a derived safe optimum.
- Radius stays 1 mm. Pitch stays 10 mm only while pressure loss is omitted.
  **Reminder trigger:** at the first coupled-reference review, and before any
  pitch/density optimization, explicitly revisit pressure-drop modeling with the
  owner. Implement lattice pressure drop with rarefaction/regime validity,
  compressor head/work coupling and gas-volume/surface changes first. Then vary
  pitch at fixed radius; denser packing is a legitimate possible result.
- Deployment speed stays 10 m/s; actual area and deployment time remain coupled.
- Burn duration is free, initially in the centered symmetric steered family.
  The [duration aside](../../investigations/reboost/BURN_DURATION.md) supplies a
  short-burn penalty equation and a cheap finite-arc calculation. Its approximately
  20-minute optimum and 258-day frozen-budget proxy are seeds/evidence, not a new
  fixed-duration rule or a payoff for the 317 m craft. Co-optimize Isp later in
  the actual coupled cycle; preserve both orbital restoration constraints.
