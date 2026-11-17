# Close-pass volume allocation

**Implementation status:** a reduced [volume and timing screen](IMPLEMENTED_VOLUME.md)
now implements working lattice envelopes, metal-displaced gas volume and equipment
packages. The specification below remains the roadmap for complete geometric and
independent-storage validation. The old fixed-bay case remains historical only.


**Status: researched requirements and explicit equations; no integrated packing
solver yet.** The former 25 m front / 100 m machinery / residual rear allocation
is an unsupported layout assumption. The primary model solves front/rear gas
inventories and four compressor blocks' states; it does **not** solve independent
interstage chamber inventories, finite intercoolers or stowed component packing.
A 100 m machinery allowance is not a derived compressor length.

The earlier [limit-case investigation](../../investigations/altitude_sensitivity/MECHANISM.md#limit-case-reference-ld-and-storage-pressure)
is therefore not a geometry-feasible reference. Its inputs and numerical outputs
remain reproducible, but its perigee boundary does not establish the deepest
craft that fits L/D=10. This dossier defines the replacement.

## Account for the actual configuration during collection

There are three different volumes for a deployable component:

1. Material volume: metal, cells, coolant, PCM and structural material.
2. Equipment envelope: the rolled/folded package, including its internal voids,
   reel/hinges, booms, manifolds, actuators and containment.
3. Installed allocation: equipment envelope plus external clearances, supports,
   pressure/thermal separation, routing and access to its deployment opening.

Use each physical region once. A cooler rack occupies its **working gas-contact
configuration** during collection, not necessarily its smallest launch package.
Gas in its accessible passages belongs to the corresponding chamber inventory;
solid metal/PCM and sealed cells displace gas. Do not add both a rack's full
working envelope and that same envelope's gas-filled pore volume to hull volume.
A deployment swept volume is a motion constraint; count it as permanently empty
only when the sequence cannot share it with another component.

## Component allocation ledger

| Component | Required close-pass allocation | What determines it | Evidence / current gap |
|---|---|---|---|
| Front shock/diffuser | Flow region plus cooled walls/leading edge | Inlet geometry, shock motion, gas residence and control response | No derived 25 m minimum; offline fluid validation required |
| Each cooler/chamber i | Solid/core volume, gas passages, plenum and frame | Heat duty, finite conductance, lattice parameters, pressure drop, transient inventory | [Metal-cooler research](../metal_coolers/README.md); specify every stage independently |
| Compressor block i | Parallel-module external envelopes and ducts | Flow area, row count/chord, casing, motor/bearings and manifold geometry | [Compressor allocation](../compressor/VOLUME_ALLOCATION.md) |
| Rear storage | Vessel envelope with usable gas volume explicitly separated | Allowed pressure, temperature, captured inventory and head/wall geometry | Residual **feasible** space, not total cylinder minus an arbitrary machinery length |
| Solar wings | Folded package plus reels/booms, powered retraction and protected bay | Required rated power/area, module design, packing and temperature | [Solar packing evidence](../solar/PACKAGING.md) |
| Warm-loop radiators | Folded panel stack/roll, fluid joints, manifolds and mechanisms | Physical panel area, panel pitch, bend radii, coolant pressure | [Radiator packaging](../warm_loop/PACKAGING.md) |
| Batteries | Module count and installed thermal/electrical envelope | Energy, peak/continuous power, cycle life and heat rejection | [Electrical packaging](../electrical/PACKAGING.md) |
| Thrusters, drives, distribution | Actual component envelopes, cable routes and separation | Selected power/voltage/thrust architecture | Mass/kW cannot determine volume; research still needed |
| Liquefaction/separation | Compressors, exchangers, cold boxes and insulation | Duty and process states | No kg-to-volume conversion accepted without equipment geometry |
| Liquid/propellant storage | Tanks, insulation, ullage, valves and supports | Inventory throughout the complete cycle | Include retained products and reserve propellant, not just warm gas |
| Hull/hatches | Shell, ribs, bulkheads, doors, latches and insulation | Pressure, mechanical/thermal loads and openings | Pressure-retaining deployment hatches remain required |

## Per-stage volumes and dynamics

Replace `front_depth_m + machinery_depth_m + rear_depth_m` as a packing model
with chambers `i=0...N`, compressor blocks between them, and named equipment
regions. Chamber usable gas volume is

`V_gas,i = V_plenum,i + epsilon_i * V_rack,i + V_connected_duct,i`.

Track `dm_i/dt = mdot_in,i - mdot_out,i`, species balances and internal energy;
calculate pressure from the EOS at `m_i/V_gas,i`. Adjacent compressor flows must
be allowed to differ. Geometry, cooler material mass and lattice dimensions are
independent choices; pressure, temperature and stored inventory are outputs.
The existing block-state calculation is not this transient chamber model.

A preliminary control-buffer estimate is
`V_gas >= Delta_m / [(partial rho/partial p)_T * Delta_p_allowed]`, where
`Delta_m = integral(mdot_in - mdot_out) dt` over the control delay. In an
isothermal ideal-gas approximation this becomes `V >= R T Delta_m/Delta_p`.
Use an energy balance instead when the transient is not isothermal. This gives
a reason for a plenum volume; assigning a number of diameters does not.

Heat transfer imposes a separate requirement: solve gas-film/solid transfer and
pressure drop for the finite rack. With a selected lattice, its metal/core mass,
porosity and hydraulic geometry determine depth and flow area. A large inventory
volume is not automatically required just because the flow is hot, and a short
buffer is not automatically sufficient for heat exchange.

## Geometric feasibility before choosing the rear tank

First require non-overlap in the close-pass configuration. For an axisymmetric
screen use cross-sectional allocations at each longitudinal station,
`sum A_allocated,j(x) <= A_inside(x)`, plus actual module shape-fit constraints.
The integral gives occupied volume but a scalar sum is only a necessary test:
a long roll may not turn through its hatch, and rectangular packages may not fit
the remaining crescent around a tank. Compressors need connected flow routes.

Small downstream compressor banks need not reserve the entire bore. Arrays,
batteries or auxiliaries may occupy the rest of the section if thermal/pressure
separation and access permit it. Conversely, do not assume arbitrary nesting
without a layout. Separate serial train depth from equipment sharing a section.
Allocate the long rear vessel from the connected space remaining after this
accounting. Enforce the requested L/D using the **outside** envelope, including
protective fairings or pods if used during the pass.

## Evidence-based first screens

See [PACKING_SCREEN.md](PACKING_SCREEN.md) for reproducible comparisons against
the saved limit cases. Published solar packing at ~40 kW/m³ is a manufacturer
reference condition, not a fundamental bound or a promise for our power scale.
It must be related to the array's rated power; mission bus power generally
requires more rated power after temperature, degradation and electrical losses.
The first screen deliberately uses equality, without invented deployment-bay
multipliers, and reports all omitted components.

Warm radiator package thickness is **not** derived from a face-sheet thickness.
Battery energy density is **not** a power-density guarantee. No zero is inserted
for an unknown component: a missing allocation leaves feasibility unresolved.
For a known reference envelope that already fails, later unknown allocations
cannot rescue that same reference packaging assumption.

## Numerical handoff and acceptance criteria

Introduce a component record with source/variant, operating duty, material
volume, close-pass envelope dimensions, allocated region, uncertainty, deployment
path and stage ownership. Technology capabilities and derived values must be
separate from freely optimized dimensions. Emit an auditable volume ledger and
remaining gas volume, along with mass, heat and electrical ledgers.

Before replacing the current model: reproduce at least two published solar
packing examples/architectures, one fully dimensioned radiator stack, and two
battery module envelopes; resolve a four-block train with independent chamber
states and coolers; conserve mass/energy and disallow overlap. Check degenerate
limits (zero equipment, zero clearance, filled pores, blocked deployment path),
and show volume convergence with the layout discretization. Unknown coefficients
must not become unconstrained optimizer variables. Only then rerun the L/D and
pressure-limited reference.
