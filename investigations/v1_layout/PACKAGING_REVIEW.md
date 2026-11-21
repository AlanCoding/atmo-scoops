# v1.0 packaging, gas feeds and thruster placement

**Historical frozen-reference review.** The current scale image now comes from
the [corrected-spacing checkpoint](../staggered_stage_a/README.md); use its
[length table](DRAWING_LENGTHS.md) and placement register for current dimensions
and estimated CM. Older locations and relocation estimates below are not the
current drawing.

This reviews the frozen case 72, not a new optimized design. See the generated
[volume register and relocation calculations](VOLUME_REGISTER.md), the
[mass register](MASS_REGISTER.md), and the [publication kit](../../docs/publication/V1_0.md).
Reproduce the volume table with `.venv/bin/python investigations/v1_layout/packaging_review.py`.

## What the scale drawing does and does not establish

`v1_perigee_scale.svg` has a scaled outer hull and axial mass assignments. Its
thin blue solar strips are symbolic, not scaled folded volumes. Warm radiators
and cryogenic packages are not individually legible. It is not yet a complete
packaging drawing suitable for constructing all Blender solids.

Two thruster groups follow the provisional allocator's two equipment-bay spans,
29–39 m and 42–70 m. There is no propulsion requirement for two groups.
Staggering the drawn pods only prevents overlap with schematic exhaust arrows;
it does not establish plume clearance. Retain the picture as a conceptual
layout, not evidence that these pod locations work.

Solar packages total **11,527 m³**: the equivalent of 16.31 m of the entire
30 m bore, distributed through the four equipment bays. The packing allocator
fills local residual capacity; tiny subdivisions in its output are not physical
cassette designs. Warm radiator stowage is **672 m³**, assigned x=66.63–69.63 m.
The coast compressor, refrigerator, cryogenic exchangers and separator total
**771 m³**, clustered around x=51–59 m. These packages are separate from the
**651 m³ warm thermal inventory**, **24 m³ liquid product tank allowance** and
**1,099 m³ propellant reserve system envelope**. Much machinery volume remains a
mass/bulk-density surrogate, not a manufacturer envelope or detailed cold-box design.

For Blender, resolve each into actual radial sectors, load paths and ports,
including opposing solar exits, independent radiator deployment corridors,
pressure-sealed downstream rack exits (v1.0), insulation and maintenance space.
The current allocation does not demonstrate those corridors or collision-free
deployment. In v1.1 downstream rack exits are superseded by fixed coolant tubes;
keep the v1.0 snapshot separate. Margin has mass but no explicit reserved volume.

## Gas and liquid routing actually in the model

Dive compressors fill the aft receiver, which has **173,793 m³ free gas volume**.
During coast a shared three-block coast compressor draws from this receiver and
nominally brings the stream to 1 bar. Its outlet splits into:

1. **Product:** precooling, refrigerator/condenser and separation accounting,
   then liquid product tanks. There is no separate large high-pressure gas tank
   on this branch. The model has finite processing/heat-transfer capacities but
   not a detailed cold-box piping layout or independently sized process buffer.
2. **Next-pass propellant:** an additional booster and cooling fill dedicated
   mixed-gas reserve tanks. Gas bypasses liquefaction and separation. Reserve
   replenishment receives priority over liquid production in the current model.

The reserve is **four spherical tanks, 500 m³ total internal volume**, each about
**6.25 m outer diameter**, rated to **15 bar**. The total system envelope includes
spacing, booster and feed hardware. Initial inventory is **4,500 kg**; about
**3,594 kg** is consumed per pass. Saved history spans **2.27–10.38 bar** and
**906–4,500 kg**, above the model's 1 bar feed cutoff. The receiver's coast
pressure decline therefore does not directly set thruster-feed pressure.
This reserve is only **0.29% of receiver gas volume**, despite holding a large
fraction of the captured mass, because it stores gas at much greater density.
It is a separate tank system, not a partition credited for free inside the receiver.

The branch explicitly assumes mixed atmospheric gas is usable propellant.
Actual N₂/O₂ thruster feed conditioning, flow distribution and operating maps
remain development requirements. The 500 kg valve/regulator/manifold allowance
is provisional. Cryogenic equipment subparts must not be counted again on top
of the refrigerator/exchanger/separator allowances without revising those totals.

## Plume angle and location

A defensible initial **layout screening angle is 30–40° half-angle** (60–80°
full cone), with 45° as a sensitivity case, not a validated plume boundary.
[NASA/CR–2004-213099, figure 9-3](https://ntrs.nasa.gov/api/citations/20040084644/downloads/20040084644.pdf)
reports roughly 27–36° half-angles enclosing 95% of integrated ion current for
NASA-173M xenon Hall thrusters over the plotted operating points.
[University of Michigan ICOPS-2000 measurements](https://pepl.engin.umich.edu/wp-content/uploads/pdf/ICOPS-00-5P02-B_optimize.pdf)
show 23–46° across configurations using a different, 90%-current definition.
These establish a broad plume, not a transferable oxygen/nitrogen specification.
Current outside these cones, charge-exchange ions and the atmospheric encounter
must be assessed; a current-containment angle is not an erosion-safe boundary.

For a straight aft-directed axis, plume radius grows approximately
`Δr = downstream_distance × tan(half_angle)`. At x=50 m, 267 m of hull remains:
30–40° implies **154–224 m radial growth** by the aft plane. Thus a pod close to
the forward hull cannot simply point aft and be presumed to clear the hull.
Outward cant can help, but reduces axial thrust and requires a fresh impulse,
energy and hardware calculation; a 30° cant alone gives an ideal 1/cos(30°)=1.155
impulse multiplier. Do not add this automatically to a thruster efficiency
already accounting for intrinsic plume divergence: cant is a separate effect.

Moving the **1,517.56 t thruster category** from its present x=50.24 m centroid
to the aft plane at 317 m moves dry CM **32.76 → 63.31 m**. Moving its associated
25% proportional mass contingency as well gives **70.95 m**. Tail mounting is
therefore still forward-heavy, but not free. If (only as an illustration) an
aft stabilizer force acts at x=300 m, its lever arm decreases from 267.24 m to
236.69 m: **11.4% less restoring moment for the same aerodynamic force**.
With relocated contingency the reduction is 14.3%. A complete center of
pressure and aerodynamic derivative calculation is needed before declaring
stability. The craft's distributed aerodynamic load is not a single tail force.
Axial thrust through the centerline does not itself acquire a torque merely
because the thrusters are aft; lateral forces, misalignment and gimbaling do.

The category is a thrust-power mass surrogate; we have not separated remote
power processors from actual discharge heads. Relocating all of it is a clear
sensitivity case, not a claim that all 1,518 t must physically move. Keeping
power electronics forward may reduce the shift, at the cost of cable runs.
Supports, cables, thermal shielding and aft structural loads are absent from
this relocation calculation. No new payoff is claimed.

## Work required before a committed 3D arrangement

- Split discharge heads, cathodes, power processors and feed equipment; establish
  N₂/O₂ plume/current/energy angular maps versus Isp, power and background density.
- Compare aft mounting with canted side pods, accounting for impingement, deployable
  surfaces, thrust-vector loss, cable mass and aerodynamic effects during the dive.
- Replace aggregate package volumes with dimensioned cassettes, cold-box modules,
  reserve spheres, insulation and service/egress envelopes. Reconcile every module
  to the mass and volume register without double counting shared coast hardware.
- Compute dry/loaded CM and aerodynamic stability across deployment states;
  update the scale drawing only once these placements are selected.

## Current proposed drawing arrangement

The scale SVG/PNG retains the 317 m hull and the reference front chamber
positions, with a 125 m aft reserve at x=192–317 m. Both gas tanks have rounded
ends in the illustration. The main receiver has a constant **24 m barrel
diameter**; the reserve retains a **30 m barrel diameter**. Head curvature is
illustrative and is not a pressure-vessel design. Reducing the main receiver
radius changes usable gas volume and must be reflected in the next cycle run.

Cryogenic equipment wraps the forward receiver at x=70–90 m; solar cassettes
move to x=90–175 m. The 30-to-24 m bore annulus offers about 254 m² of peripheral
area, or 21,630 m³ over the 85 m solar span, versus an 11,527 m³ folded solar
allowance. This is gross packing room, not demonstrated deployment clearance.
Liquid storage is provisionally increased to **60 m³ internal capacity**, about
15 reference batches of 4.03 m³ before ullage allowance. A 72 m³ package would
follow the existing 1.2 envelope multiplier. Insulation, enlarged tank mass,
retention time and boiloff need accounting in the next model update.

Thrusters are wholly behind the hull at x=319–329 m. Moving the existing
thruster mass to x=324 m, solar mass to x=132.5 m, coast-processing equipment
to x=80 m, and liquid-tank mass to x=85 m gives **86.00 m illustrative dry CM**.
Other existing masses are held fixed, including contingency and old reserve
hardware. Enlarged liquid-tank mass and revised gas-vessel mass are not yet
included. Thus this is a placement sensitivity, not a closed new mass budget.

The first cooler rack is 0.8964 m deep; the next racks are 0.05557, 0.03241 and
0.02328 m. Those are now drawn at their true axial thicknesses. The first gas
chamber is not larger in the saved case: its envelope is 0.8964 m, versus
3.0556, 3.0324 and 3.0233 m downstream, which include vessel heads. Free gas
volumes are 514, 1,093, 1,082 and 1,076 m³. No larger front gas volume was
invented to reconcile the visual expectation. Machinery-bay lengths remain
provisional at 12/10/10/27.62 m; vacated packaging space is not automatically
converted into new gas volume without a model update.

Reserve control remains: isolate during coast, draw down before collection,
then reopen when main-receiver pressure catches reserve pressure. Model both
inventories, energy states and valve flow explicitly next, including shared
feeding, refill and coast isolation. Keep the 125 m length fixed initially;
low-pressure feed capability and any required pumping remain unresolved.

For the complete optimizer → geometry → flow indexing → drawing audit, see
[why the front compartment is smaller](FRONT_GEOMETRY_TRACE.md). The fixed
head-volume assumptions, not a reversal of stages, explain the dimensions.

### Compressor-length display correction

The latest scale figure draws each compressor at its actual modeled bank length,
at the start of its inherited shared bay. The remainder is light/dashed shared
packing allowance, not extra compressor length or new gas volume. This moves
the illustrated compressor centroids and gives a relocation-only dry CM of
85.77 m, superseding the prior 86.00 m placement sensitivity. See the
[generated present lengths](DRAWING_LENGTHS.md). The redundant aft-reserve
dimension bar has been removed.
