# Two-compartment scoop model

The program follows gas from a cooled front compartment through compressor
banks into rear storage, then through a coast liquefaction plant. Its public
interface is `atmo_scoops.system.simulate`; inputs are described in PARAMETERS.md.

## Orbit and collection

Kepler motion and a reproducible NRLMSIS 2.1 atmosphere give encounter velocity,
density, composition and enthalpy. The opening time is the inbound crossing of
a selected fraction of peak ram pressure. An installed door closes at perigee; the no-door variant
continues collecting/pumping outbound. Atmospheric rotation is included for an equatorial prograde
trajectory. Illumination uses the fixed perigee-noon orientation.

    mdot_in = rho_infinity * encounter_speed * mouth_area

Full geometric inbound intake is prescribed, not a simulated inlet result.
Captured-air impulse is integrated once. Any additional impulse is an explicit
scenario allowance, not an inferred aerodynamic coefficient.

## Physical geometry and inventory

The front is cylindrical. Rear storage is a cylinder with two 2:1 ellipsoidal
heads, each D/4 deep; rear length includes both heads.

    V_front = pi * D_front² / 4 * L_front
    V_rear = pi * D_rear² / 4 * (L_rear - D_rear/6)
    L_total = L_front + L_rear + machinery_allowance

Rear length must be at least D_rear/2. Hull diameter is the largest mouth/chamber
diameter plus twice the specified radial clearance. This is an envelope, not a
qualified equipment arrangement.

At prescribed uniform front temperature:

    dM_front/dt = mdot_in - S * M_front / V_front
    p_front = M_front * R * T_front / V_front
    dM_rear/dt = S * M_front / V_front

Automatic sizing uses S = A_mouth R T_front / (C u_perigee), where C is the
pressure-control target. Alternatively specify S directly. After closure,
constant suction V_front ln(1/f_residual) / recovery_time gives exponential
pumpdown. The same hardware serves both phases; its maximum capacity governs.
Recovery stops earlier if the compressor inlet reaches its configured pressure
floor. Actual shock position and cooler pressure loss remain unresolved.

## Open-mouth outbound boundary

With `mouth_closure=false`, collection suction capacity continues after perigee.
The compressor stops at `performance.compressor_min_inlet_Pa`; `recovery_s` is
the maximum permitted outbound pumping time. Reaching that timeout above the
floor fails a completion screen. `front_residual_fraction` is inactive in this
variant. Rear storage is then isolated and remaining front gas is lost.

The reduced outbound boundary uses an explicitly assumed support pressure
`p_support = scenario.open_mouth_support_over_ram * rho*u²`. It is **not** a
computed shock/stagnation pressure. If support exceeds plenum pressure, admission
is the smaller of geometric interception and an ideal compressible-port capacity.
If plenum pressure exceeds support, flow reverses through the same effective
mouth area. The port uses the cooled gas state and a scenario discharge factor;
it does not model inlet cooling/pressure recovery. At pressure ratio r=p_down/p_up:

    mdot_port = Cd * A * p_up / sqrt(R*T) * F(r, gamma)
    F = sqrt[2*gamma/(gamma-1) * (r^(2/gamma)-r^((gamma+1)/gamma))]

Below the critical ratio `(2/(gamma+1))^(gamma/(gamma-1))`, F takes its sonic
maximum. Net front inventory is `dM/dt = admission - leakage - S*M/V`.
This is an exposed approximation for coefficient sensitivity, not a substitute
for [offline fluid studies](../fluid/README.md). Zero leakage with strong support
is not evidence that a real inlet will retain gas. Early-entry heating/drag
without a protective door is unresolved. An open-case input whose prescribed
inbound plenum pressure exceeds its assumed support fails a compatibility screen;
such weak-support transients are sensitivity diagnostics, not viable passes.

Admitted mass, transferred mass, leaked mass, final residual, incoming energy
and capture impulse have separate accounts. All admitted mass incurs encounter
impulse even if later lost; exterior/expelled-gas momentum corrections remain
unresolved. Open-phase oxygen is transported as a well-mixed front/rear tracer
using altitude-dependent incoming composition. Thermal properties remain at the
inbound-mean mixture. The [closure study](MOUTH_CLOSURE.md) compares options with
identical independent inputs and includes support/floor/door-mass sensitivities.

## Compression and thermal accounting

Hot compression targets an intermediate pressure at the front gas temperature;
aftercooling reaches the warm receiver temperature, followed by warm compression
as rear pressure rises. Ideal cooled work is RT ln(p_out/p_in), divided by the
specified efficiency and motor efficiency. This is a work/flow requirement, not
a stage map. Hot and warm duties include retained gas, vented gas and work.
Isothermal residual depletion needs a heat return. The general hot-side balance
accounts for this without assigning leaked gas to useful storage:

    Q_hot = incoming_energy + hot_compressor_work
            - (stored_mass + leaked_mass)*h_hot - final_front_mass*u_hot

Leaked gas carries enthalpy; the final vent allowance carries the remaining
internal energy. The audit checks the total energy residual for both mouth
options. Thermal transients during the final vent are not spatially resolved.

The gas entering the compressor has been precooled by the metal rack:

    T_metal_hot = T_compressor_inlet - gas_metal_approach
    metal_capacity = integral(Cp_metal(T), T_metal_cold, T_metal_hot)
    M_metal = net_absorbed_heat / metal_capacity
    A_sheet = M_metal / (material_density * sheet_thickness)

NIST alpha/delta iron is the implemented heat-capacity proxy, 298–1042 K.
A uniform rack endpoint with positive approach is a conservative temperature
compatibility screen; it is not a distributed exchanger solution. Conductance,
flow channel spacing and pressure loss must eventually connect endpoint to
physical rack geometry. Metal hot temperature, mass and cooling heat are not
extra independent knobs when these input coordinates are used.

Sheet radiation uses two emitting faces and an explicit emissivity/background.
Its ideal cooldown duration is checked against coast time. The warm radiator
uses its own emissivity, view factor and background. Warm panel area assumes
both faces emit, while specific mass is per emitting area.

The product process uses nitrogen-equivalent sensible/latent duty, staged
refrigeration with finite temperature approaches, and a coast feed compressor.
Warm receiver temperature follows warm radiator temperature plus process reject
approach. Species separation has an energy/mass allowance; a detailed mixed-air
phase/separation process is not solved.

## Propulsion, electrical system and hardware

    J_total = scenario_multiplier * J_capture
    propellant = J_total / exhaust_velocity
    electric_reboost_energy = J_total * exhaust_velocity / (2 * efficiency)

The default multiplier is one, the capture-only floor. Oxygen supply is checked
against retained composition. A finite-duration, impulse-equivalent power burst
sizes hardware; it is not yet a finite-thrust orbit-restoration solution.
Batteries cover stowed demand and deployed eclipse demand; solar production
covers the full energy cycle with electrical losses and available sunlight.

Compressor-bank installed mass is max(alpha * required suction volume rate,
peak power / electrical_specific_power). Alpha is a development target. Each
hot/warm/coast bank includes stages, motors and immediate manifolds. The mass
ledger also includes hull/TPS, tank skin/supports, metal deployment, refrigeration,
radiators/buffers, solar, batteries, propulsion, distribution, other allowances
and margin. Mouth closure has a separate area-based mass allowance, set to zero
when absent; the compressor bulkhead remains in both cases. Circulating warm fluid is kept outside the dry total.

## Constraints and objective

The API returns signed margins for front pressure target, compressor access
area, oxygen availability, ideal metal radiation time and positive production.
Temperature ordering, material-property domain and tank geometry are validated
before evaluation. Invalid/unimplemented input domains raise descriptive errors.
Finite port area is screened with the sonic mass-flow bound of a cooled plenum.

Passing these screens is not proof of capture or vehicle feasibility. Shock
stability, gas/metal conductance and pressure loss, actual pump maps, structural
loads, deployment and finite-thrust trajectory are listed as unresolved.

The current outputs include dry mass and net operating-orbit product per cycle.
The implemented optimizer minimizes operating-orbit dry mass divided by net
daily production, subject to the implemented margins and explicit search bounds.
See [optimization results](../optimization/RESULTS.md) for seeds, replay checks and unresolved boundary effects.
The mission objective remains delivered-liquid mass payoff at circular apogee;
it requires an additional delivery/return calculation.
