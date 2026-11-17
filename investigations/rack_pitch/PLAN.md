# Stage-specific rack pitch with pressure loss

**Status:** planned. Here 'variable pitch' means independently chosen rod spacing
in each stage, not variable-pitch compressor blades. Blade pitch remains part of
the separate compressor off-design-map investigation. No in-flight rack-spacing
actuator is assumed.

Keep rod radius fixed at **1 mm** initially. Add five independent pitches and
jointly search them with the five rack depths/masses and chamber allocations.
The present reference has 10 mm pitch and no lattice pressure loss; its spacing
is not yet an optimum.

## Geometry comes before choosing a correlation

The current scalar lattice has solid fraction `pi*(radius/pitch)^2`. A woven
screen or crossed-wire stack can have different solid fraction, open area,
flow direction and row interactions. Specify one physically buildable unit cell
and derive solid volume, heat-transfer area, pore volume, frontal opening and
axial row count from it. Do not attach a packed-bed Ergun correlation to an
unrelated wire geometry and call the result validated.

At fixed envelope and radius, tightening pitch increases metal mass and wetted
area approximately as `1/pitch²` in the current representation. At fixed metal
mass it primarily changes envelope, flow path and packing. Run **both controlled
comparisons** before interpreting an optimized pitch as better heat transfer.

## Research starting points

- [NASA-CR-198442, Gedeon and Wood](https://ntrs.nasa.gov/citations/19960015878):
  experimentally derived screen/felt friction and heat-transfer correlations
  from oscillating-flow regenerator tests. Useful paired thermal/hydraulic
  evidence; oscillatory geometry and flow regimes do not automatically cover
  this low-pressure, hot, transient scoop.
- [NASA-CR-120559](https://ntrs.nasa.gov/citations/19750005995): measurements of
  water pressure drop through square-weave and dutch-twill screens, including
  nonuniform flow. Useful for porosity and velocity definitions and a continuum
  benchmark; it does not establish rarefied-gas coefficients.

Extract correlation definitions, units, geometry, Re range and uncertainty from
full reports before implementation. Map local Knudsen, Reynolds and Mach numbers
from each chamber trajectory; rarefaction on a 2 mm rod can matter even when
flow over the 30 m spacecraft is approximately continuum. Slip/accommodation
and molecular resistance need separate treatment outside correlation limits.

## Reduced-model implementation

Use a pressure-loss law consistent with the chosen geometry, for example a
calibrated Darcy–Forchheimer representation in its domain:

```
-dp/dx = mu/K * u_superficial + rho*beta*|u_superficial|*u_superficial
```

`K` has units m²; `beta` has units 1/m. Update density along a compressible rack
instead of applying a constant-density drop larger than inlet pressure. Place
losses at their physical locations: a rack upstream of a compressor reduces its
suction pressure. It therefore changes suction density, volumetric capacity,
required pressure ratio, rotor work and interstage filling. Do not merely add a
post-processing wattage penalty to an unchanged gas trajectory.

Conserve enthalpy: pressure loss creates entropy; it is not an unexplained
external heat sink. Separate gas/solid heat transfer from flow-work bookkeeping.
Include bypass/maldistribution and a finite inlet-to-rack gap; a single blended
gas temperature may overstate how uniformly the front rack is used. Use the
isolated spatial model to calibrate reduced coefficients, outside the optimizer.

## Acceptance and deliverables

- Zero-resistance limit reproduces the existing model; positive resistance cannot
  create total pressure, mass or energy. Check pressure-ratio and low-density
  limits, mesh refinement and regularization sensitivity.
- Test front, intermediate and receiver racks independently before joint search.
- Compare fixed-envelope and fixed-mass pitch sweeps, then coupled optimums with
  the same external drag and propellant architecture.
- Report pitch, radius, row count, clear depth, material mass, pressure loss,
  peak compressor work/flow, gas/rack temperatures, deployment area and payoff.
- For the geometry handoff, export unit-cell dimensions, supports and bypass
  boundaries explicitly. A solid-fraction formula alone is not a CAD lattice.
