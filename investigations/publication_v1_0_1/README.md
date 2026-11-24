# v1.0.1 publication evidence and comparison

`build.py` reads the frozen refined trajectory and generates publication metrics,
feed/cooler histories, orbit timing and mass-budget SVG/PNG assets. It runs no
optimization or new forward simulation. `metrics.json` includes the source hash.

```sh
PYTHONPATH=. MPLCONFIGDIR=/tmp/atmo-mpl .venv/bin/python investigations/publication_v1_0_1/build.py
```

## Why the payoff increased

| Quantity | Rejected boosted reserve | Accepted v1.0.1 |
|---|---:|---:|
| Perigee / apogee (km) | 85 / 2,000 | 85.804456 / 2,000 |
| Main receiver gas volume (m³) | 152,725 | 75,029 |
| Dry mass (tonnes) | 13,249.48 | 12,840.22 |
| New useful liquid per orbit (kg) | 3,538.125 | 3,085.886 |
| Operating-orbit payoff (days) | 275.730 | 306.399 |

The current architecture dedicates the last 125 m to retained, low-pressure gas
for propulsion; the main receiver shares its cross-section with stowed equipment.
This removes most of the former main receiver storage capacity. The reserve
participates in filling and feeding during the pass but is isolated from product
processing during coast. It is not dead space or product available for offload.

Perigee was optimized, within 80–100 km, alongside receiver filling and capture
constraints. The selected higher altitude admits a smaller batch. Dry mass fell
3.09%, but product per orbit fell 12.78%; the ratio of these, with the very small
period change, explains the 11.12% payoff increase. This is a budget decomposition,
not a controlled causal ablation. Reserve architecture, packaging, power ratings,
capacities and constraints changed together. We have not established the isolated
penalty of the reserve, or proved a globally optimal perigee/design combination.

Against the original 278.02-day v1.0.0 snapshot, the increase is 28.38 days. Against
the rejected 275.73-day candidate, it is 30.67 days. Keep the two comparisons distinct.

## Complete collection and continuous propulsion

The integrated incident supply is **6,190.178 kg**; **6,188.858 kg** is admitted:
**99.978681%** capture, with a 1.320 kg deficit against a 0.1% acceptance tolerance.
Later leakage/purge is separately **1.570 kg**; propellant use is **3,101.412 kg**.
Reserve closure differs by −0.010 kg; the final useful new liquid is **3,085.886 kg**.
Capture is therefore effectively complete within the model, not literally 100%.
The capture denominator is the modeled inlet forcing, not every particle striking
the hull. The separately estimated unresolved high-altitude/exospheric incident
mass is 0.137 kg; it is not counted as guaranteed collection. Neither this number
nor the capture constraint establishes resolved shock/rarefied-flow efficiency.

The reserve retains at least **2,072.302 kg**, its minimum pressure is **1,898.252 Pa**,
and its minimum modeled feed capacity is **3.67754 kg/s**. Full-thrust demand is
**2.51098 kg/s**. Delivered impulse equals required impulse to numerical precision
(relative residual −4.44e−15); the thrust allocation is capped at its request, so
later overthrust cannot compensate an earlier shortfall. The valve opens at about
−43.616 s and closes after the burn, before product processing.

These are checks of the existing model. The finite feed opening is 1 m² discharging
to 100 Pa; qualification of the actual thruster distribution/feed hardware remains
open. Inventory availability alone is not proof that a real thruster accepts it.

The reduced/staged next-work proposal is in
[the methodology plan](../../local-issue-drafts/specifications/modeling/optimization/STAGED_DESIGN_PLAN.md).

## Fill-while-thrusting audit

The [new pressure/inventory/flow graph](reserve_balance.svg) ([PNG](reserve_balance.png))
and [event values](reserve_balance.json) come directly from the frozen trajectory.
Generate them with `PYTHONPATH=. MPLCONFIGDIR=/tmp/atmo-mpl .venv/bin/python investigations/publication_v1_0_1/reserve_balance.py`.
This postprocessing changes neither the model nor the publication result.

| Event | Seconds from perigee | Reserve mass (kg) | Reserve pressure (kPa) | Cumulative thrust consumption (kg) |
|---|---:|---:|---:|---:|
| Burn starts | −617.570 | 3,513.831 | 3.975 | 0 |
| Valve opens, pressures equal | −43.616 | 2,072.645 | 1.899 | 1,441.186 |
| Minimum reserve | −43.132 | 2,072.302 | 1.898 | 1,442.402 |
| Perigee | 0 | 2,498.433 | 2.548 | 1,550.706 |
| Maximum reserve | +167.449 | 3,990.757 | 4.803 | 1,971.167 |
| Burn ends and reserve isolates | +617.570 | 3,513.821 | 3.975 | 3,101.412 |

**Fill-as-you-use is implemented and clearly operates.** At pressure catch-up the
valve latches open; finite, bidirectional flow exchanges species and enthalpy.
At perigee, main-receiver pressure is 3.067 kPa versus reserve pressure 2.548 kPa,
so it is not modeled as an instantaneous equalization. The reserve gains gas
while thrust continues. Net valve transfer during the burn is **3,101.402 kg**;
its inventory returns within 0.010 kg of its starting value. Net transfer is
computed as reserve inventory change plus cumulative propellant consumption,
which avoids quadrature ambiguity at the opening event.

The starting reserve is **113.30% of the entire pass's propellant use**, even
though only **1,441.186 kg** is consumed before the valve opens and **1,660.226 kg**
is consumed afterward. At minimum inventory, **58.98% of the starting gas remains**.
Thus v1.0.1 demonstrates replenishment, but it does not demonstrate a reserve sized
to exploit that replenishment economically: the 125 m partition was fixed.
Initial gas mass and temperature were closure coordinates; reserve geometry was
not optimized. There is substantial retained gas supporting pressure and feed.

This does not establish that all 2.07 tonnes of minimum inventory can be removed:
less tank volume/inventory changes pressure drawdown, temperature, valve opening,
refill peak and available feed flow. The existing minimum feed capacity exceeds
burn demand, but a smaller reserve requires a new coupled sizing/validation case.
The hypothesis that the fixed partition accounts for much of the payoff penalty
is plausible; it remains unquantified without that comparison. The observed
penalty cannot be attributed to the fill-as-you-use mechanism being absent.

## Reading the cooler-temperature graph

`v1_0_1_coolers.png` plots the **lumped solid temperature in kelvin**, not heat
rejection power or gas temperature. There are four dive compressors but five
solid inventories: one upstream of each dive compressor, plus an aluminum rack
inside the main aft receiver, downstream of compressor 4. There is no modeled
solid rack in the isolated thruster reserve.

The receiver rack (5) contains 20.559 tonnes of aluminum. It follows the same
heat-transfer/radiation equations as the other racks. Its deployment schedule
is different: front racks release at +12 minutes; receiver rack releases at
+72 minutes, after coast processing and the purge window. These are prescribed
schedule rules, not optimized release times. The receiver pressure check allows
the scheduled release only below 100 Pa.

Before release, rack 5 cannot radiate directly to space in this model. It peaks
near 339.5 K, then transfers heat back into the withdrawing gas: at +20 minutes
rack/gas temperatures are approximately 333.41/332.96 K and heat flow into the
rack is −0.144 MW. Energy leaves with the processed gas and is accounted in the
coast plant/warm loop. Near +60 minutes the receiver contains only 0.35 kg; heat
transfer becomes negligible and the rack sits near 322.70 K. At +72 minutes it
deploys, then radiates down to approximately 302.49 K by +75 minutes.

All five racks use the same net radiation law proportional to exposed area and
emissivity × T⁴ minus environmental loading. However, the code also throttles
radiation within 0.5 K of each rack's prescribed starting temperature, stopping
further cooling there. The flat final tails therefore represent an assumed
controlled cooldown target, **not** an unconstrained passive radiative equilibrium.
Hardware implementing that throttling is not resolved. The prescribed late
receiver release and cooldown control should be revisited in the staged thermal
model, without silently changing frozen v1.0.1 results.

## Orbit illustration

The orbit figure includes an illustrative 1,000 × 2,000 km product-collection orbit,
with aligned apsides and the same apogee location as the diver. Its higher perigee
keeps the collection/storage craft out of the atmospheric dive. The 1,000 km value
is a drawing choice, not an optimized mission parameter. Shared position does not
imply matched velocity or timing; rendezvous and export/return accounting remain
unimplemented. Earth land shapes are decorative, not a geographic trajectory.
Regenerate only this asset with `build.py --orbit-only` using the same environment
as the command above.

## Separate cycle schedule

The orbit geometry and timeline are now separate assets. The schedule omits discrete
hatch/valve events and shows reboost, collection and the coast-processing window.
Collection uses the selected model's prescribed inlet-support pressure (`rho*v²`,
with its inlet-altitude window), not chamber pressure or a resolved stagnation state.
Linear interpolation on the actual forcing grid gives 10%-of-peak crossings at
−150.888 and +150.894 seconds: **5.030 minutes**, versus **20.586 minutes** reboost.
Peak support pressure is 398.681 Pa; the cutoff is 39.868 Pa. The cutoff is a
visual convention, not a change to collection control. Metrics are in `schedule.json`.
`build.py --orbit-only` regenerates both the orbit and schedule assets.

## Deployed-scale illustration

Run `.venv/bin/python investigations/publication_v1_0_1/draw_deployed.py`
(requires ImageMagick `magick`) to regenerate
[SVG](../../docs/images/v1_0_1_deployed_scale.svg) and
[PNG](../../docs/images/v1_0_1_deployed_scale.png). The saved refined cycle supplies
physical sheet areas; the existing perigee SVG supplies hull rectangles. All
physical lengths use 0.65 SVG units per metre. Each rack is represented by one
area-equivalent square, solar by two equal squares, and the warm-loop radiator by
one square. Areas are physical footprint, not summed emitting faces. Attachments
trace the front mouth, corresponding chambers, and existing receiver equipment
strips; support lengths and deployment arrangements are illustrative, not a
validated mechanism or mass allowance. Rack 5 is shown after late-coast release.
