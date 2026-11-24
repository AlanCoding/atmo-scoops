# Gaseous propellant reserve and liquefaction bypass

Current implementation and results: [feed/rack comparison](../feed_pitch/RESULTS.md).

**Historical research scope.** Gaseous feed and liquefaction bypass are now
implemented. The accepted reference uses a valve-only reserve, not the older
boosted tank. See [v1.0.1](../../docs/publication/V1_0_1.md). Unresolved propulsion
capability work is tracked in [draft 10](../../local-issue-drafts/10-calibrate-propulsion-and-plume-clearance-tradeoffs.md).

## What the evidence supports

The thruster consumes gas/plasma, not a stream of LN₂ droplets. The old model's
liquid inventory is a storage/accounting choice, not a requirement that electric
thrusters be supplied with cryogenic liquid. It has not separately sized the
vaporizer/feed system either.

- [ESA's 2018 air-breathing electric-thruster demonstration](https://www.esa.int/articles/world-first-firing-of-air-breathing-electric-thruster)
  establishes ground operation on a nitrogen–oxygen mixture. This supports
  investigating mixed-gas feed without first separating or liquefying it; it
  does not establish our efficiency, scale, lifetime or storage architecture.
- [Schwertheim et al., IEPC-2024-385](https://electricrocket.org/IEPC_2024/385.pdf)
  reports an RF gridded ion engine and air-compatible RF cathode operated on
  nitrogen–oxygen mixtures. The reported thruster mixture is 1:1 by mass and
  performance includes indirect thrust measurements. This is stronger evidence
  than assuming a xenon cathode works unchanged with oxygen. Its operating
  conditions are not our atmospheric composition or hundreds-of-MW plant.
- [NASA ion-propulsion system overview](https://www.nasa.gov/wp-content/uploads/2015/08/ionpropfact_sheet_ps-01628.pdf)
  distinguishes thruster, power processor, propellant management and controls.
  Gas feed still requires managed delivery and power electronics; bypass does
  not remove these subsystems.

A Hall thruster is not mandated. Compare oxygen-compatible gridded/RF and Hall
architectures using demonstrated operating envelopes, including neutralizer
power and flow. Do not transfer xenon efficiency to molecular air, or treat
voltage, Isp and efficiency as independent physical knobs.

## Initial numbers and timing

The selected comparison uses **3,487.6 kg propellant per orbit**, from **7,105.0 kg
of gross liquid production**. Thus nearly half the liquid train's mass output
is later spent on propulsion. The average burn demand is **2.91 kg/s** over
20 minutes. Exactly half the commanded impulse occurs before perigee; much of
that burn precedes substantial fresh collection. Gas feed must therefore retain
a previous-pass reserve, even if direct feed during the encounter is allowed.

A full burn's gas reserve at 300 K has these HEOS volumes, for the current
nitrogen/oxygen propellant blend:

| Storage pressure | Gas volume | Equivalent depth at the 30 m bore |
|---|---:|---:|
| 5 kPa | 60,289 m³ | 85.29 m |
| 100 kPa (1 bar) | 3,014 m³ | 4.26 m |
| 1 MPa (10 bar) | 301 m³ | 0.43 m |

These are **gas displacement equivalents**, not complete tank lengths. Real
heads, walls, insulation, supports, regulators, unusable heel and pressure range
must be added. A smaller-diameter pressure vessel or several vessels may be
preferable to a very shallow full-bore tank. Regulated blowdown needs
`V = m_usable R T / (p_max - p_min)` in the isothermal ideal limit, not simply
`m R T / p_max`; finite-temperature blowdown requires an energy balance.

Under the existing refrigeration assumptions, bypassing this mass avoids about
**0.707 GJ of latent heat removal**. The associated electrical refrigeration
work is much larger because of the temperature lift: **18–24 GJ** for latent
cooling alone, or **24–35 GJ** including sensible refrigeration, over the
340–445 K warm-store screen. The latter is an avoided-duty envelope **before**
charging for reserve compression, thermal management and hardware changes.

For scale, the comparison uses about **71.6 GJ** for the coast train/plant and
**871.7 GJ** for propulsion per orbit. Bypass can materially reduce the plant,
but it does not remove the incoming momentum or double net product. The same
propellant mass still leaves the spacecraft if Isp and impulse are unchanged.

Reproduce: `.venv/bin/python -m atmo_scoops.studies.propellant_feed_screen`.
Exact inputs and numbers: `results/propellant_feed/screen.json`. No plant mass
is subtracted in proportion to the avoided energy without resizing its actual
peak duty and cycle throughput.

## Designs to compare

1. **Cryogenic reserve baseline.** Include vaporization, regulation and feed
   hardware explicitly; avoid treating the old baseline as fully qualified.
2. **Unseparated warm-gas reserve.** Divert a controlled fraction after capture/
   compression to a dedicated pressure buffer. Use it before collection begins;
   allow direct encounter feed only when inlet pressure/temperature/flow permit.
   Refill it during coast, and liquefy only the useful surplus. Account for argon
   if it joins the propellant rather than remaining entirely product.
3. **Cold gaseous reserve.** Trade less tank volume against sensible refrigeration
   and insulation, without crossing the mixture dew point. Temperature and
   pressure are independent bounded design variables, not free density gains.
4. **Selective-condensation route.** Recover oxygen-rich liquid and leave a
   nitrogen-rich gaseous stream for propulsion. A single condenser does not
   produce pure LOX plus pure N₂: use mixture vapor–liquid equilibrium, dissolved
   species and argon partitioning, then size separation/recuperation as needed.

The main receiver cannot simply keep the reserve while its rack is removed:
that chamber must depressurize for hatch opening. An independent buffer, an
isolated receiver partition or another explicit cooling/deployment arrangement
is necessary. Compare their actual geometry and structural cost.

## Model implementation and acceptance

Add buffer species inventories and internal energy; independent pressure rating,
volume, initial mass/temperature, fill-compressor capacity, feed regulator minimum
pressure, feed mass-flow limit and controls. Bound minimum intake pressure and
match actual thruster feed/efficiency maps. Add tank/valve/manifold/support mass
and package volume before computing the residual receiver depth.

Route gas through a mass/enthalpy-conservative branch. Actual plant duty follows
only the stream that reaches it. The buffer must recover its starting species
and energy each orbit, and must deliver the entire pre-perigee burn without
borrowing future collected gas. Keep nitrogen mixing inventory separate.
Compare net useful liquid **after all propellant replenishment**, with the same
orbit, skin-friction scenario, materials, delivered impulse and closure criteria.

First run identical installed capacities to isolate physics, then perform an
outer capacity/pressure/temperature search. Report feasible payoff, tank depths,
peak loads, gas heel, species purity and the crossover tank/plant mass. Credit
only the resulting closed-cycle difference; do not apply the 24–35 GJ screen as
an unconditional mass/payoff discount. Retain the alternative even if the first
comparison loses under today's provisional compressor/propulsion assumptions.
