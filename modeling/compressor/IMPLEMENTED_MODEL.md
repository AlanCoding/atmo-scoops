# Compressor refinement implemented in the primary cycle

The active cycle now feeds this mass/real-fluid framework with
[finite front and interstage rack states](../metal_coolers/FINITE_RACK_MODEL.md),
rather than prescribed dive cooler temperatures. No new empirical compressor
mass calibration is claimed; measured maps and complete hardware validation
remain open.


**Status: real-fluid work calculation and conditional geometry-based mass model;
not a validated flight compressor or calibrated low-Reynolds-number map.**
`atmo_scoops/compressor.py` supplies the public `Compressor` configuration, and
`system.simulate` defaults to `mode="real_gas"`. Explicit `mode="legacy"` retains
the former isothermal/volume-coefficient calculation for paired comparisons.
The lower-level `two_volume.calculate` without a compressor argument remains a
legacy reproduction interface; use `system.simulate` for current results.

## Thermodynamic state solution

CoolProp 8 HEOS evaluates a frozen N2/O2/Ar real-fluid mixture. It uses the molecular
composition already calculated by the capture model, including nitrogen mixing.
Unrepresented species below 0.1% by mass are normalized out and reported; larger
fractions raise an error. Thus it is a documented molecular approximation, not
an arbitrary perfect-air gas or a reacting-flow property model. The intake and
receiver inventory ODEs still use their existing ideal-mixture pressure relation;
this refinement replaces compressor thermodynamics, not the whole gas-dynamics
solver. Near the reference intake state Z is extremely close to unity.

For every block and time sample, solve `s(p2,T2s)=s(p1,T1)`, then
`h2=h1+(h2s-h1)/eta_isentropic`, and invert `(p2,h2)` for actual T2. All property
calls use composition-dependent h, s, density, sound speed and viscosity. Reject
states outside the declared 200–2,000 K and 1e-4–1e7 Pa calculation domain.
Real-fluid departure and variable heat capacity are distinct; a near-unity Z
is not justification to revert to constant cp or isothermal compression.

The four default dive blocks have first inlet at the front gas temperature and
later inlets at min(first inlet,600 K). Coast uses three blocks cooled to receiver
temperature. Pressure-rise logarithms are allocated in inverse proportion to
block inlet temperature: a stated schedule, not an optimized or measured map.
A minimum overall ratio of 100 avoids sizing all downstream banks for the first
bank's volume flow when the tank is initially empty. Excess discharge pressure
is throttled into the receiver; no expansion-work recovery is credited.
This policy costs work and is an independent parameter to investigate.

Interstage gas temperatures remain specified cooling targets. Required heat is
charged to the warm thermal system, heat buffer and exchanger mass. Independent
finite metal intercoolers and their deployment are NOT yet implemented. Reported
payoffs therefore test compressor refinement under declared thermal capability,
not the fully refined metal-rack architecture. Coolant mixing remains supported.

The finite-backflow intake envelope now also respects receiver pressure divided
by `head_limit_ratio`. This bounds total head but is not a surge/stall map. Net
transfer, reverse leakage, cutoff and residual product loss still come from the
continuous encounter integration. Internal backflow throughput pays compression
work. Compressor rows are not assumed gas-tight storage isolation.

## Installed mass from states, flow and a declared geometry

For each bank, record maximum suction volume flow, specific work and electric
power over the actual encounter. A bank must accommodate all three, even when
they occur at different times. The default configuration uses:

- Axial face velocity 80 m/s, maximum module diameter 1 m, hub/tip radius ratio 0.5.
- Blade aspect ratio 2, tip solidity 1, total row volume factor 0.12.
- Tip speed 250 m/s and row loading `delta_h / U_mean² = 0.4`.
- Metal density 7,800 kg/m³, assumed allowable centrifugal stress 400 MPa.
- Case thickness 2.54 mm, minimum disk thickness 5 mm, accessory factor 1.3.
- Motor/drive specific power 1,000 W/kg; a separately exposed structural mass multiplier.

These are engineering inputs, not measured scoop hardware or optimized choices.
The [comparable-system table](COMPARABLE_SYSTEMS.md) documents the evidence and
its boundaries. In particular, the material allowable is not qualified at every
computed outlet temperature; thermal gradients, creep and cyclic life remain open.

Use `Q=m_dot/rho`, annulus `A=Q/C_axial`, and parallel module count from maximum
module annulus area. Actual module diameter follows that count. Row count is
`ceil(bank_specific_work / (loading * U_mean²))`. Each row has the full inlet
annulus: a conservative constant-annulus screening layout, not a tapered optimized
compressor. Independent bank speed is permitted; a common bank shaft is assumed.
The cold low-flow tail can set row count while peak capture sets total flow area.

With `height=R_tip-R_hub` and `chord=height/AR`, row blade mass is
`rho_material * K * height³ / AR²`. Stators receive the same allowance. Use row
length `2.34 chord` and cylindrical case mass `pi D length gauge rho_material`.
The disk is a uniform circular disk with a conservative self-stress screen
`0.5 rho_material U_hub²`; blade centrifugal force adds a rim-load thickness
requirement. Reject centrifugal stress above the declared allowable. This is a
screen, not a finite-element disk/shaft/bearing design. It omits detailed torque,
buckling, blade vibration and thermal stress; the accessory factor is not proof
those are covered. Motors are added once, after the structural multiplier.

Count full rotor spin-up each orbit without regeneration credit. Assumed constant
angular acceleration over 120 s gives peak electric power `2 E_rot/(eta_motor t)`.
Motors are sized for the larger of gas-compression and spin-up power. Prespin is
required before full-speed intake; its energy is conservatively in the stowed
battery budget. For quadrature bookkeeping its energy is spread over the encounter,
but bus/battery sizing separately includes its peak. Spin-down heat is conservatively
charged to thermal rejection. Keeping rotors spinning or recovering their energy
would be a separate quantified scenario. Coast machinery has its own spin-up.

New packing screens check aggregate first-bank module face area against 90% of
front bore area and sum of dive bank lengths against the machinery allowance.
They do not include all interstage cooler volumes, ducts or maintenance clearance.
Low-Re efficiency remains a capability scenario: reported Re and relative Mach
must not be mistaken for validation of the assumed 75% block efficiency.

## Mass evidence and uncertainty interpretation

Manufacturer data constrain realistic hardware accounting, not a universal mass
coefficient. We do not fit molecular, Roots and centrifugal pumps onto one curve.
The implemented axial buildup is a transparent alternative to the previous
30 kg/(m³/s) target. Its uncertainty is explored through module geometry, head,
efficiency and structural-mass scenarios. No statistical confidence interval or
empirically validated scoop mass bound has been obtained. Terrestrial package
mass comparisons and a simplified NASA-inspired structural method cannot establish
one without relevant low-density test data and a more complete rotor design.

Small modules can reduce rotating mass but also reduce blade chord and Reynolds
number; many modules add unmodeled integration/lifetime challenges. A mathematical
preference for arbitrarily small rotors is not a qualified optimum. The reported
sweep therefore uses explicit finite geometries, not an unconstrained mass minimum.

## Reproduction and validation

```
.venv/bin/python -m atmo_scoops.studies.compressor_refinement
.venv/bin/python -m pytest -q
.venv/bin/python -m atmo_scoops.audit
```

The study saves complete inputs, per-bank geometry and states, energy/mass/payoff
outputs and source hashes under `results/compressor_refinement/`. These are paired
reference/sensitivity calculations, not a new global optimization. The candidate
90 km perigee is not established as reusable. All payoff remains operating-orbit;
circular-apogee delivery is still absent.
