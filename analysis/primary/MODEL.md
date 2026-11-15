# Continuous two-compartment model

`atmo_scoops.system.simulate` is the single active cycle API. The CLI and optimizer
call it. [Inputs](PARAMETERS.md) separate geometry, capability assumptions,
controls and optional mixing. No detailed CFD runs inside this model.

## Orbit and intake

Kepler motion, equatorial prograde atmosphere-relative velocity and a fixed
NRLMSIS 2.1 scenario supply density, composition and incoming enthalpy. The
encounter begins with an empty front at inbound 200 km. Both legs use the same
boundary:

```text
p_front = M_front R T / V_front
p_support = κ ρ∞ u²
admission = min(A ρ∞ u, compressible_port(p_support, p_front))
reverse_leakage = compressible_port(p_front, p_support)
dM_front/dt = (1+r) admission − leakage − pump_flow
dM_rear/dt = pump_flow
```

The effective port includes discharge coefficient and choking. Its support,
area and lag are scenarios, not a resolved shock position or start/unstart law.
Mixture thermodynamic properties use a fixed molecular endpoint representative
of the inbound half-peak window; atmospheric oxygen is transported through the
front/rear mass balance. The actual intake window begins at 200 km. Full
geometric intake is not prescribed: inadequate pumping can reject incoming gas.

## Geometry, pumping and cutoff

```text
V_front = π D_front² L_front / 4
V_rear = π D_rear² (L_rear − D_rear/6) / 4
p_ultimate = max(capability floor, intermediate pressure / compression ceiling)
pump_flow = S_rated max(p_front − p_ultimate, 0) / (R T)
```

Rear depth includes two 2:1 ellipsoidal heads and must be at least D_rear/2.
Nominal automatic suction is `(1+r) A R T / (C u_perigee)`, multiplied by the
installed-capacity control. An explicit suction input can replace that nominal
size. This sizes paid-for machinery, not free pumping. C is a sizing coordinate;
it does not constrain or establish actual shock location.

Useful speed declines to zero at the ultimate pressure. Internal backflow work
and idle power remain charged while pumping. Stop on the outbound downward
crossing of the commanded cutoff, strictly above ultimate pressure. Failure to
reach it within the encounter timeout fails a screen. Rear storage is isolated;
remaining front gas is lost. No recovery fraction is prescribed independently.

## Cooling, optional mixing and plant restoration

The metal rack endpoint is the dry stream temperature minus positive gas/metal
approach. Integrate NIST iron heat capacity between cold/hot endpoints for stored
heat per kilogram; iron is a proxy, not a selected alloy. Its range is 298–1042 K.
The attached sheet area is metal mass divided by density and sheet thickness;
both faces radiate. Ideal cooldown must fit the deployed coast.

For LN2 mixing, `r` is injected coolant / newly admitted air. `fixed_rack` holds
the dry stream's rack outlet temperature and solves mixed temperature from
enthalpy. `fixed_inlet` holds mixed temperature and lets the heat removed by the
rack fall. It is invalid to independently fix r, mixed temperature and rack heat.
Pure-N2 liquid enthalpy uses NIST sensible/latent heat tied to the gas reference
at 298.15 K. Injection-pump work is charged. No gas-polynomial extrapolation to
liquid temperature is used.

```text
Q_metal = incoming air energy + injected coolant enthalpy + injection work
          − (stored + leaked) h_mixed − final_front u_mixed
Q_warm = stored (h_mixed − u_receiver) + compressor electric work
new liquid = 0.999 stored_mass − total_injected_mass − propellant
```

All compressor heat enters the warm loop in both mixed and unmixed cases. This
avoids assigning compressor rejection to a metal rack hotter than the mixed
compressor gas. Isothermal compression and the uniform endpoint remain duty
approximations. The rack has not yet acquired a conductance/pressure-drop model.

Coast processing sizes a feed compressor, nitrogen-equivalent staged
refrigerator, separate product heat exchangers and separation allowance.
Refrigeration processes the entire retained mixture, including recovered
coolant. Replacement for lost coolant is reserved from new nitrogen; recycled
coolant is excluded from useful new product. Startup LN2 is working inventory,
not dry mass; its tank, injector and pump hardware have explicit mass allowances.
The process remains a nitrogen-equivalent duty, not mixed-air phase equilibrium.

## Propulsion, energy and installed mass

Admitted atmosphere incurs arrival momentum once. Injected onboard coolant has
no atmosphere-relative arrival momentum. Escaping gas adds a conditional nozzle
recoil estimate. Intercepted but rejected air has a separate projected-momentum
allowance. Hull/fins and surface shear require offline aerodynamic analysis.

```text
J = capture_multiplier J_capture + J_escape + J_uncollected
propellant = J / (Isp g0)
reboost electric energy = J (Isp g0) / (2 η_propulsion)
```

Retained atmospheric oxygen must cover propellant. An impulse-equivalent burn
sizes power and hardware; it is not a powered-orbit replay. Solar area follows
cycle energy, losses and deployed sunlight. Batteries cover stowed loads and
coast eclipse. Warm radiator area follows rejected heat and view assumptions;
peak aftercooler duty sizes the exchanger allowance.

Hot/warm/coast compressor banks use the greater of volume-rate and power mass
requirements. The ledger includes structure/TPS, aft tank, permanent compressor
bulkhead, metal/deployment, refrigeration, heat exchange, radiators, buffers,
solar, batteries, thrusters, power distribution, liquid systems and margin.
Coefficients are development targets; they are not independent free efficiency
or mass improvements for an optimizer.

## Constraints and scope

Implemented screens cover hydraulic compressor access, oxygen supply, coolant
replacement, ideal metal cooldown, positive new production and completed cutoff.
Input validation covers temperatures, geometry, efficiencies and model domains.
Mass/species/energy checks and resolution studies establish numerical consistency.
Actual inlet stability, coupled heat transfer, measured pump maps, structural
loads, reusable mechanisms and finite-thrust export remain unresolved.

Payoff is dry mass / net daily production in the diving orbit. Circular-apogee
delivery and return are still outside the calculation.
