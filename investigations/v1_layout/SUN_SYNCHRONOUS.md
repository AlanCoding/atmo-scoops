# v1.0 intended orbit: dawn–dusk sun-synchronous

Adopt a **dawn–dusk sun-synchronous orbit** as the v1.0 mission target: 85 km
perigee and 2,000 km apogee, with the mean node maintained near 06:00/18:00 local
solar time. The low pass is not, by itself, a mathematical incompatibility with
sun synchronization. Its drag and reboost must keep the required mean elements.

Using the usual first-order J2 mean-node relation,

    Ωdot = −(3/2) J2 sqrt(μ/a³) [R_E / (a(1−e²))]² cos(i),

and Ωdot=360°/365.2422 days gives **i≈99.35°** for this eccentric orbit. Period is
**106.03 min**, and Kepler perigee speed is **8.34 km/s**. The calculation uses
the repository Earth radius and gravitational parameter, J2=0.00108262668 and
mean-solar-year precession, and is reproduced in `build.py` / `results.json`.

Sources: [NASA orbital mechanics for thermal engineers](https://ntrs.nasa.gov/api/citations/20205003902/downloads/Introduction%20to%20Orbital%20Mechanics%20and%20Spacecraft%20Attitudes%20for%20Thermal%20Engineers%20CHARTS%20PDF.pdf)
gives the J2 node relation; [ESA's orbit overview](https://www.esa.int/articles/about-us/directorates/space-transportation/types-of-orbits)
explains the fixed local-solar-time / dawn–dusk motivation. The numerical
inclination here is our calculation, not a published mission design.

## What this justifies

This is a sensible target for predictable solar geometry and a power-intensive
coast. It does **not** justify treating every second of the coast as illuminated.
The saved reference's solar model uses a simplified fixed Sun/shadow geometry;
it does not propagate inclination, RAAN, date and seasonal Sun direction.
**The 278.02-day payoff is still that saved calculation**, not a new sun-synchronous
optimization. Do not silently remove eclipse losses or credit a new payoff.

A simple geometry screen illustrates the issue. At equinox, a dawn–dusk plane
at this inclination has solar beta about 80.65°. Avoiding Earth's cylindrical
shadow at *every possible orbital location down to perigee* requires beta above
asin(R_E/r_perigee)≈80.70°. The two are nearly equal; the inequality is a
sufficient all-phases condition, not a prediction that this particular orbit
must eclipse. Seasonal Sun declination and the location of perigee matter.

The same first-order J2 model gives argument-of-perigee drift near **−2.63°/day**.
A sun-synchronous node does not freeze the apsidal orientation. Low-pass drag,
atmospheric rotation, finite reboost and any plane/apsis corrections also need
accounting. The existing tangential reboost calculation restores energy/angular
momentum in its planar approximation; it does not establish long-term 3D SSO
maintenance or include all of its costs.

Publication wording: “The intended orbit is dawn–dusk sun-synchronous; a first-order
J2 calculation gives about 99.35° inclination. Seasonal illumination and 3D
orbit maintenance remain future refinements to the current cycle model.”
