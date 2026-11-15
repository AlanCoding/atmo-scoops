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
