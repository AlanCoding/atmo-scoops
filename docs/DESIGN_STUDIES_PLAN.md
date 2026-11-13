# Planned architecture decisions: mouth closure and coolant mixing

## Objective and scope

Answer two questions with controlled numerical experiments: under what
assumptions does a reusable mouth closure improve mass payoff, and under what
assumptions does adding cold nitrogen to the front compartment improve it?
The visual concept uses an open mouth. Both options remain in the numerical
comparison until the evidence selects between them.

**Status: work plan, not an executed optimization or a selected design.** The
existing closure comparison is preliminary. Cold-gas/LN₂ mixing is not yet
implemented in the current cycle model. This plan does not change reference
inputs, hardware targets or saved search results.

Use operating-orbit dry-mass payoff for the initial controlled comparisons;
repeat the decision after circular-apogee delivery is implemented. Track net
new cryogenic product, oxygen balance, circulating coolant, dry hardware and
startup inventory separately. A recycled coolant kilogram is not a newly
collected product kilogram. No dry-mass ceiling is imposed.

## 1. Common prerequisites

1. **One continuous inlet boundary on both legs.** Resolve admission, spillage
   and outward leakage from opening/startup through the pressure peak and the
   falling-density outbound leg. The current inbound full-capture assumption
   followed by an outbound port law cannot establish a closure verdict. In
   particular, changing the support coefficient at perigee creates an artificial
   initial pressure relaxation; do not interpret that burst as evidence of a
   real outbound failure.
2. **Represent the moving pressure/shock boundary.** The external support falls
   as the craft climbs; internal backpressure and suction can move the shock
   system toward and beyond the mouth. Represent inlet start/unstart, capture
   loss and backflow with a conservative reduced model, including transient lag.
   Equality of two scalar pressures does not determine a shock position. Use
   offline flow cases to bound/calibrate this model; do not run CFD inside the
   optimizer. Include uncertainty when coefficients are not established.
3. **Establish a compressor operating envelope.** Relate suction volume rate,
   mass flow, inlet pressure/temperature/composition, pressure ratio, commanded
   speed or other control, electrical power, heat rejection and installed mass.
   Include declining-pressure performance, minimum useful inlet pressure,
   startup/shutdown, and thermal limits. Identify technology families and their
   validity ranges before choosing a map. No assumed blade speed or compressor
   count is needed for the first envelope, but constant efficiency and a single
   kg/(m³/s) coefficient cannot settle these architecture decisions.
4. **Conserve mass, species, energy and momentum.** Separately integrate new
   atmospheric intake, recycled nitrogen injection, front/rear inventories,
   outward leakage, residual vents, product and propulsion. Apply encounter
   momentum only to newly admitted atmosphere; onboard circulating nitrogen
   does not repeatedly arrive at 8 km/s. Account for lost coolant and the
   direction of escaping gas in vehicle impulse. Include thermal-cycle recovery
   and net energy needed to restore the starting state.

Acceptance gate: benchmark the reduced inlet against limiting cases and selected
offline cases; verify conservation and numerical convergence; establish bounded
compressor capabilities across the actual pressure/temperature domain. Until
then, report sensitivity thresholds, not a categorical engineering winner.

## 2. Mouth closure: optimize a fair comparison

### Options

- **No door:** remove closure skin, supports, actuation, seals and door-specific
  cooling. Retain the compressor bulkhead and rear isolation valves. Include
  open-mouth heating and drag before useful collection and after pump cutoff;
  add protective hardware if the design actually requires it.
- **Closure fitted:** include its pressure/thermal structure, cooling, actuation,
  seals, mechanisms, imperfect sealing and repeated-cycle life. Allow the
  optimizer to choose closure time, rather than forcing it to stop admission
  at perigee while the no-door craft collects on the outbound leg.

In both options, size compressor banks consistently and optimize pumping control
through the encounter. The hardware minimum pressure is a capability constraint;
the commanded cutoff pressure is a design/control choice at or above that floor.
Stopping because useful net recovery becomes negligible is also a valid policy.
A timeout must not masquerade as a pressure-limited optimum.

### Independent controls and scenarios

Optimize front/rear physical depths and diameters, opening/start policy,
closure timing when present, suction/throttle schedule, cutoff pressure,
staging, thermal endpoints and orbit, together with the existing feasible
continuous design coordinates. Do not optimize redundant controls: for example,
pump hardware capacity and its pressure target cannot both independently define
the same capacity. Remove residual-fraction coordinates when they are inactive.

Hold hardware capabilities fixed within each search. Sweep door specific mass,
thermal/protection penalties, inlet pressure recovery, backflow conductance,
pump-map families/floors, atmosphere variability and external drag. Do not let
an optimizer improve a coefficient instead of improving a design.

### Required result

Produce a map of which option wins and the assumptions that change the answer.
For each case give mass retained/lost, useful product, circulating inventories,
component masses, energy, all three deployed areas, pressure histories, shock
boundary validity, cutoff time and active constraints. Include fixed-input
comparisons and separately reoptimized comparisons.

For fixed operating policies, let B_closed be dry mass excluding the door,
D the door system mass including its allocated margin, and P the daily net
production. Equality of payoff gives a useful diagnostic threshold:

    D_break_even = (B_open / P_open) * P_closed - B_closed

Positive D_break_even means a sufficiently light door can help under those
assumptions. Negative means even a massless door loses for those policies.
Reoptimization can change B and P; use this formula to explain a result, not
replace the paired searches. Report an uncertainty band around the threshold.

## 3. Cold nitrogen injection: evaluate only after the compressor gate

### Define the thermodynamic path

Keep cold gaseous N₂ injection distinct from stored LN₂ that vaporizes during
mixing. Specify inlet phase, temperature, pressure, enthalpy and injection
location. If liquid is stored but gas is injected, count vaporization and its
heat source. The gas-injection and liquid-injection paths can share hardware
blocks but have different heat and inventory budgets.

Choose and state the restoration path: recover and reliquefy the injected
nitrogen during coast, or return it to a cold gaseous store with its own volume
and refrigeration budget. The baseline comparison should restore the same
starting coolant state every orbit. No free cold supply or one-pass depletion
of a carried reservoir is allowed.

Use a recirculation ratio `r = injected coolant mass / new admitted air mass`
and an injection schedule/location as candidate controls. Retain `r=0` as an
exact recovery of the no-injection model. If film cooling is required, represent
its minimum local flow and temperature/life constraint; distinguish that
requirement from optional bulk mixing. Film loss may differ from bulk-plenum
loss, so a single fully mixed leakage fraction is only a first approximation.

### Coupled balances and the suction-volume check

Solve the gas outlet temperature from incoming enthalpy, coolant enthalpy and
heat actually transferred to the metal. Do not independently prescribe mixing
ratio, final temperature and removed heat as if all three were free choices.
The rack must have finite conductance, capacity and pressure loss. Count any
extra inventory, injector/manifold/pump mass, gas treatment, compressor duty,
refrigeration, radiator/solar/battery mass and lost nitrogen replacement.

Lower temperature alone does not establish a compressor benefit. At the same
suction pressure, an ideal-gas screening ratio is:

    S_with_mixing / S_without = (1+r) * (R_mix/R_base) * (T_mix/T_base)

This is a comparison of volumetric requirements at equal new-air throughput;
actual efficiency and mass still require the compressor map. As an independent
limiting-case test, adiabatically mixing two ideal streams of the same gas and
constant Cp gives `(1+r)T_mix = T_hot + r*T_cold`. Adding cold **gas alone** then
does not lower total suction volume at fixed pressure, despite lowering gas
temperature. This test must pass before interpreting a numerical improvement.
It does not settle liquid injection, real chemistry, different heat-transfer
performance, a higher admissible inlet pressure or a temperature-dependent
compressor map. Those are the physical routes a benefit would have to come from.

If available research cannot support a credible compressor envelope or the
coupled cooler/mixer model over the required domain, stop this optimization at
that gate and record the missing measurements/models. Do not publish a preferred
mixing ratio from the present constant-efficiency model.

## 4. Experiment sequence and decision outputs

1. Implement and validate the shared boundary, compressor and thermal balances.
2. Run four branches: door/no door × no injection/variable injection. First hold
   geometry and orbit fixed; then optimize independent variables in each branch.
   Use identical technology assumptions and comparable control freedom.
3. Repeat over credible capability scenarios; use multiple search seeds and
   high-resolution replays. Inspect bounds and inactive/redundant coordinates.
4. Publish the current decision map and break-even thresholds in the analysis
   area, with fully resolved configs, model versions, failed constraints and
   reproducible results. Update the single design description only when the
   evidence warrants a selection.

Useful outcomes include “door beneficial only below this installed mass and
above this recovery fraction,” “mixing required for edge life but costly for
payoff,” “a nonzero mixing ratio improves payoff within this validated map,” or
“the existing uncertainty is larger than the difference.” None requires a
universal winner independent of engineering assumptions.

Related work: [model improvements](MODEL_IMPROVEMENTS.md),
[fluid analysis](../analysis/fluid/README.md),
[stability](../analysis/stability/README.md), and
[atmospheric-column argument](../analysis/primary/ATMOSPHERIC_COLUMN.md).
