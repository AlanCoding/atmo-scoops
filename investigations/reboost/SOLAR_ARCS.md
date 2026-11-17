# Direct-solar reboost before stow and after deployment

**Worth retaining as a design option, but deleting the propulsion battery is not
an automatic large payoff improvement.** At optimized Isp, the solid-rack case
improves from 371 to 346 days; warm ammonia is essentially tied near 393–394 days
if an additional, explicitly costed rejection-heat buffer is available.

These are separate fixed-capture budget/trajectory investigations. The main
simulation still uses battery-fed perigee thrust. Orbit is 85 × 2,000 km,
period 106.0 minutes; all payoff values end in that operating orbit.

## Optimized comparisons

Both arcs have the same duration: inbound thrust ends before stowing; outbound
thrust starts after recovery and deployment. The search varies Isp (1,000–7,000 s)
and duration (60–1,600 s per leg), with first-order orbit-restoring steering.

| Cooling / rejection | Isp, s | Each burn, min | Impulse / perigee impulse | Solar, MW | Battery, tonnes | Dry mass, tonnes | Net kg/pass | Payoff, days |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Solid racks / direct rejection | 3087 | 22.1 | 1.868 | 995 | 174 | 17,121 | 3,640 | 346.4 |
| Ammonia 200–300 K / direct rejection | 2906 | 13.6 | 1.672 | 1,363 | 123 | 27,061 | 3,791 | 525.6 |
| Ammonia 200–300 K / buffered | 3076 | 18.0 | 1.772 | 1,153 | 140 | 22,187 | 3,787 | 431.4 |
| Ammonia 280–340 K / direct rejection | 2903 | 14.9 | 1.697 | 1,263 | 130 | 24,006 | 3,752 | 471.0 |
| Ammonia 280–340 K / buffered | 3072 | 19.5 | 1.806 | 1,083 | 151 | 19,954 | 3,732 | 393.7 |

The appropriate battery-perigee comparisons are **371, 419 and 393 days** for
solid, cold ammonia and warm ammonia respectively, after optimizing their Isp.
Against the original 4,000 s cases, all these gains look larger; that comparison
would conflate Isp optimization with changing the thrust schedule.

## Why the orbit penalty is larger than an energy-only estimate

Thrust must restore both orbital energy and angular momentum. In polar components,
`dE = vr*dvr + vt*dvt` and `dh = r*dvt`. Tangential thrust away from perigee
has the wrong energy/angular-momentum ratio to undo perigee drag. Paying only the
speed/Oberth penalty changes the next perigee and therefore the next air capture.

The symmetric finite-arc solution steers partly radially and can eventually point
past 90 degrees from the prograde tangent. This costs 67–87% additional impulse
in the selected cases. Attitude, gimbal, plume clearance and array pointing still
need engineering; unrestricted in-plane steering is an assumption.

For example, the solid-rack optimum starts outbound thrust 10.6 minutes after
perigee, at about 321 km, and continues to about 1,486 km. Direction varies from
20 to 113 degrees from the local prograde tangent. The inbound arc is symmetric.
These are long burns, not short pulses immediately beside atmospheric contact.
At 3,000 s Isp, shortening each solid-rack burn to five minutes gives roughly
883 days, versus about 392 days with fifteen minutes: peak solar power matters.

The deliberately invalid energy-only runs give 158 days (solid), 291 (cold ammonia)
and 251 (warm ammonia). **These are not sustainable-cycle payoff predictions**;
they are retained only to expose the error from ignoring angular momentum.

## Where the battery saving goes

For solid racks, battery mass falls from 2,067 tonnes at the optimized perigee
Isp to 174 tonnes with direct-solar thrust. Warm ammonia falls from 2,115 to
151 tonnes in its buffered case. Those are roughly 92–93% battery reductions,
but only one part of the total dry-mass trade.

The model removes propulsion battery demand, retains compression and eclipse
batteries, and sizes arrays for peak thrust as well as later processing/recharge.
Cryogenic processing pauses during thrust; its plant must handle the same batch
in the remaining time. Area-dependent deployment feeds back into available
sunlight and burn altitude. The solid optimum retains only 82 seconds of sunlit
non-thrust processing and consequently uses eclipse processing/storage heavily.
This tight schedule is a sensitivity, not a robust operations margin.

Ammonia regeneration is sunlit-only. Compressing its operating window makes its
instantaneous heat rejection large. An optional warm-side buffer permits rejection
through the whole deployed coast; it is charged at the existing, unqualified
200 kJ/kg capability plus packing. It is distinct from the cold ammonia inventory
and from the existing pass/thruster heat buffer.

| Cooling | Extra rejection buffer, tonnes | Remaining sunlit processing, min | Physical solar area, m² |
|---|---:|---:|---:|
| Ammonia 200–300 K | 1,376 | 9.0 | 4,610,955 |
| Ammonia 280–340 K | 825 | 6.2 | 4,330,367 |

Thus direct rejection alone gives 526/471 days for cold/warm ammonia; adding the
costed buffer gives 431/394 days. Neither clearly beats its corresponding
Isp-optimized battery case under current assumptions. Hybrid solar/battery thrust,
flexible power schedules and longer battery-fed burns have not been searched.

## Verification and reproducibility

Mass sums, solar energy sufficiency, product/propellant accounting, thermal buffer
capacity, deployment and packing screens are checked. Arc quadrature changes
impulse by less than one part per million between 301 and 1,201 samples.
An independent Newtonian finite-burn integration with a perigee drag impulse
restores perigee/apogee to within 4 mm for these reference cases. This validates
the geometry calculation only: it uses constant mass and an impulsive drag event,
not the distributed atmospheric encounter, aerodynamic lift or flight controls.

Capture/thermal duty and compressor pass hardware are frozen from the existing
1,601-sample references. Coast plant mass uses a modular throughput scaling;
no new detailed plant layout or propellant-specific throttle map is claimed.
Efficiency stays 60%. Sun orientation is fixed. No circular-apogee delivery is charged.

```sh
.venv/bin/python -m atmo_scoops.studies.reboost_solar
.venv/bin/python -m atmo_scoops.studies.reboost_validation
.venv/bin/python -m atmo_scoops.studies.reboost_report
```

Inputs are the three ammonia-integrated reference results named in each best-case
JSON's `source_result`; exact settings, arc states, mass breakdowns and duty budgets
are in `results/reboost/*_direct_*_best.json`. Search summaries are `solar_optima.json`
and `solar_screen.json`; independent checks are `verification.json` in that folder.
[Equations and primary references](../../modeling/propulsion/REBOOST_INVESTIGATIONS.md).
