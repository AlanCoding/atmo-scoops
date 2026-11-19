# Independently spaced transverse rack planes

Implemented as `rack_flow_layout="outlet_planes"`, five `stage_pitch_m` values,
and `capabilities.rack_loss_multiplier`. Rod radius stays 1 mm in this study.
The old zero-loss mixed-volume layout remains available to reproduce the
checkpoint, not as evidence that pressure loss is negligible.

## Geometry that can be drawn

Each plane contains parallel rods across the circular bore. Rod centers are
spaced p apart. Successive planes are p apart axially and rotate 90 degrees.
This is not a woven mesh with two sets of rods in every plane. For frontal area
A, radius r, and rack depth L rounded upward to an integer number N of planes:

```
N = ceil(L_requested/p); L = N p
rod length ≈ N A/p
solid volume = N A πr²/p = A L π(r/p)²
wetted area = 2πr N A/p
single-plane open fraction β = 1 − 2r/p
unfurled footprint = N A
```

The inherited reference has zero explicitly allocated clear depth ahead of the
front rack: its 5.42 m chamber is the rack envelope. This is not a validated shock
stand-off or leading-edge layout. A 3D concept should mark that unresolved inlet
region rather than invent an uncharged plenum; `clear_depth_m[0]` can allocate it
in a subsequent candidate.

Circular-edge truncation is homogenized. Frames, supports and retraction
mechanisms retain the existing mass allowance; their detail has been deferred.
Hardware exports all these dimensions, removes solid volume from gas volume,
and enforces rack envelope and total fixed-hull packing limits. Deployment time
still follows sqrt(footprint)/10 m/s. Material is SiC in front, aluminum downstream.

## Coupled resistance, flow and heat transfer

The rack occupies the outlet of each blended gas volume, ahead of its compressor.
The receiver rack is ahead of the coast compressor. The local hydraulic solve
finds one mass flow consistent with both suction pressure and the finite pump
map, including real-gas compression work, head and electrical limits.

With mass flux G=ṁ/A and viscosity μ(T), the **provisional independent-cylinder
screening law** is:

```
Re = G (2r)/(β μ)
Cd = 1 + 10/Re^(2/3)
K = multiplier N Cd (2r/p)/β²
p_suction² = max(0, p_bulk² − K G² R T)
```

This follows integrating an isothermal ideal-gas momentum loss, with density
varying through the pressure drop. K is dimensionless; G²RT has units Pa².
It is a low-Mach resistance approximation, not a choked-flow solution. Accepted
cycles require calculated pore Mach ≤0.3. Stagnation enthalpy is not discarded
by this loss; heat transfer remains a separate conservative gas-to-rack exchange.
The existing finite crossflow conductance uses actual **outgoing** flow through
the planes. It does not credit incoming gas as forced circulation through an
outlet rack before that gas reaches the outlet. Residual zero-flow conductance
remains a lumped approximation. This layout change is tested independently of
resistance.

The coefficient formula is an engineering screen, **not a fitted correlation
for this array**. Successive wakes, bypass, spatial thermal gradients, slip and
accommodation are unresolved. Re, rod-scale Kn and pore Mach are saved for every
stage/time. A multiplier sensitivity is not a statistical confidence interval.

## What the references establish

- [NASA-CR-120559](https://ntrs.nasa.gov/citations/19750005995) measures woven-screen
  pressure drop with water, and defines open-area velocity. It supports treating
  geometry/velocity consistently, not importing water coefficients into hot
  rarefied flow or claiming this transverse array is a woven screen.
- [Gedeon and Wood, NASA-CR-198442](https://ntrs.nasa.gov/citations/19960015878)
  supplies paired screen/felt thermal and friction evidence for oscillating
  regenerators. Its flow/geometry must be matched before adopting its coefficients.
- [Li et al., 2022](https://arxiv.org/abs/2205.15886) studies slip effects on cylinder
  drag across Re 1–180. It establishes the importance of a separate slip treatment;
  its slip-length parameter is not automatically the molecular Kn used here.

A validated multirow thermal/hydraulic law remains future work. The current
implementation lets the optimizer see the missing trade, without presenting
its preferred pitch or payoff as experimentally established.

## Correlation review and revised variable scope

The owner prefers independent **rod radius and common pitch**, retaining equal
axial and transverse pitch. Do not add independent axial pitch as a prerequisite.
A future outer search should vary radius and pitch with rack inventory/depth;
all material volume, wetted area, Re, Kn, thermal response and resistance must
respond consistently. This note does not change the implemented correlation.

Express the engineering loss convention explicitly:

```
d = 2r; beta = 1 - d/pitch; u_gap = u_bulk/beta
Re_d = rho*u_gap*d/mu
Delta_p_row = zeta_row * rho*u_gap^2/2
```

A bank correlation supplies zeta_row versus Re, spacing ratios, arrangement and
applicable corrections. Current code instead assumes
`zeta_row = Cd*d/pitch`, with `Cd = 1 + 10/Re_d^(2/3)`, and adds all rows
independently. This is not a validated bank coefficient. The pressure-square
form follows integrating the same loss with `rho=p/(RT)` under constant-T,
low-Mach assumptions; it is not a separate empirical loss law. Strong cooling
requires local properties/temperatures rather than an isothermal full-stack fit.

New primary research leads:

- [Colgan, Nellis and Anderson (2024), Experimental measurement of the pressure
  drop and heat transfer characteristics of a crossflow heat exchanger in
  low-density flows](https://doi.org/10.1016/j.ijheatmasstransfer.2023.124782).
  Air/CO2 experiments at 1–10 kPa, Re 7–150, Kn 0.0009–0.009; an equilateral
  staggered tube bank with pitch/diameter 2. Defines Eu as
  `2*Delta_p_row/(rho*u_max^2)` and compares with HEDH correlations. Below Re 75,
  measured losses exceeded existing predictions by 50–150%. A close research
  lead, not direct calibration of our alternating orthogonal planes at p/d=5,
  front Re approximately 2.6 and rod-scale Kn approximately 0.026. Publisher
  abstract/introduction/conclusion were accessible; full coefficient extraction
  and domain verification remain outstanding.
- [Yu et al., Multi-Objective Design Optimization of Precoolers for Hypersonic
  Airbreathing Propulsion](https://doi.org/10.2514/1.T4921),
  [author-hosted full text](https://aero.kyushu-u.ac.jp/stsel/_stsel/wp-content/uploads/2020/09/Yu2017_JTHT-Multi-objective-design-optimization-of-pre-coolers-for-hypersonic-air-breathing-propulsion.pdf).
  Explicitly treats heat transfer, pressure recovery and compactness together.
  Equation 10 uses the row Euler coefficient; discusses Zukauskas/Ulinskas data
  and HEDH fits, and discrepancies from compressibility. Useful method/geometry
  benchmark; its principal operating point is far denser than our front stage.
- [Armour and Cannon (1968), Fluid flow through woven screens](https://doi.org/10.1002/aic.690140315).
  The abstract reports Re 0.1–1000, void fractions 0.35–0.76 and pore diameters
  5–550 micrometres. This is a screen correlation candidate, but those geometries
  differ substantially from our roughly 97% void rod stack. Do not extrapolate
  a woven-screen coefficient solely because the Re ranges overlap.

Before optimizing to a claimed preferred radius/pitch, match a bank correlation
to the actual arrangement or clearly define and compare a standard tube-bank
alternative. The alternating 90-degree geometry is a model choice, not a
user-imposed requirement, and should not force an unjustified coefficient.
