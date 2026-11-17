# Variable Isp and direct-solar reboost models

The [Isp investigation](../../investigations/reboost/ISP.md) uses the primary
model, with an explicit `scenario.allow_nitrogen_propellant` switch. It defaults
to false. When true, available oxygen is used first and remaining propellant is
charged against retained nitrogen. All propellant is subtracted from useful new
liquid. Argon is not silently treated as an available propellant. The old oxygen
margin remains a diagnostic, but the active constraint becomes nitrogen supply.
Neither atmospheric species receives a free engine-performance improvement.

The [direct-solar arc investigation](../../investigations/reboost/SOLAR_ARCS.md)
is separate, implemented in `reboost.py`. It freezes the reference capture and
thermal duty, but recalculates propulsion, processing throughput, batteries,
arrays, radiators, duty windows, packing and deployment. It is a first-order
orbit-restoration and hardware-budget calculation, not an integrated atmospheric
finite-thrust trajectory optimizer. The primary default remains a battery-fed
perigee burst.

## Isp, impulse and electricity

For effective exhaust speed `u=g0*Isp`, required impulse J and thrust efficiency eta:

```
propellant = J/u
propulsion electricity = J*u/(2*eta)
constant-burst power = J*u/(2*eta*burst_duration)
```

The lower exhaust velocity consumes more product but reduces thrust power,
electrical energy and power-dependent dry mass. If dry mass can locally be
approximated by `A+B*u` and useful liquid before propulsion is C, minimizing
`(A+B*u)/(C-J/u)` gives:

```
u_opt = (J/C) * [1 + sqrt(1 + A*C/(B*J))]
```

This is explanatory dimensional analysis. Reported Isp minima use the full
primary simulation, including solar/deployment iteration. Propellant efficiency,
thruster kg/kW and bus kg/kW are held at their existing capability assumptions.
No validated atmospheric-propellant efficiency-versus-Isp map is available here.

## Voltage is a control, not an efficiency guarantee

An ideal ion obeys `u_ion = sqrt(2*q*V/m_ion)`. Actual Isp also depends on neutral
flow, charge state, dissociation, divergence and voltage utilization. Thus a
specific-impulse target is not a literal discharge-voltage command. Lower voltage
can reduce ionization/utilization efficiency; one cannot assume the same 60%
performance over an arbitrary range merely because voltage is adjustable.

Primary references:

- [JPL, Fundamentals of Electric Propulsion, second edition](https://descanso.jpl.nasa.gov/SciTechBook/series4/Electric_Propulsion_2nd_edition.pdf): ion acceleration and the distinction between beam, utilization and total thruster efficiency.
- [NASA-457M v2 tests](https://ntrs.nasa.gov/citations/20120014613): demonstrated variable Isp on xenon; at 300 V, approximately 2,000 s and efficiencies 0.57–0.63. This does not establish the same efficiency for O2/N2.
- [NASA 100-kW nested Hall-thruster tests](https://ntrs.nasa.gov/citations/20210013351): measured xenon performance near 100 kW. The present multi-gigawatt aggregate installation is an assumed modular scaling, not demonstrated hardware.
- [Oxygen Hall-thruster experiment](https://www.jstage.jst.go.jp/article/jjsass/51/598/51_598_606/_article/-char/en): reports 9% efficiency around 1,000 s in that experiment. This is evidence that atmospheric propellant needs its own performance model, not a ceiling on a developed future machine.

## Why off-perigee restoration needs steering

In polar components, small thrust impulse per unit mass changes specific energy
and angular momentum by

```
dE = vr*dvr + vt*dvt
dh = r*dvt
```

An equivalent tangential impulse at perigee has `dE/dh = vp/rp`. Away from
perigee, tangential-only thrust gives `dE/dh = h/r²`, a different ratio. Paying
only an energy/Oberth penalty therefore generally changes the next perigee.

The study uses two symmetric arcs, each with constant thrust magnitude and
variable in-plane direction. Symmetry cancels first-order apsidal rotation.
For each trial arc, a scalar Lagrange multiplier chooses steering to maximize
restoration per unit impulse subject to restoring both invariants. Let
`a=(vr/vp,vt/vp)` and `b=(0,r/rp)`. The unit thrust direction is parallel to
`b + lambda*(a-b)`; solve `mean[(a-b) dot direction]=0`. Its equivalent-perigee
impulse efficiency is `mean[b dot direction]`. Required impulse is divided by
that efficiency. Some late-arc directions can have a retrograde tangential
component. Gimbal, plume, solar pointing and attitude constraints are not assumed
proven. A separate energy-only case is retained as a deliberately non-closing
lower bound, never a valid recurring-cycle payoff.

An independent Newtonian integration checks the selected steering, two finite
burns and a perigee drag impulse. It is a constant-mass verification of the
orbit geometry, not a replacement for distributed aerodynamic forces, captured
mass, engine transients or flight stability. The reference sunlight/eclipse
orientation is retained; seasons and orientation are not optimized.

## Solar sharing and hardware accounting

Each outbound burn starts after encounter recovery and complete array deployment.
The inbound counterpart finishes before array retraction. Both must fit in
sunlight. Solar power is redirected to thrust; processing pauses for those two
intervals. Existing cryogenic batch mass still has to be completed before the
next pass. Feed compressors, separator, refrigerator and product exchangers
scale with the shortened processing time as a modular-throughputput approximation.
Ordinary coast processing may use eclipse batteries; ammonia regeneration is
sunlit-only. Arrays are sized for the larger of thrust-slot power and non-thrust
processing/recharge power, not just orbit-average energy. Thruster battery energy
is removed; compression, auxiliary loads and eclipse processing still need batteries.

The model retains all energy costs, power-dependent engine/bus mass, rejection
heat and a conservative pass/thrust thermal buffer. A piecewise coast heat ledger
checks the minimum cyclic buffer range. Array and radiator sizes feed back into
10 m/s deployment travel, burn altitude, sunlight time and packing. Existing L/D
and material-recovery limits remain applied; capture is held fixed only for cases
that restore the orbit to first order.

Two ammonia rejection treatments are compared:

1. Direct rejection: radiator must accept the heat-pump output during the shortened
   sunlit processing intervals. No extra thermal store is assumed.
2. Buffered rejection: an explicitly charged warm-side store permits rejection
   throughout deployed coast. Its capacity is the range of the periodic cumulative
   heat input minus radiative output. It uses the existing 200 kJ/kg thermal-buffer
   capability and its packing density; that material/system target remains unqualified.

No new circular-apogee export budget is included. These studies optimize only
Isp and, for direct solar, arc duration/steering under the declared assumptions.
They do not optimize the reference 300 s battery-burst duration, every possible
hybrid battery/solar schedule, orbit altitude, or the complete spacecraft.

## Centered battery-fed duration study

[Duration aside](../../investigations/reboost/BURN_DURATION.md) varies the total
burn duration centered on perigee, reusing the symmetric energy/angular-momentum
restoring steering calculation. For short burns, K = 1 + mu*tau²/(24*rp³) + O(tau⁴);
use the numerical finite-arc map for longer burns. This is an orbital impulse
multiplier, not electrical efficiency. The first-order model assumes equivalent
perigee drag; distributed encounter forces must supply actual restoration targets
in the coupled model. Duration should be optimized with Isp and hardware sizing.
