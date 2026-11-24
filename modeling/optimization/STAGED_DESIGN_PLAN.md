# After v1.0.1: staged sizing and transient correction

Status: proposed methodology, not implemented. Freeze v1.0.1 and its publication
assets first. Settle this workflow before starting further design/publication
expansions or the v1.1 coolant architecture. Do not replace the frozen result or
revive obsolete scalar assumptions in the name of simplification.

## What the latest solve establishes

Perigee was an independent coordinate, bounded 80–100 km, and selected 85.804456 km.
Apogee remained 2,000 km. The 46-coordinate solve included capacity, geometry,
initial thermal states and reserve state. Constraints required capture ≥99.9%,
receiver peak within 50 Pa of 4,766.83 Pa, full impulse, and cyclic closure.
Full collection does not make constrained optimization mathematically unsuitable.
The issue is numerical conditioning and redundant/tightly coupled design freedom.
A successful local termination is not evidence that the best basin was found.

The search needed three-coordinate state/orbit restoration, derivative-free
COBYLA after noisy SLSQP differences, positive constraint scaling and conservative
resolution margins. Some processes were interrupted externally; that is distinct
from integration failure. A low-solar seed matched gas closure but failed battery
recharge by 16.7 MWh. Energy totals alone cannot size a scheduled power system.
Use these as requirements for a more transparent workflow, not as proof that the
physics is unstable or that constraints should be discarded.

## 1. A deterministic design worksheet

One input set produces one sizing report, with intermediate calculations exposed.
Begin with fixed diameter (system scale), L/D, apogee, materials, deployment speed,
pressure ratings and component capability assumptions. Declare which are requirements
and which are provisional. **Reserve length is an internal sizing result, not a
project-level input.** The 125 m value belongs only to frozen v1.0.1. Size the
reserve and main-receiver partition together from the burn/refill schedule, finite
feed/valve capability, thermal state and allowable pressure. The partition may be
an internal search coordinate, but the user should not have to prescribe it.
Every other scalar is labeled input, derived quantity, integrated state, control
rule or closure residual.

Keep L/D=10 for this next step. Later, after a sufficiently credible exterior
skin-friction model and structural/packaging limits are available, hold diameter
fixed and let length be selected by the design process. The existing constant-Cf
screen alone is not that qualification; do not release length yet.

1. Allocate actual package volumes and pressure-vessel heads. Allocate the remaining
   space between main receiver and reserve, rather than subtracting a fixed 125 m.
   Size reserve working inventory from the maximum cumulative deficit between
   thrust demand and net valve replenishment, plus the gas needed for finite feed
   pressure/flow. Include refill during thrust, the refill peak, periodic closure
   and any explicit engineering margin. No requirement to carry an entire pass
   of propellant before firing. Compute both gas capacities without subtracting
   equipment twice. Because power sizing
   changes packaging, the first pass is an explicitly provisional estimate.
2. Specify a target collected batch and receiver fill state. Account for propellant
   taken during the pass and replenishment of reserve, not just final main-tank mass.
   Do not independently prescribe receiver volume, mass, pressure and temperature.
3. Determine a candidate perigee from the orbit-integrated column mass:
   `m_incident(h) = A_mouth ∫ rho(altitude(t; h, ha)) v_relative(t) dt`.
   Use a bracketed scalar root against the required batch; verify monotonicity over
   that bracket and report infeasible brackets explicitly. This root uses reduced
   equations, not repeated transient cycle shooting. It is not a survival limit.
4. Size compressor/cooler blocks from the required *time profiles*, including the
   ascent evacuation tail, and estimate the fill temperature. Compute power and
   propulsion from the same mass/impulse budget. Reconcile package displacement in
   a visible outer design sweep if it changed enough to invalidate step 1.
5. Integrate a simplified time schedule for battery state, warm-store temperature,
   deployment and coast processing. Select installed ratings from both power and
   energy constraints. Show every limiting time and capacity.
6. Emit a complete transient input file and a ledger of assumptions/derived values.
   A one-pass worksheet must report mismatch; it must not hide internal iteration
   or silently force closure by changing stored energy or discarding gas.

The scalar column root selects altitude for inventory. Admission capacity and
shock support are separate checks: sufficient integrated storage does not ensure
that the first compressor can accept the peak flow. Keep the transient capture
check and pressure/flow envelope as acceptance gates.

## 2. Small, coordinated subsystem optimizations

- **Compressor and cooler blocks:** optimize plate inventory, physical/effective
  spacing, thickness and installed suction/head/motor capacities with real-gas
  states, finite heat transfer, thermal storage and the currently declared loss
  approximation. Boundary inputs include inlet mass/enthalpy/pressure histories,
  downstream pressure envelope, available length and electrical limits.
- **Receiver and coast processing:** size processing capacity and heat rejection
  against time-varying receiver pressure and the required end inventory. Reserve
  stays isolated through coast; no implicit refill compressor.
- **Propulsion and power:** optimize Isp and burn duration jointly with propellant,
  thruster rating, battery and solar capacity under the same orbit-restoration
  requirement. Include time-resolved loads and deployment delays.

Do not optimize each compressor stage greedily for its own mass. Upstream cooling
changes downstream suction volume, head, receiver density and electrical demand.
Use stage response curves or Pareto tables (mass, work, outlet enthalpy, volume,
heat to reject), then optimize the four-block chain or iterate coordinated boundary
contracts. An explicit outer sweep is preferable to hidden nested convergence.

## 3. The transient model is the referee

Compile hardware once and run one forward cycle per candidate. Check species and
energy conservation, full admission within a stated numerical/tail tolerance,
propellant-feed margin at every burn phase, valve timing, temperature/pressure
limits, physical packing and periodic rack/battery/reserve/warm-store closure.
A reduction must not relax these checks. Include a tighter-resolution replay.

Store *bounded correction maps* from worksheet predictions to transient results:
peak admission derating, final receiver temperature, suction/head capacity needed,
compressor work, rack recovery time, battery recharge deficit and valve/feed margin.
Keep numerical tolerances, source revision, calibration domain, residuals and
held-out prediction errors with every map. Use additive corrections near zero
closure residuals; multiplicative ratios there are ill-conditioned. Do not use one
payoff multiplier to conceal inconsistent subsystem balances or extrapolate beyond
the sampled domain. Low-dimensional maps require enough independent samples.

## 4. Limited outer coordination, then optional polishing

First use transparent sweeps over a few genuine choices (Isp, burn duration,
receiver target, selected thermal allocation). Derive altitude conditionally and
carry a small set of starting states as explicit closure variables where necessary.
A small outer constrained optimizer can then coordinate those choices against the
subsystem maps. Alternatively retain a grid/Pareto selection when discrete choices
make a smooth optimizer misleading. Global optimization is not mandatory.

Only use full transient constrained polishing once the reduced candidate is already
near feasible and shows margins larger than numerical noise. It remains an outer
solve; the forward model never iterates a candidate through repeated cycles.
Report total simulations, errors, termination, bound hits and resolution sensitivity.

## Acceptance gates before replacing the current workflow

1. Replay frozen v1.0.1 exactly; preserve its config and hashes.
2. Reconstruct its mass, package volume, capture, feed and scheduled energy budgets
   with the worksheet. Publish discrepancies rather than calibrating them away.
3. Verify response directions using controlled perturbations of altitude, rack
   inventory/gap, compressor capacities, solar and reserve length.
4. Validate corrections on held-out designs. Set accuracy and feasibility-margin
   requirements from measured numerical repeatability before accepting a surrogate.
5. Demonstrate fewer costly transient evaluations and reliable physical closure
   for a new design. Compare equal freedoms and assumptions to the old solve.
6. Commit a separately labeled design only after numerical and engineering review.

This work changes the design workflow first, not the physical capabilities or the
v1.0.1 publication numbers. Skin-friction refinement, detailed compressor maps,
cryogenic integration and v1.1 remain separately tracked work.


## Thermal scheduling detail to carry into the redesign

Distinguish receiver rack 5 from the four compressor-inlet racks. v1.0.1 holds
it stowed until plant stop + purge (+72 minutes), whereas racks 1–4 release at
+12 minutes. All racks throttle modeled radiation at their input starting
temperature. In the staged model, make these control assumptions explicit:
state/pressure-based deployment timing, passive cooldown versus controlled
exposure, and the hardware/energy needed to stop at a target temperature.
Validate gas-to-solid heat direction during receiver blowdown. Reserve partition
sizing remains a subsequent internal-design TODO, not a fixed user requirement.
