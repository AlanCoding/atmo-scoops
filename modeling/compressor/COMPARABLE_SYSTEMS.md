# Comparable compressor hardware: initial evidence

**Status: initial manufacturer data, not a mass fit.** Values below are nominal
catalog entries at their specified conditions, not simultaneously achievable
scoop operating points. Reviewed 2026-11-14. The annotated thermodynamic/map
references in [README](README.md) do not themselves establish hardware mass.

| Manufacturer/model | Mechanism | Nominal inlet pumping speed | Reported mass | Derived mass / nominal Q |
|---|---|---:|---:|---:|
| Leybold RUVAC WH 700, 50 Hz | Roots booster | 710 m³/h = 0.197 m³/s | 120 kg | 608 kg/(m³/s) |
| Leybold RUVAC WH 2500, 50 Hz | Roots booster | 2,500 m³/h = 0.694 m³/s | 430 kg | 619 kg/(m³/s) |
| Leybold RUVAC WH 7000, 50 Hz | Roots booster | 7,000 m³/h = 1.944 m³/s | 650 kg | 334 kg/(m³/s) |
| Pfeiffer HiPace 2300, leaflet variant | Turbomolecular pump | 1,900 L/s N₂ = 1.9 m³/s | approx. 36.6 kg | 19.3 kg/(m³/s) |

[Leybold WH/WHU brochure](https://www.leybold.com/content/dam/brands/leybold/downloads/brochures/product-brochures-fore-vacuum/mechanical-booster-pumps/3611019802_RUVAC%20WH_web.pdf),
PDF p. 8, supplies speeds and masses with standard feet. Backing equipment is
separate. Actual system pumping speed depends on pressure and backing pump;
the brochure provides differential-pressure limits and system curves. Establishes
industrial Roots hardware mass anchors, not hot-gas spacecraft capability.

[Pfeiffer HiPace leaflet](https://www.pfeiffer-vacuum.com/us/assets/112395/1/Product%20Leaflet%20HiPace%201800_2300%20Global%20EN.pdf),
PDF pp. 2–3, gives the quoted nitrogen speed, approximate mass, four-minute
run-up, nitrogen forevacuum limit 1.8 hPa, and separately specified throughput.
The rated nitrogen throughput at final rotational speed is 28 hPa L/s =
2.8 Pa m³/s. At 26.8 Pa, multiplying the nominal 1.9 m³/s by pressure would
give 50.9 Pa m³/s: those nominal numbers cannot be applied together at our
first-bank pressure. Establishes a lightweight molecular-pump reference and a
throughput warning; neither its headline compression ratio nor mass/Q validates
a scoop stage. Confirm configuration/accessory boundaries in a selected manual.

The existing 30 kg/(m³/s) target lies between these nominal ratios, but that
does **not** validate it: the operating regimes and hardware boundaries differ.
Do not average these values or multiply them by scoop Q to declare a mass bound.

## Required next comparisons

- Axial compressor/fan stages with disclosed rotor/casing mass, flow, speed,
  pressure rise and efficiency; seek multiple independent test programs.
- Centrifugal stages and complete industrial/process trains with separable
  compressor and motor/package masses and documented inlet density.
- Vacuum boosters with measured low-pressure throughput/efficiency and thermal
  limits near candidate bank states, rather than nominal displacement alone.
- Coast compressor packages and cryogenic-feed duties; distinguish continuous
  operation from dive pulse machinery and account for backing requirements.

Extract full operating points and build the mass model using
[RESEARCH_REQUIREMENTS.md](RESEARCH_REQUIREMENTS.md). Missing efficiency,
temperature and package details are unresolved evidence, not implicit defaults.

## Centrifugal package comparisons added in the compressor refinement

[AERZEN G5plus/G6 manufacturer table](https://www.aerzen.com/product/aerzen-turbo-blower-generation-5plus)
reports the following package data (metric table; flow converted to suction
conditions of 1.0 bar, 20°C, dry gas). These are catalog envelope entries; do
not infer efficiency by assuming every maximum is one simultaneous operating point.

| Model | Pressure difference | Suction flow | Motor rating | Package mass | Mass / Q |
|---|---:|---:|---:|---:|---:|
| AT 100-0.6 S G5plus | 600 mbar | 5,100 m³/h | 85 kW | 750 kg | 529 kg/(m³/s) |
| AT 150-0.6 S G5plus | 600 mbar | 7,800 m³/h | 120 kW | 870 kg | 402 kg/(m³/s) |
| AT 200-0.8 S G5plus | 800 mbar | 8,400 m³/h | 165 kW | 870 kg | 373 kg/(m³/s) |

These establish complete terrestrial centrifugal-package mass/flow scales.
They do not identify bare rotor mass, low-density efficiency or hot-gas lifetime.
Packaging, motor, density and pressure differential prevent direct transfer of
these ratios to a lightweight vacuum-facing axial bank. The Roots, centrifugal
and molecular examples collectively show why nominal Q alone is inadequate.

## Axial hardware weight method

[NASA CR-168049, WATE-S](https://ntrs.nasa.gov/api/citations/19830008072/downloads/19830008072.pdf)
provides stagewise blade, disk, case and connecting-hardware accounting and
comparison with four small aircraft engines. See printed pp. 8–16 and 52–53.
Its engine-validation accuracy must not be assigned to our different model.

The scanned printed p.14 equation (5) was visually checked: total row blade
volume is written `V_B = K h_B³ / AR²`; do not multiply this total by blade
count a second time. The screening implementation uses K=0.12 and the p.16
2.54 mm equivalent case thickness as explicit reference assumptions. Its disk
stress screen, constant-annulus bank geometry, electric motors, module packing,
and envelope sizing are our simplifications, not a complete WATE-S port.

This reference supplies the structural-estimation method missing from nominal
pump mass/Q comparisons. It does not establish our low-Reynolds-number maps,
high-temperature material allowables or the optimum number of parallel modules.
