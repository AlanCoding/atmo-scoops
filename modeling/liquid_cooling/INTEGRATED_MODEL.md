# Integrated ammonia option

`system.simulate(..., ammonia=AmmoniaCooling(enabled=True))` now replaces the
front and interstage passive racks with fixed, once-through ammonia tube banks.
The default remains the ordinary-metal architecture. PCM and gas mixing are
retained. The earlier [standalone screen](README.md) remains reproducible but
its fixed gas states are not used to predict the integrated payoff.

## Independent inputs

The `ammonia` configuration section supplies cold supply temperature, target
warm return temperature, liquid pressure, four independent wetted areas, four
maximum flow rates and four available batch inventories. Tube radius, wall,
pitch ratio, design liquid velocity, radiator temperature, Carnot fraction and
refrigerator specific mass are also explicit. Hardware capabilities must not be
optimized as though better material or machinery performance were free.

Geometry derives wall metal, liquid hold-up, sealed tube displacement, gas pore
volume, bank depth, parallel passage count and path length. Tubes remain fixed:
there is no metal-sheet deployment mass or emitting area for this architecture.
Independent coolant storage adds physical tank volume; compressor, refrigerator,
folded radiator and solar envelopes enter the existing length calculation.

The present model accepts cold supply at or above 200 K, matching the real-gas
compressor domain. Colder ammonia is close to freezing and is not supported by
this integration. This does not constrain future alternatives using other fluids.

## Dynamic coupling and control

Front chamber mass and internal energy retain the continuous admission, leakage,
pumping and incoming kinetic/chemical energy equations. At every ODE evaluation,
gas-side conductance changes with the solved pressure, temperature and flow.
Tube-wall and internal liquid resistances are added in series. The controller
varies liquid flow toward the warm-return target with a 1 K margin for pump heat,
subject to the specified maximum flow. The available liquid heat-capacity rate
limits transfer; a cold supply does **not** impose a cold gas temperature.

The front ODE integrates energy removed, spent liquid mass and pump work.
Intermediate compressor blocks use counterflow effectiveness with both gas and
liquid heat-capacity rates. Their flow controller has a 5 K target margin, allowing
for the local-cp approximation versus the subsequent real-gas enthalpy check.
Every compressor's inlet, isentropic endpoint, efficiency-adjusted outlet, flow
volume, power and installed mass are recalculated. Interstage heat and spent
coolant/pump energy are time-integrated. The existing small-interstage-gas-holdup
screen still applies; intermediate gas tanks are not yet fully dynamic.

Liquid cp during heat exchange is the CoolProp enthalpy secant over the specified
cold-to-target interval. Regeneration uses temperature-dependent CoolProp cp and
enthalpy. Gas compression still uses real-gas endpoints. Internal liquid h uses
the minimum fully developed laminar coefficient over the coolant range; no
unearned turbulent enhancement is credited when the controller throttles flow.
This is conservative but requires a more detailed flow/transport correlation.

The tube wall is quasi-steady, not a separate heat-storage state. Inlet startup,
axial advection delays, wall thermal transients and flow maldistribution are not
resolved. Output `final_metal_K` retains the legacy field name but denotes the
cold reference boundary for liquid banks; `max_metal_K` is the estimated peak
liquid-side wall temperature. Use the explicit liquid wall/return fields to
interpret this architecture.

A candidate that spends more than its available inventory is **rejected**.
The solver does not claim valid post-exhaustion collection or instant recycling:
its trajectory assumes the commanded cold feed remains available, and is usable
only if the inventory screen passes. No exhaustion-based control optimization
is implemented. Upper target enthalpy, wall boiling and tube-pressure stress are
also screened. Controllers, pressures and inventories are serialized in results.

## Coast energy, mass and packing

Each stage's spent return is assumed to mix in its warm reservoir. Its mean
enthalpy comes from actual removed gas heat plus pass-pump work, divided by spent
mass. Coast refrigeration restores this mass from its solved mean return state
to the cold supply. Unused cold stock is not reheated for free or charged an
entire extra regeneration cycle. Liquid remaining in tubes gets an explicitly
conservative full-temperature restoration allowance, included in both cold duty
and electrical work. Heat-pump work is the temperature-integrated Carnot-fraction
model, not a single COP evaluated at the cold endpoint.

The heat pump runs during the actual deployed sunlit coast; all added electricity
is assigned solar area and mass. Its radiator rejects removed heat, pump heat,
heat-pump work and pump electrical losses. Pass pumping gets battery energy and
power allowances. Refrigeration, pumping, pressure tanks, tube supports and
additional power distribution have explicit dry masses. Dry-mass margin is applied
once. Ammonia inventory and an allowance for the rejection-loop fluid are reported
separately in working mass. A second payoff numerator includes ammonia inventory,
so changing a solid thermal store into liquid cannot hide its carried mass.

No extra propellant proportional to coolant mass is invented: the current
fixed-trajectory reboost budget is based on drag impulse. Extra working mass
changes delta-v for a given impulse, but not that required impulse. Finite-thrust
trajectory changes remain an unresolved limitation common to both architectures.

The tank uses the largest hot-full/cold-full volume plus ullage, not two full
tanks. Its structural mass remains a thin spherical lower-bound allowance plus
supports; it is not a qualified diaphragm or hull-spanning tank. Insulation,
separator thermal bridges, manifolds, containment fatigue and pipe supports need
better engineering. The existing fitted hardware mass/volume assumptions remain
conditional. New radiator and combined solar deployment feed back into the
coast-time/area fixed point. The warm product receiver temperature is unchanged;
this is not an optimization of cold intermediate or final storage.

## Reported payoff and limits

`operating_mass_payoff_days` uses total dry mass divided by useful new cryogenic
liquid per day. `payoff_including_ammonia_inventory_days` additionally charges
ammonia batch and tube inventory. Total working mass separately includes the warm
rejection-loop fluid. Circular-apogee delivery remains unimplemented and is not
included in either payoff.

See the [integrated investigation](../../investigations/liquid_cooling/INTEGRATED.md)
for exact inputs, passing/rejected cases, resolution checks and reproduction.
References and fluid-property provenance are retained in the [component dossier](README.md).

## Tube-geometry sensitivity and hydraulic interpretation

The [radius/pitch investigation](../../investigations/liquid_cooling/TUBE_GEOMETRY.md)
varies diameter at fixed external area. Equivalent path count is sized from the
maximum liquid flow at the design velocity, and path length follows from surface
area. Consequently, smaller diameter creates more, shorter parallel paths.
Darcy friction and a fixed 100 kPa header allowance are implemented, but this is
not a resolved manifold network. Do not interpret it as shrinking an unchanged
plumbing installation. Radius and wall thickness must be distinguished; the study
includes both matched wall/radius and fixed-wall controls.
