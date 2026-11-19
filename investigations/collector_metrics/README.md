# Collector-only mass yield: one-pass boundary metrics

This is a **frozen-reference subsystem accounting calculation**, not a new
trajectory simulation or optimizer result. Source: verified plate case 72,
85 × 2,000 km nominal orbit. Exact source hash, assumptions and values are in
[results.json](results.json). Reproduce from the repository root:

```sh
.venv/bin/python investigations/collector_metrics/calculate.py
```

## Definitions to retain across design revisions

Let m_capture be **new atmospheric gas in the aft receiver at dive-compressor
cutoff**, minus initial receiver gas. Do not count upstream gas that will be
vented, recycled coolant or preloaded propellant. Define:

- **Battery collector yield** Y_B = m_capture / M_B, kg captured gas per kg dry
  collector per pass. Batteries begin externally charged; orbit restoration,
  handoff, liquefaction and eventual thermal reset are outside this boundary.
- **Solar-assisted collector yield** Y_S = m_capture / M_S. Same collector and
  battery, plus arrays sufficient to recharge it in the nominal available coast.
  This adds electrical replenishment, not a complete thermal/operational reset.
- **Equivalent-pass count** N = 1/Y. This is a mass ratio expressed as identical
  passes, not a demonstrated lifetime or elapsed-time payoff.

Neither replaces the principal useful-liquid payoff metric. A future complete
mothership comparison must add the allocated mothership power, refrigeration,
thermal reset, impulse/energy restoration, transfer apparatus and consumables.
If several collectors share hardware, allocate by throughput/capacity/time rather
than treating the mothercraft as free. Store these boundary definitions with each
reported metric so a future design cannot improve it by quietly moving equipment
outside the denominator.

## Current-reference estimate

At 600 s after perigee, the aft receiver contains **7,110.76 kg of new gas** at
about **4,137 Pa and 352 K**. This is before coast compression/liquefaction starts.

| Boundary | Dry mass | Yield per pass | Percent of dry mass per pass | Equivalent passes |
|---|---:|---:|---:|---:|
| Battery collector | 2,508.8 t | 0.002834 kg/kg | **0.2834%** | **352.8** |
| Same collector plus recharge solar | 2,577.6 t | 0.002759 kg/kg | **0.2759%** | **362.5** |

The original complete craft was 13,250 t dry and produced 3,509 kg of useful
liquid per orbit. Removing propulsion both removes hardware and leaves its gas
allocation available for capture, but the roughly 7.11 t here is *not* a promise
that a removed liquefier produces 7.11 t of liquid.

### What remains in the battery collector

| Component | Mass, tonnes |
|---|---:|
| Four dive-compressor banks including motors | 921.7 |
| All five SiC/Al cooler inventories | 454.7 |
| Rack deployment mechanisms (retained conservatively) | 107.7 |
| All original pressure vessels | 229.7 |
| Original hull | 126.3 |
| Resized battery | 42.6 |
| Resized electrical bus | 62.0 |
| Resized warm thermal buffer | 57.3 |
| Auxiliary hardware | 5.0 |
| 25% mass margin, reapplied to retained hardware | 501.8 |
| **Total** | **2,508.8** |

Delete thrusters, gaseous propellant reserve/booster, coast compressors,
liquefier, separator, external cryogenic exchangers, product liquid tanks, solar
and warm radiators. Replace the original battery, bus and warm store with
capture-only sizes. Retain hull and pressure-vessel mass and existing envelopes:
no credit for thinner structure or use of freed package volume. Keeping rack
mechanisms is a conservative carryover; they are not needed merely to store
heat once, but deleting them requires resolving how the racks are supported and
reset/serviced. Their deletion is not included in these numbers.

### Energy, power and thermal support

The saved trajectory supplies **4.553 MWh** of dive-compressor/startup/idle,
friction and auxiliary electricity through cutoff. Subtract thrust and cryogenic
holding power from the saved load; coast processing has not started. Include
rotor spinup and the initial auxiliary interval, not only shaft work on gas.
The extracted trace peaks near 45.70 MW, but size battery/bus power conservatively
to **62.00 MW**, the sum of installed dive motor ratings plus auxiliaries.

Battery capacity is E_load / [eta_discharge × (initial_SOC − minimum_SOC)] =
**6.391 MWh**, with eta_discharge=0.95, initial_SOC=0.95 and minimum_SOC=0.20.
Battery mass is the larger of energy- and power-limited mass, retaining the
reference 150 Wh/kg and 1,500 W/kg capability assumptions. No regenerative braking
credit. Bus mass retains 1 kg/kW.

Warm heat is conservatively E_load/eta_discharge minus shaft energy deposited
in gas, including eventual dissipation of rotor kinetic energy. That is
**12,596 MJ**. Store it between 340 and 450 K using the existing 2,000 J/kg/K
buffer assumption, giving **57.26 t**. No warm-radiator credit is taken during the
pass. This is lumped capacity accounting; new peak heat-transfer/pump hardware
and coupled transient temperatures have not been validated.

The solar variant adds **33,042 m²**, **55.07 t of arrays** before margin, to
supply **5.058 MWh** of recharge and post-capture auxiliary energy. It uses the
reference sunlight history, deployment rate and inward stow constraint. Arrays
start deploying only after collection/handoff; the battery still supplies all
capture power. Intervals when the original arrays were fully stowed receive no
sunlight credit because the saved trace does not establish sunlight there.
Charge/discharge losses are included. The added array mass includes the existing
solar capability allowance, not a newly designed boom/structure. No spare energy
for liquefaction or orbital restoration is included.

## Interpretation and next implementation

This isolates why a supported collector could be much lighter: the remaining
compressor bank is about 37% of battery-collector dry mass. The denominator falls
from 13.25 kt to roughly 2.51 kt, but a pass still returns only about 0.28% of
collector dry mass. This is a useful architecture metric, not proof of economic
viability or a complete mothership design.

The frozen flow history retains the original orbit. Without propulsion the
collector will lose orbital energy/angular momentum; a mothercraft or other
mechanism must eventually account for it. Changed inertia/trajectory, thermal
support, handoff retention and compressor controls require a dedicated forward
case before treating these estimates as a physically closed alternative.

Later add these metrics as read-only reports derived from common trajectory and
component ledgers, with a declared handoff time, dry/consumable boundary, support
allocation and retained product state. Do not subtract a percentage of total
battery/solar mass or count annual/monthly payoff from N alone.
