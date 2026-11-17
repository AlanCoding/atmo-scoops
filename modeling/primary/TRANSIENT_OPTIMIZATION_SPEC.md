# Periodic coupled design optimization: mathematical specification

**Status: first forward evaluator and limited constrained candidate search implemented.** The full general optimization remains a target; see [implementation scope](TRANSIENT_IMPLEMENTATION.md). This is the authoritative optimization
formulation for the [transient implementation plan](TRANSIENT_MODEL_PLAN.md).
The [scalar search scope](SCALAR_SEARCH_SCOPE.md) fixes the owner-selected diameter
and exact L/D, and separates proposed temporary locks from scalar optimizer inputs.
It replaces the plan's earlier one-sided readiness interpretation with a periodic
single-shooting problem. One forward trajectory evaluates one candidate; design,
controls and periodic initial states are co-solved in the outer optimization.

## 1. Problem definition

For a fixed architecture/capability/environment scenario `a`, write

```
x = (d, u, z0)
H = compile_hardware(d; a)
z_dot = F(t, z, H, control(t, z; u), a)
z_end = Phi(x; a)                 # exactly one forward integration
minimize J(x) = M_dry(d) * T_cycle(d) / (86400 * Delta_m_useful(x))
subject to c(x) = 0, g(x) <= 0, and x_lower <= x <= x_upper.
```

`d` contains installed design choices; `u` contains a finite set of schedule and
feedback-policy parameters; `z0` is the independent initial reusable state.
`J` is operating-orbit mass payoff in days. `c` is the cycle-closure vector;
`g` includes geometric, operating and model-validity constraints. When useful
export is nonpositive, payoff is undefined: return a domain/feasibility result
rather than dividing by zero or presenting a negative payoff. The outer solver
may seek feasibility before evaluating the accepted objective. This is a
constrained nonlinear program for each discrete architecture. Discrete material,
stage-count and module choices require enumeration or an explicitly mixed-integer
outer method, not an ordinary smooth continuous optimization.

No inner periodic-state solver, design fixed point, nested controller optimizer,
or automatic hardware resize follows the trajectory. Integrator Newton steps and
local EOS/enthalpy inversions are allowed. A finite-difference derivative evaluates
additional nearby candidates, each with one trajectory; this does not violate
the evaluation contract.

The epoch is the same specified orbital phase before each encounter, initially
-600 s from perigee on the reference Kepler orbit. Initial and final deployment,
valve and control modes refer to that same phase. With the first prescribed-orbit
provider, `T_cycle` is the Kepler period, derived from perigee/apogee, not a freely
chosen extra coast time. Environmental forcing must be periodic for this nominal
problem: atmosphere and eclipse/orientation are a declared scenario. Seasonal or
orbit-to-orbit variation later requires a campaign/robust study, not a false exact
periodicity assumption.

## 2. Independent variables and dependent quantities

Reference topology: five gas/rack volumes (front, three interstage, receiver),
four dive compressor blocks, a separate coast train, and a liquefaction plant.
A compressor block can contain many aerodynamic rows. SiC is the front material;
the four downstream racks use aluminum. FeCrAl is a separate front-material run.
The owner fixes the 30 m common bore and 10:1 overall length/outside-diameter
ratio. With retained 0.85 m radial clearance, outside diameter is 31.7 m and
overall length is 317 m. Other proposed temporary locks and free-coordinate seeds
are in the scalar search scope; they must not be confused with owner decisions.

### Installed hardware d

| Group | Independent coordinates | Derived quantities / exclusions |
|---|---|---|
| Orbit and inlet | Apogee `h_a`; perigee `h_p` available in the general schema but proposed fixed at 85 km initially; diameter fixed by owner | Period, speed, atmospheric history, inlet area. Do not optimize period independently. No diameter search in the current scope. |
| Chamber allocation | Five rack-envelope depths `L_r,i`; four extra clear barrel depths for front/intermediate volumes | Receiver clear depth follows the fixed total length minus other chambers, actual equipment and heads. No independent receiver empty volume or rack mass. |
| Lattice, each rack | Radius `r_i` and radius/pitch ratio `alpha_i`; initially held at 1 mm and 0.1 | Pitch `p_i=r_i/alpha_i`, solid fraction, area, displaced gas, heat transfer. Do not independently vary pitch, radius, porosity and surface. |
| Sealed volumes | Rated pressure `p_rated,i` for i=1…4; front structural load scenario | Wall/support/hatch mass uses rating, not the future observed pressure. Actual pressure must remain below it. The 110 kPa receiver cap is a study limit. |
| Dive compressor i=0…3 | Nominal suction capacity `S_i`, nominal maximum specific head `H_i`, installed motor rating `P_motor,i` | Use a declared module/row sizing rule to derive module count, rows, structural mass, inertia and package. Evaluate the map of that installed machine. Do not also vary module count/row count as independent coordinates in the same parameterization. |
| Coast compressor | Installed suction/head/motor ratings using the same rules; number of blocks fixed initially | Actual feed rate, pressure ratio, work and residual recovery follow receiver state, machine map and power allocation. No fixed 2 kg/s extraction unconstrained by hardware. |
| Liquefaction and separation | Refrigerator rating at a declared reference lift, external precooler and condenser `UA` ratings, separator capacity; feed-pressure setpoint initially fixed to the chosen process | Derive machine/exchanger mass once; actual thermal duty, COP, approach, flow and electrical load depend on feed state. A single kg/s plant multiplier cannot replace these coupled limits. |
| Solar/battery/bus | Array physical area `A_s`; battery rated energy `E_b` and permitted power `P_b`; installed bus rating `P_bus` | Generation from area/exposure; battery mass at least `max(E_b/e_specific, P_b/p_specific)` plus declared integration hardware. Charge/discharge limits use a fixed ratio initially, or separate ratings if justified. |
| Ordinary heat rejection | Radiator physical area `A_rad`, warm-store inventory `M_w`; loop pump capacity if flow modeled | Stored capacity derives from material/temperature range. Loop/radiator temperature is a state, not an independent fixed rejection temperature. Reference area distinguishes emitting faces and physical footprint. |
| Propulsion | Supported Isp operating point and installed electrical rating `P_thr` | Exhaust speed, achievable efficiency and thermal losses from a capability scenario/map. Thrust/propellant flow derive from actual delivered power. Isp does not independently set efficiency. |
| Tanks and auxiliaries | Product/propellant usable volumes and ratings; explicitly optional insulation/deployment configuration choices | Mass, headspace, heat leaks and maximum inventory from geometry. Working-fluid inventory sets mass and volume; it is not a free state. Common fixed ancillary allowances remain identified. |

For the current cross-wire family, with bore area A and rack barrel envelope
`V_env = A L_r`:

```
phi = pi*(r/p)^2
V_solid = phi*V_env
M_rack = rho_material*V_solid
A_wet = 2*V_solid/r
V_gas = V_chamber_internal - V_solid - other_displacement
V_chamber_internal = A*(L_r + L_e) + V_heads
L_chamber_physical = L_r + L_e + L_heads
```

Heads are a declared shape and belong once in both volume and length. Rack pores
remain gas volume. Clearance and hatch access cannot be inferred solely from a
positive volume. Installed equipment bay length follows the sum of actual folded
packages and packing clearances, not a free 100 m or 98.7 m carryover.

The compressor sizing rule is provisional: existing `bank_mass` can provide a
starting mechanical estimate, but the nominal `S,H` inputs must map to the same
rounded hardware used by dynamics. If instead a geometry-native parameterization
(module count, rows, tip speed) is selected, derive `S,H` and remove them from x.
Never let the optimizer buy a light low-head bank while simulating the old
high-head flow envelope. Rounding creates discontinuities; hold a discrete bank
layout fixed for local smooth searches or enumerate alternatives explicitly.

### Controls u

Use a small number of physically interpretable parameters, not one free command
at every integration timestep:

- Each dive bank: start/stop window, commanded speed fraction or a few throttle
  knots, and pressure cutoff. A pressure target may be a feedback setpoint;
  achieved pressure, flow and head are not simultaneous independent inputs.
- Coast train and plant: enable window, throttle/feed demand and cutoff, with
  power/thermal limits enforced. Intermediate recovery routing is a fixed
  declared policy first, then a discrete architecture/control alternative.
- Reboost: start time, duration and throttle; use a centered symmetric constant-magnitude family initially, with in-plane
  steering constrained to restore energy and angular momentum. Total duration
  is free; the old 300 s choice is only a comparison. The optimizer must restore the orbit, not just pay a scalar impulse.
- Deployment: start/retract commands per assembly or per group, subject to safety
  interlocks; travel speed initially 10 m/s is a capability, not a free gain.
- Reset/curtailment: charge limit/SOC target, rack-exposure or retraction target,
  warm-loop setpoint/bypass, if their actual hardware supports those actions.
  These are controls, not instantaneous state resets or uncharged heating/cooling.
- Optional LN2 mixing: injection schedule/ratio and injection location only in
  enabled scenarios, with coolant inventory, pump hardware and recovery charged.

One deterministic power-priority policy is fixed for each comparison. Delivered
power limits actual flow/thrust, rather than recording an electrical shortage
while continuing nominal mechanical performance. Surplus solar may be curtailed.
Actuator clipping is an actual modeled action; gas mass, energy and temperatures
must not be clipped to make constraints disappear.

### Initial reusable states z0

| State group | Independent initial coordinate | Closure variable |
|---|---|---|
| Five racks | **Five blended temperatures `T_r,i,0`** | Material specific enthalpy at end minus start |
| Gas in each volume | Species masses `m_i,k,0` and total internal energy `U_i,0` | Same species masses and energy at end |
| Battery | Initial SOC (or energy, choose one) | Absolute stored-energy difference |
| Warm store/loop | Initial energy or temperature; inventory fixed by installed design | Energy plus any mobile inventory not fixed by construction |
| Product/propellant working reserve | Initial species inventories and thermal states sufficient for first burn, mixing and cooldown | Restore reserve species and energy after useful-product removal |
| Any explicitly dynamic cryoplant/motor node | Initial stored energy/inventory/speed | Corresponding terminal state; known stopped mode can be fixed at both ends |

Pressure, temperature and density of a gas are derived from its mass/energy,
composition and free volume. Do not optimize `(m,U,p,T,rho)` independently.
Composition fractions sum to one; species masses avoid an extra redundant total
mass coordinate. Alternative `(p,T,composition)` initialization is acceptable
only as a one-to-one conversion to the conserved states.

For intentionally evacuated nodes, use a declared residual state or bounded
vacuum inventory, not an arbitrary temperature for exactly zero gas. At zero
inventory remove undefined caloric coordinates. All active conserved states need
an endpoint rule even if their initial values are fixed. A zero-size rack/node
removes its unused state and residual to avoid a rank-deficient problem.

All five starting rack temperatures are optimization variables in the periodic
formulation; 298 K is an initial guess, not a mandatory regenerative target.
Material property/domain limits and maximum allowable temperatures still apply.
A hotter periodic starting point may reduce radiator time but impair capture;
the optimizer must price both through the same trajectory.

### Not optimizer variables

Density/cp/conductivity, surface emissivity, accommodation, compressor efficiency
maps, stress allowables, battery specific energy/power, thruster/PPU kg/kW,
radiator kg/m², property domain, deployment speed, safety margins and atmospheric
profile are **capabilities/environment scenarios**. Uncertainty runs vary them
outside design optimization. Dry mass, captured mass, work, radiator heat, peak
pressure and payoff are outputs. No optimizer can independently dial down a mass
coefficient or select a better material property at no cost.

The implementation must serialize a variable registry with name, units, bounds,
initial guess, fixed/free status, derivation and scenario identity. Report the
actual number of free variables and independent closure conditions for each run.
Under the fixed-length allocation, the core rack allocation has five rack depths,
four clear depths and five initial rack temperatures; receiver clear depth is
derived from the remaining physical length after installed equipment and heads; the rest of the count depends on the released hardware,
control and reusable-state coordinates. Do not invent a fixed total before those
choices are instantiated.

## 3. Payoff and material accounting

For a repeatable cycle with positive exported useful liquid:

```
Delta_m_useful = sum_k m_useful_liquid_exported,k  [kg/cycle]
production_rate = Delta_m_useful/T_cycle         [kg/s]
J_days = M_dry*T_cycle/(86400*Delta_m_useful)
```

`k` covers all accepted useful cryogenic products, not nitrogen only. Gas sent to
a plant is not liquid production. Define explicit product quality/phase criteria.

For the first periodic operating-orbit study, use a **declared local offload
boundary** before returning to the initial phase. Replenish working/propellant
reserves, count any relevant transfer/vent/boiloff losses, and remove only surplus
useful liquid. The product buffer then returns to its starting inventory; the
cumulative export counter increases and is excluded from closure. The transfer
cannot create or delete unaccounted enthalpy/species. This boundary is a screening
assumption, not a modeled delivery service or free circularization. During the
cycle, the full accumulating batch must fit in the actual tanks.

At closure, the species ledger has the independent cross-check

```
export_k = admitted_atmosphere_k + external_makeup_k
           - leak_k - vent_k - boiloff_lost_k - propulsion_k
           - other_discarded_k - change_in_total_onboard_inventory_k.
```

Internal condensation, phase transfer and coolant recycling cancel in this ledger.
External makeup is zero in the self-sustaining reference; otherwise it is disclosed
and not credited as newly gathered product. Boiloff recovered internally is not
lost. If reserve replenishment/propulsion has already reduced exported liquid,
**do not subtract propellant a second time** from that export counter. Initial
cryogen cannot be sold as product while closure leaves its reserve depleted.

`M_dry` is the sum of installed component masses plus a stated margin applied
once. Preserve separate outputs for dry equipment, contained thermal-storage
medium, reusable working fluids, propellant reserve, product and wet mass. The
selected dry-mass convention must be identical across candidates; required buffer
medium is included in its installed package under the current convention. Also
report an equipment-plus-reusable-inventory payoff sensitivity so fluid inventories
cannot disappear from the engineering comparison simply through classification.

Circular-apogee delivery remains a separate mission output. Until transport and
return/orbit restoration are included, no `delivered_payoff_days` is populated.
Startup reserve acquisition, real offload cadence and long-run storage/illumination
variation require a campaign model. A non-closing one-cycle ratio remains a
labeled diagnostic, not an accepted sustained-payoff optimum.

## 4. Closure equations c(x)

Let `R_event` be only the physically specified offload/valve/mode transitions,
with all mass/enthalpy transfers counted. Define the terminal reusable state as
`z_plus = R_event(Phi(x))`. For each active reusable state, require equality to
its initial state. This is **outer single shooting**, not an inner root solve.

| Residual | Equation / interpretation |
|---|---|
| Rack i | `c_r,i = h_material(T_r,i,+) - h_material(T_r,i,0) = 0` |
| Gas species i,k | `c_m,i,k = m_i,k,+ - m_i,k,0 = 0` |
| Gas caloric i | `c_U,i = U_i,+ - U_i,0 = 0` |
| Battery | `c_b = E_b,+ - E_b,0 = 0` |
| Warm store/loop | `c_w = E_w,+ - E_w,0 = 0`, plus any variable coolant-inventory closure |
| Cryogenic working reserves | Each species inventory and independent energy state restored after export |
| Rotating machinery / dynamic plant nodes | Shaft speed/rotational energy, inventory and thermal states return; omit redundant coordinates |
| Deployment/modes | Racks, panels and radiators back to their initial stowed state; hatches/valves/controls in the specified ready mode |
| Orbit | Restore a nonredundant set of orbital invariants at the same reference phase |

Specific enthalpy rather than temperature difference gives a consistent rack
blend when cp varies: mass-weight the material enthalpy, then invert to T.
Within one candidate the rack mass is fixed, so specific-enthalpy closure and
solid-energy closure are equivalent. If racks later gain spatial cells, close
each independent cell energy; a blended mean alone cannot hide a changing hot spot.

For planar orbital restoration, use specific orbital energy and the two planar
eccentricity-vector components, or another independent three-element set. Do not
simultaneously impose energy, angular momentum, perigee, apogee and eccentricity
magnitude as if all were independent. In the initial reflection-symmetric burn
family, energy and angular momentum suffice only when the imposed symmetry also
fixes the apsidal direction; report/check that separately. No energy-only reboost
credit. In the prescribed-orbit approximation these are integrated perturbation
residuals, not an exact propagated orbit. Keep its validity screen explicit.

A known mechanism mode is an endpoint condition, not a continuous artificial
root variable. Cumulative throughput, dissipated energy and exported-product
counters do **not** close; they measure the cycle's exchanges. Likewise, no demand
is made that the spacecraft's total internal energy equal its start after
ignoring the exported liquid's energy.

### Numerical tolerances and readiness

Mathematically use `c=0`. Numerically return both dimensional residuals and scaled
residuals `c_j/s_j`, with fixed, declared characteristic scales. Do not normalize
an energy leak only by a freely enlarged battery/store so the optimizer can hide
it in a large capacity. Final tolerances must exceed integration/property noise
but be small enough that resource drift cannot materially improve payoff. Verify
both their physical magnitude and their equivalent cycle energy/mass subsidy;
tighten tolerances and re-evaluate the selected candidate.

One-sided readiness (`end SOC >= start`, `end racks cooler than start`) is useful
for exploratory feasibility, but **is not the final periodic equality formulation**.
Surplus generation can be curtailed; rack exposure can stop earlier if the
mechanism permits. Do not replace exact periodicity with a magical reset. If no
physical control permits the selected endpoint, the optimizer must select a
different initial state/design or report infeasibility.

## 5. Inequalities g(x): separate from closure and conservation

- Geometry: rack and package fit, positive usable gas volume, actual vessel-head
  lengths, finite tank capacity, available compressor annulus/access, hatch and
  deployment clearances; fixed overall L/D = 10 and fixed diameter as detailed
  in the scalar search scope, with receiver length derived from the remaining budget.
- Pressure: each chamber below its installed rating at every point; receiver
  rating/operation within the scenario's 110 kPa cap. Ratings do not prescribe
  the actual intermediate pressure history.
- Materials/thermal: stage-specific temperature limits (initially 1000 K SiC,
  550 K aluminum study caps), supported properties, heat-transfer/Biot validity,
  finite exchanger approaches, warm-loop limits and pressure-safe hatch opening.
- Power/actuation: SOC and battery charge/discharge limits throughout the cycle,
  bus/motor/thruster ratings, finite torque/ramp/deployment speed, compressor map
  domain, plant capacity and physically modeled saturation. Unmet mandatory load
  is a constraint violation; optional load can be throttled by the declared policy.
- Inventory: nonnegative species, sufficient propellant/coolant at the **time of
  use**, tank fill/headspace limits, required reserve and positive useful export.
  End-of-cycle production cannot retroactively power a pre-perigee burn.
- Orbit/environment: restoration residuals plus validity of the reduced orbital
  model, stow/deploy altitude windows, illumination, and explicit uncertified
  aerothermal/leading-edge limits. No invented survivable altitude boundary.

Time-dependent inequalities must be checked on dense output and at events/extrema,
not only the coarse plotting grid. An optimizer cannot hide a short overpressure
or overload between saved samples. Numerical mass/energy/species audit residuals
are separate correctness checks: never adjust design variables to compensate for
an integrator conservation error or disguise it as an allowed resource drift.

## 6. Code-derived corrections required for this formulation

| Existing implementation | Required change |
|---|---|
| `chambers/model.py`: independent m/U/rack energies, fixed empirical pump envelope and prescribed coast withdrawal | Reuse conserved-node structure; replace forced feed with finite coast equipment; introduce explicit speed/power constraints and material/species property contract |
| `chambers/proxy.py`: frozen hardware and signed changes from an old baseline | Remove from new objective; derive all installed mass from d, and all loads/exchanges from the same trajectory |
| `compressor.bank_mass`: structural/module/row accounting from Q, head and power | Compile from selected ratings before integration, including inertia and spin capability; do not resize from observed peaks and retain the old trajectory |
| `process.liquefaction_train`: nitrogen-equivalent pressurized feed benchmark | Keep as a benchmark; model actual incoming enthalpy, phase/species bookkeeping, finite UA, plant rating and rejection. Do not quietly label all gas withdrawal as useful liquid |
| `two_volume.py`: aggregate power/heat budgets with retained hardware duties | Replace with absolute instantaneous electric/thermal flows, spin/idle/drive loss and energy storage; no old warm-buffer/radiator plus overlapping rack duty |
| `packaging.allocation`: sizes from post-simulation outputs; scalar deployment fixed point | Compile package volumes directly from installed hardware; integrate motion and actual exposure once, with no internal resizing iteration |
| Initial rack states fixed at 298 K in saved laboratory cases | Promote five initial temperatures to outer variables and enforce enthalpy closure |
| Old post-pass cooldown/drain allowance | Integrate actual pressure-safe transfer/vent, heat rejection and retraction; no assumed successful reset after the plotted history |

A complication discovered in the source review is that the cryoplant benchmark
only represents nitrogen-equivalent duty near one bar; it excludes O2/Ar phase
separation and upstream hot-gas cooling. The coupled model must explicitly improve
or label that approximation. Linking its existing kg/s output to chamber
withdrawal would not constitute full species/thermal coupling.

## 7. Expensive outer optimization and implementation gates

Implement one cached `evaluate(x, scenario)` returning **objective, all closure
residuals, all inequality margins, audits and diagnostics together**. Separate
optimizer callbacks read that shared result instead of rerunning the same
trajectory for each constraint. Cache keys include every capability/environment
setting and model version; cache exact candidates, not rounded perturbations that
would destroy finite-difference derivatives.

Start with fixed architecture and a modest control parameterization. Inspect the
constraint Jacobian/rank: five rack initial temperatures introduce five closure
conditions, not five gratuitous new freedoms. Remove redundant EOS, inventory and
orbital equalities. With reliable derivative scales, use a constrained NLP method;
finite differences are initially acceptable, with tolerances below the induced
response. Events, clipping, property-table joins and module rounding make blind
complex-step/automatic differentiation unsafe. Check event derivatives and smooth
approximations against the original physical model before trusting gradients.

A solver may use feasibility restoration and a merit/filter strategy internally;
that is part of the **outer** constrained solve. Do not replace closure with an
arbitrarily weighted payoff penalty that permits profitable nonperiodic designs.
Integrator failures/timeouts are numerical statuses, not evidence of physical
infeasibility. Record them, retry promising cases with deliberate solver settings,
and report unresolved regions. Multistart/discrete alternatives are necessary
before claiming a global optimum; a single converged KKT point is only local.

Sequence: establish a feasible periodic reference with SiC/Al, then optimize rack
allocation and starting temperatures with installed ratings, then compressor/control
choices and Isp, then the agreed orbit/control variables. Diameter and L/D stay fixed; lattice
geometry remains a proposed lock until missing penalties are modeled. Initial-state variables remain
in the outer solve at every stage; there is no preliminary inner closure loop.
Keep fixed-capability sensitivity runs separate, especially for dominant thruster
and electrical specific masses. A short prescribed multi-cycle validation may be
run after selection to expose accumulated drift, not to repair an optimizer input.

Acceptance: one integration per evaluation; shared callbacks; matching component
mass/volume/performance; independent conservation and derivative checks; physically
small terminal residuals; path constraints checked beyond plot samples; positive
new liquid with restored reserves; and refined-resolution verification of both
payoff and closure. No new numerical payoff is claimed by this specification.

## Method references

- [CasADi, direct single shooting](https://web.casadi.org/docs/#direct-single-shooting): describes parameterizing controls and evaluating trajectories by integration within an outer nonlinear program. This supports the formulation, not an automatic migration of existing Python/HEOS code to differentiable CasADi expressions.
- [SciPy NonlinearConstraint](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.NonlinearConstraint.html): documents vector-valued equality and inequality constraints and Jacobian interfaces. It is an interface example, not a claim that a particular solver will handle this hybrid model robustly without scaling and derivative checks.

Hardware/property references remain in the component dossiers and
[material specification](../chambers/MATERIALS.md). Prior numerical evidence:
[mass audit](../../investigations/chamber_transient/MASS_AUDIT.md).
