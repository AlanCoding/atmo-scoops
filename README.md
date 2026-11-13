# Atmospheric Scoop Divers

**A reusable orbital factory, fed by Earth's atmosphere.**

The concept was first published on AlanCoding's
[Atmospheric Scoop Divers page](https://alancoding.github.io/concepts/atmospheric-scoop-divers/).
This repository develops its engineering description and numerical analysis.

The concept is a spacecraft that collects air during repeated 7–8 km/s
atmospheric passes, transfers it into rear tanks, and makes useful cryogenic
liquids during the coast. A solid metal rack absorbs entry heat. Once clear of
the atmosphere, the craft extends that same metal through its mouth to radiate
the heat to space, unfolds solar arrays, and runs its separation and
liquefaction plant. Recovered oxygen supplies electric propulsion for reboost.

![Atmospheric scoop diver during collection and coast](docs/images/spacecraft_overview.svg)

**Mouth → shock/diffuser → solid precooling rack → compressor wall → rear gas
storage → coast liquefaction.**

The ambition is sustained production from repeated passes, with the spacecraft
and its thermal inventory reused each orbit. This package asks what that takes:
physical dimensions, compressor duty, heat storage, deployed areas, power,
hardware mass and net production—all connected by explicit balances.

Start with the [illustrated design description](docs/DESIGN.md). The open-mouth
layout above is the concept being developed; the drawings specify component
roles, not a qualified layout or scale. A pressure-retaining closure and cold
nitrogen injection are the next [planned architecture comparisons](docs/DESIGN_STUDIES_PLAN.md).
Neither comparison has selected a winner.

The [atmospheric-column derivation](analysis/primary/ATMOSPHERIC_COLUMN.md)
explains a central result: hundreds of kilometres of swept atmosphere still
require kilometres of unpumped chamber at the assumed cooled-gas pressure.
Precooling increases density; compressors move that gas into storage whose
pressure is supported by a vessel. Diving deeper increases both available
pressure and admitted mass, so density alone does not solve the volume problem.

The mission metric is time to deliver one dry spacecraft mass of useful
cryogenic liquids into a **circular orbit at apogee**. The implemented metric is
currently dry mass divided by net daily production in the operating orbit.
Circular delivery/return is an open item, so those two metrics remain distinct.
Dry mass has no imposed ceiling. The numerical results are conditional on the
stated component capabilities and flow assumptions; this is a living engineering
model and design specification.

## Analysis areas

| Area | Purpose | Entry point |
|---|---|---|
| Primary numerical model | Fast cycle inventory, heat, power, hardware mass and constraints | [Model](analysis/primary/MODEL.md), [inputs](analysis/primary/PARAMETERS.md), `atmo_scoops/system.py` |
| Design optimization | Search independent coordinates using the primary model | [Search definition and results](analysis/optimization/RESULTS.md), `atmo_scoops/optimization/` |
| Detailed fluid analysis | Evaluate selected geometries; resolve shocks, cooling, capture and leakage | [Fluid study specification](analysis/fluid/README.md); solver integration pending |
| Flight stability | Fluid forces/moments coupled to attitude, mass distribution and flexibility | [Stability study specification](analysis/stability/README.md); solver integration pending |

Detailed fluid and stability simulations are **outside the optimization loop**.
They can supply reviewed coefficient tables or reduced constraints back to the
primary model. The [improvement list](docs/MODEL_IMPROVEMENTS.md) tracks these
interfaces and missing physics. [Sources](docs/SOURCES.md) separate evidence from
hardware-development targets.

## Calculate a cycle

Use the project-local virtual environment:

```sh
.venv/bin/python -m atmo_scoops --config configs/reference.json
.venv/bin/python -m atmo_scoops --config configs/reference.json --front-depth 100 --rear-depth 25 --output results/short_front.json
.venv/bin/python -m atmo_scoops --config configs/reference.json --no-mouth-closure --output results/open_mouth.json
.venv/bin/python -m atmo_scoops --write-config configs/my_design.json
```

Lengths are physical metres, including rear tank heads; temperatures are kelvin.
Configurations separate `design`, `hardware`, `performance`, `process` and
`scenario`. All resolved inputs, component masses, three deployed areas,
production and constraint margins are saved. Unknown input names are rejected.
The 250 m front in `configs/reference.json` is a comparison coordinate, not a
recommended dimension. Search candidates have separate input files.

```python
from dataclasses import replace
from atmo_scoops.system import Design, simulate

result = simulate(replace(Design(), front_depth_m=100, mouth_closure=False))
print(result["outputs"]["total_dry_kg"])
print(result["outputs"]["operating_mass_payoff_days"])
print(result["constraints"])
```

`simulate` writes no files. Passing its implemented screens does not validate
omitted shock, heat-transfer, aerodynamic or structural constraints.

## Run analysis

```sh
.venv/bin/python -m atmo_scoops.optimization.search --mode free_orbit --iterations 120 --seeds 11 29
.venv/bin/python -m atmo_scoops --config results/optimization/free_orbit_config.json --samples 3201 --output results/optimization/replayed_system.json
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.mouth_closure
```

The [closure comparison](analysis/primary/MOUTH_CLOSURE.md) holds design and
capability inputs fixed, recalculates dependent hardware, and includes leakage,
pump-floor and door-mass sensitivities. It is not an optimization of the open
variant. Continuous searches retain the configured mouth choice; compare
architecture options in separate runs.

Reproduce the column derivation (no optimization):

```sh
.venv/bin/python -m atmo_scoops.studies.column_physics
```

Other reproducible primary-model studies:

```sh
.venv/bin/python -m atmo_scoops.physical_cycle
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.physical
.venv/bin/python -m atmo_scoops --config configs/reference.json --sweep-precooling 650 700 750 800 900 1000 1100 --output results/precooling_trade.json
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.precooling
```

Reports: [physical depth and mass](analysis/primary/PHYSICAL_CYCLE.md),
[precooling trade](analysis/primary/PRECOOLING_TRADE.md).
Numerical output belongs in `results/`; generated figures belong in `figures/`.

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m atmo_scoops.audit
```
