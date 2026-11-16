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

Start with the [illustrated design description](docs/DESIGN.md). Completed
engineering decisions and their numerical evidence live in
[investigations/](investigations/README.md). The active program follows one open-inlet
architecture, with an optional incremental LN2-mixing parameter for analysis.
The drawings specify component roles, not a qualified layout or scale.

The [atmospheric-column derivation](modeling/primary/ATMOSPHERIC_COLUMN.md)
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

## The orbit is part of the machine

![Scoop orbit, atmospheric pass and coast timing](docs/images/orbital_cycle.svg)

The illustrated **100 × 2,000 km** comparison orbit takes **106.2 minutes**.
The Earth and orbit use the same distance scale; the low-altitude pass is enlarged
at right. The dashed circle is the circular delivery destination at apogee
altitude. Reaching apogee on the diving ellipse does not itself circularize the
product's orbit. The diagram's cutoff and deployment timings come from the
open-mouth control/capacity search at this geometry, not a final operating policy.

## Modeling and analysis

| Area | Purpose | Entry point |
|---|---|---|
| Subsystem modeling research | Comparable hardware, real-gas physics, heat transfer and validated replacements for numerical approximations | [Research index](modeling/README.md), [compressor](modeling/compressor/README.md), [metal coolers](modeling/metal_coolers/README.md) |
| Primary numerical model | Fast cycle inventory, heat, power, hardware mass and constraints | [Model](modeling/primary/MODEL.md), [inputs](modeling/primary/PARAMETERS.md), `atmo_scoops/system.py` |
| Design optimization | Search independent coordinates using the primary model | [Search definition and results](modeling/optimization/RESULTS.md), `atmo_scoops/optimization/` |
| Detailed fluid analysis | Evaluate selected geometries; resolve shocks, cooling, capture and leakage | [Fluid study specification](modeling/fluid/README.md); solver integration pending |
| Flight stability | Fluid forces/moments coupled to attitude, mass distribution and flexibility | [Stability study specification](modeling/stability/FLIGHT_STUDY.md); solver integration pending |

Detailed fluid and stability simulations are **outside the optimization loop**.
They can supply reviewed coefficient tables or reduced constraints back to the
primary model. The [improvement list](docs/MODEL_IMPROVEMENTS.md) tracks these
interfaces and missing physics. [Sources](docs/SOURCES.md) separate evidence from
hardware-development targets.

The [compressor refinement](modeling/compressor/RESULTS.md) replaces isothermal
work and fixed volume-flow mass coefficients with real-fluid compression states
and an explicit hardware buildup. Paired candidate cases give **520–556 days**
of operating-orbit mass payoff under the two tested hardware assumptions;
low-density compressor efficiency and mass remain unvalidated.

## Calculate a cycle

Use the project-local virtual environment:

```sh
.venv/bin/python -m atmo_scoops --config configs/reference.json
.venv/bin/python -m atmo_scoops --config configs/reference.json --front-depth 100 --rear-depth 25 --output results/short_front.json
.venv/bin/python -m atmo_scoops --mixing-ratio 0.1 --mixing-path fixed_rack
.venv/bin/python -m atmo_scoops --write-config configs/my_design.json
```

Lengths are physical metres, including rear tank heads; temperatures are kelvin.
Configurations separate geometry, hardware/performance/process capabilities,
atmosphere, inlet capabilities, operating controls and mixing. Unknown input
names are rejected. The 250 m reference front is a comparison coordinate,
not a selected dimension.

```python
from dataclasses import replace
from atmo_scoops.system import Design, simulate
from atmo_scoops.mixing import Mixing

result = simulate(replace(Design(), front_depth_m=100),
                  mixing=Mixing(ratio=0.1, thermal_path="fixed_rack"))
print(result["outputs"]["operating_mass_payoff_days"])
print(result["outputs"]["mixing"])
print(result["constraints"])
```

The continuous inlet computes admission, reverse leakage and pump cutoff on
both legs. Useful pump speed declines toward its ultimate pressure. Mixing
balances enthalpy and reserves coolant for the next pass before counting new
product. `simulate` writes no files; its output records exact inputs, component
masses, deployed areas, production and constraint margins.

The updated [altitude sensitivity](investigations/altitude_sensitivity/ANALYSIS.md)
compares 50–150 km perigees with fixed geometry and resized equipment.

## Reproduce analyses

```sh
.venv/bin/python -m atmo_scoops.studies.incremental_mixing --workers 4
.venv/bin/python -m atmo_scoops.studies.incremental_mixing --sensitivity --workers 4
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.mixing_report
.venv/bin/python -m atmo_scoops.studies.column_physics
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.orbital_diagram
.venv/bin/python -m atmo_scoops.studies.current_cycle
.venv/bin/python -m atmo_scoops.studies.compressor_refinement
.venv/bin/python -m atmo_scoops.studies.altitude_sensitivity
```

The [incremental mixing conclusion](investigations/incremental_mixing/ANALYSIS.md)
compares ratios with equal control freedom, counts coolant restoration and
reports sensitivity thresholds. Broader geometry searches use the same active
model; [their definition](modeling/optimization/RESULTS.md) states current
coordinates and limits. No revised whole-vehicle optimum is claimed here.

Passing the numerical screens does not establish omitted shock, heat-transfer,
aerodynamic or structural performance. The original decision experiments are
preserved separately with frozen inputs/source so later model changes do not
silently rewrite their evidence.

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m atmo_scoops.audit
```
