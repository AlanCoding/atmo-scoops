# Model improvement list

This is a maintained list of missing capabilities, not a work diary. Remove or
rewrite an item when the model resolves it, and link its validation. Priorities
reflect how strongly a missing relationship can distort design selection.

Completed numerical decisions are indexed in [investigations](../investigations/README.md).
The [mixing development plan](DESIGN_STUDIES_PLAN.md) describes the remaining
physical calibration needed beyond the current conditional trade.

The [staged-compressor model plan](../modeling/compressor/MODEL_PLAN.md)
sets the next core refinement: three/four cooled blocks, independently allocated
rack masses, lattice-based heat transfer and solved gas states. Real-fluid compression
states and a conditional geometry mass model are implemented; independent rack
inventories and finite heat transfer remain planned. See the
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
| P2 | High | Finite-thrust reboost and real drag | Integrate thrust around perigee with mass/inertia, atmospheric force and expelled-gas momentum. Bound burn duration physically. Couple density/altitude to the actual powered trajectory. |
| P3 | High | Gas-to-metal exchange | Spatial/temporal gas and solid temperatures, conductance, passage spacing, pressure drop and storage utilization. Connect sheet thickness, gas endpoint and front depth so optimization cannot reduce area or approach without cost. |
| P4 | High | Actively cooled leading edge and reusable perigee envelope | Resolve local heat flux, cooling flow, temperature, stress, oxidation/erosion and fatigue over repeated dives. Output allowable operating envelopes versus geometry/material/cooling, including life and replacement mass. Extend the atmosphere domain when justified; do not mistake 75 km for a materials limit. |
| P5 | High | Compressor maps and transients | Real-fluid block work, geometry mass, spin-up and receiver-dependent head limits are implemented. Calibrate low-Re efficiency, surge/stall, variable-speed/pitch operation and module mass against relevant hardware. Validate hot material allowables and replace prescribed efficiency/head envelopes with bounded maps. |
| P6 | High | Inlet admission, pressure support and reverse flow | Use reviewed fluid-study coefficients with a domain of validity. Calibrate the continuous bidirectional port shared by the API and optimizer; include time-varying composition and non-equilibrium energy consistently. |
| P7 | High | Oxygen propulsion hardware | Efficiency, Isp, specific mass, power, lifetime and throttling must be coupled operating points. Add initial inventory and control reserve explicitly. The present independent Isp/constant-efficiency choice is a screening target. |
| P9 | High | Deployment and packaging at scale | Stowed volumes, deployed support/tether/cable mass, mutual shading, two-face radiator view factors, cycling times, failure modes and life. Five-minute timing cannot be assumed scale-independent indefinitely. |
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

Phase-change rack development: [candidate cores and cycle requirements](PHASE_CHANGE_COOLERS.md). Add independent core enthalpy/melt fraction, containment mass, finite heat transfer and coast refreezing before claiming savings.

**Volume accounting priority:** replace arbitrary front/machinery lengths with per-stage rack/plenum and compressor envelopes plus stowed equipment allocations. [Research and acceptance criteria](../modeling/deployment/CLOSE_PASS_VOLUME.md); [source-based diagnostic](../modeling/deployment/PACKING_SCREEN.md). The existing bank-state model does not implement separate interstage inventories.
