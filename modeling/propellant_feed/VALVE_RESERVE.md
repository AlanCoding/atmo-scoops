# Valve-connected reserve: v1.0.1 restoration

This implementation has completed constrained optimization and independent
resolution checks; see [results](../../investigations/valve_reserve/README.md). The boosted sphere architecture remains
reproducible for historical inputs with `propellant_storage="gas"`; the current
architecture is `"valve"`. No boosted hardware is compiled for valve inputs.

## Geometry and installed hardware

The last 125 m of the 317 m hull is reserved for gas, at the full 30 m bore.
A second rounded-head main receiver ends at x=192 m. Packages ahead of that
boundary reduce its radius. Each tank has two 1.5 m-deep spherical-cap heads;
therefore V = pi r² (L-h) + pi h³/3. Main receiver gas volume subtracts solid
rack material. Packages are charged once through radius reduction, not again
as a subtraction inside the narrowed tank. Receiver plate inventory, wetted
area, thickness and spacing are retained when computing its longer, smaller-area
rack. Physical row clearances remain fixed.

Externally mounted thrusters retain their dry mass but occupy no internal tank
package volume. Their bus, batteries and other internal support still do.

Both tank shells, including the added pressure boundary, are charged with the
existing pressure-vessel model. Valve/manifold mass is provisionally 500 kg plus
500 kg/m² of equalization opening: 2,500 kg for the 4 m² baseline. This is an
explicit development allowance, not a demonstrated mass. It occupies an internal
package volume. There is no refill motor, booster rotor or reserve aftercooler.

## Transfer, feed and thermal state

The reserve is initially isolated. An integration event locates the instant that
receiver pressure catches reserve pressure. The valve then stays open and allows
**bidirectional** donor-to-recipient flow until max(pump-stop, burn-end). It is
isolated before product processing. The existing compressor stops at +600 s;
product processing starts no earlier than +650 s and 30 s after burn completion.

Transfer uses the existing compressible orifice relation with Cd=0.8, including
choking. A 0.1% pressure-difference regularization removes the square-root cusp
at equality. Every transfer carries the donor's species and enthalpy. The
reserve never participates in receiver purge or product withdrawal.

A fixed 1 m² feed opening is modeled against a 100 Pa downstream manifold.
Its calculated mass-flow capacity limits thrust. This is **not a qualified
thruster inlet requirement or a validated feed-system design**. No compressor
is silently added. The low-pressure propulsion interface remains a capability
assumption to be checked against a developed thruster distribution system.
An initial 0.15 m² trial failed the thrust requirement, demonstrating that the
flow boundary is enforced rather than granting unlimited feed.

The reserve is adiabatic in this baseline, without a free coast temperature
reset or the rejected 50 kW/K jacket. Its initial mass and temperature are outer
optimization coordinates constrained to cycle closure. The unused legacy booster
rotor state remains at zero to preserve state/ledger indexing; it contributes
neither energy, mass nor power. A future wall/insulation model must replace the
adiabatic assumption rather than impose a free terminal state.

## Capture, capacities and optimization

The receiver filling target is the previous actual peak, 4,766.83 Pa, with a
50 Pa numerical/design matching band; the independent structural rating remains
6,500 Pa. Perigee is a coordinate constrained by that target. Supply is
recomputed from the orbit and the reference atmosphere for every candidate.

Full capture is defined as at least 99.9% of the incident mass integrated through
the existing tapered atmospheric collection window (fully open below 200 km,
tapering to zero at 250 km). The 0.1% allowance is a declared numerical/tail
allowance, not a free efficiency coordinate. Later leakage/venting and propellant
consumption remain separate ledgers. No missed incident gas earns product.

The full search includes dive suction and head capacities, coast suction/head,
installed motors, racks, energy capacities, Isp and burn time, plus reserve
initial state and perigee. Installed bus and battery discharge ratings are
conservatively derived before integration from the sum of installed motor,
plant and thrust powers plus 1 MW auxiliaries. Their mass and folded volume are
charged before integration; no candidate is resized from its own trajectory.

One forward cycle evaluates each point. The outer restoration solve closes
reserve mass, reserve energy and receiver filling; it is not an inner loop in
`simulate`. The subsequent constrained COBYLA search retains all original
thermal, electrical, material, pressure, inventory, capture and closure checks.
Parallel initial trust-region probes evaluate independent complete cycles in
separate processes; COBYLA itself requests and uses exact cached evaluations.
A preliminary SLSQP attempt was stopped because its small finite differences
were comparable to forward-solve noise. No SLSQP optimum is claimed.
Exact input caches are source-manifest protected. A numerical failure
stops the optimizer; it does not become a fictitious physical penalty value.

Reported payoff remains useful-liquid production in the operating orbit.
Circular-apogee delivery has not been implemented and is not credited.
