# v2.0 source handoff — retained research brief

This is the supplied two-craft/tether handoff, retained as planning source
material. Its requests to implement, sweep and optimize are **future work**, not
authorization to implement them now. The [version roadmap](VERSION_ROADMAP.md)
is the controlling disposition of the current plan.

Two explicit overrides from the accompanying user request:

- The v2.0 diver has **no thrusting capability**, including the optional trim
  thrusters permitted in this brief. Resolve guidance and release requirements
  without silently restoring onboard propulsion.
- The diver retains its own solar panels, batteries, collection/processing
  equipment and deployable thermal systems. Mothership propulsion power does
  not replace the diver's processing power for free.

All suggested altitudes, resonance preferences and prior findings below are
hypotheses to recalculate, not accepted simulation results. The equatorial
starting model is distinct from the intended v1.0 sun-synchronous orientation.

---

# Research / Simulation Handoff: Two-Craft Atmospheric Scoop with Orbital Tether

## Core concept

Develop and numerically investigate a reusable, two-component Earth atmospheric propellant-harvesting system.

**1. Scoop-diver:** An elliptical-orbit spacecraft that repeatedly dips to approximately 85 km perigee to collect atmospheric gas. It retains ALL equipment needed for collection, cooling, compression, storage, and potentially liquefaction. It carries the captured gas back to orbit. It does NOT carry bulk propulsion or a conventional orbital reboost system. Small trim propulsion is permissible, but aerodynamic trajectory control is preferred. The diver may complete multiple atmospheric encounters without thrusting between them.

**2. Tether mothership:** A large spacecraft in a roughly circular orbit, initially targeting the 1,500–2,500 km altitude region. It maintains a long, approximately radial, gravity-gradient-aligned tether. It releases the scoop-diver, catches it after multiple atmospheric encounters, retrieves it along the tether, unloads the harvested gas, and prepares it for another sortie. The mothership houses the primary propulsion and power systems. Its propulsion replenishes the orbital energy and angular momentum ultimately lost to atmospheric drag and collection.

The central thesis is that conventional atmosphere-breathing electric propulsion (ABEP) becomes dominated by the mass, power, and aerodynamic consequences of its propulsion system. Separating the atmospheric collector from the bulk propulsion system may radically improve the economics, provided orbital rendezvous can be solved.

**The critical innovation is delayed rendezvous through orbital resonance, combined with a passive gravity-gradient tether that supplies different orbital velocities at different altitudes.**

## Orbital architecture

The scoop-diver is released from a position along the tether BELOW the mothership's center of mass (CM), preferably above the lower capture point.

After release, it follows an elliptical trajectory with approximately 85 km perigee. It encounters the atmosphere repeatedly, accumulating gas and losing orbital energy. Its apogee progressively decreases.

The diver eventually returns to the lower tether tip, ideally at the apogee of its final orbit.

**Target zero relative velocity at capture.** This is a primary design condition, not merely an optional optimization. Small guidance corrections may be necessary.

The tether's lower tip moves more slowly than the circular-orbit velocity at its altitude, because the whole structure rotates at the mothership's orbital angular velocity. This permits the lower tip's velocity to match the apogee velocity of an elliptical scoop-diver orbit.

Release likewise occurs from the tether, but higher than capture. The release point is a variable, NOT necessarily the upper tip or the CM.

The diver generally requires a retrograde velocity adjustment at release. Lowering the release position reduces this requirement. As release approaches capture, the required adjustment approaches zero.

A key trade-off is therefore the separation between release and capture positions.

## Orbital resonance: one orbit of slip

We discovered an especially useful family of resonances:

- 3 diver revolutions : 2 mothership revolutions
- 4:3
- 5:4
- 6:5
- 7:6
- 8:7
- And so on.

The defining relationship is **N:(N−1)**.

The diver completes exactly one more revolution than the mothership during separation. This is the minimum positive integer orbital slip, and minimizes separation time within this resonance family for a given diver period.

The exact mothership altitude is NOT fixed in advance. It must be solved from the orbital timing and rendezvous geometry, including atmospheric decay.

Earlier calculations indicated that 5:4 and 6:5 have promising solutions reasonably close to 2,000 km. The lower release point makes 5:4 more attractive than it appeared when we assumed release from the upper tether tip.

Do not assume a 6:5 resonance or a 2,000 km CM is obligatory. Sweep the integer families.

## Key mathematical constraints

For the initial model, assume:

- Earth gravitational parameter μ and radius R.
- A circular, equatorial mothership orbit of radius r_m.
- A radially aligned tether rotating at angular velocity ω_m = sqrt(μ/r_m³).
- A diver with perigee radius r_p = R + 85 km.
- Release at radius r_rel below r_m.
- Capture at radius r_c below r_rel.
- Atmospheric energy losses at successive perigee encounters.
- Tangential release impulse, with release occurring at the initial elliptical orbit's apogee.
- Capture occurring at the final elliptical orbit's apogee.

For a given apogee radius r_a, the diver's apogee speed is:

v_a = sqrt[2 μ r_p / (r_a (r_a + r_p))]

The tether velocity at radius r is:

v_tether(r) = ω_m r

**Zero-relative-velocity capture requires:**

v_a(r_c) = ω_m r_c

The signed tangential release velocity adjustment is:

Δv_rel = v_a(r_rel) − ω_m r_rel

The goal is to minimize the magnitude of this adjustment while maintaining orbital closure and an acceptable tether geometry.

The total atmospheric braking determines the difference between the initial and final apogees:

Δh = r_rel − r_c

This is a controlled variable, not a predetermined constant.

**Resonance must be solved using total accumulated orbital phase and flight time.** A first Keplerian approximation is useful, but atmospheric braking changes the orbital period each pass. Later include J2 apsidal precession, nodal effects if applicable, and full propagation.

For N atmospheric encounters, an idealized impulse-at-perigee model has flight time:

t_flight = T_0/2 + Σ(T_i, i=1 to N−1) + T_N/2

where the T values are the orbital periods before and after successive atmospheric impulses. Ensure the mothership is at the final interception longitude at the same time, with the tether appropriately oriented.

## Ballast as an orbital control variable

An important design feature is intentional **ballast mass in the diver**.

Adding inert ballast increases its ballistic coefficient and reduces atmospheric deceleration for a given aerodynamic force history. This can decrease its accumulated apogee loss over the sortie.

The diver can also vary aerodynamic drag and collection geometry between encounters, providing another control over the braking schedule.

As ballast increases, the release and capture positions may approach one another, reducing the required relative release velocity.

For approximately constant total atmospheric impulse:

- Atmospheric Δv scales approximately inversely with diver mass.
- Apogee loss scales approximately inversely with diver mass.
- Required release Δv similarly decreases.
- Release impulse, m × Δv_rel, can remain nearly constant.
- Relative release kinetic energy, ½m(Δv_rel)², decreases with increasing mass.

These are approximate scaling relationships, not imposed conservation laws. Verify numerically.

This produces an unusual limiting behavior: as ballast becomes very large, release and capture approach the same position and relative release velocity approaches zero. However, the tether's required downward reach remains finite because the passive capture point is substantially below the mothership CM.

The design is NOT intended to use infinite ballast. Ballast creates other costs: tether tensile load, retrieval energy, structural mass, and reduced collection productivity per unit carried mass.

Find the useful trade-offs.

## Primary numerical investigation

Implement a parametric sweep across resonances, atmospheric braking, release geometry, and ballast.

**For each resonance N:(N−1):**

1. Fix the 85 km reference perigee.
2. Choose a total atmospheric braking budget or apogee reduction.
3. Initially assume equal apogee reduction at successive atmospheric encounters.
4. Solve simultaneously for mothership CM altitude, release altitude, and capture altitude, enforcing exact orbital phase closure and zero-relative-speed capture.
5. Require release to lie between the CM and lower capture point.
6. Calculate signed release Δv, required release impulse, and mechanical relative kinetic energy.
7. Calculate total tether downward reach, release-to-capture separation, and diver flight time.
8. Sweep decreasing apogee loss, representing increasing ballast.
9. Identify the zero-drag/infinite-ballast limit.
10. Repeat for alternative braking schedules, including early-heavy, late-heavy, and independently adjustable encounter drag.

For ballast calculations, introduce a reference unballasted spacecraft mass and atmospheric impulse. Initially use a fixed aerodynamic impulse approximation to isolate the orbital mechanics. Then replace it with a physical atmospheric force model.

Do not hardcode previously suggested mothership altitudes, tether lengths, or release velocities as ground truth. Recalculate them independently and verify closure.

## Atmospheric and spacecraft model

Eventually replace instantaneous perigee impulses with time-resolved aerodynamic propagation through the upper atmosphere.

Relevant parameters:

- Atmospheric density versus altitude, including variability.
- Atmospheric corotation and relative encounter velocity.
- Effective collection area and capture efficiency.
- Aerodynamic drag including noncollecting surfaces.
- Ballistic coefficient and adjustable aerodynamic geometry.
- Mass accumulation as gas is captured.
- Gas storage capacity, pressure, and/or cryogenic density.
- Compressor and liquefaction power, cooling requirements, and heat rejection.
- Dynamic pressure, heating, and integrated thermal load per encounter.
- Electrical power and battery requirements during atmospheric passes.
- Structural and thermal cycling over repeated encounters.

The collected gas remains onboard through the sortie. The diver must actually be capable of retaining it, not merely ingesting it transiently.

The gas-handling subsystem is part of the diver's mass budget. Propellant delivery to the mothership occurs after capture.

Model the effect of increasing carried gas mass on later passes.

The diver should preferably perform guidance through aerodynamic control. Small onboard trim propulsion may be included as a sensitivity parameter, but **do not quietly introduce large onboard reboost propulsion**. That defeats the architectural premise.

## Mothership and tether mechanics

The mothership has primary propulsion, large-scale power generation, and equipment for handling returned gas.

Investigate:

- Gravity-gradient stability of the radial tether.
- Required counterweight/upper tether extension and tether mass.
- Lower-end capture loads and tolerances.
- Mechanical application of the retrograde departure impulse.
- Momentum and angular momentum exchange with the mothership during release and capture.
- Diver retrieval along the tether after capture.
- Energy needed to move the loaded diver upward toward the release point.
- Effects of diver release, capture, and climbing on tether dynamics and mothership orbit.
- Continuous or intermittent mothership reboost.
- Net energy, momentum, and angular momentum accounting across a complete reusable sortie.

Distinguish carefully between release impulse, relative kinetic energy, gravitational potential energy, and actual external propulsion requirements.

The mothership must replenish the orbital losses. It should not be assumed that the small relative kinetic energy at release represents the total energy cost of atmospheric collection.

Initially, treat the tether as rigid and perfectly radially aligned for orbital calculations. Later introduce flexibility, oscillation, capture tolerances, distributed mass, and control.

## Desired results and deliverables

Prioritize orbital mechanics and parameter-space exploration before detailed hardware design.

Produce:

1. A validated numerical orbit propagator, initially two-body with discrete braking and subsequently higher fidelity.
2. Resonance tables for 3:2 through at least 10:9.
3. For each resonance, a sweep across apogee loss/ballast showing CM altitude, release altitude, capture altitude, tether reach, release Δv, release impulse, and relative kinetic energy.
4. Graphs of those quantities versus ballast mass and apogee loss.
5. Numerical investigation of different atmospheric braking schedules.
6. Position/velocity plots illustrating several complete multi-pass rendezvous trajectories.
7. Energy and angular-momentum accounting for full operating cycles.
8. Clear identification of physically invalid solutions, including missed rendezvous, Earth-intersecting orbits, and release/capture points outside the available tether geometry.
9. Sensitivity analysis for atmospheric variability and small guidance errors.

Use reproducible code, numerical tolerances, independent consistency checks, and explicit physical units.

If useful, inspect my existing orbital simulation repository: https://github.com/AlanCoding/orbital-shape-sim

That repository explores earlier orbital geometries and may provide reusable numerical machinery, but this is a distinct architecture.

## Central research question

**Can a ballast-adjusted, propulsion-light atmospheric scoop-diver repeatedly harvest gas and return to a gravity-gradient tether mothership at effectively zero relative velocity, following a one-slip orbital resonance, with all major orbital reboost delegated to the mothership?**

The main optimization is the relationship among:

- Resonance integer N.
- Atmospheric impulse and harvested mass.
- Diver ballast and total vehicle mass.
- Release-to-capture altitude separation.
- Required tether length.
- Release velocity, impulse, and mechanical energy.
- Mothership reboost requirements.
- Gas harvested per cycle and per unit system mass.

We are deliberately at a high-level design stage. Do not prematurely optimize one arbitrarily selected resonance, tether length, or atmospheric braking schedule.

**Find the families of physically closed solutions first. Then determine where the system becomes mechanically and economically attractive.**
