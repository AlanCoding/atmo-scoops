# Ammonia tube radius and pitch

## Reference geometry and what is actually modeled

Both integrated ammonia references use **1 mm outer radius, 0.1 mm wall and
10 mm center-to-center pitch**: 1.8 mm internal diameter, 8 mm clear external gap.
Warm ammonia runs 280–340 K at 5 MPa; cold ammonia 200–300 K at 2 MPa.
Exterior exchange area is 170,000 m² in front and 6,000 m² in each of three
interstage coolers. This is tube surface area, not spacecraft frontal area.
The 30 m bore has 707 m² frontal area.

The front bank occupies 3.83 m depth, and each intermediate bank 0.135 m under
the idealized lattice-volume rule. All banks together contain 140.6 tonnes of
metal; warm-reference tube liquid hold-up adds 48.2 tonnes. The front alone has
about **3.01 million parallel paths**, each about **8.98 m** long. Interstage
banks each have about 134,000 paths, 7.13 m long. These are inferred hydraulic
passages, not a manufactured manifold design.

Pump head is already represented, but only approximately: Darcy friction along
an equivalent path plus a fixed 100 kPa header allowance, with 65% pump efficiency.
The warm reference has about 150 kPa peak pressure drop and 291 MJ pass pump work.
Its approximately 116 GJ ammonia regeneration electricity is much larger.
Five MPa is containment pressure, not an assumed five-MPa pressure drop every pass.
Real manifold branching, connectors, maldistribution, supports and startup still
need modeling. Gas-side lattice pressure loss remains deliberately omitted.

At the reference's reported peak-flow states, gas-side resistance accounts for
about **96% of the combined gas/wall/liquid thermal resistance**. Improving liquid
convection alone cannot remove that bottleneck. Smaller diameter can improve
external gas heat transfer, as well as reducing metal and tube liquid inventory.

## Controlled radius sweep

Orbit remains 85 × 2,000 km, with battery-fed 300 s perigee thrust. Isp is fixed
at each architecture's previous optimum: 1,815.65 s warm, 1,869.41 s cold. The
thermal geometry sweep does not re-optimize Isp or orbit. All heat-transfer states,
compressors, regeneration, deployment, packing and power masses are recomputed.

Hold exterior area, maximum coolant flow and installed tank inventories fixed.
Hold radius/pitch=0.1 and wall/radius=0.1. Thus pitch and wall thickness change
with radius; pressure-stress capability is approximately comparable. Thin walls
are a sensitivity assumption, not qualified manufacturing/cycling capability.
The model adjusts parallel-path count to retain 2 m/s at the specified maximum
flow; it does **not** keep the plumbing network fixed when changing radius.

Payoffs end in the operating orbit, not circular-apogee delivery. Rejected rows
show diagnostic model output only, not viable designs.

| Coolant | Radius, mm | Pitch, mm | Tube metal, t | Peak front inlet, K | Dry mass, t | Payoff, days | Screens |
|---|---:|---:|---:|---:|---:|---:|---|
| Warm | 0.25 | 2.5 | 35.1 | 477 | 20,775 | 386.8 | Pass |
| Warm | 0.5 | 5 | 70.3 | 538 | 20,880 | 389.1 | Pass |
| Warm | 1 | 10 | 140.6 | 622 | 21,037 | 392.7 | Pass |
| Warm | 2 | 20 | 281.1 | 735 | 21,409 | 401.0 | Rejected: ammonia_inventory_kg, ammonia_boiling_K |
| Warm | 5 | 50 | 702.8 | 898 | 22,185 | 506.8 | Rejected: interstage_small_holdup_fraction, ammonia_inventory_kg, ammonia_boiling_K |
| Warm | 10 | 100 | 1405.6 | 1054 | 23,633 | 726.3 | Rejected: interstage_small_holdup_fraction, ammonia_inventory_kg, ammonia_boiling_K |
| Cold | 0.25 | 2.5 | 35.1 | 433 | 22,423 | 408.4 | Pass |
| Cold | 0.5 | 5 | 70.3 | 495 | 22,575 | 411.9 | Pass |
| Cold | 1 | 10 | 140.6 | 581 | 22,885 | 419.0 | Pass |
| Cold | 2 | 20 | 281.1 | 695 | 23,516 | 433.4 | Rejected: ammonia_inventory_kg, ammonia_boiling_K |
| Cold | 5 | 50 | 702.8 | 866 | 25,089 | 536.6 | Rejected: interstage_small_holdup_fraction, ammonia_inventory_kg, ammonia_boiling_K |
| Cold | 10 | 100 | 1405.6 | 1019 | 27,736 | 793.8 | Rejected: interstage_small_holdup_fraction, ammonia_inventory_kg, ammonia_boiling_K |

Reducing the warm-case radius fourfold saves roughly six days (about 1.5%), while
the same-solid-rack benchmark is about 371 days. Thus these tube changes alone
do not reverse the earlier ranking. Very small tubes also multiply passage
count: at 0.25 mm radius the front needs about 48 million equivalent paths,
2.25 m long. No detailed mass model for those manifolds is present.

Larger tubes have more liquid hold-up and larger bank volumes at fixed surface
area. The conservative liquid-side heat-transfer model also loses conductance.
A wall-boiling failure means the assumed single-phase exchanger is no longer a
valid representation; its numerical payoff must not be used as a feasible result.

## Separate wall-thickness and resolution checks

| Radius, mm | Wall, mm | Samples | Payoff, days | Tube metal, t | Peak pressure drop, kPa | Screens |
|---|---:|---:|---:|---:|---:|---|
| 0.25 | 0.025 | 801 | 387.10 | 35.1 | 156.3 | Pass |
| 0.25 | 0.1 | 201 | 389.01 | 118.4 | 156.3 | Pass |
| 0.5 | 0.1 | 201 | 390.41 | 133.2 | 157.7 | Pass |

The fixed-wall cases retain the original 100-micron wall while shrinking the
outer diameter. These distinguish thermal/geometry improvements from credit for
thinner metal. High-resolution baseline results are 392.99 days warm and 418.99
cold; the table's baseline screening runs use 201 samples, so compare radius
changes at matched resolution. No sub-day optimum is claimed.

## Pitch sensitivity

Here radius stays 1 mm and exterior area stays fixed. Pitch changes bank envelope,
gas hold-up and the modeled gap velocity, rather than adding exchange surface.

| Pitch, mm | Front bank depth, m | Payoff, days | Screens |
|---|---:|---:|---|
| 10 | 3.83 | 392.66 | Pass |
| 20 | 15.31 | 396.99 | Rejected: interstage_small_holdup_fraction |
| 5 | 1.00 | 391.56 | Rejected: ammonia_boiling_K |

These are conditional packing/convection results. Without gas pressure loss and
manifold layout, tighter pitch is not a qualified optimization direction.

## Scaling and modeling priorities

For exterior area A, outer radius r, wall thickness t and radius/pitch ratio q:

- Tube length: A/(2πr).
- Sealed tube volume: Ar/2; gas-bank envelope: Ar/(2πq²).
- Metal volume: A[r²−(r−t)²]/(2r), approximately At for thin fixed walls.
- Liquid hold-up volume: A(r−t)²/(2r).

At fixed wall/radius and liquid design velocity, equivalent parallel count scales
as 1/r² and path length as r. Therefore a radius reduction does not incur the
same pressure-drop scaling as shrinking a fixed-length, fixed-count pipe network.
Resolving manufacturable branching and hydraulic path length is the most important
next geometry refinement. Then qualify internal heat transfer (including variable
Reynolds number), wall temperatures, boiling margins and cycling allowables.

Thrust-loss heat coupling to this coolant is a separate integration question. The
current model retains a fraction of thruster waste heat in the warm rejection
system; this sweep does not move it into the cold once-through ammonia inventory.
Such a change must add coolant enthalpy, flow and regeneration duties explicitly.

## Reproduction

```sh
.venv/bin/python -m atmo_scoops.studies.ammonia_tubes
.venv/bin/python -m atmo_scoops.studies.ammonia_tubes --checks
.venv/bin/python -m atmo_scoops.studies.ammonia_tube_report
```

Inputs start from `configs/reboost_{warm_ammonia,ammonia}_isp_optimum.json`.
All resolved inputs, per-stage geometry and mass/energy ledgers are saved in
`results/ammonia_tubes/`; summaries preserve every rejected screen.
[Integrated model and property treatment](../../modeling/liquid_cooling/INTEGRATED_MODEL.md).
