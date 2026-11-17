# Coupled primary model: one forward cycle per candidate

**Status: first coupled implementation available.** See [implemented equations, scope and remaining differences](TRANSIENT_IMPLEMENTATION.md). This document retains the broader development plan. This replaces the anchored
hardware proxy with a time-dependent spacecraft cycle. The present models and
saved results remain available during the transition.

The [mathematical optimization specification](TRANSIENT_OPTIMIZATION_SPEC.md)
is authoritative for independent variables, payoff, periodic closure, operating
constraints and the outer solver contract. It adopts **periodic single shooting**:
design, controls and initial reusable states are co-solved outside the integrator.

The working architecture is an open inlet, high-temperature front rack, four
compressor blocks with independently cooled intermediate volumes, an aft receiver,
coast compression/liquefaction, and stored product. Use **SiC in the front rack
and aluminum in all downstream racks** for the first reference. Keep FeCrAl as a
front-material alternative and retain the explicit material/surface limits in
[the property dossier](../chambers/MATERIALS.md). SiC deployment/supports and the
aluminum alloy/emissive surface are development assumptions, not qualified designs.
No mouth closure is reintroduced; pressure-retaining rack-access hatches are
separate hardware with their own mass, leakage and operating conditions.

## Isp carried forward

The current reference uses **1765.95197 s Isp**, or **17.318 km/s** exhaust speed.
This was optimized with the preceding primary model at 85 × 2000 km, a 30 m bore,
a 300 s battery-fed reboost burst and the declared propulsion/electrical mass
coefficients. The isolated allocation/material studies held that Isp fixed. The subsequent
[burn-duration aside](../../investigations/reboost/BURN_DURATION.md) shows that the
300 s burst must not remain fixed: duration joins Isp as an outer variable,
initially with a centered symmetric steered burn family.
It is a starting point, **not the demonstrated optimum for the new cycle**.
Isp becomes an outer design variable again. Efficiency, installed kg/kW and
propellant compatibility must come from a declared capability scenario/map;
the optimizer cannot independently improve them. N2 and O2 propulsion remain
allowed, with species inventories and net product charged explicitly.

## Non-negotiable evaluation contract

```text
inputs = design + controls + capabilities + environment + initial_state
hardware = compile_design(inputs)              # direct geometry/mass/packing
history = integrate_one_cycle(hardware, inputs) # one forward trajectory
result = audit_and_score(hardware, history)     # no resize-and-rerun
```

One candidate has **one installed spacecraft, one initial state and one forward
integration**. The simulator must not:

- repeat orbits until temperatures, SOC or inventories converge;
- run an **inner** shooting/root solver to find periodic initial conditions;
- resize arrays, batteries, radiators, compressors or tanks from a trial history
  and rerun the candidate until a fixed point is reached;
- silently change a burn, cutoff, flow capacity or initial inventory to rescue
  feasibility;
- invoke an optimizer, CFD or a detailed structural simulation internally.

Adaptive timesteps, implicit ODE stage solves and local thermodynamic property
inversions are ordinary numerical integration, not prohibited cycle iteration.
Predetermined event segmentation remains one forward trajectory; there is no
restart from an earlier state to repair the design. Postprocessing may report
required capacity or a suggested next design, but must not charge that new mass
while retaining the performance of the old hardware.

The **outer optimizer** changes the candidate and calls this pure evaluation.
No optimizer is required to inspect or run one design. Every result serializes
the exact input set, installed hardware, initial/final state, events, constraint
residuals and mass/energy/species ledgers.

## Installed capacities and independent variables

Use `x = (design, controls, initial_reusable_state)` as specified in the
[variable registry](TRANSIENT_OPTIMIZATION_SPEC.md#2-independent-variables-and-dependent-quantities).
Installed capacities are selected before integration. The trajectory reports
performance and deficits; it never buys different hardware after the fact.

The registry distinguishes chamber/rack dimensions, installed compressor and
plant ratings, power/rejection hardware, propulsion and finite schedule parameters
from dependent mass, volume, flow, pressure and temperature. All five initial rack
temperatures are explicit outer variables, each matched by an enthalpy-closure
condition. Gas initial conditions have only independent mass/composition and energy
coordinates; P/T/rho are derived. Battery, warm-store and reserve states also close.

Do not independently optimize ratings and the mechanical geometry that derives
those same ratings. The initial compressor parameterization uses suction/head/motor
ratings with an explicit installed-bank sizing rule; a geometry-native variant
must replace those coordinates, not add redundant ones. Actual maps and rounded
installed hardware must agree. The cryoplant needs separate finite refrigeration
and exchanger capacities; unconstrained kg/s withdrawal is not a plant model.

Initial searches fix four blocks, common bore, SiC/Al materials and the reference
lattice. Release geometry, operating point and schedules in stages. Capabilities
such as emissivity, efficiency and kg/kW remain declared scenarios, not free
optimizer improvements. Full coordinate definitions, dependent quantities and
phase/volume equations live in the linked specification.

## Conserved states and subsystem exchanges

Reuse the isolated chamber equations and useful property/geometry components,
but replace their proxy budgeting and imposed withdrawal with coupled components.

| Subsystem | Integrated states and interactions |
|---|---|
| Every gas volume | Species masses and total internal energy; derive P, T, rho consistently; inlet/leakage, compressor ports, coast-feed ports, mixing and vent enthalpy |
| Each rack | Material energy and deployment position/exposure; finite gas-to-solid exchange, radiative loss, temperature limits and internal-gradient screening |
| Compressors | Flow/head/efficiency capability at actual inlet state; shaft speed/inertia where modeled; separate gas enthalpy rise, motor/drive loss, spin and idle electricity |
| Warm loop/store | Stored energy/temperature, coolant inventory, pump consumption, incoming component heat, available radiator rejection and insulation losses |
| Electrical system | Battery energy/SOC, permitted charge/discharge power, conversion losses, actual array exposure and illumination, curtailment and unmet demand |
| Coast processing | Feed/buffer inventories where needed, compressor and exchanger states, finite cooling/UA and refrigeration capacity, electrical demand and rejected heat |
| Product/propellant storage | N2/O2/other useful liquid, boiloff/vent, gas and liquid withdrawals; distinguish recycled coolant from new atmospheric product |
| Propulsion/orbit accounting | Consumed species, actual thrust and drag impulses, orbital energy/angular-momentum restoration residuals, component heat loads |

Use a **shared caloric reference** for each species across gas nodes, compressor
ports, phase change and storage. Do not splice absolute Cantera and HEOS
enthalpies. For supported cooled molecular states use real-fluid mixture
properties and isentropic endpoints plus efficiency; benchmark efficient tables
against the backend. For hotter/rarefied atmospheric entry, expose the selected
chemistry model and validity limits. Unsupported states cause a reported failure,
not silent extrapolation or treating dissociation energy as nonexistent.

For a fixed gas volume:

```
dm_species/dt = sum(species inflows) - sum(species outflows)
dU_gas/dt = sum(mdot*h_in) - sum(mdot*h_out) - Q_to_rack - Q_to_wall
dE_rack/dt = Q_from_gas - Q_to_space - other counted exchanges
```

Compressor shaft work is added to the discharge enthalpy exactly once; motor
losses go to their thermal node. Stored rack energy cannot also appear as warm
buffer duty. If withdrawing a rack changes the gas volume, include moving-volume
work `-P dV/dt` and its opposite mechanism-energy transfer, or use a documented
fixed-volume evacuated extraction approximation. Never change free volume at
finite pressure without accounting for that work.

Retain optional LN2 mixing through explicit mass/species/enthalpy ports, initial
inventory, injection power and recovery. Zero mixing is the reference; recycled
nitrogen is not product. PCM and ammonia alternatives remain separate comparison
architectures, not simultaneous mandatory systems in the first implementation.
Lattice pressure loss stays a declared zero-loss assumption for the initial
coupled release; preserve an interface for later correlations and sensitivity.

## One cycle and deterministic controls

Choose a reproducible epoch before the atmospheric encounter (initially -600 s
relative to perigee), and integrate through one nominal orbital period to the
same reference phase. Use the inherited orbit as a starting scenario, not an
optimized answer.

1. **Approach and intake:** arrays/radiators/racks stowed as required; inlet is
   open. Density, support pressure, total incoming energy, admission and reverse
   leakage follow the trajectory/environment. Pump flow is limited by installed
   machinery and actual downstream pressure, not unconstrained evacuation.
2. **Perigee reboost:** battery-supported thrusters operate according to the
   chosen schedule alongside compressors. Their simultaneous bus demand, battery
   draw, retained heat and propellant draw are integrated. Do not debit a nominal
   reboost energy and also integrate the same thruster energy.
3. **Recovery:** pumps continue until the selected pressure/capability/time cutoff;
   residual gas and leakage remain in the mass/energy ledger. Retained gas is not
   automatically liquid product.
4. **Coast:** actual partial array/radiator deployment supplies time-dependent
   generation and rejection. Coast processing draws from the receiver and
   intermediate volumes where specified; capacity and power can limit its rate.
   Separation, feed compression, liquefaction and warm rejection have distinct
   ports and costs. No required high-pressure feed is inserted without defining
   the chosen process and its pressure requirement.
5. **Rack extraction/reset:** isolate and depressurize the relevant chamber before
   opening a pressure hatch. Transfer recoverable residual gas or explicitly
   charge vent loss. Track mechanical travel, exposed area/view factor, radiation,
   retraction and hatch sealing. No rack simultaneously receives full internal
   convection and full external radiation. Stage racks may deploy at different
   times; no unnecessary rule makes every rack wait for the receiver to empty.
6. **End epoch:** report residual states and actual new liquid after propellant,
   recycled inventories, vents and other losses. No reset to nominal state.

The load allocator uses a declared deterministic priority policy and finite
ratings. It throttles discretionary processing or records unmet demand; it does
not grant free electricity. The same control policy is used in all candidates.
Local feedback (SOC limits, pressure cutoff, temperatures) is permitted and does
not require rerunning the cycle. Compressors, thrusters and cryoplant must expose
consistent demand and achievable-flow laws so power limiting cannot leave
upstream mass flow unchanged.

First orbit coupling: prescribed Kepler geometry with integrated drag/thrust
energy and angular-momentum residuals, plus apsidal consistency where relevant.
This is explicitly a small-perturbation model. Integrating actual planar position,
velocity and changing spacecraft mass can replace that trajectory provider later
without a shooting loop. Reject candidates outside the approximation's range;
do not optimize a non-restoring thrust schedule using energy alone.

## Volume, deployment and mass: evaluated from the installed design

Compute all stowed envelopes before integration: racks, compressor cases and
motors, liquefaction equipment, folded arrays/radiators, batteries, thermal stores,
propulsion/bus, liquid storage, mechanisms and clearance. Keep shared hardware
counted once. Machinery depth follows actual packages and bore area/fill factor;
there is no arbitrary 100 m allowance.

All chamber dimensions are physical; model vessel heads explicitly rather than
using full cylindrical volume for a length that includes heads. Gas volume cannot
be negative; rack envelopes cannot exceed their allocated space; lattice pores
remain gas volume. The same mass and geometry determine packaging and thermal
performance. Rated vessel pressure sets installed mass, while actual peak
pressure tests the rating.

Fix overall L/D = 10 and the reference diameter by owner instruction; see the
[scalar scope](SCALAR_SEARCH_SCOPE.md) for the 30 m bore / 31.7 m outside / 317 m
length convention and residual receiver allocation. Retain the 110 kPa storage
pressure screen as a declared study constraint, not a universal physical limit. Enforce actual temperature limits,
liquid/gas tank capacities, access openings and deployed/stowed collision
allowances to the implemented fidelity. Leave unmodeled aerothermal/stability
constraints clearly identified rather than calling these shapes survivable.

Deployment time comes from physical travel (initially a coefficient times
sqrt(deployed footprint)/10 m/s), not mass. Partial travel changes active area
using a declared geometry law; generation/rejection does not jump to full output
at the start of deployment. Use the same deployment law in the mass/volume and
cycle calculations. Re-evaluating geometry for a new optimizer candidate is
allowed; iterating its geometry within its one simulation is not.

Provide a component mass ledger with explicit scope, including thrusters versus
PPUs/bus, motors versus drives, coating/supports and mechanisms. Apply margin once.
Report structural/equipment dry mass, carried reusable working inventories,
propellant reserve, product inventory and launch/wet mass separately. Do not
hide a necessary coolant inventory by changing its category between designs.

## Periodic closure in the outer optimizer

The [closure specification](TRANSIENT_OPTIMIZATION_SPEC.md#4-closure-equations-cx)
requires equality of independent reusable states at the same cycle phase, after
only physically modeled transitions such as product offload. Each candidate still
runs once. The outer optimizer adjusts initial states, hardware and controls to
minimize payoff subject to these closure equations and operating inequalities.

Close rack specific enthalpies, gas species masses and internal energies, battery
energy, warm-store energy, working/propellant reserves and any dynamic machine
states. Restore modes/deployment and a nonredundant set of orbital invariants.
Useful-product export and cumulative energy/flow counters do not close.

One-sided readiness checks are exploratory diagnostics, **not substitutes for
periodic equality in the final optimization**. Allow physical solar curtailment
and controlled rack exposure; do not silently reset energy, gas or coolant.
Use scaled residuals with declared physical tolerances and a resource-drift
check; numerical conservation is independently required. There is no inner
periodic-state solve, and no automatic repeated-cycle convergence run.

The first periodic payoff assumes a declared local operating-orbit product-offload
boundary with reserve replenishment, storage capacity and counted transfers.
It does not claim a circular-apogee delivery service. A short fixed multi-cycle
validation after selection is permitted to diagnose drift, not to repair the
initial state used by the optimizer.

## Four audit findings addressed

| Finding | Replacement rule |
|---|---|
| Plant mass scaled without power/rejection | Install a selected plant capacity; derive its actual flow, electricity and heat from state and throttle; all exchanges enter shared ledgers |
| Legacy warm cooling overlaps rack cooling/surcharge | Assign every heat stream to an explicit node; remove anchored warm masses and the 10 kg/MJ surcharge from the new model; size installed devices from selected capacities |
| Compressor energy splices incompatible baselines | Integrate absolute pumping, spin, idle and drive losses using the same installed machinery; no delta added to an old reference |
| Stale package/deployment accounting | Compile all installed component envelopes once; integrate deployment from physical travel and exposure; enforce geometry and operational constraints directly |

The old 2 kg/kW thruster, 1 kg/kW distribution and 60% efficiency assumptions must
remain visible capability scenarios until better supported. Report sensitivity
because they dominate mass. Rack-material refinement is not a substitute for
propulsion/electrical component work.

## Repository transition

Do not move live modules during this planning change. In implementation:

```text
atmo_scoops/
  scalar/          # preserved legacy primary budgeting/orchestration
  transient/      # new coupled primary candidate evaluator
    inputs.py     # schema, independent coordinates, capabilities
    hardware.py   # installed geometry/mass/package compilation
    state.py      # conserved states and ledger definitions
    components/   # ports, compressors, racks, power, thermal, plant, storage
    controls.py   # deterministic schedules and power allocation
    cycle.py      # one forward integration
    metrics.py    # constraints, drift, mass and product/payoff outputs
  chambers/       # retain isolated laboratory and frozen comparison scripts
  studies/        # separate optimization, sensitivity and reporting drivers
```

“Scalar” names the legacy budgeting approach; it already contains some transient
submodels, so it must not be described as purely steady state. Move orchestration
and legacy assumptions first; share independently tested property/geometry/orbit
utilities instead of copying all code or leaving two inconsistent implementations.
Preserve old CLI/import entry points with compatibility wrappers and unchanged
archived inputs/results. Provide explicit `scalar` and `transient` entry points;
switch the default only after comparison and validation. Version output schemas
and model identity so old 373-day proxies cannot be mistaken for new results.
Detailed CFD and stability solvers stay outside both candidate integration and
the outer optimization loop; reviewed maps may supply coefficients/capabilities.

## Implementation sequence and acceptance criteria

1. **Freeze the reference and define the contract.** Preserve scalar results and
   mixed-material laboratory cases. Add validated schemas, material references,
   installed-hardware ledger and package compiler. Acceptance: deterministic mass
   closure, no duplicate component scope, valid volumes, reproducible serialization.
2. **Conservative transient core.** Reuse chamber/rack states with one property
   reference, physical component ports and independently limited compressor blocks.
   Acceptance: reproduce laboratory limits, sealed equilibration, mass/species and
   energy conservation, meaningful pump cutoff/stall scenarios and resolution checks.
3. **Power, propulsion and warm heat.** Add finite solar/battery/bus/thermal-store/
   radiator capacities and deterministic controllers. Acceptance: no free SOC or
   heat sink; reproduce analytical impulse-energy relations and simple charge/
   discharge, eclipse and rejection limits. Separate nominal requests from actual
   delivered thrust and compression; test simultaneous peak demands.
4. **Coast plant, storage and rack motion.** Couple actual liquefaction and species
   storage, pressure-safe extraction, partial deployment, reset and repacking.
   Acceptance: withdrawal is not product until condensed, every heat/load counted
   once, volume/enthalpy conservation through events, reserve and boiloff accounting.
5. **One complete reference cycle.** Return P/T/rho, rack temperature, inventories,
   component power/heat, SOC, exposed areas, thrust and all endpoint residuals.
   Produce a full mass breakdown. Acceptance: no hidden reruns, meaningful
   readiness constraints and explicitly stated orbital/thermophysical limits.
6. **Outer optimization.** Start with rack/volume allocation and hardware ratings
   at the reference orbit; then free Isp/burn controls, compressor capacities and
   coast scheduling and apogee. Diameter and L/D remain fixed; the scalar scope
   recommends holding perigee and lattice geometry while their limits are unresolved. Reoptimize
   Isp rather than carrying 1766 s forward as a permanent optimum. Report multiple
   starts, active bounds, solver failures, sensitivity and refined verification.

End-to-end acceptance includes conservation, limiting cases, timestep/property
resolution, installed-power saturation, material/rack fit, cycle inventory drift,
phase-safe hatch operation, and repeatability of a selected short validation
campaign. Test that a candidate evaluator calls the forward cycle once and cannot
resize hardware after seeing its trajectory. Preserve scalar benchmark tests.

## Payoff reporting

For a feasible periodic candidate,

```
payoff_days = dry_mass_kg * cycle_seconds / (86400 * net_useful_liquid_kg_per_cycle)
```

The [product-ledger specification](TRANSIENT_OPTIMIZATION_SPEC.md#3-payoff-and-material-accounting)
counts actual useful cryogenic liquid exported after restoring reusable reserves;
propellant/recycled coolant must not be credited or deducted twice. Retained gas
is not liquid product. Non-closing candidates receive diagnostics, not an accepted
sustained-payoff claim. Initial product/energy cannot subsidize repeated operation.

Report dry equipment and working/wet inventories separately under one consistent
mass convention. Circular-apogee export/return remains a separate mission module;
leave delivered payoff unset until modeled. Component capabilities and physical
validity remain distinct from numerical periodicity and conservation.

Related: [mass audit](../../investigations/chamber_transient/MASS_AUDIT.md),
[material study](../../investigations/chamber_transient/MATERIALS.md),
[compressor development plan](../compressor/MODEL_PLAN.md),
[propulsion assumptions](../propulsion/REBOOST_INVESTIGATIONS.md).
