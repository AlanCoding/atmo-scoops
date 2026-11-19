# Mixed-gas propellant reserve

Implemented in `transient/gas_feed.py`, `hardware.py` and `cycle.py`. Select
`design.propellant_storage = "gas"`; liquid storage remains a reproducible
comparison. This is a conditional engineering model, not a qualified thruster.

## Physical flow path

Aft receiver → existing three-block coast compressor/intercooler → branch:

- Product: separation/refrigeration → liquid product tanks.
- Propellant: additional booster and aftercooler → four spherical gas tanks →
  regulated manifold → electric thrusters during the **next** pass.

The reference stores 4,500 kg of unseparated N₂/O₂/Ar in 500 m³ total gas volume.
Four tanks have 6.25 m outer diameter, 23.3 mm calculated walls and a 1.5 MPa
rating. The branch includes a 10 m³/s, 5 MW booster, two 50 kW/K exchanger
allowances and 500 kg for valves/manifold/regulation. Combined installed mass is
51.9 tonnes before contingency. A 1 bar minimum feed pressure and 5 kg/s feed
limit are declared design assumptions. They are not measured thruster requirements.

Gas-tank spheres, local packing clearance, booster and exchangers consume actual
package volume; the receiver gets shorter. Their location inside the general
machinery package is not yet a resolved three-dimensional packing solution.

## Conservative cycle treatment

Three species inventories and internal energy are integrated in the reserve.
The burn consumes actual current mixture and enthalpy, never future capture.
Refill has priority over liquid production. Coast compression charges both
branches; only product incurs separation and liquefaction. Gas boosting uses
real-mixture isentropic work with compressor efficiency, finite suction/head,
motor rating, rotor spin energy and finite aftercooler conductance. The shared
warm store receives compression/aftercooling heat. A bidirectional thermal jacket
also exchanges heat with the reserve during blowdown and recovery. It is neither
isothermal by decree nor allowed free cooling.

Closure requires each gas species to return within 0.1 kg and internal energy
within 1 MJ. Pressure, temperature, available propellant, feed rate, electrical
power and restored impulse are checked along the trajectory. The low-density
chamber EOS also receives an independent HEOS check for the buffer. Net product
is the increase in liquid inventory: subtracting propellant again would double
count its diversion. Optional LN₂ mixing remains supported; it needs its own
initial liquid reserve and can require a different initial gas composition for
species closure.

## Evidence and limits

[ESA's air-breathing electric-thruster demonstration](https://www.esa.int/articles/world-first-firing-of-air-breathing-electric-thruster)
establishes that nitrogen/oxygen gas can be ionized and accelerated: liquid feed
is not intrinsically necessary. [NewOrbit's IEPC 2024 paper](https://electricrocket.org/IEPC_2024/385.pdf)
is a comparable mixed-air RF propulsion development. Neither establishes this
model's 60% efficiency, enormous power, lifetime, or unchanged Isp with the added
argon. Those remain explicit capabilities held fixed for this comparison.

The existing liquid-feed comparator does not have a detailed vaporizer/feed
assembly, so it is a favorable baseline for liquid storage. No speculative
credit for selective condensation or improved thruster performance is taken.
Detailed cryogenic recuperation and shared-loop integration are priority future
work requested by the owner; they are not needed to conserve this bypass branch.
