# Coupled forward-cycle model

**Active reference:** [parallel plates](../../investigations/plates/README.md)
with gaseous propellant bypass, independently optimized plate thicknesses, gaps
and inventories, and full plane-Poiseuille resistance charged as compressor
electricity. A 33-coordinate constrained COBYLA solve completed all 99 forward
cycles and terminated successfully. The released feasible history point has a
battery closure reserve and passes three integration resolutions; the exact
solver-returned point failed refined battery closure. See the investigation for
scope, numerical fixes and reproduction. Rod/pressure-coupled models remain
available for comparison. Each candidate still integrates once, without inner
hardware resizing or periodic shooting.

## Evaluation contract and inputs

`simulate(config)` compiles **installed hardware before integrating**. Exactly
one forward trajectory follows. It returns objective, closure residuals,
constraint margins, histories and conservation audits. There is no periodic
shooting loop, hardware resizing, or convergence iteration around the cycle.
Integrator Newton iterations and local property inversions are numerical solves,
not repeated missions. `search.py` evaluates independent candidates externally.

The complete editable input list is
[`configs/transient_reference.json`](../../configs/transient_reference.json).
The typed registry is `transient/inputs.py`. `design` contains installed
capacities, controls and initial conditions; `capabilities` contains technology
assumptions. Lengths are metres, powers explicitly MW, battery energy MWh,
pressures Pa, specific head J/kg, and areas physical m² unless stated otherwise.

| Independent design scalars | Current search disposition |
|---|---|
| Isp; total symmetric burn duration | Varied in first comparison |
| Solar area, battery energy and discharge rating, bus rating | Independent inputs; proposed together with propulsion in the first limited grid |
| Warm radiator area, buffer mass; initial buffer temperature | Independent inputs; energy-scaled areas/masses in first grid |
| Five rack depths, four clear chamber depths | Independent; held in first grid |
| Five initial rack temperatures | Independent; all 330 K in first grid |
| Four suction capacities, heads, motor ratings, vessel pressure ratings | Independent; held in first grid |
| Coast suction capacity and three relative flow areas, total head and motor rating | Independent; three finite blocks, held in first grid |
| Plant kg/s and electrical rating; exchanger conductances | Independent; held in first grid |
| Initial battery SOC, initial liquid reserve, liquid tank volume | Independent; held in first grid |
| Dive-pump stop, coast-plant start/stop, low-pressure cutoff | Independent; held in first grid |
| LN₂ mixing ratio | Supported, zero reference |
| Apogee | Input; 2,000 km comparison |
| Five radii and five common axial/transverse pitches; rack layout; resistance capability | Independent geometry in the inline-bank search, radius ≥0.2 mm; resistance multiplier is an uncertainty assumption, not a free improvement variable |
| Gas/liquid propellant architecture; gas tank volume/count/rating, initial mass/composition/temperature, booster suction/head/motor/UA, jacket UA, feed pressure/flow limits | Independent installed/control inputs for the gas option |
| Perigee, bore, outside diameter, L/D, materials | Scope locks below |

Perigee is fixed at **85 km** in this initial molecular-air implementation.
Atmospheric chemistry, leading-edge life and drag constraints must precede its
release as an optimizer variable. The geometry is 30 m bore, 31.7 m outside,
317 m overall. The materials are SiC then four aluminum racks. Radius and pitch
now float per rack in the [low-Re inline-bank search](../metal_coolers/LOW_RE_BANK.md),
with a 0.2 mm minimum radius and common axial/transverse pitch. Historical
1 mm radius / 10 mm pitch configurations retain their original geometry options.
Array resistance is charged against actual compressor suction. Calibrated slip
and sparse-bank resistance remain pending.

Receiver depth is the remainder after the other chambers, pressure-vessel heads
and installed equipment packages. Pressure rating affects vessel mass, not an
imposed gas pressure. No design can grow the receiver beyond the fixed hull.
Compressor masses use the existing stress-screened axial-bank buildup; motors
are included once. Installed suction/head/power set hardware, not trajectory
maxima. The common 250 kg/m³ machinery packing capability is still a screening
assumption. Shallow dished heads use a membrane stress estimate; buckling,
attachment and hatch qualification remain outside this release.

## States, equations and controls

Five volumes each carry three species inventories, gas internal energy and rack
enthalpy. Additional states are battery energy, warm-store energy, three liquid
inventories and five rotor-energy accounts. The gas-feed option adds three
reserve species, reserve internal energy and a sixth booster rotor account.
Those slots remain zero for liquid-feed comparisons. The simulation starts 20 minutes
before perigee and ends at the same phase one orbit later (longer burns can move
that epoch earlier).

For each chamber:

```
dm_species/dt = inlet_species - outlet_species
dU_gas/dt = inlet_enthalpy_flow - outlet_enthalpy_flow
            + upstream_compressor_shaft_power - heat_to_rack
dE_rack/dt = heat_from_gas - deployed_radiation
```

Gas-to-metal conductance retains the continuum/molecular bridging correlation,
actual lattice area, material conductivity, temperature-dependent heat capacity
and Biot screen. The lattice displaces gas and imposes a minimum chamber size.
The open inlet admits or leaks according to support pressure and chamber state.
The spatial shock position is not solved in this lumped model.

Compressor work uses **HEOS N₂/O₂/Ar isentropic enthalpy rise / efficiency**.
Its numerical entropy inversion is checked against the separately bracketed
`RealAir.compress` calculation. The gas-volume energy tables retain variable
heat capacity with a low-density mixture EOS; this is not a full nonideal
mixture chamber solver. A separate HEOS audit quantifies that approximation for
the realized trajectory. High-temperature/vanishing-pressure continuation is
only for numerical trial states; the reference audit must remain in domain.
See the [CoolProp low-level property interface](https://coolprop.org/coolprop/LowLevelAPI.html)
for the property backend and phase specification. A comparison of equations of
state is not physical validation of compressor maps.

Finite rotor energy controls speed; suction scales with speed, and available head
with speed squared. A provisional `1-(required_head/available_head)^2` flow
factor, cutoff and motor power limit determine throughput. Check valves seal
stopped banks. These are **uncalibrated pump-map assumptions**, not evidence that
low-Reynolds-number compressors maintain 75% efficiency. Motor idle losses,
spin-up energy and dissipative braking are counted.

The coast train has three finite suction/head/motor blocks and intercooling,
then a finite-flow, finite-power liquefaction train. The warm exchanger and cold
condenser have UA limits. Liquefaction work integrates sensible refrigeration
and real-fluid species boiling/latent duties with a 15%-of-Carnot capability;
this is a reduced separation/refrigeration model, not a designed air-separation
plant or mixture flash. Its rejection, compressor losses, bus storage losses
and retained thruster heat enter the warm store/radiator **once**.

Power allocation gives propulsion and housekeeping priority, then spin-up, dive
compression and the coast train. Solar output follows deployment and a declared
orbital eclipse geometry. Battery power, SOC and bus capacity limit supply.
Unserved commanded load and insufficient delivered thrust reject the candidate.
The battery is recharged only with actual solar energy. It curtails at its
specified initial SOC; the store and racks bypass radiation near their specified
initial temperatures. These are feedback controls, not terminal-state resets.

A symmetric steered burn uses the independently derived finite-arc impulse
penalty. Required thrust rating is analytically eliminated using the incident-air
impulse, Isp, duration and efficiency **before** integration. Actual delivered
impulse is integrated and must match. This is the small-perturbation,
equivalent-perigee-drag orbital provider, not a fully propagated variable-mass
trajectory. Incident momentum over the mouth is charged even for uncollected
air. A configurable external skin-friction impulse is now added; see the [skin-friction investigation](../../investigations/skin_friction/ANALYSIS.md). Saved historical configurations default to zero skin friction. Fin/base/shape pressure drag and external heating remain unmodeled.

Nitrogen and oxygen supply propulsion in their atmospheric ratio, excluding
argon. Liquid reserve replenishment is deducted before product is counted.
Optional injected LN₂ transfers its mass and liquid enthalpy internally; it is
never fresh captured product.

## Rack hatches, deployment and residual disposal

There is **no mouth door**. After the dive banks stop, intermediate volumes vent
with a specified 10 s blowdown timescale; the receiver does so after processing.
After 120 s the remaining gas is discarded and charged as loss only if pressure
is below 100 Pa. Racks then deploy through pressure hatches. A high-pressure
receiver cannot radiate its rack through a fictitious open hatch while retaining
its gas. Vent-port geometry and hatch mechanism mass need detailed refinement;
the blowdown model is a capability assumption, not a resolved nozzle solution.

Motion time is `sqrt(physical_area)/10 m/s`; partial deployed area supplies partial
radiation or solar collection. Racks retract before the next cycle. Metal
wetted emitting area and deployment footprint are distinct. No deployed area
is physically unbounded without a time penalty.

The warm thermal store currently uses a **generic sensible-storage capability**:
2 kJ/kg/K, 340–450 K range and 800 kg/m³ packaging. This is not a qualified
ammonia inventory; ammonia near its critical region must not be represented by
that constant-cp model without a separate property/tank design.

## Objective, closure and numerical domain

```
net_useful_liquid = sum(final_liquid_species - initial_liquid_species)
payoff_days = dry_mass * orbit_period / (86400 * net_useful_liquid)
```

Each species reserve must be restored. Surplus is implicitly offloaded in the
**operating orbit**, returning liquid inventory to its initial value. Circular-
apogee delivery remains unimplemented; `delivered_payoff_days` is null.

A trajectory must also satisfy periodic rack enthalpies (500 J/kg each), battery
and warm-store energy (100 MJ each), residual gas (0.1 kg and 0.01 MJ), rotor energy
(0.01 MJ), and relative delivered impulse (1e-4). The tolerances are declared
numerical acceptance scales, not exact mathematical equality. Materials,
pressure ratings, battery reserve, warm-store temperature, tank capacity,
positive product, Biot number and thermodynamic domain are additional constraints.
Failed candidates get no accepted operating payoff, only a labeled diagnostic.

Species and whole-system energy ledgers include inlet/vent enthalpy, solar
energy, radiation, thrust exhaust, tank heat leak, liquid enthalpy, and rotor
energy. They must close independently. Accepted-step states are included in
path checks as well as requested output times; this is a numerical screen, not
an analytic certificate of continuous-time extrema.

Trace inventories start at 0.001 Pa. A 1 g temperature regularization handles
the singular zero-gas limit without adding mass to the conservation ledger.
The continuum inlet is tapered between 200 and 250 km and disabled above that;
this is an explicitly unmodeled exospheric tail, **not a mouth closure**. Its
incident mass is reported, and its momentum is still charged. Timestep and trace-
regularization sensitivity belong in the numerical validation report.

## Outstanding work before a broad optimum

- Calibrated off-design/stall maps, low-Re efficiency, module choices and finite
  coast heat-exchanger dynamics; measured hardware mass comparisons remain vital.
- Validated multirow/slip lattice resistance, deployable structure/actuators, vent and pressure-hatch
  mechanisms, vessel buckling, and full three-dimensional package layouts.
- Reacting inlet, thermochemical recovery, calibrated skin friction and remaining external pressure drag, wall heating and flight stability.
- Real warm-loop fluid/store selection, refrigeration package calibration and
  actual separation cycle; robust eclipse/array pointing scenarios.
- Nonideal mixture chamber EOS when extending pressure/temperature/composition
  beyond the low-density audited regime; full orbital/export/return provider.
- Broad outer optimization of stage allocation, installed capacities, schedules
  and initial states. The first six-case search is a limited co-design screen.

The evaluator also returns the explicit surplus offload and liquid reserve map. It applies the independent property-domain audit before granting an accepted payoff. Optional LN₂ injection is species/enthalpy conservative; a dedicated injection hardware/flow-limit model remains pending. Numerical controls include a Jacobian differencing step and an RHS evaluation budget; an exhausted budget is reported as unresolved, not physical infeasibility.

See [mass allowance definitions](MASS_ALLOWANCES.md) for bus, rack mechanisms and contingency. The [next refinement plan](../../docs/NEXT_REFINEMENTS.md) covers gaseous propellant bypass, pressure-loss-constrained pitch and the geometry handoff.

The [gas-reserve branch](../propellant_feed/GAS_RESERVE.md) conserves mass and enthalpy through coast refill and next-pass drawdown. It shares the coast compressor and warm loop with the product branch; only the product branch pays liquefaction. See the [coupled comparison](../../investigations/feed_pitch/RESULTS.md).
