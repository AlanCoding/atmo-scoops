# Design versions and planned model work

Specific integrated snapshots now use **v1.0.z**; see the
[snapshot register](DESIGN_VERSIONS.md). The boosted-reserve candidate is rejected; the valve-connected replacement is
in planning. Version headings below describe broader work scopes.

**Disposition: documentation only.** This records the agreed development path;
it does not introduce code branches, new configuration fields, replacement
physics, optimization runs or new payoff claims. The saved v1.0 reference stays
reproducible. Future versions must report their own inputs and validation.

| Version | Role | Cooling architecture | Orbital recovery |
|---|---|---|---|
| **v1.0** | Frozen publication reference | Front SiC and downstream aluminum plates; direct coast deployment | Integrated electric propulsion with finite-duration reboost |
| **v1.0.1** | Accuracy improvements to the same architecture | Retain v1.0 thermal design | Retain onboard propulsion; improve physical penalties and accounting |
| **v1.1** | Simplify downstream cooling hardware | Deployable front SiC rack; fixed coolant tubes in higher-pressure gas volumes | Retain onboard propulsion |
| **v2.0** | Split collector and propulsion into two craft | Diver inherits the v1.1 thermal arrangement and retains processing hardware | Mothership/tether release, capture and retrieval; bulk reboost on mothership |

Versions describe study scope, not flight readiness. The [publication kit](publication/V1_0.md)
and [reference configuration](../configs/transient_plates_reference.json) define
the numerical v1.0 snapshot. The component research library remains in
[modeling](../modeling/README.md); unresolved items remain in the
[improvement register](MODEL_IMPROVEMENTS.md).

## v1.0.1 — improve accuracy without changing architecture

**Current immediate priority:** the [scale-review implementation sequence](SCALE_REVIEW_IMPLEMENTATION_PLAN.md), beginning with the longer staggered plate cooler. External shear refinement follows that sequence. There is
already an implemented effective-coefficient screen and the frozen plate
configuration explicitly sets `skin_friction_coefficient = 0.002` and
`skin_area_multiplier = 1`. Therefore this task improves the coefficient model
and its use, rather than adding a previously absent penalty or charging it twice.
The [existing study](../investigations/skin_friction/ANALYSIS.md) includes older
zero-shear comparisons; those are not the current plate reference.

Planned accuracy work, in order:

1. Replace or bound the constant external shear allowance using the relevant
   flow regime, wall temperature, Reynolds/Mach numbers, transition, roughness,
   accommodation and wetted geometry. Integrate shear impulse over the pass.
   Separate exterior shear from plate-channel friction, inlet/spillage pressure
   drag and fin/base drag. A single coefficient must not conceal those different
   contributions. Keep L/D fixed until the evidence supports releasing it.
2. Carry the revised external impulse consistently into finite-duration thrust,
   propellant, installed power, battery recharge and heat rejection. Determine
   wall heating separately: total drag work is not heat deposited in the skin.
3. Audit existing capability assumptions and accounting before resizing: gas
   propellant bypass, startup/rotor energy, compressor capacity versus operating
   points, thermal losses and end-to-start inventories. Flag unsupported values
   rather than claiming a new compressor hardware design. Full map development,
   channel hydraulics and structural qualification remain larger research items.
4. Improve orbital/illumination accounting where needed for an honest cycle:
   distinguish the intended sun-synchronous orbit from the simplified lighting
   history, and check finite-burn energy/angular-momentum consistency. A complete
   3D guidance solution is not a prerequisite for the first shear sensitivity.

Acceptance: an unchanged-hardware comparison isolates each added penalty, then
an explicitly identified constrained resizing/search produces any replacement
reference. Recheck conservation, periodic thermal/electrical closure and
integration resolution. Report uncertainty and infeasible cases. Keep the v1.0
278-day operating-orbit result labeled with its original assumptions; do not
silently replace it with new numbers. Circular-apogee delivery remains a distinct
unimplemented mission boundary until separately resolved.

## v1.1 — retain the open-mouth cooler, change downstream heat storage

The front material is **silicon carbide (SiC), a ceramic**. Retain its solid
rack and direct deployment through the open mouth. It remains the front heat
absorber, returning to its starting thermal state through coast radiation.
The mouth stays open; this plan does not revive the rejected inlet door.

Replace the passive aluminum plate racks **only in the higher-pressure volumes**
with fixed coolant-tube heat exchangers. In the current five-volume model this
means volumes 2–5, including the aft receiver. Gas is cooled by fluid circulating
inside tubes; gas and coolant do not mix in the baseline arrangement. A carried
coolant inventory accepts pass heat and an ordinary deployable radiator rejects
it during coast. Existing ammonia investigations are a starting point, not a
qualified final fluid or operating-temperature choice.

Delete the downstream rack-extraction mechanisms and their large
pressure-retaining deployment doors. Pressure vessels remain sealed around
fixed exchangers, with the necessary pipe penetrations, gas isolation valves
and service interfaces still accounted for. Removing rack doors is not deleting
all pressure boundaries or valves. The coolant radiators and solar panels still
deploy and stow outside the atmospheric pass.

The intended scope is the material/deployment distinction above, **not a newly
assigned chamber-volume split**. In the frozen axial layout the aft receiver
occupies roughly 247 m of the 317 m craft; the mouth chamber is not most of its
gas volume. The front SiC rack is the dominant solid-cooler mass. Preserve those
separate statements until a new layout is calculated.

Future implementation must explicitly trade:

- Removed aluminum thermal mass, extraction hardware, pressure doors and any
  gas recovery/venting duties that become unnecessary.
- Added fixed tubes/fins, finite gas-side and coolant-side heat transfer,
  tube displacement, coolant inventory and its storage volume, plumbing,
  pumps, pressure losses, insulation and radiator/deployment equipment.
- Cold and hot coolant states, thermal gradients, usable capacity, freezing/
  boiling/pressure limits and restoration during coast. A hot/cold split or
  moving diaphragm is an option, not a free ideal reservoir.
- Interaction with the existing warm loop and cryogenic plant. Avoid counting
  shared radiator/thermal capacity twice, and do not credit a heat pump without
  its work, mass and rejected heat.

Keep the front solid-rack and downstream coolant cycles separately visible in
closure conditions. Compare v1.1 against the accuracy-refined v1 baseline using
the same mission boundary. This is a planned design choice, not a demonstrated
payoff improvement.

## v2.0 — propulsion-free diver and tether mothership

The [supplied tether research handoff](V2_TETHER_HANDOFF.md) is retained in full
as a source brief. Its implementation requests are deferred. The following
disposition incorporates the user's accompanying architecture instructions.

### Equipment allocation and operating sequence

| Scoop-diver retains | Scoop-diver deletes | Mothership/tether provides |
|---|---|---|
| Inlet, front SiC rack, compressors, fixed downstream coolant exchangers, gas/product storage and processing, including liquefaction as required by the product boundary | All onboard thrusters and the propulsion-only portions of feed, power conditioning, batteries and thermal hardware | Bulk electric propulsion, its power supply and orbital maintenance |
| Its own solar panels, batteries, coolant radiators, front-rack deployment and control hardware | No blanket deletion of solar, batteries or radiators: compressor and processing duties still require them | Release impulse mechanism, capture equipment, retrieval/climber system, gas transfer and tether control |

The diver starts a sortie at a **higher apogee**, is released below mothership
CM, and makes several atmospheric encounters without reboost. Collection and
drag reduce its apogee while retained product increases its mass. It returns
near the final **lower apogee** to a lower tether point with a target of zero
relative capture velocity. The mothership/tether retrieves the diver, unloads
product, restores the appropriate release state and starts another sortie.

Mechanical retrieval and release replace the diver's thrust, not the system's
external energy and angular-momentum requirements. Mothership propulsion pays
the orbital losses and release/capture disturbances. Its cost cannot be
excluded from the system payoff.

**No diver trim thrusters are included in the baseline.** This overrides the
brief's optional trim-propulsion allowance. Study aerodynamic guidance and
mothership/tether control authority. Any inability to achieve rendezvous without
diver propulsion must be reported as a feasibility issue, not quietly repaired
by introducing reboost or trim engines. The generally retrograde release
adjustment must be applied mechanically by the tether/mothership system.

### Orbital mechanics investigation, before hardware optimization

Initial hypotheses: approximately 85 km perigee; a circular mothership orbit in
the roughly 1,500–2,500 km region; radial gravity-gradient tether; release above
the lower capture point but below CM. None of those mothership heights or
tether lengths is a solved design. The brief's initial equatorial two-body
model is an explicit simplification; it does not inherit v1.0 SSO lighting.

With Earth radius R, gravitational parameter mu, fixed trial perigee radius
rp, and mothership radius rm, the idealized kinematics are:

```text
omega_m = sqrt(mu / rm^3)
v_apogee(ra) = sqrt(2 mu rp / [ra (ra + rp)])
v_tether(r) = omega_m r
capture: v_apogee(rc) = omega_m rc
release: delta_v_rel = v_apogee(rrel) - omega_m rrel
geometry: R < rp < rc <= rrel < rm
apogee reduction over sortie: delta_ra = rrel - rc
```

Zero relative velocity is only one condition: capture also needs matching
position and epoch, including tether orientation. Sweep the **N:(N−1)**
one-slip families from 3:2 through at least 10:9, rather than selecting 5:4 or
6:5 in advance. For N encounters and impulsive perigee braking:

```text
t_sortie = T0/2 + sum(Ti, i=1 ... N-1) + TN/2
```

Require the mothership's accumulated phase to reach the interception longitude
at that time. In the fixed-apsis two-body family this corresponds to N−1
mothership revolutions. Neither a single average diver period nor a velocity
match alone establishes rendezvous. In subsequent propagation, integrate phase,
mass accumulation, atmospheric corotation and distributed forces; later include
J2, apsidal/nodal motion, tether flexibility and capture tolerances.

Ballast is an independent trade variable, not a prescribed benefit. Start with
a fixed atmospheric-impulse screen, then couple collection and drag. Increasing
mass can reduce apogee loss and relative release speed, while increasing tether
load, retrieval costs and system mass. Sweep equal, early-heavy and late-heavy
encounter braking; do not impose a constant braking history as the final answer.
Report release impulse and relative kinetic energy separately from orbital
energy, gravitational/retrieval work and external reboost. No infinite-ballast
solution is an acceptable vehicle selection.

### Required evidence and performance boundary

First establish families of feasible trajectories and their sensitivity before
choosing a detailed tether or optimizing hardware. Include counterweight/upper
extension, tensile load, capture/retrieval dynamics, release mechanisms,
repeated deployment, density uncertainty and guidance authority. The diver
must retain and cool its inventory over the full multi-pass sortie, with
real electrical recharge and storage capacity between encounters.

Close mass, energy and angular momentum over **the complete two-craft sortie**,
including changing mothership state, tether/climber work, propellant spent,
gas transfer and restoration for the next release. A rigid, prescribed tether
is a useful initial kinematic boundary, not an infinite momentum reservoir.

Primary future metric:

```text
system mass payoff = total installed dry mass / net useful product delivery rate
total dry mass includes diver(s), ballast, mothership, tether, capture/retrieval,
power/thermal systems and all propulsion/support equipment
```

Net delivery excludes recycled inventory, losses and gas consumed by system
propulsion. Report operating-orbit production, delivered gas and delivered
cryogenic liquid separately. Do not compare a gas-only or diver-only number
directly with the integrated v1 useful-liquid payoff. Product condition and
delivery orbit must be stated; transfer to a circular mothership may address
delivery, but only after its complete mechanics and costs are included.

Future deliverables are resonance tables, release/capture geometry and velocity
plots, ballast/apogee-loss sensitivities, per-encounter retained mass and energy,
system budgets and rejected-solution diagnostics. No such results are claimed
by this plan.
