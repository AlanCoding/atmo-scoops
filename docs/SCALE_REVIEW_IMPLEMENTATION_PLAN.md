# Incremental model changes from the scale-image review

Status: plan for owner review. Commit the current documentation and artwork as
checkpoint zero before implementation. The first numerical change is the
[longer, wider-pitch staggered cooler](../modeling/metal_coolers/STAGGERED_PLATES_PLAN.md).
This sequence supersedes older immediate-work lists; it does not initiate code
changes or a new optimization merely by being recorded.

The frozen plate case 72 remains the numerical baseline: approximately 278 days
operating-orbit payoff. Recent scale drawings are proposed packaging revisions,
not geometry from a new accepted cycle. Preserve the frozen config and outputs.

## Checkpoint discipline for every stage

1. Save parent commit, exact input config, geometry revision, solver settings,
   property/correlation versions and state-vector schema. Use named state fields
   and units; do not silently change indices or reuse stale optimizer caches.
2. Establish a forward baseline and controlled unchanged-design comparison before
   allowing resizing. New states get explicit initial values, conservative mass
   and energy balances and periodic closure residuals. One cycle per candidate;
   no inner cycle-to-cycle shooting or implicit hardware resizing.
3. Check limiting cases, conservation, physical path limits and integration
   resolution. Numerical failure is unresolved, not a low-quality feasible point.
4. Run the actual constrained optimizer with documented coordinates and bounds.
   Save termination reason, constraint residuals, evaluated candidates and the
   chosen design; distinguish local convergence from global optimality. Independently
   re-evaluate the selected point at refined resolution. Preserve any rejected
   or merely feasible results without promoting them to an accepted reference.
5. Write a review report, then **git commit the completed stage** with a stage-specific
   message. Record the commit in the chat for review. Every next stage starts from
   an accepted checkpoint, making rollback or cherry-picking possible. If a search
   fails to converge or violates the physical gates, record that outcome and stop
   promotion rather than bundle additional changes into an attempted rescue.
6. The review packet contains old/new payoff and endpoint definition, total and
   component dry masses, net gas/product/propellant per cycle, geometry/volume
   ledger, rack masses/gaps/thicknesses, compressor and rack-loss energy, peak
   pressure/temperature/Mach/Re/Kn and validity flags, closure/conservation errors,
   active constraints and bounds, solver status, and reproduction commands. Plot
   every gas volume's P/T/mass and each thermal inventory through the full cycle.
   Highlight surprising numbers and unvalidated assumptions explicitly.

## 1 — Longer distributed plate cooler FIRST

Implement material-conserving wider pitch and serial offset rows. Retain SiC
front and Al downstream, no new working coolant architecture. Freeze the current
propellant system, storage duty and external-drag assumptions while evaluating
this change.

- Baseline geometry: fourfold pitch at unchanged thickness/material gives a
  fourfold plate-bearing length. Separate total rack length, segment length,
  gap, pitch, offset and axial clearance; no fictitious parallel-branch credit.
- Validate aligned/wider channels first, then finite-row offsets. Use offline
  flow/heat-transfer work or evidenced bounded correlations to quantify both
  heat-transfer enhancement and edge/turning losses. Do not assign free mixing.
  The offline solver stays outside optimization.
- Establish a conservative axial reduced model, using a fixed small row count
  initially. If each row has a thermal state, distribute original heat capacity
  without duplication, initialize explicitly and add per-row closure conditions.
  Gas subvolumes and enthalpy transfer must conserve the original inventories.
- Keep the energy-only friction accounting initially, with explicit pressure-loss
  validity diagnostics. The old front result has loss comparable to absolute
  pressure; numerical convergence alone cannot qualify it as hydraulically valid.
  Do not hide this with a friction multiplier or claim a realized suction state.
- Optimize the existing plate material/gap/thickness/initial-temperature and
  system-capacity coordinates for the selected geometry; release additional
  segmentation/offset variables only after fixed-geometry behavior is stable.
- Commit a reviewed cooler result before changing receiver/feed architecture.

## 2 — Chamber heads and actual front machinery packing

The remembered 10 m intervals are **machinery bays**, not extra empty gas depth.
The frozen layout allocated 12 / 10 / 10 / 27.62 m to four bays. The numerical
compiler instead has one aggregate equipment-volume allowance; those individual
bay lengths are not optimized model inputs. Extra clear gas depths were zero.
Separate empty volume comes mainly from two 1.5 m vessel heads per intermediate
chamber (~1,064 m³), as documented in the
[geometry trace](../investigations/v1_layout/FRONT_GEOMETRY_TRACE.md).

Replace the arbitrary bay partitions with package-based allocation. Use **5 m
per front interstage machinery bay as the initial target**, extending only where
compressor-bank length, real package volume, service space or deployment routes
require it. The remainder of the old last bay must be reassigned to actual
packages, not deleted. Never truncate a compressor or throw away battery/bus/
radiator volume to obtain the target. Report any bay needing more than 5 m and why.

Make the cooler occupy its declared active gas region and account separately for
necessary manifolds, heads and clearance. Examine shared pressure boundaries or
other head arrangements before removing credited gas volume; retain structural
mass/pressure constraints. Keep empty-vessel geometry and machinery packing
changes identifiable in the comparison. Re-optimize and commit this stage.

## 3 — Receiver and peripheral equipment geometry

Move cryogenic processing around the forward part of the receiver and solar
stowage farther aft alongside it; warm radiators, batteries, power distribution
and deployment corridors remain accounted for. Narrow the main receiver to a
constant barrel radius, with rounded heads and explicit envelope/usable-volume
accounting. The drawing's 24 m receiver diameter and x=70–90 / 90–175 m zones are
starting proposals, not demonstrated fits.

Derive the permitted receiver size from physical package volumes and clearance.
Reclaim vacated forward space only once. Do not charge already-budgeted solar or
radiator packages a second time. Recompute pressure-vessel mass and receiver
volume, and their effects on compression and payoff. Move thruster hardware
wholly aft of the 317 m hull; keep that hull length definition explicit. Track
CM and cable/support/feed-route allowances, and retain plume-clearance flags.
Use the existing boosted propellant reserve until stage 4 replaces it. Re-optimize,
report mass/volume/CM changes and commit.

## 4 — Replace boosted reserve with the isolated aft receiver section

Keep a **125 m** aft reserve as the initial fixed geometry; do not optimize its
length in the first implementation. Give it its own species inventory and gas
energy/temperature/pressure. Add the valve and its finite conductance, mass and
pressure boundary. Remove the old 500 m³ boosted reserve and associated hardware
only when their functions are actually replaced.

Sequence: isolate stored propellant during coast liquefaction; feed the pre-entry
burn from it; open the connection when collecting-receiver pressure catches up;
permit physically resolved equalization and continued shared feeding. Define
refill and coast isolation timing so the next orbit starts with the required
reserve. Use hysteresis or event handling to avoid valve chatter. No imposed
10–20% unused fraction: a low residual is allowed if feed capability supports it.

Do not assume gas at a few kPa directly satisfies the old one-bar thruster feed
requirement. Include any necessary feed compressor/regulation, power and thermal
load; retain a clearly identified capability assumption until researched. Preserve
finite-burn energy/angular-momentum restoration. Re-optimize and plot **both** tank
pressures, inventories, valve flow/state and thruster flow over the whole cycle.
Commit separately; this is an architecture change, not a free valve-only saving.

## 5 — Several-pass liquid storage

Use **60 m³ internal liquid capacity** as the proposed starting allocation,
approximately 15 reference batches before ullage. Size tanks, insulation,
containment and boiloff/holding duty; account for their peripheral packaging.
Specify the collection/offload cadence rather than equating capacity to an exact
number of future optimized batches.

Preserve a periodic processing-cycle solve for fast optimization, but distinguish
product accumulation from cyclic working inventories. Specify representative
carried liquid and audit empty-to-full campaign states; use an explicit offload
map or finite campaign validation instead of forcing accumulating product to have
zero one-orbit closure. Propellant, battery and rack closure still apply. Report
loaded mass/CM and any propulsion changes. Do not silently change the payoff
endpoint to delivered circular-apogee product. Re-optimize and commit separately.

## 6 — Regenerate the scale image from the accepted numerical design

Return to the original purpose of this work: a physically interpretable scale
image. Export one versioned geometry/mass manifest from the accepted candidate.
Generate SVG and PNG from it, including exact rack envelopes and gas boundaries,
compressor and machinery bays, narrower receiver, isolated reserve, folded solar
and radiators, cryogenic plant, multi-pass liquid tanks, aft thrusters and CM.
Distinguish actual gas volume from solid material, rack gaps, heads and package
clearance. Include readable detail insets for thin or compact components.
Remove provisional numerical labels only when the model genuinely supplies them.
Commit the illustration and review packet linked to the numerical checkpoint.

## Deferred work

This sequence takes priority over improving the existing Cf=0.002 skin-friction
allowance. Retain it for controlled comparisons. Full cryogenic-process integration,
compressor empirical maps, deployment lifetime/structure, SSO seasonal lighting,
flight stability and propellant plume qualification remain explicit follow-ups.
The v1.1 downstream coolant-tube conversion and v2.0 mothership/tether system
remain later architectures; do not mix them into these plate-model checkpoints.
