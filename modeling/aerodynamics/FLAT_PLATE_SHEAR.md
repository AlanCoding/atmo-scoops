# External skin shear from a finite flat plate

This replaces an arbitrary coefficient with a conditional engineering equation.
It is an optional **laminar screening model**, not a qualified drag prediction.
The [numerical investigation](../../investigations/flat_plate_skin/RESULTS.md)
uses the current 31.7 m × 317 m exterior. Published configurations retain their
constant coefficient. No new optimized payoff is claimed here.

## Physical approximation and derivation

Unroll the cylinder's outside into a plate of width πD and streamwise length L.
Only the outside face is exposed; do not double the wetted area. At zero incidence,
the approximation treats flow at the boundary-layer edge as the undisturbed
atmosphere. The inlet lip is the leading edge. Fins, base drag, inlet/spillage
pressure forces and shock-induced side pressure are separate contributions.

Viscous shear is τw = μ(∂u/∂y)wall. Momentum diffusion over a parcel's travel time
x/U gives δ ~ sqrt(νx/U), hence τw ~ sqrt(ρμU³/x). Integrating in x yields a
finite force even though the ideal leading-edge shear is singular. Thus a
finite plate has a defined estimate; an infinite sheet alone has no streamwise
length or startup time with which to determine the boundary layer.

For constant properties, the Blasius solution fixes the numerical constant:

    Re_L = ρe Ue L / μe
    mean Cf = 1.328 / sqrt(Re_L)
    Fskin = (ρe Ue²/2) × πDL × mean Cf

The **local** coefficient uses 0.664, not 1.328. Confusing those gives a factor
of two error. NASA's [flat-plate validation case](https://www.grc.nasa.gov/www/wind/valid/fplam/fplam.html)
uses Blasius as comparison data; that case establishes the low-speed laminar
benchmark, not applicability to our orbital speed.

## Compressibility and temperature

A cold ambient-viscosity calculation misses the hot boundary layer. The
implemented Eckert reference-enthalpy approximation uses

    haw = he + sqrt(Pr) Ue²/2
    h* = 0.28 he + 0.50 hw + 0.22 haw
    C* = ρ* μ* / (ρe μe)
    mean Cf = 1.328 sqrt(C*/Re_L)

Reference pressure equals edge pressure. Frozen molecular-air caloric tables
(NASA species polynomials already used by the model) convert h* to T*, rather
than extrapolating a constant room-temperature heat capacity. At fixed
composition ρ*/ρe = Te/T*. Pr=0.72 is an explicit molecular-air approximation.
Sutherland viscosity uses μ0=1.716e-5 Pa s, T0=273.15 K, S=110.4 K:

    μ(T) = μ0 (T/T0)^(3/2) (T0+S)/(T+S)

[Simon, Liu and Hartnett, NASA CR-420 (1966)](https://ntrs.nasa.gov/api/citations/19660012405/downloads/19660012405.pdf)
give the reference-property skin-friction relation in equation 2 and discuss
reference enthalpy when heat capacity varies. Their laminar N₂/CO₂ comparisons
support the method, not our geometry or chemistry assumptions.
[Tauber, NASA TP-2914 (1989), §4.2](https://ntrs.nasa.gov/api/citations/19890017745/downloads/19890017745.pdf)
records the enthalpy weighting in equation 53a and discusses transition,
real-gas heating and limits of boundary-layer approximations. No accuracy
percentage from either source is transferred to this craft.
[NASA's viscosity treatment](https://www.grc.nasa.gov/www/BGH/viscosity.html)
explains the shear-gradient law and temperature-dependent viscosity.

## Why this is still a screen

At the current perigee, the calculation has Re_L≈1.41 million, T*≈5,014 K,
and a free-stream mean free path around 9 mm. A million-scale Reynolds number
does not establish either an everywhere-laminar or everywhere-turbulent state
for a cooled hypersonic surface. Lip disturbances, steps, roughness and transition
need separate characterization. The code does not invent a transition location.

Frozen molecular calorics and Sutherland viscosity at ~5,000 K are substantial
approximations: dissociation, catalytic wall chemistry and finite-rate transport
are not solved. Wall temperatures 300/600/1,000 K are assumptions, not a thermal
solution. Their small effect here is not a measure of total aerodynamic uncertainty.

The reference-state thickness proxy 5L/sqrt(Re*_L) is about 19 m, comparable
to the 15.85 m radius. It is **not** a solved compressible thickness, but warns
against assuming a thin locally planar layer without checking curvature and
viscous interaction. Knudsen number based on diameter is a coarse rarefaction
screen; it cannot validate the near-leading-edge layer. About 11% of this
computed shear impulse comes from portions with Kn_D>0.01. The full-pass result
therefore includes an explicitly flagged continuum extrapolation.

Do not present extrapolated 120–150 km results as continuum predictions or use
an arbitrary min/max splice with free-molecular flow as validation. For a purely
grazing collisionless plane, diffuse tangential accommodation would instead give
τ = α ρ U sqrt(RT/(2π)); that follows from incident thermal molecular flux times
accommodated tangential momentum. It is a different physical regime, not an
additional force to add to continuum shear.

## Integration into the numerical package

`capabilities.skin_model = "flat_plate_laminar"` selects the new method;
`skin_wall_K` fixes the assumed exterior wall temperature. The old default
`"constant"` preserves historical configurations. The plate option **replaces**
`skin_friction_coefficient`; it does not add to it. The same exterior area
multiplier applies. Model selection is a capability assumption, not an optimizer
variable allowed to choose the cheaper branch.

The compiler integrates Fskin(t) over its existing orbital forcing grid, adds
that impulse once to incident-mouth impulse, then uses the existing finite-burn
calculation for propellant, thruster power and mass. No captured mass is added.
It reports impulse-weighted Cf and applicability diagnostics. Drag work ∫FU dt
is not wall heat: no external thermal-protection mass credit or penalty follows
from this mechanical-work number.

This implementation retains the existing atmospheric-relative orbital kinematics;
it does not fix the separate sun-synchronous inclination/wind issue. A reacting
axisymmetric boundary-layer calculation with the actual inlet-edge state is the
appropriate refinement before treating this as a calibrated exterior drag model.
