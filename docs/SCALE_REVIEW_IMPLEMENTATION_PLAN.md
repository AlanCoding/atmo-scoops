# Model changes from the scale-image review: accepted grouped sequence

**Completed historical plan.** The [finalized v1.0.1 design](publication/V1_0_1.md) supersedes implementation planning. The sequence below is retained only as historical context.

The owner has combined the earlier six steps into three numerical checkpoints.
The numerical baseline remains frozen plate case 72 (~278 operating-orbit days).
Checkpoint A now has a [converged 275.7-day result and review packet](../investigations/staggered_stage_a/README.md). Front dimensions in the updated scale figure come from that result; aft placement remains proposed. B and C follow independently after review.

## Current disposition and remaining agenda

The boosted spherical-reserve architecture has been rejected. Its [timing/power audit](../investigations/staggered_stage_a/RESERVE_REFILL.md) is historical evidence. The valve-connected compartment remains the agreed architecture.

**Further numerical changes are on hold while the owner reviews the design.**
The existing coast liquefaction approximation is accepted for now; detailed
cryogenic-process refinement is deferred. The receiver coast readout and explicit
thruster-reserve drawing document existing behavior, not new hardware or payoff.

The present model already contains four boosted gas-reserve spheres: 500 m³
combined internal volume, 4,500 kg initial charge, 15 bar rating, refill booster,
feed hardware and separate gas/energy states. Their actual optimized-cycle
pressure varies approximately 2.30–10.35 bar. The updated scale drawing shows them
at a proposed axial station around 88.6 m; tank diameters are scaled, radial
placement and pipe routes are conceptual. This is different from checkpoint B's
proposed full-cross-section 125 m compartment.

Remaining agreed geometry/storage checkpoints:

1. **B: radial packaging and alternative aft reserve.** Resolve folded panels,
   radiators, cryogenic packages, deployment exits and CM; replace the existing
   boosted reserve with the proposed aft compartment only with explicit valve,
   feed-pressure and cycle-closure accounting. Deduct other packages only from
   the receiver portion forward of its protected 125 m.
2. **C: five-cycle product storage.** Size usable liquid volume and ullage, carry
   growing product mass, and account for thermal holding and offload.

Unscheduled model-quality follow-ups, to be scoped individually:

- **Rack hydraulics/buildability:** resolve front-tail losses greater than inlet
  pressure, review pump cutoff, and investigate active rack area/row count. Test
  staggered thermal-spacing equivalence and offset losses together.
- **Compressor sizing freedom:** current motor powers vary, but flow capacities
  and available head remain fixed. Release them in a controlled collection/mass
  trade before calling the compressor hardware globally optimized. No additional
  receiver-pressure coordinate is currently requested.
- **Numerical robustness:** replace fragile automatic event-start steps with
  tested initialization and/or physically scaled state tolerances. Preserve
  single-cycle evaluation and resolution checks without weakening closure.
- **Flight and deployment:** refine exterior skin-friction/spillage allowances,
  inlet behavior, material limits, plume clearance, CM/stability, actual package
  routes and sun-synchronous illumination. Detailed CFD remains outside the
  optimizer. Circular-apogee delivery remains a separate mission-accounting gap.

Later architecture studies remain **v1.1** (fixed downstream coolant tubes,
retained deployable front SiC) and **v2.0** (diver plus tether mothership).
These are agenda items, not instructions to start simultaneous implementation.

## A — Staggered cooler AND explicit stage geometry together

- Preserve plate material inventory while increasing pitch and serial core length;
  use n-way offset rows. Keep SiC front and Al downstream. Use wider physical
  spacing for friction and smaller effective thermal spacing for heat transfer.
  Pay for this equivalence with the full longer core volume; retain row-entry loss.
- Fix **10 m empty inlet space** ahead of the first rack. This is gas inventory,
  not machinery. It does not validate a spatial shock/diffuser design.
- Each front stage explicitly locates gas space, rack and actual compressor bank;
  give it **1 m of hatch-equipment space**. Delete arbitrary 12/10/10/27.62 m
  shared bay lengths. Retain necessary vessel heads explicitly and account for
  their fluid space only once. Compressor lengths come from their hardware model.
- Do not delete batteries, solar/radiator stowage or other equipment. Until B gives
  them resolved radial locations, retain their individual package volumes as an
  explicit displacement from the aft region, not as generic front grey blocks.
- Keep existing propulsion/feed and product-storage architecture for comparison.
  Start with a fixed row count and existing five gas/solid thermal inventories;
  thermal-spacing equivalence is an explicit reduced-model assumption, not resolved CFD.
  If row temperatures become independent states later, add explicit initial
  conditions, conservation terms and closure constraints in a separate refinement.
- Establish fixed-design behavior and meaningful limiting-case tests, then run
  the actual constrained optimizer. Validate the selected point at refined
  resolution, record the review packet and **commit checkpoint A**.

## B — Receiver packaging AND 125 m isolated propellant section together

- Protect the **last 125 m** for the aft propellant compartment. Subtract solar,
  radiator, cryogenic and other package displacement **only from the main receiver
  region forward of that section**. Respect existing front allocations; do not
  charge packages twice. A nonpositive main gas volume is infeasible.
- Narrow the main receiver to a constant barrel radius with explicit heads;
  resolve cryogenic equipment around its forward end and solar stowage farther
  aft. Move thrusters wholly behind the hull. Track CM, routes and clearances.
- Reuse the existing reserve species/energy states for the isolated aft compartment,
  calculate its pressure, and add finite valve flow. Isolate in coast, feed pre-entry thrust from it, reopen
  when collecting-receiver pressure catches reserve pressure, and resolve shared
  feeding/refill and subsequent isolation. Prevent chatter with documented controls.
- Replace old boosted-reserve equipment only when its function is replaced. Few-kPa
  storage cannot silently satisfy the old one-bar feed requirement; include any
  needed feed pumping and its energy/hardware. No arbitrary residual reserve floor.
- Re-optimize, validate, plot both pressures and inventories plus valve/thruster
  flows, and **commit checkpoint B** independently of A.

## C — Gentle multi-pass storage: FIVE cycles

- Target **five cycles**, superseding the earlier 60 m³/~15-pass drawing proposal.
  At the old ~4.03 m³/batch yield this is ~20.2 m³ of liquid before ullage; use
  actual updated production when sizing the tank rather than fixing that estimate.
- Include tank/insulation/holding costs, inventory growth and explicit offload.
  Keep cyclic working inventories distinct from accumulating product. Validate
  a five-pass campaign; do not require product itself to close after each pass.
- Use a tractable operating-cycle optimization with stated carried-product/load
  assumptions, then check campaign endpoints and offload balances. Report loaded
  CM and relevant propulsion effects. Do not silently claim circular-apogee delivery.
- Re-optimize as required, validate and **commit checkpoint C**.

## Gate, state-vector and review discipline

For each checkpoint save parent commit, exact configuration, state schema, units,
solver/correlation versions, coordinate bounds and optimizer termination. One
forward cycle per candidate; no inner closure shooting or hardware resizing.
New physical states need explicit mass/energy balances and periodic residuals.
Never mix cached evaluations from different equations or geometry versions.

Run conservation, limiting-case and integration-resolution checks. Use the real
constrained optimizer and record its termination separately from feasibility.
Numerical failure is unresolved, not a bad physical design. A failed gate must
not be hidden by more simultaneous architecture changes or weaker tolerances.

The review packet includes old/new payoff and its endpoint, component mass and
volume, gas/product/propellant per cycle, rack geometry, front and aft depth,
compressor/rack energy, full-cycle P/T/inventory histories, closure residuals,
active constraints/bounds and numerical/physical validity flags. Highlight odd
results explicitly. Commit accepted checkpoints separately for rollback/review.
Do not describe power-only losses as a solved pressure field when loss is large
relative to available pressure.

## Return to the scale image

After the numerical checkpoints, regenerate SVG/PNG and the length/mass table
from one accepted geometry manifest: empty gas space → rack → compressor,
1 m hatch equipment, actual residual receiver, protected aft reserve, peripheral
packages and thrusters. No enlarged inset, generic shared front allocation or
redundant 125 m dimension bar. Publish any still-proposed locations as such.

## Deferred

Keep the existing Cf=0.002 for controlled comparisons; detailed skin-friction
refinement, cryogenic-process integration, compressor maps, plume/stability and
deployment qualification remain follow-ups. The v1.1 downstream coolant tubes
and v2.0 mothership/tether architecture remain later work. See
[staggered-cooler research plan](../modeling/metal_coolers/STAGGERED_PLATES_PLAN.md).

### B implementation detail: working inventory is a closure variable

The existing gas-feed reserve already has three species inventories and an energy
state. Reuse those for the physical aft compartment where possible rather than
adding a duplicate tank state. Replace the old refill-compressor connection with
the declared finite isolation/equalization valve; model any required thruster-feed
booster separately. Its output pressure must come from the propulsion feed model,
not an assumed free pressure rise.

An oversized isolated section can retain more than half a burn's propellant.
Its starting inventory must therefore satisfy the end-of-cycle working-inventory
closure, rather than being hard-coded to half the burn consumption. In a simple
isothermal equalization limit, if fraction f of the shared gas volume is isolated
at the end of collection, the steady reserve satisfies
`R = f (R + captured - propellant)`, or
`R = f/(1-f) × net_retained_per_cycle` before other withdrawals/losses.
This is a diagnostic limiting case, not a substitute for the transient valve,
thermal, feeding and liquefaction balances. It makes the protected 125 m volume's
inventory implications explicit without turning its length into a new optimizer
coordinate.
