# Why the SiC chamber is smaller than the downstream chambers

**There is no stage reversal. The frozen plate optimization did not optimize
empty chamber volumes. Fixed downstream vessel heads dominate the resulting
gas volumes.** The first SiC rack is much larger than the downstream Al racks,
but its open compartment has no corresponding head-volume allowance.

See the [reproducible numerical decomposition](FRONT_GEOMETRY_NUMBERS.md).
This investigation changes neither the reference inputs nor its payoff.

## Provenance, from optimizer to drawing

1. `results/transient/plates/cobyla_stable/search.json` defines the actual
   33-coordinate search. `plate_optimize.specs` varies five plate gaps, five
   thicknesses, five solid-depth inventories, five starting temperatures and
   selected power/thermal/propulsion inputs. **No `clear_depth_m` appears.**
   The inherited four clear depths are all zero. A separate older rod/global
   search did include clear-depth coordinates; its freedoms must not be
   attributed to this plate reference.
2. `plate_optimize.decode` converts solid-equivalent depth to rack depth using
   `rack_depth = solid_depth × (thickness + gap) / thickness`. Decoding saved
   evaluation 72 reproduces the reference rack geometry exactly. The reference
   selection subsequently chose a recorded feasible point with battery-closure
   reserve and checked resolution; it did not rearrange chamber dimensions.
3. `plates.geometry` calculates solid fraction `thickness/(thickness+gap)` and
   the remaining gas gaps in each rack. At this point the SiC rack has the
   largest envelope and largest gas-gap volume.
4. `hardware.compile_hardware` then adds vessel geometry. The open front gets
   `depth = rack_depth + clear_depth`. Each enclosed downstream volume gets
   `depth = rack_depth + clear_depth + 2 × head_depth`, with head depth fixed at
   **1.5 m** and bore fixed at **30 m** for every stage.
5. Each modeled head is a shallow spherical cap. Its volume is
   `π h (3 r² + h²) / 6`. The pair contributes **1,063.822 m³** at r=15 m,
   h=1.5 m. This is real head-interior space in the adopted geometry, not solid
   material or a full-bore 3 m cylindrical volume. About **97–99% of the
   downstream gas space comes from those prescribed heads**.
6. `cycle.simulate` uses these resulting `gas_m3` values for its five gas states.
   Incoming gas enters index 0; pump i transfers gas/enthalpy from i to i+1.
   Material index 0 is SiC; 1–4 are Al. There is no reverse indexing or material
   swap between geometry, dynamics and drawing.
7. `investigations/v1_layout/build.py` interleaves the saved chamber depths with
   **assigned** machinery bays of 12/10/10/the remaining 27.62 m. Those bay
   partitions are packaging choices, not independently optimized stage lengths.
   The scale drawing follows these chamber positions. Earlier rendering colored
   each entire chamber as a rack; current rendering distinguishes rack material
   at its actual axial thickness from its chamber envelope.

## What this establishes—and what it does not

The first rack contains **382.8 t** of SiC, versus **26.6, 12.9 and 11.8 t** of
Al in the next three chambers. The intended strong front thermal absorber is
present. However, the numerical result **does not establish that a smaller front
plenum is optimal**. Extra free depth was held fixed at zero, not driven there
by this search. Rack dimensions change gas gaps indirectly; that is not an
independent optimization of chamber hold-up volumes.

The approximately 1,080 m³ intermediate volumes are largely a consequence of
using separate, full-diameter capped vessels at every stage. That is a structural
architecture assumption, not a thermodynamic requirement of compression.
Common bulkheads, narrower intermediate vessels or different head geometry would
produce different volumes and masses and require a deliberate model revision.

The front is a lumped open inventory with admission/leakage and finite cooling
and pumping. It does not resolve spatial shock location, diffuser length, inlet
starting or a velocity/temperature field through the 0.896 m rack. Numerical
feasibility therefore does not demonstrate that this very short front envelope
is a physically adequate hypersonic inlet. Nor does it demonstrate it is
impossible. The missing spatial inlet requirement must not be filled in by
silently lengthening the illustration.

For scale: adding just **1 m** of front clear depth would increase front gas
volume from 514 to **1,221 m³**, making it the largest of these four compartments.
At fixed hull and unchanged packages that metre must come out of the aft
receiver. No payoff or flow benefit is claimed without evaluating that candidate.

## Disposition

Keep the frozen front dimensions in a drawing labeled as the numerical reference;
do not swap compartments to satisfy the original visual expectation. Keep the
recent narrowed receiver, isolated reserve and relocated equipment explicitly
labeled as proposed packaging, because they have not been simulated.

Before the next volume-allocation optimization, explicitly choose which clear
volumes can vary, resolve shared versus separate vessel heads, and introduce an
inlet/diffuser allowance supported by a separate flow study. Reconcile machinery
bay lengths to actual packages after relocating cryogenic equipment and solar.
These are required modeling decisions, not grounds to describe this reference
as an unconstrained optimum over chamber sizes.
