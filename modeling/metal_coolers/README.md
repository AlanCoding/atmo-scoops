# Metal coolers: finite gas-to-surface heat transfer

**Current implementation:** [Finite convection, rack geometry and cyclic restoration are now implemented](FINITE_RACK_MODEL.md). See that specification for scope and unresolved physics.


**Status: research specification, not a validated correlation or implemented
replacement.** Metal thermal capacity alone cannot determine gas outlet
temperature. Model how heat crosses from flowing gas to the actual lattice,
how it diffuses into metal, and how that same metal cools during coast.

The next [stage-specific pitch investigation](../../investigations/rack_pitch/PLAN.md) pairs heat transfer with pressure loss and defines geometry/correlation acceptance criteria.

## Geometry and independent inputs

For each chamber, choose a lattice family (woven wire, foil passages, fins or
another specified geometry), wire/foil thickness and pitch/spacing, frontal
flow area and metal mass. Derive consistent porosity, wetted area, hydraulic
dimensions and rack depth; do not independently optimize redundant quantities.
Include bypass, contact resistance, supports and deployment packaging. Chamber
gas volume excludes solid displacement. Each stage has its own rack allocation.

## Required gas/solid calculation

Use local composition-, temperature- and pressure-dependent gas density,
enthalpy, viscosity, thermal conductivity and cp, together with solid cp(T),
conductivity, density and emissivity. Evaluate local Reynolds, Prandtl, Mach
and passage-scale Knudsen numbers. Do not infer continuum validity from hull
diameter alone or substitute standard-volume flow for local volume flow.

For a justified continuum correlation, `Nu = h_conv L_characteristic/k_gas`;
select Nu(Re, Pr, geometry, boundary condition) from applicable measurements.
Specify whether velocity is superficial or pore velocity and which wire/pore
length defines Re. The heat-transfer conductance is a derived result:

```
Q_dot_cell = h_conv * wetted_area_cell * (T_gas - T_surface)
```

Couple gas mass/enthalpy storage and advection to solid internal-energy storage,
conduction and surface exchange in multiple axial cells. Fin efficiency and
through-thickness temperature gradients must be resolved or bounded with Biot
and diffusion-time checks. NTU/effectiveness is a check in the appropriate
steady limit, not permission to impose a fixed outlet temperature on a warming
finite-capacity rack. Include bypass/maldistribution and finite residence time.

Choose a matching pressure-drop relation: viscous/inertial porous resistance or
screen/duct friction and local losses with measured coefficients and stated
validity. Heat transfer cannot be optimized independently of pressure loss and
flow blockage. Low-pressure temperature jump/slip or molecular heat exchange
requires an appropriate accommodation model when continuum correlations fail.
Check radiation and chemical/recombination heat where relevant to the front rack.

## Coast restoration and deployment coupling

Track metal conduction and radiation to the actual environment using exposed
area, view factors, mutual shielding, solar/Earth loading and emissivity(T).
Gas-wetted area is not automatically space-exposed radiating area. Recover
chamber gas and depressurize before hatch opening; stored intermediate gas can
delay deployment. Enforce repeat-orbit metal temperatures, not a free cold start
every pass. Include mechanism/support mass and time with the deployment dossier.

## Evidence and verification requirements

Collect multiple gas-flow heat-transfer **and** pressure-drop datasets for the
chosen lattice families, with material, porosity, wire/pore geometry, flow and
temperature ranges. Prefer paired measurements so high conductance is not
credited with unrelated low pressure loss. Include low-density gas data and
finite thermal-storage experiments; do not transpose liquid correlations without
checking similarity and rarefaction.

Initial source lead: [NASA-CR-120559, woven-screen pressure-drop measurements](https://ntrs.nasa.gov/citations/19750005995).
It reports water-flow screen pressure losses and nonuniform-flow effects. It can
inform geometry/flow definitions and comparison methods; it does not establish
gas heat transfer or rarefied-gas coefficients. Gas heat-transfer sources remain
to be selected rather than inventing a generic h value.

Validate energy conservation, zero-conductance and finite-capacity saturation,
steady benchmark cases, axial/time resolution and coast restoration. Output gas
states, pressure loss, solid temperature distribution, mass, exposed area and
deployment requirements for every rack, with uncertainty and regime flags.
Hand these reduced relations to the primary model only after benchmarking.

Related: [compressor plan](../compressor/MODEL_PLAN.md),
[screening arithmetic](../compressor/SCREENING_CALCULATIONS.md),
[properties](../gas_properties/README.md), [deployment](../deployment/README.md).

Design option: [encapsulated phase-change cores](../../docs/PHASE_CHANGE_COOLERS.md), including stage-specific temperature matching and finite solidification. Optional finite-rate implementation: [PCM model](PCM_MODEL.md).

## Working volume during the pass

A deployed radiator's smallest folded package is not necessarily its working
in-chamber cooling geometry. For each stage, retain solid material/core volume,
rack envelope, gas-accessible pore volume and connected plenum separately.
`V_rack = V_solid/(1-epsilon)` only when epsilon describes the full selected
lattice consistently; add frames or closed cells that it excludes. PCM cores,
liners and expansion cavities need explicit geometry. Gas-accessible pore
volume counts inside chamber inventory, not as a second hull allocation.

For planar sheets, material volume is physical sheet area times actual thickness;
stack pitch also includes gas passages and supports. Pitch must follow heat
transfer and pressure-loss calculations. It cannot be set to material thickness
merely to obtain compact storage. A rolled coast package, a folded transit
package and the collection configuration may be different states; check each
required state and transition. [Close-pass allocation](../deployment/CLOSE_PASS_VOLUME.md)
connects these quantities to the per-stage dynamics and remaining rear tank.
