# Longer, more widely spaced, staggered plate cooler

Status: the provisional reduced implementation is part of accepted v1.0.1; offline validation is not established. See the [implemented approximation](INTERRUPTED_REDUCED_MODEL.md) and [validation issue draft](../../local-issue-drafts/05-validate-staggered-plate-heat-transfer-and-hydraulic-limits.md). [Illustration SVG](../../docs/images/staggered_plate_cooler.svg) ·
[PNG](../../docs/images/staggered_plate_cooler.png).

## Design being investigated

Keep the frontal area, material inventory and plate thickness. Increase transverse
pitch, reduce the number of plates side-to-side, and extend the total streamwise
cooler length to preserve material and wetted area. Subdivide that longer array
into successive rows and alternate their transverse offsets. Every parcel passes
through the rows in series. This is not the earlier proposed parallel-branch
exchanger with fourfold combined entry area.

For bore area A, solid inventory V_s, thickness t and clear gap g:

- pitch p=t+g; solid fraction t/p; open fraction g/p;
- occupied core length L=V_s p/(A t);
- gas inside the plate-bearing core = A L - V_s;
- wetted broad-face area = 2 V_s/t;
- nominal plate count across diameter D is D/p (homogenized, no integer rounding).

Fourfold **pitch** gives fourfold core length and one quarter the sheet count
in each row. Four equal rows then each have the original axial plate length.
The same total material is preserved. Fourfold **clear gap** is slightly different
because plate thickness is not zero; it must not be confused with fourfold pitch.

### Front SiC illustration, based on frozen case 72

| Quantity | Reference | Fourfold pitch, unchanged material |
|---|---:|---:|
| Thickness | 1.435 mm | 1.435 mm |
| Pitch | 7.625 mm | 30.499 mm |
| Clear gap | 6.190 mm | 29.064 mm |
| Total plate-bearing length | 0.896 m | 3.586 m |
| Number of rows for illustration | 1 | 4 |
| Plate length in each row, no row clearance | 0.896 m | 0.896 m |
| Solid material | 119.26 m³ / 382.83 t | unchanged |
| Gas volume within plate-bearing envelope | 514.38 m³ | 2,415.32 m³ |
| Wetted broad-face area | 166,207 m² | unchanged |

The drawing includes visible row separation solely for clarity. A physical axial
clearance must be an explicit input and must add to chamber depth and gas volume.
Broad-face area excludes cut edges; resolve or account for these in detailed work.

At frozen reference density, viscosity and mass flow, the existing *uninterrupted*
channel law scales as delta_p_new/delta_p_old = (p_new/p_old)^2 × (g_old/g_new)^3.
It would predict roughly 0.155 times the old loss (about 72 Pa instead of 466 Pa).
This is a geometry sanity check, not a prediction for offset rows or a realizable
compressible flow state. Fourfold gap gives 3.435-fold length and roughly
0.184-fold loss. Both illustrate why spreading the material is worth testing.
Staggered-row heat-transfer gains and added edge/turning losses are uncalculated.

## Independent inputs and derived quantities

For each rack retain material inventory, thickness, clear gap and initial solid
temperature. Add geometry-family selection, axial segment length, offset fraction
of transverse pitch, and axial inter-row clearance. Start with half-pitch offsets
and a small finite set of row counts; do not add all of these to the global
optimizer immediately. Material, bore and available spacecraft length remain fixed.

Given an integer row count n, row length is V_s p/(A t n). Total installed rack
length is n times row length plus (n-1) axial clearances. Account for supports,
manifolds, edge setbacks and bypass separately. These formulas specify one shared
frontal area and sequential rows, never n parallel flow branches.

## Offline fluid investigation

The current `modeling/fluid` area specifies an offline interface; it does not
contain a ready integrated detailed solver. Do not claim the lumped cycle is CFD.

1. Export case-72 time samples: composition, pressure, temperature, mass flow,
   rack temperature and geometry. Sample entry, peak capture and exit, plus
   downstream and coast points. The old uniform chamber state is a boundary
   estimate, not the true spatial inlet state of the front cooler.
2. First benchmark a two-dimensional straight channel, then a periodic strip
   containing several offset rows. Use compressible viscous gas flow with energy
   transport and finite plate thickness. Temperature-dependent transport and
   the chosen gas properties must be explicit. Resolve leading/trailing edges,
   thermal boundary layers, offsets and wakes. Three-dimensional supports and
   manifolds are a later correction, not assumed lossless final hardware.
3. Use physically compatible boundary conditions: prescribe inlet total state
   and outlet pressure and measure flow, or prescribed mass flux with compatible
   pressure reference while solving required inlet pressure. Do not prescribe
   mass flow plus both endpoint pressures and demand a solution. The reference's
   power-only charge can exceed local pressure; do not use it as a realized drop.
4. Screen local Re, Mach and Kn based on the actual gaps and changing state.
   Low Re supports viscous laminar starting cases, not automatic turbulence.
   Include velocity slip and temperature jump where applicable; front reference
   Kn is about 0.009–0.091 over significant flow. Flag transition-regime cases
   for kinetic treatment/benchmarking rather than stretching continuum formulas.
5. Begin with fixed wall temperature comparisons; progress to transient conjugate
   solid heating. Split solid heat capacity among rows, conserving the total.
   Compare straight/narrow, straight/wide and offset/wide arrays at equal material,
   wetted area and inlet boundary conditions. Separately compare equal heat duty
   and equal pressure budget. These are different engineering questions.
6. Report mass flow, actual inlet/outlet pressure, total-pressure loss, heat duty,
   outlet enthalpy, per-row surface flux and temperatures, flow distribution and
   maximum material temperature. Map both useful heat transfer and hydraulic cost.
   Do not select a correlation only because it gives the desired geometry trend.

## Reduced model and eventual cycle integration

Keep CFD outside the optimizer. Fit reviewed heat-transfer and pressure-flow maps
for the selected geometry, including valid ranges and uncertainty. Map geometry
ratios, local flow/thermal state and row development rather than a single universal
Nusselt multiplier. Add an axial finite-volume rack component so gas cools and
changes density along the rows; track row solid temperatures or a validated reduced
representation. Do not simply apply the same lumped chamber temperature to every
row and claim resolved thermal development.

Initially retain the requested **compressor-energy-only** accounting to compare
against the existing case. Label hydraulic infeasibility explicitly and report
loss/available-pressure and power ratios. A later pressure-flow coupling must use
a bracketed, monotone passive-flow relation or otherwise robust solve; no negative
suction pressure and no silent numerical clipping into apparent feasibility.

Geometry integration must use the new full rack envelope, subtract solid volume,
and include necessary vessel heads/clearances only once. Larger rack length takes
space from the receiver at fixed hull length. Include finite material capacity,
additional segmented-panel supports/deployment mechanisms and coast radiation.
Splitting a rack adds mechanical complexity even with unchanged plate area.

## Validation status

The cycle model uses a provisional thermal-spacing equivalence and energy-only
resistance surcharge. Channel, offset-row and rarefied-flow validation is not
established by a converged system optimization. The benchmark and release gates
are recorded in [draft 05](../../local-issue-drafts/05-validate-staggered-plate-heat-transfer-and-hydraulic-limits.md).

## Research starting points

- [Berkeley offset-fin design report](https://fhr.nuc.berkeley.edu/wp-content/uploads/2014/10/05-006_CSiC_heat-safety.pdf): interrupted boundary-layer development and the accompanying edge/form drag; useful geometry framework, not a validated correlation for our gas regime.
- [DOE plane-Poiseuille benchmark](https://mfix.netl.doe.gov/doc/vvuq-manual/main/html/fluid/fld-01.html): straight, no-slip laminar limiting-case verification.
- [NASA rarefaction-regime reference](https://ntrs.nasa.gov/api/citations/20230014996/downloads/Presentation%20charts%20Leak%20Correlation%20AIAA.pdf): Kn-based screening; does not itself validate staggered-channel heat transfer.
