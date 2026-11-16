# Flight stability and control

This area develops the rotational-stability question illustrated on the
[concept website](https://alancoding.github.io/concepts/atmospheric-scoop-divers/).
It is separate from both scalar payoff optimization and inlet stability:
**inlet start/unstart** concerns the shock system; **vehicle stability** concerns
translation, orientation and flexible motion of the whole craft.

A body shape, fins and aft gas volume can change aerodynamic forces and moments
as well as usable storage. Their benefit cannot be represented by an assumed
center of pressure or a generic stabilizing-fin allowance.

## Study sequence

1. Freeze geometry and mass distribution for entry, peak collection, recovery
   and deployment. Compute center of mass and inertia, including moving gas,
   cryogenic inventory and propellant depletion.
2. Request fluid cases at positive/negative incidence and sideslip, with rate
   perturbations where needed. Include suction settings and mouth state. Record
   force/moment axes, signs, reference point, area and length.
3. Derive restoring and damping derivatives with uncertainty. Check how the
   center of pressure moves as the inlet shock, gas inventory and thrust change.
4. Integrate six-degree-of-freedom motion through the density pulse. Perturb
   attitude, rates, atmospheric density and thrust alignment; measure recovery,
   control effort, peak loads and departure from the planned trajectory.
5. Add flexible-body modes, deployable motion, tank slosh and actuator limits
   before declaring stability or usable control margins.

The fluid solver supplies forces/moments; the rigid/flexible-body dynamics
solver determines the resulting motion. Fluid images alone cannot establish
stability. No implemented solver or validated stability result is claimed here.

## Feedback to design analysis

Supply validated stability/control envelopes and required fin, actuator and
structural mass to the primary model. Offline coefficients may later support a
fast dynamics approximation, but full fluid and six-degree-of-freedom validation
stays outside the optimizer. Track work in
[MODEL_IMPROVEMENTS.md](../../docs/MODEL_IMPROVEMENTS.md), items S1–S4 and F3.
