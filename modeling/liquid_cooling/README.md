# Fixed tubes, once-through liquid inventory and coast regeneration

**Current extension:** the [integrated ammonia model](INTEGRATED_MODEL.md) now couples this architecture to capture, compressors, packing and operating payoff. The standalone model described below remains a separate reproducible component screen.

Status: **implemented standalone component model**, `atmo_scoops.liquid_cooling`.
It takes prescribed chamber heat loads and gas-side conductances. It does not
replace `system.simulate`'s rack dynamics, change capture, or produce a new payoff.
The [first comparison](../../investigations/liquid_cooling/ANALYSIS.md) states that
boundary explicitly. Solid metal, encapsulated PCM and pumped liquid remain
three separate cooling architectures; incremental gas mixing also remains available.

## Physical sequence

During collection, cold liquid is pumped through fixed tubes in each compressor
chamber and discharged to a separated warm inventory. No liquid is sprayed into
the captured gas. Each stage can ultimately have its own flow controller and
liquid temperatures. The first screen uses the same fluid/endpoints in four
independent tube banks. It does not assume a warm return line is recirculated
into the cold inlet during the dive.

A pressure-balanced moving diaphragm or piston separates hot and cold sides of
one tank. Tank size is the larger of the cold-full and warm-full volumes, plus
ullage; it is **not the sum of two independently full tanks**. Fixed tubes occupy
chamber volume. Additional coolant held in those tubes is charged separately
from the usable once-through batch. The tank depth quoted in reports is volume
divided by the 30 m-bore area, not a proposed diaphragm spanning the whole hull.
Several smaller pressure modules may be required.

In coast, warmed inventory returns through a regeneration train to the cold
side. A radiator rejects heat directly when sufficiently cold; otherwise a
heat pump lifts heat to a warmer radiator. The refrigerant inside the heat pump
need not be the inventory coolant. In particular, the inventory fluid's boiling
limit does not automatically set the heat-pump condenser temperature. Regeneration
must finish before the next pass. Tubes stay inside; radiator and solar arrays
deploy. An insulated separator requires actual conduction/leakage and mechanical
design; the present tank model charges pressure containment but not a qualified
insulation/diaphragm mechanism.

## Equations and independent inputs

`LiquidCooling` serializes fluid, cold/warm endpoints, pressure, pass/coast/sunlit
durations, tube radius/thickness, flow velocity, radiator temperature, approaches,
Carnot fraction and all hardware mass assumptions. Each chamber boundary supplies
heat per pass, representative gas temperature, gas-side h, and frontal area.
Radius/pitch is currently fixed at 0.1 for the envelope calculation.

CoolProp supplies liquid h(T,p), density, cp, viscosity and conductivity. Every
sample must remain liquid above the triple point; no constant-cp extrapolation
is used across a phase boundary. The useful batch follows:

```
m_batch [h(Twarm,p)-h(Tcold,p)] = Qgas + Wpass_pump
mdot = m_batch / pass_duration
```

Tubes are parallel smooth circular passages. At each sampled temperature,
`Re=rho*v*D/mu`, `Pr=cp*mu/k`; laminar Nu=3.66, and turbulent Nu uses the
Gnielinski expression with smooth-pipe Darcy friction. Transition is conservatively
assigned the laminar value below Re=3000. The minimum internal h along the path
is used for sizing. This is not an experimentally calibrated cryogenic exchanger.

For a prescribed well-mixed chamber gas temperature, outer-area conductance is

```
1/U = 1/hgas + ro*ln(ro/ri)/kwall + ro/(ri*hliquid)
A = mdot/U * integral[cp(T)/(Tgas-T) dT]
```

This is a component sizing boundary condition, **not a computed chamber gas
outlet temperature**. The full kinetic/chemical heat deposition is represented
by the supplied duty. It must not be confused with cooling a gas stream having
only cp times the specified chamber-temperature difference.

Flow determines parallel passage count; required area determines passage length.
Darcy pressure drop plus an explicit header allowance gives pump work. The
inventory/flow/area/pump-heat calculation iterates to closure. Wall hoop stress
and the local inner-wall temperature along the path relative to saturation are screened.
Single-phase failure is reported, not silently credited as boiling cooling.
Tube metal, supports, enclosed liquid and inaccessible tube volume are explicit.

Coast refrigeration uses an enthalpy integral, not COP evaluated just at the
coldest point:

```
Wfridge = m_regen / eta_Carnot
          * integral cp(T) max[(Trad+dTapproach)/(T-dTapproach)-1, 0] dT
Qreject = m_regen*delta_h + Wfridge + Wregeneration_pump
Aradiator = Qreject / [t_reject*(epsilon*sigma*Trad^4 - environment_flux)]
```

A 35% Carnot fraction is a **capability assumption**, not measured hardware
performance across this temperature range. Heat-pump cases regenerate during
sunlight and charge the full refrigeration energy to solar arrays. Passive
cases may reject throughout deployed coast; their small eclipse pump energy is
charged to battery. The model adds a conservative full hot-to-cold allowance for
line-fill liquid beyond the spent batch. That is an explicitly additional heat
allowance, not heat removed from the captured gas.

Dry component mass includes tube/support, pressure tank, heat pump, pump,
radiator, extra solar and pass-pump battery allowances. Coolant is reported
separately as working inventory and also included in total installed mass.
No apparent payoff advantage is obtained by calling a massive coolant inventory
'dry-mass-free'. Integrated reboost must include its inertia and any losses.

## What is and is not established

The tube/tank dimensions and equations are physical sizing calculations; mass
coefficients for refrigerators, radiator panels, supports and pumps are adjustable
development targets. The tank uses a thin spherical pressure-shell lower bound
plus 50% support allowance; a hull-spanning cylindrical tank would differ.
The radiator kg/m² uses emitting-area convention (one effective emitting face).
Folded radiator volume uses 20 mm stack pitch; solar volume uses 40 kW/m³.
Deployment time is sqrt(area)/10 m/s. These are reported, not inserted into the
whole-craft length/deployment fixed point by this standalone study.

Still required for full integration:

1. Solve chamber gas, wall and finite coolant advection jointly through the pass;
   vary flow per stage and stop at inventory exhaustion. Recompute gas-side h
   as the gas cools. Keep wall storage and startup thermal transients.
2. Recompute inlet pressure/leakage, gas storage, every compressor state, peak
   electric demand, retained product and propulsion. Fixed duty cannot predict
   the benefit of colder gas. The current gas-only compressor domain stops at 200 K.
3. Handle air condensation/frost, impurities and blockage where relevant, plus
   local wall boiling, coolant freezing and viscosity effects. A cold liquid
   inlet is not a promise of equally cold gas throughout the chamber.
4. Fit tanks, manifolds, fixed tubes, refrigerator and folded panels together;
   integrate deployment/sunlight. Include line insulation, diaphragm conduction,
   thermal bridges, radiator-loop inventory, valves and credible module packaging.
5. Replace the Carnot fraction and W/kg refrigerator target with temperature-lift
   and load-dependent machinery data; qualify cyclic life and compatible materials.
   Gas-side lattice pressure loss remains omitted by the earlier scope decision.

## Primary references

- [NASA adaptable active-loop study](https://ntrs.nasa.gov/citations/20150023460): establishes an architecture with pumped-loop/direct-radiation and heat-pump modes. It does not validate this vehicle's heat loads or mass targets.
- [CoolProp nitrogen](https://coolprop.org/fluid_properties/fluids/Nitrogen.html), [ammonia](https://coolprop.org/fluid_properties/fluids/Ammonia.html), [propane](https://coolprop.org/fluid_properties/fluids/n-Propane.html): identify equations of state and transport references used by the installed library. The local CoolProp version is serialized with study results.
- [NIST propane EOS paper](https://trc.nist.gov/refprop/Documents/Propane.pdf): covers the triple-point-to-650 K range and high pressures. It supports fluid-property calculation, not propane/material compatibility or exchanger life.
- [Argonne PLTEMP documentation](https://publications.anl.gov/anlpubs/2018/04/143592.pdf): documents engineering internal-flow heat-transfer correlations, including Gnielinski. Applying these to the present tube geometry remains a reduced approximation.

Reproduce with `.venv/bin/python -m atmo_scoops.studies.liquid_cooling`.
An editable single case is `configs/liquid_cooling_reference.json`:

```
.venv/bin/python -m atmo_scoops.liquid_cooling \
  --config configs/liquid_cooling_reference.json --output /tmp/liquid-cooling.json
```
