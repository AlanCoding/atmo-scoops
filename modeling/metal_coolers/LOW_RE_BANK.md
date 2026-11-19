# Low-Re rack bank: radius, pitch and constrained system search

This is an experimental ordinary-solid-rack refinement. The active staged
reference uses a numerical 1% resistance continuation and fixes radius/pitch; see
[the staged plan](../../investigations/staged_refinement/README.md). It uses **standard inline
square banks of parallel circular rods**, with flow perpendicular to the rods
and equal axial/transverse center pitches. The earlier alternating orthogonal
planes and independent-cylinder drag screen remain available only for comparison.
Changing their orientation to match a documented bank correlation is explicit.
No hypersonic correlation is used for the cooled compressor-volume rack.

## Physical geometry and independent variables

Each stage has radius r, common center pitch s, and solid inventory (represented
in the outer search by solid volume divided by bore area). The code accepts five
`stage_radius_m` and five `stage_pitch_m` values. Rod radius has a **0.2 mm minimum**;
the current search upper bound is 10 mm. Pitch/diameter a=s/(2r) is searched over
1.25–2, near the square-bank geometries in the source's laminar comparisons.
Axial pitch is the same s. A request for rack depth L rounds up to N=ceil(L/s)
physical rows. An accepted bank must have at least five rows.

```
A = pi * bore^2/4
V_solid = A N pi r^2/s
V_envelope = A N s
A_wetted = 2 V_solid/r
A_deployed_footprint = N A
beta = 1 - 2r/s
```

The gas occupies chamber volume minus actual solid volume, not envelope volume.
The rack envelope is a minimum chamber-volume constraint. No candidate can grow
the 317 m hull: receiver depth is the residual after other volumes, rounded heads
and installed equipment. Individual rod supports are still represented by the
existing mechanism allowance. This calculation is not structural qualification.

**Heat capacity alone does not bound radius** if metal volume is held fixed.
Smaller rods then increase surface area and row count without adding heat
capacity. Pressure loss, finite gas/solid exchange, thermal conduction (Biot
screen), deployment mass/area and radiation time provide the competing effects.
The explicit lower radius bound also prevents an unqualified manufacturing limit
from emerging as a mathematical optimum.

## Pressure loss: coefficient and gas-density correction

The gap-velocity convention is used throughout:

```
u_gap = mdot/(rho A beta)
Re_d = rho u_gap (2r)/mu
Delta_p_row = xi * rho u_gap^2/2
```

The implemented **laminar contribution** from Gaddis–Gnielinski, reproduced by
Martin and Gnielinski (2000), Appendix A8, is

```
xi_lam = 280*pi * [(sqrt(b)-0.6)^2 + 0.75]
         / [a^1.6 * (4*a*b-pi) * Re_d]
a = transverse pitch/diameter
b = longitudinal pitch/diameter = a in this study
```

This is an array coefficient, not an isolated-cylinder coefficient times a
projected-area fraction. At fixed gas properties it gives a **linear viscous
pressure loss versus mass flow**. The present release uses only this laminar
term and rejects trajectories exceeding Re_d=75 in the reported hydraulic
states. Below Re=1 it uses the laminar 1/Re continuation; that extrapolation is
reported, not described as measured data. No unverified transitional blending
formula is needed in this restricted regime.

A one-bank exit expansion contributes `(1-beta)^2` on the gap-velocity basis,
a low-Mach Borda–Carnot estimate. The pressure-square relation uses

```
K_bulk = resistance_multiplier * [N*xi_lam + (1-beta)^2]/beta^2
p_suction^2 = max(0, p_chamber^2 - K_bulk*(mdot/A)^2*R*T_gas)
```

This integrates the ordinary resistance with ideal-gas density varying through
the bank, assuming the blended gas temperature is representative. Gas acceleration
and spatial cooling are not resolved through individual rows. The existing pore
Mach <=0.3 screen is retained. No drag energy disappears from the energy ledger;
pressure loss changes the compressor suction state and real-gas compression work.
A scalar local root enforces the same mass flow through the rack and compressor.
It is not a repeated cycle or a hardware-resizing iteration.

## Paired heat-transfer treatment

For this bank geometry the continuum term uses the generalized Leveque analogy
from Martin and Gnielinski (2000), with their friction fraction 0.5:

```
Nu = 0.404 * [0.5*xi_lam*Re_d^2*Pr*(4*a/pi-1)/b]^(1/3)
Pr = 0.71
h_continuum = Nu*k/(2r)
```

The existing Nu=0.3 stagnant-conduction floor remains as an explicit lumped
approximation; it prevents falsely asserting zero heat exchange when pumping
stops. The existing series molecular accommodation resistance is retained:
`1/h = 1/h_continuum + 1/h_molecular`. Properties are evaluated at the gas/metal
film temperature. No extra wall-temperature multiplier is applied on top of that
film-property convention. This is a reduced bank model, not a resolved thermal
boundary-layer or rarefied CFD solution. Gas and solid energy remain separate
finite inventories, and actual heat capacity and radiation vary with temperature.

## Evidence, applicability and uncertainty

1. **Martin and Gnielinski, Calculation of Heat Transfer from Pressure Drop in
   Tube Bundles (2000)** — [author/institution full text](https://publikationen.bibliothek.kit.edu/1000034867/2579184).
   Primary coauthor account reproducing the Gaddis–Gnielinski pressure law and
   testing the thermal analogy against bank data. The printed Appendix A8 was
   visually checked before transcription. The pressure-law stated Re range begins
   at 1; square inline geometries 1.25, 1.5 and 2 are among the illustrated laminar
   comparisons. The authors note that their analogy tends to overpredict inline
   heat transfer at low Re. This is a reason to test thermal uncertainty, not to
   treat the coefficient as exact. Actual physical row count is used; the source's
   axial-gradient notation must not be substituted for the explicit rack row count.
2. **Colgan, Nellis and Anderson, Experimental measurement ... low-density flows
   (2024)** — [publisher](https://doi.org/10.1016/j.ijheatmasstransfer.2023.124782).
   Air/CO2 tests at 1–10 kPa, Re 7–150 and Kn 0.0009–0.009, for a staggered bank
   with pitch/diameter 2. Below Re 75, existing pressure predictions underpredicted
   measurements by 50–150%; heat transfer also differed. The accessible abstract,
   introduction and conclusions establish a relevant low-density discrepancy.
   **Its fitted coefficients have not been extracted from the full paper and are
   not claimed to be implemented.** The standard inline laminar law is used
   instead. A 2x resistance sensitivity is motivated by this evidence but is not
   a calibration to a different geometry.
3. **Gaddis and Gnielinski (1985), Pressure drop in cross flow across tube bundles**,
   Int. Chem. Eng. 25(1), 1–15 — original correlation identified by the primary
   coauthor paper above. The coefficient is a combined viscous/form resistance;
   it should not be added to a second independent-cylinder drag estimate.

Rod-scale Kn, Re and pore Mach are exported for every stage/time. Smaller radii
can enter slip/transitional conditions even where the spacecraft-scale flow is
continuum. No unsupported slip drag-reduction credit is granted. The molecular
heat-transfer bridge alone does not validate rarefied hydraulic resistance.
Results remain conditional on that treatment and on the existing compressor,
structure, electrical, heat-pump and propulsion capabilities.

## Numerical search and acceptance

See `transient/global_search.py` and its saved `search.json` for every scalar,
transform, bound and seed. It is a bounded differential-evolution search with
feasibility-first selection, not a fixed set of rack-only cases. A feasible
candidate minimizes `dry_mass / net_liquid_per_orbit * orbit_period`. An infeasible
candidate is ranked by explicitly normalized path/closure violations. Numerical
failures are recorded as unresolved, never as physical rejections. Hardware is
compiled before **one** forward integration per trial; no inner closure shooting
or capacity resizing occurs. The gas reserve must refill, not merely produce some
liquid by spending initial reserves.

The orbit diameter/L/D/material choices remain fixed as agreed. Apogee, Isp,
burn duration, rack inventories, chamber clear depths, compressor capacities,
power/thermal capacities, plant capacities, gas reserve/volume and initial rack
temperatures participate in the search. Performance coefficients are not free
variables. The run is a finite global-search attempt, not proof of a global
optimum in this high-dimensional domain.

A configurable inlet tail taper makes the stiff trace-gas regime explicit. The
search cuts off admission at 150 km, reaches full admission at 140 km, reports
all omitted incident mass, and still charges its drag impulse. This omits about
1.5 kg per reference orbit, compared with thousands of kg collected; a tighter
cutoff/resolution check must accompany an accepted preferred design. Defaults
retain the historical 250/200 km taper for reproduction. This approximation does
not change the perigee or claim the excluded air is absent.

Circular-apogee export/return is still absent: reported payoffs end in the
operating orbit. Cryogenic process integration remains the next requested
component research topic, rather than an uncharged improvement in this search.

### Search controls and numerical implementation

The current search has **55 scalar coordinates**. In addition to the hardware and
initial-state variables, it varies compressor cutoff (1–20 Pa), front-train stop
(120–600 s after perigee), and vent interval before rack deployment (10–60 s).
Residual gas at deployment is charged as lost mass and enthalpy; a hatch cannot
open above the existing 100 Pa limit. This is not a mouth door.

A precomputed CoolProp HEOS enthalpy/entropy table accelerates atmospheric-mixture
compressor evaluations. It solves the same constant-entropy outlet and applies
the same efficiency. Other compositions and out-of-table conditions fall back
to direct HEOS, including optional nitrogen mixing. The table is generated by
`python -m atmo_scoops.transient.property_table`; its metadata accompanies the
binary data. The saved trajectory is independently checked against direct HEOS.
It does not replace real-gas compression with an isothermal or constant-gamma law.

The optimizer can terminate grossly unphysical paths early (material temperature,
battery depletion, chamber pressure or warm-store temperature); these are marked
as path rejections, not assigned an invented payoff. Integration time/budget
failures remain unresolved. Resumable searches reject a changed input/bounds
manifest. Use a new results directory after changing equations or capabilities.

**Scope of the first search:** the compact pitch/diameter interval 1.25–2 does
not include the historical pitch/diameter 5. It tests the evidence-near compact
bank option, not every possible sparse lattice. A sparse-bank extension needs
explicit correlation-extrapolation sensitivity or additional low-Re evidence;
no conclusion that every rack design fails follows from this restricted search.

### Extended-domain follow-up

The compact pilot did not recover a feasible cycle. It was stopped before its
planned mutation generations, rather than spending the full search budget while
excluding the historical sparse spacing. A separate run uses `--pitch-max 8`
and `--isp-max 6000`, with a declared higher-power 4,000 s seed. This extends
spacing beyond the illustrated low-Re square-bank anchors; it is a **conditional
extrapolation study**, not validation of a sparse-bank correlation. The same
published formula is evaluated without an artificial change at pitch/diameter 2.
It must receive sensitivity checks before any feasible design is recommended.
Both domains retain the 0.2 mm radius floor, common axial/transverse pitch,
finite heat transfer, row-count and packing constraints. The initial compact
pilot remains saved separately, so broad-domain results cannot overwrite its
input provenance. The extended run uses eight population members and one
mutation generation: a genuine but small global attempt, not convergence.

### Staged hydraulic-only use

`rack_pressure_model="inline_laminar"` can now select this pressure law without
selecting `rack_flow_layout="inline_bank"`. The staged comparison holds the
historical cylinder heat-transfer correlation and mixed-volume flow proxy fixed.
At the initial 1 mm radius / 10 mm pitch, geometry, solid inventory, wetted area,
package volume and dry hardware mass are identical before adding resistance.
The stage test explicitly checks those equalities. The hydraulic pump solve then
changes suction pressure and finite-capacity throughput. This is a controlled
model-development comparison, not a claim that the retained single-cylinder
thermal approximation validates heat transfer through a sparse inline array.

The geometry still uses common axial/transverse pitch and rounded physical row
count when the explicit bank pressure model is selected. Pressure-model Re/Mach
screens remain active; no extra radius/pitch optimization is enabled implicitly.
# Reduced-resistance continuation

The [continuation investigation](../../investigations/staged_refinement/REDUCED_LOSS.md)
holds rack geometry and cooling fixed while multiplying the complete hydraulic
coefficient by a prescribed factor. The factor is outside the optimizer. A small
factor can establish a numerically tractable starting point, but cannot establish
the actual drag of the rack. Restore physical coefficient evidence separately;
do not infer that a converged reduced-loss result validates the full-loss model.

