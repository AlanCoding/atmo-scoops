# v1.0.1 propulsion and collection: an accounting split

This is frozen-trajectory attribution, not two physically independent spacecraft or a new optimizer result. Collection includes intake, all solid coolers, compression, liquefaction and product storage. Propulsion includes orbit-restoring thrust and its allocated support. Neither side gets free shared hardware.

## Payoff definition

`t_i = M_i / m_new_liquid_per_orbit × orbit_period`. Both sides use the same **3,085.886 kg of net new useful liquid per orbit**, or **41,906.904 kg/day**, including the existing propellant deduction. Thus the two allocated payoffs sum to the full-craft payoff. They measure how long the joint production stream takes to equal each dry-mass allocation; the propulsion system alone produces no liquid.

| Accounting case | Allocated dry mass (t) | Payoff contribution (days) |
|---|---:|---:|
| Propulsion, existing cycle | 9,849.72 | 235.04 |
| Collection and processing, existing cycle | 2,990.50 | 71.36 |
| Combined existing craft | 12,840.22 | 306.40 |
| Continuous-duty propulsion paper screen | 5,810.65 | 138.66 |

## Allocation rules

- Direct components: thrusters, reserve valves/manifolds and the reserve shell/support mass go to propulsion. Racks, rack mechanisms, dive/coast compressors, cryogenics, separator, product tanks and auxiliaries go to collection.
- Solar: allocate installed mass by each side’s source-energy burden. Propulsion gets its thrust electricity plus its share of battery losses, **95.59%** of solar. This allocates all installed capacity, including unused/spare capacity; it does not resize the arrays.
- Battery: allocate by the propulsion fraction of battery-delivered energy, **97.65%**. At each saved time, direct solar and battery power are apportioned in proportion to the simultaneous electrical loads. This is an explicit neutral attribution rule, not physical wiring or a marginal battery-resizing calculation.
- Bus: allocate by installed thrust power / installed bus rating, **86.94%**. Collection receives the remaining installed power capacity.
- Warm store/radiators: allocate by attributed warm-loop heat, **78.67%** propulsion. Propulsion heat includes the modeled retained thruster loss and attributed battery losses; the remainder includes processing and auxiliaries. This is integrated heat-use attribution, not a new transient sizing of the two buffers.
- Common hull: allocate **125/317 = 39.43%** to propulsion, corresponding to the dedicated reserve length. Collection receives the rest. This is a spatial convention, not a structural proof. Reserve pressure-shell mass is separately identified by the model.
- Apply the existing 25% margin proportionally to each allocation. The approximately 3.514 t of retained propellant is wet inventory and is not charged as dry mass; its tank/support hardware is.

These rules are not unique. A different peak-load or marginal-capacity allocation can move mass between columns. They are reproducible, sum exactly to the installed design, and avoid claiming either subsystem can operate independently at this mass. Hull allocation alone is a small ambiguity compared with electrical hardware.

| Component | Propulsion (t) | Collection (t) | Total (t) |
|---|---:|---:|---:|
| racks | 0.00 | 453.19 | 453.19 |
| rack mechanisms | 0.00 | 106.32 | 106.32 |
| dive compressors | 0.00 | 919.11 | 919.11 |
| coast compressors | 0.00 | 46.90 | 46.90 |
| refrigerator | 0.00 | 140.27 | 140.27 |
| external exchangers | 0.00 | 2.25 | 2.25 |
| separator | 0.00 | 2.50 | 2.50 |
| solar | 2,930.92 | 135.11 | 3,066.03 |
| battery | 2,166.36 | 52.16 | 2,218.52 |
| bus | 660.71 | 99.29 | 760.00 |
| thrusters | 1,321.43 | 0.00 | 1,321.43 |
| warm store | 409.85 | 111.10 | 520.95 |
| warm radiator | 264.48 | 71.70 | 336.18 |
| liquid tanks | 0.00 | 6.00 | 6.00 |
| auxiliary | 0.00 | 5.00 | 5.00 |
| gas reserve system | 2.50 | 0.00 | 2.50 |
| pressure vessels | 73.73 | 165.01 | 238.74 |
| hull | 49.79 | 76.48 | 126.28 |
| margin | 1,969.94 | 598.10 | 2,568.04 |

## Continuous-duty paper calculation

Keep Isp **1811.98 s**, propulsion efficiency, and the same **55.111 MN·s** impulse per **6362.211 s** accounting orbit. Change only the burn duty and associated battery/thruster mass:

`P_continuous = P_burn × burn_duration / orbit_period`

The duty factor is **0.194137**. Electrical power falls from **660.713 to 128.269 MW**. At the existing 2 kg/kW thruster assumption, thruster mass falls from **1,321.426 to 256.537 t**. Delete **2,166.364 t** of attributed propulsion battery. Reapply margin to the remaining hardware.

The resulting propulsion allocation is **5,810.65 t**, equivalent to **138.66 days** of the unchanged net product stream. Adding the unchanged collection allocation would give **210.02 days** as a paper total, not a feasible spacecraft prediction.

All other allocated masses are deliberately retained, including solar, bus, reserve, warm radiator and warm store. Consequently this does not also claim savings from reduced battery losses or smaller peak-power distribution. The current deployment/shadow history cannot guarantee continuous direct solar supply. Continuous thrust in a real orbit changes energy/angular-momentum restoration and may require different impulse, steering or external support. No such solution is implied. No extra product is credited from the same propellant.

## Energy basis and checks

Thrust uses **226.687 MWh/orbit**. Other delivered loads use **10.921 MWh**. Battery losses add **21.923 MWh**; used solar is **259.531 MWh**. Numerical quadrature versus the integrated solar ledger differs by **0.000723 MWh**. Exact input source hash, energy terms and mass allocations are in [results.json](results.json).

Reproduce from repository root:

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 .venv/bin/python investigations/subsystem_payoff/calculate.py
.venv/bin/python investigations/subsystem_payoff/report.py
```

[Current design](../../docs/publication/V1_0_1.md) · [Earlier collector-only one-pass boundary](../collector_metrics/README.md). The earlier metric excludes liquefaction and uses compressed-gas yield; do not mix its denominator with these useful-liquid payoff contributions.
