# Model improvement list

This is a maintained list of missing capabilities, not a work diary. Remove or
rewrite an item when the model resolves it, and link its validation. Priorities
reflect how strongly a missing relationship can distort design selection.

The next controlled architecture studies are specified in
[DESIGN_STUDIES_PLAN.md](DESIGN_STUDIES_PLAN.md): optional mouth closure and
cold-nitrogen injection. Their prerequisites and decision criteria govern the
order of work; the present plan does not declare either option a winner.

## Primary model and optimization

| ID | Priority | Missing relationship | Required implementation / acceptance evidence |
|---|---|---|---|
| P1 | High | Circular-apogee delivery and return | Integrate the delivery/recovery trajectory, mass changes, tanks, export hardware and propellant; report delivered payoff alongside operating payoff. |
| P2 | High | Finite-thrust reboost and real drag | Integrate thrust around perigee with mass/inertia, atmospheric force and expelled-gas momentum. Bound burn duration physically. Couple density/altitude to the actual powered trajectory. |
| P3 | High | Gas-to-metal exchange | Spatial/temporal gas and solid temperatures, conductance, passage spacing, pressure drop and storage utilization. Connect sheet thickness, gas endpoint and front depth so optimization cannot reduce area or approach without cost. |
| P4 | High | Actively cooled leading edge and reusable perigee envelope | Resolve local heat flux, cooling flow, temperature, stress, oxidation/erosion and fatigue over repeated dives. Output allowable operating envelopes versus geometry/material/cooling, including life and replacement mass. Extend the atmosphere domain when justified; do not mistake 75 km for a materials limit. |
| P5 | High | Compressor maps and transients | Suction capacity, pressure ratio, efficiency, module sizing/mass, low-pressure limit, spin-up and thermal limits. Replace constant efficiency and kg/(m³/s) targets with a bounded map. |
| P6 | High | Inlet admission, pressure support and reverse flow | Use reviewed fluid-study coefficients with a domain of validity. Replace prescribed full inbound capture and the provisional outbound reservoir boundary; include time-varying composition and non-equilibrium energy consistently. |
| P7 | High | Oxygen propulsion hardware | Efficiency, Isp, specific mass, power, lifetime and throttling must be coupled operating points. Add initial inventory and control reserve explicitly. The present independent Isp/constant-efficiency choice is a screening target. |
| P8 | Medium | Mouth closure and protection | Door/iris structure, actuators, seals, pressure loads, cooling, opening/closure timing as a control variable, actuation duration, leakage and repeated life. Compare with open-mouth early-entry heating and any protective hardware. Area-specific mass is currently only a sensitivity input. |
| P9 | High | Deployment and packaging at scale | Stowed volumes, deployed support/tether/cable mass, mutual shading, two-face radiator view factors, cycling times, failure modes and life. Five-minute timing cannot be assumed scale-independent indefinitely. |
| P10 | Medium | Warm thermal system | Confirm ammonia fluid/phase regime across operating temperatures, heat exchangers, pumping, heat storage, radiator distribution and transient peak duties. Replace the averaged aftercooler sizing allowance. |
| P11 | Medium | Cryogenic process and storage | Species-resolved separation/liquefaction, pressure management, tank heat leaks and boiloff. Remove the current below-1-bar coast-feed-compressor domain restriction with a suitable process model. |
| P12 | High | Atmosphere and operating uncertainty | Evaluate density/composition/solar variability and navigation/control error over repeated passes. Optimize robust operating policies, not one deterministic atmospheric profile. |
| P13 | Medium | Optimization formulation | Keep architecture options discrete; optimize independent continuous coordinates within each. Separate numerical bounds from validated limits, quantify active constraints, scale degeneracy and uncertainty, and re-search after model changes. |
| P14 | High | Cold-gas / LN₂ mixing and film cooling | Couple injection enthalpy/phase, local thermal protection, rack heat transfer, compressor maps, circulating inventory, leakage and coast restoration. Preserve r=0 and reject free cooling or recycled coolant counted as new product. Execute only after the compressor/thermal readiness gate in the architecture plan. |

## Detailed fluid analysis (offline)

| ID | Priority | Study | Output to primary model |
|---|---|---|---|
| F1 | High | Transient inlet, knife edge, throat and compressor boundary; startup, unloading, closure and reopening | Capture map, recovered-pressure map, leakage/backflow map, start/unstart envelope and time delay. |
| F2 | High | Rarefaction, non-equilibrium chemistry, gas-solid transfer and wall cooling | Validity/regime map, heat flux, species/enthalpy transport, exchanger pressure loss and heat-transfer coefficients. |
| F3 | High | Whole-body pressure and shear for candidate shapes | Integrated drag/lift, local heat/load distributions, centers of pressure, uncertainty and mesh/domain convergence. |
| F4 | Medium | Resolution and physical verification | Conservation, shock benchmarks, wall/port boundary checks, timestep/mesh studies and geometry provenance before supplying coefficients. |

See the [fluid analysis specification](../analysis/fluid/README.md). The numerical
port-flow helper in the primary model is not the detailed fluid solver.

## Flight stability and control (offline, coupled to fluid studies)

| ID | Priority | Study | Output / completion criterion |
|---|---|---|---|
| S1 | High | Pitch/yaw/roll forces and moments versus incidence and rates | Aerodynamic derivatives and center-of-pressure motion for open/closed mouths, varied suction and changing gas inventory. State sign/axis/reference conventions. |
| S2 | High | Six-degree-of-freedom pass dynamics | Perturbation response, trim, damping, control demand and trajectory sensitivity using computed mass distribution/inertia and fluid coefficients. |
| S3 | High | Fins, aft volume and thrust alignment | Trade stabilizing surfaces and bulb shapes against drag, heat, structure and usable volume; calculate control authority and off-axis thrust moments. |
| S4 | Medium | Flexibility, slosh and deployments | Long-body structural modes, tank slosh, absorber motion and deployment disturbance; check aeroelastic/control coupling and coast attitude constraints. |

See the [stability specification](../analysis/stability/README.md). Positive static
restoring stiffness alone does not establish dynamic stability.

## Current simplifications to retain visibly

- Full geometric inbound capture and uniform cooled-plenum temperature.
- Open outbound pressure support and discharge coefficient are scenario values;
  the compressible port law is not a hypersonic inlet solution.
- Thermal properties use a fixed inbound-mean mixture during a cycle; open-phase
  oxygen inventory has a transported species budget, but full species/chemistry
  feedback on thermal properties is not resolved.
- Capture impulse is charged on all admitted gas, including gas later lost.
  Exterior, open/closed-door and jet/reverse-flow momentum corrections remain
  unresolved; a multiplier is not a shape solution.
- Metal heat capacity is an iron proxy, not a selected alloy. Bulk endpoint
  temperature is not a cooled-edge material-life calculation.
- Hardware coefficients, constant efficiencies and deployment timing are
  development targets. They are held fixed in design searches.
