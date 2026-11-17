# Model improvement list

This is a maintained list of missing capabilities, not a work diary. Remove or
rewrite an item when the model resolves it, and link its validation. Priorities
reflect how strongly a missing relationship can distort design selection.

The current ordered [refinement and geometry-handoff plan](NEXT_REFINEMENTS.md) identifies gaseous propellant routing, pressure-loss-constrained rack pitch, skin friction, and the main potentially optimistic omissions. The [mass allowance definitions](../modeling/primary/MASS_ALLOWANCES.md) separate bus, rack mechanisms and contingency.

Completed numerical decisions are indexed in [investigations](../investigations/README.md).
The [mixing development plan](DESIGN_STUDIES_PLAN.md) describes the remaining
physical calibration needed beyond the current conditional trade.

The [staged-compressor model plan](../modeling/compressor/MODEL_PLAN.md)
sets the next core refinement: three/four cooled blocks, independently allocated
rack masses, lattice-based heat transfer and solved gas states. Real-fluid compression
states and a conditional geometry mass model are implemented; independent rack masses, finite heat transfer, pore-volume accounting and dynamic interstage storage are implemented in the coupled transient model. See the
[compressor results](../modeling/compressor/RESULTS.md).

Component equations and annotated evidence belong in the
[model calculation library](../modeling/README.md). The
[rear-depth investigation](../investigations/rear_storage_depth/INVESTIGATION.md)
identifies shared structure, head-limited recovery and coast pressure management
as necessary to resolve the elongated-storage trade.

## Primary model and optimization

| ID | Priority | Missing relationship | Required implementation / acceptance evidence |
|---|---|---|---|
| P1 | High | Circular-apogee delivery and return | Integrate the delivery/recovery trajectory, mass changes, tanks, export hardware and propellant; report delivered payoff alongside operating payoff. |
| P2 | High | Finite-thrust reboost and real drag | Finite-arc penalty and configurable skin impulse are implemented; calibrate the coefficient and add remaining pressure drag/wall heating. Integrate thrust around perigee with mass/inertia, atmospheric force and expelled-gas momentum. Bound burn duration physically. Couple density/altitude to the actual powered trajectory. |
| P3 | High | Gas-to-metal exchange validation | Finite lumped rack capacity/convection and geometric porosity are implemented. Validate array correlations, rarefaction/accommodation, temperature gradients, reactions and cycling. Lattice pressure loss is deliberately omitted for the current scope. |
| P4 | High | Actively cooled leading edge and reusable perigee envelope | Resolve local heat flux, cooling flow, temperature, stress, oxidation/erosion and fatigue over repeated dives. Output allowable operating envelopes versus geometry/material/cooling, including life and replacement mass. Extend the atmosphere domain when justified; do not mistake 75 km for a materials limit. |
| P5 | High | Compressor maps and transients | Real-fluid block work, geometry mass, spin-up and receiver-dependent head limits are implemented. Calibrate low-Re efficiency, surge/stall, variable-speed/pitch operation and module mass against relevant hardware. Validate hot material allowables and replace prescribed efficiency/head envelopes with bounded maps. |
| P6 | High | Inlet admission, pressure support and reverse flow | Use reviewed fluid-study coefficients with a domain of validity. Calibrate the continuous bidirectional port shared by the API and optimizer; include time-varying composition and non-equilibrium energy consistently. |
| P7 | High | Oxygen/nitrogen propulsion hardware | Efficiency, Isp, specific mass, power, lifetime and throttling must be coupled operating points. Add initial inventory and control reserve explicitly. The present independent Isp/constant-efficiency choice is a screening target. |
| P9 | High | Deployment and packaging at scale | Volume envelopes and 10 m/s area-dependent deployment are implemented. Validate complete folded radiator/plant envelopes, support/tether/cable mass, partial deployment, shading, loads and repeated cycle life. Replace provisional bulk-envelope densities with designs. |
| P10 | Medium | Warm thermal system | Confirm ammonia fluid/phase regime across operating temperatures, heat exchangers, pumping, heat storage, radiator distribution and transient peak duties. Peak aftercooler duty now sizes the shared exchanger allowance; validate transient exchanger behavior and all compression heat routing to the warm loop. |
| P11 | Medium | Cryogenic process and storage | Species-resolved separation/liquefaction, pressure management, tank heat leaks and boiloff. Above-feed-pressure coast gas now bypasses through a regulator without expansion credit. Resolve real-fluid throttling temperature, valve sizing and feed control. |
| P12 | High | Atmosphere and operating uncertainty | Evaluate density/composition/solar variability and navigation/control error over repeated passes. Optimize robust operating policies, not one deterministic atmospheric profile. |
| P13 | Medium | Optimization formulation | Keep architecture options discrete; optimize independent continuous coordinates within each. Separate numerical bounds from validated limits, quantify active constraints, scale degeneracy and uncertainty, and re-search after model changes. |
| P14 | High | Cold-gas / LN₂ mixing and film cooling | Incremental LN2 enthalpy, circulation, leakage, replacement and coast restoration are implemented. Add spatial film protection, exchanger conductance and calibrated temperature-dependent compressor maps before selecting a flight ratio. Preserve r=0 and all mass/energy ledgers. |
| P15 | High | Integrated aft tank, hull and stability structure | Replace independent surface allowances with explicit shared load paths, minimum gauge, buckling, bending, thermal and empty-tank loads. Couple rear pressure to compressor head/cutoff and coast process pressure. Distinguish extending the hull from using already-required skirt volume; validate minimum front depth before reallocating it. |
| P16 | High | Intermediate storage and compression scheduling | Optimize each chamber's usable volume and installed bank capacity jointly with dive/coast operation. Solve unequal interstage flows through inventory balances. Include isolation, delayed rack deployment/cooldown, cyclic recovery and downstream processing. Test whether later-bank/battery savings matter when first-bank mass dominates; use a specified liquefaction pressure and small process buffer initially. See the [staged model plan](../modeling/compressor/MODEL_PLAN.md#optimize-intermediate-storage-and-when-compression-occurs). |

## Detailed fluid analysis (offline)

| ID | Priority | Study | Output to primary model |
|---|---|---|---|
| F1 | High | Transient inlet, knife edge, throat and compressor boundary; startup, unloading and changing suction | Capture map, recovered-pressure map, leakage/backflow map, start/unstart envelope and time delay. |
| F2 | High | Rarefaction, non-equilibrium chemistry, gas-solid transfer and wall cooling | Validity/regime map, heat flux, species/enthalpy transport, exchanger pressure loss and heat-transfer coefficients. |
| F3 | High | Whole-body pressure and shear for candidate shapes | Integrated drag/lift, local heat/load distributions, centers of pressure, uncertainty and mesh/domain convergence. |
| F4 | Medium | Resolution and physical verification | Conservation, shock benchmarks, wall/port boundary checks, timestep/mesh studies and geometry provenance before supplying coefficients. |

See the [fluid analysis specification](../modeling/fluid/README.md). The numerical
port-flow helper in the primary model is not the detailed fluid solver.

## Flight stability and control (offline, coupled to fluid studies)

| ID | Priority | Study | Output / completion criterion |
|---|---|---|---|
| S1 | High | Pitch/yaw/roll forces and moments versus incidence and rates | Aerodynamic derivatives and center-of-pressure motion for the open inlet, varied suction and changing gas inventory. State sign/axis/reference conventions. |
| S2 | High | Six-degree-of-freedom pass dynamics | Perturbation response, trim, damping, control demand and trajectory sensitivity using computed mass distribution/inertia and fluid coefficients. |
| S3 | High | Fins, aft volume and thrust alignment | Trade stabilizing surfaces and bulb shapes against drag, heat, structure and usable volume; calculate control authority and off-axis thrust moments. |
| S4 | Medium | Flexibility, slosh and deployments | Long-body structural modes, tank slosh, absorber motion and deployment disturbance; check aeroelastic/control coupling and coast attitude constraints. |

See the [stability specification](../modeling/stability/FLIGHT_STUDY.md). Positive static
restoring stiffness alone does not establish dynamic stability.

## Current simplifications to retain visibly

- One continuous reduced inlet law computes admission and reverse flow; support,
  effective area and discharge coefficients remain scenarios, not shock CFD.
- Uniform cooled-plenum temperature and fixed representative molecular mixture;
  oxygen is transported, but full non-equilibrium species feedback is missing.
- A finite-backflow pump envelope replaces abrupt ideal-speed cutoff. Actual
  temperature-dependent efficiency, throughput and mass maps remain missing.
- Rejected-air momentum and escaping-gas recoil are charged as scenarios.
  Exterior pressure/shear and post-cutoff heat deposition need a shape solution.
- Metal heat capacity is an iron proxy. Bulk temperature is not edge lifetime.
- Mixing is a lumped LN2 stream with either fixed rack endpoint or fixed mixed
  inlet temperature. Vaporization kinetics, film distribution and pressure loss
  are unresolved. Compressor heat is assigned to the warm loop in every case.
- Hardware mass, constant efficiencies and deployment timing are development
  targets held fixed within each search. Circular-apogee delivery is not included.

Phase-change rack development: [candidate cores and cycle requirements](PHASE_CHANGE_COOLERS.md). These now have a reduced implementation; spatial phase-front and containment qualification remain open.

**Volume accounting:** [implemented screen](../modeling/deployment/IMPLEMENTED_VOLUME.md)
replaces arbitrary machinery lengths. Complete geometry, pressure bulkheads,
hatches and independent intermediate storage remain priorities. The
[finite rack model](../modeling/metal_coolers/FINITE_RACK_MODEL.md) documents the
small-interstage-inventory approximation and its explicit 1% acceptance screen.

### Encapsulated cooler cores

The optional two-temperature PCM model is implemented. Next establish compatible shell/core chemistry, cycling and pressure life, microgravity wetting/contact, spatial melt-front conduction and conductive-insert geometry. Compare stage-specific melting points and axial cascades. Retain the existing gas pressure-loss and interstage inventory TODOs; the present PCM sensitivity is not a global material/design optimum.

### Once-through liquid-cooling architecture

The [integrated ammonia option](../modeling/liquid_cooling/INTEGRATED_MODEL.md)
now couples finite exchanger conductance, controlled liquid flow, inventory
limits and regeneration to capture, compressor states, packing and deployment.
Next add axial liquid/wall startup dynamics and inventory-exhaustion control;
replace conservative liquid-side h and the Carnot-fraction/W-per-kg refrigerator
model with reference hardware maps. Study hot-front/cold-terminal cascades and
independent stage supply temperatures. Cold supply below 200 K still needs gas
phase/frost handling. Insulation, separator conduction, manifolds, fatigue and
pressure-tank geometry need engineering refinement. Retain solid metal, PCM and
mixing; the initial fixed-orbit ammonia sweep does not rule out other combinations.

### Reboost scheduling follow-up

The [Isp and solar-arc investigations](../investigations/reboost/README.md) establish
conditional screening minima. Next couple efficiency/Isp/species and engine mass;
search hybrid battery/direct-solar schedules and battery burst duration; integrate
variable mass and distributed drag; constrain gimbals, plume clearance and array
pointing. Require operational sunlight margin and qualify rejection-buffer material,
capacity and heat-transfer rates. First-order orbit closure is independently checked,
but does not resolve these flight/hardware limits.

### Ammonia tube geometry and manifolds

The [tube sweep](../investigations/liquid_cooling/TUBE_GEOMETRY.md) finds modest
payoff improvements with thinner tubes under current assumptions. Resolve headers,
branching, feasible passage lengths/counts, connectors, distribution uniformity and
startup. The present friction model automatically adds shorter parallel paths when
radius falls and charges only a fixed header drop. Qualify minimum wall thickness,
pressure/cycling stress, local boiling and liquid-side correlations. Pitch also
needs gas-side pressure loss before optimization. Large-bank failures of the
small-interstage-holdup screen require dynamic chamber modeling, not simply
deleting the screen. Coupling retained thruster heat to coolant requires a separate
enthalpy/inventory/regeneration balance.

### Independently evolving chamber inventories

The [isolated chamber laboratory](../modeling/chambers/README.md) now integrates
separate gas and metal energies and independent gas inventories across a compressor
network, including coast withdrawal. It is not integrated into the primary payoff
model. Before handoff, qualify quiescent gas/rack exchange, spatial mixing, real-fluid
properties, compressor controls/maps and physical deployment/heat paths. Do not
credit simultaneous retained-gas cooling and externally deployed racks without a
physical thermal connection. Use the module for controlled allocation studies;
no transient allocation optimum has yet been established.

The [transient allocation search](../modeling/chambers/OPTIMIZATION.md) now varies
independent rack and empty depths with pressure, temperature, geometry, conservation
and estimated repeat-cycle timing constraints. Its hardware-anchored payoff proxy
needs replacement by coupled plant, peak-power and packing budgets. Broaden search
across compressor capacity and coast schedules; resolve timed-out trials rather
than treating them as physically impossible. Intermediate buffer volume may have
different value when compressor stop times and discharge control can change.

### Material-specific isolated rack model

Implemented per-chamber sensible material identities (iron, FeCrAl, SiC, aluminum),
temperature-dependent caloric energy, density/displacement, emissivity-dependent
reset and a lumped-temperature Biot screen. See
[the material dossier](../modeling/chambers/MATERIALS.md) and
[allocation comparison](../investigations/chamber_transient/MATERIALS.md).
Still required: selected aluminum alloy and emissive surface life/mass; SiC
segmented supports and deployment mass; temperature-dependent conductivity and
internal gradients where necessary; material-specific accommodation, rarefied
heat-transfer validation, thermal shock, fatigue and repeated reset tests.
These properties are not yet propagated into the primary mission optimizer.

### Priority: replace the anchored transient mass proxy with an absolute cycle budget

[Mass audit](../investigations/chamber_transient/MASS_AUDIT.md): reboost/electrical
hardware dominates the 19,442 t mixed-material proxy. Recompute stage compressor
capacity/head/motor/spin/idle requirements, receiver-dependent coast processing,
thermal paths and periodic electrical/heat ledgers; then resize all machines,
battery/arrays/buffers/radiators/distribution and packing together. Define the
boundary between thruster hardware and power processors to prevent overlapping
kg/kW estimates. Source and vary the dominant 2 kg/kW thruster and 1 kg/kW bus
coefficients. The old warm thermal package plus hot-feed surcharge is not a
resolved component allocation. Preserve the 373-day result only as the documented
conditional operating-orbit proxy, not a fully recoupled or delivered payoff.

### Implemented first coupled cycle; remaining broad optimization

The [implementation plan](../modeling/primary/TRANSIENT_MODEL_PLAN.md) defines the
new transient evaluator, SiC-front/aluminum-downstream reference, physical volume
accounting, installed subsystem capacities, deterministic controls and independent
conservation/readiness checks. Each candidate integrates once: no cycle shooting,
periodic-state iteration or resize-and-rerun loop. The outer optimizer will vary
hardware, schedules, geometry and Isp. Legacy primary budgeting will migrate to
`scalar/` during implementation, with compatibility wrappers and frozen results;
The implementation now lives in `transient/`; `scalar/` provides a compatibility gateway without moving legacy imports. See [implementation details](../modeling/primary/TRANSIENT_IMPLEMENTATION.md).

### Formal periodic constrained optimization specification

The [mathematical specification](../modeling/primary/TRANSIENT_OPTIMIZATION_SPEC.md)
now makes design, controls and initial reusable states joint outer variables.
Five independent starting rack temperatures have five enthalpy-closure equations.
It replaces one-sided readiness as the final acceptance formulation with periodic
state equality, independently checked path limits and conservation. It also
clarifies actual liquid export versus reserve replenishment, a declared local
offload boundary, nonredundant geometry/compressor variables, real phase/plant
capacity requirements and caching one trajectory across objective/constraint
callbacks. The first evaluator now returns these residuals and rejects incomplete cycles. The broad joint optimization remains pending; the initial grid only explores a limited set of propulsion and power-capacity choices.

### Fixed outer geometry for the coupled search

Owner scope: retain reference diameter and set overall L/D exactly to 10. The
[scalar scope](../modeling/primary/SCALAR_SEARCH_SCOPE.md) makes the inherited
30 m bore / 31.7 m outside-diameter convention explicit (317 m overall), derives
receiver clear depth from remaining length, lists scalar seeds, and recommends
temporary locks on perigee, lattice geometry, topology and burn/control family.
Those additional locks are recommendations; apogee and Isp remain proposed search
coordinates. Saved 119 m-class proxy cases are not recomputed or relabeled as
results for the longer craft.

### Next coupled-reference review: pitch/pressure-loss reminder and burn duration

Owner accepts fixed 1 mm radius and temporarily fixed 10 mm pitch while lattice
head loss is omitted. **Remind the owner at the first coupled-reference review,
and before releasing pitch:** add pressure-drop/rarefaction treatment, compressor
head/work coupling and packing/heat-transfer consistency, then optimize pitch at
fixed radius. Denser packing is a legitimate hypothesis, not a rejected design.
Perigee should ultimately be selected by explicit reusable-entry and machinery
constraints; 85 km remains only the interim comparison scenario.

The [burn-duration aside](../investigations/reboost/BURN_DURATION.md) rejects the
300 s fixed-duration scope choice: a symmetric steered ~20-minute burn gives a
large conditional mass benefit. Duration is now an outer input alongside Isp,
using a finite-arc energy/angular-momentum penalty and actual power/thermal/duty
histories in the first coupled implementation. Its ~258-day frozen-budget estimate is not the new coupled payoff.
Fixed outer length prevents receiver volume or L/D diverging as hardware shrinks.

### Gaseous propellant and thermal/hydraulic pitch trades

The [gas-feed plan](../investigations/propellant_feed/PLAN.md) has primary-source evidence and a duty/storage screen; the cyclic gas buffer, feed hardware and selective-condensation comparisons remain to implement. The [rack-pitch plan](../investigations/rack_pitch/PLAN.md) requires a physical unit cell and paired heat-transfer/pressure-drop treatment before stage-specific pitch optimization. The [skin-friction investigation](../investigations/skin_friction/ANALYSIS.md) is implemented as an explicit coefficient scenario, not a validated coefficient prediction.
