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
[the methodology plan](../../modeling/optimization/STAGED_DESIGN_PLAN.md).
