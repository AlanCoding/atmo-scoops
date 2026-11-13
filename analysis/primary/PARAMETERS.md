# Independent variables and derived quantities

`configs/reference.json` lists the complete editable inputs. `system.Design`
contains design choices. Hardware/performance/process capabilities and scenario
assumptions are separate sections. Defaults are comparison values, not measured
capabilities or an optimized design. In particular, **250 m front depth has no
optimization justification**.

## Design coordinates

| Group | Independent choices | Values derived from them |
|---|---|---|
| Geometry | Physical front/rear depths; mouth/front/rear diameters; machinery depth and radial clearance | Free volumes, rear head geometry, shell dimensions, pressure history, structure allowances |
| Orbit and timing | Perigee/apogee; opening fraction of peak ram | Encounter history, collection duration, orbit period and sunlight; installed closure operates at perigee |
| Rack precooling | Compressor inlet gas temperature; starting metal temperature; positive gas/metal approach | Metal hot endpoint, heat per kg, absorber mass, sheet area, ideal cooldown |
| Rack construction | Sheet thickness | Physical area for the required metal mass; deployment mass and radiation rate |
| Front pressure/pumping | Pressure target; optional explicit aggregate suction capacity | Pressure/inventory history, required compressor duty and mass |
| Mouth / residual recovery | Boolean mouth closure; maximum duration; sealed residual fraction | Recovery suction, outbound capture/leakage, stop time, door mass, coast start |
| Compression staging | Intermediate pressure | Hot/warm pressure ratios and duties |
| Warm thermal system | Radiator temperature | Receiver temperature using fixed reject approach, refrigerator work, radiator area |
| Propulsion | Isp and impulse-equivalent burst duration | Oxygen consumption, electrical work, peak power and installed hardware |

These coordinates have feasibility relationships; being independent inputs does
not make every combination permissible. For example, metal cold < gas inlet -
approach <= material limit. More realistic exchanger and pump constraints must
replace simple temperature/flow screens as those designs develop.

There are two distinct pumping modes:

- `pump_suction_m3_s: null`: automatic sizing from pressure target and gas state.
  Pump capacity is an output; do not optimize it a second time.
- A numeric `pump_suction_m3_s`: capacity is a design choice. The pressure target
  is then an admissibility constraint rather than a second way to set capacity.

Rear pressure, gas mass, compressor power/mass, metal mass, solar area, radiator
area, battery mass and total dry mass are **outputs**, not independent knobs.
The geometry needed to obtain a specified gas endpoint is not yet solved, so
endpoint temperature remains a requirement coordinate for this stage of study.

## Capability assumptions: vary as scenarios, not unconstrained design knobs

- `hardware`: compressor kg/(m³/s) and W/kg; propulsion/distribution kg/kW;
  shell/TPS mass per area; tank material, minimum gauge and supports; deployment,
  ancillary systems and mass margin; separate mouth closure and compressor bulkhead kg/m²; compressor clear area and discharge factor.
- `performance`: compressor/motor/propulsion efficiencies; solar and battery
  specific capabilities; metal density/emissivity; thermal-buffer capacity;
  deployment/retraction durations; compressor minimum inlet pressure; auxiliary load and electrical losses.
- `process`: refrigeration fraction of Carnot, heat-exchanger approaches and
  conductance, cold-package mass, warm-radiator optical properties and mass.
- `scenario`: atmospheric profile, additional drag impulse allowance, and open-mouth
  support-pressure/discharge coefficients. Actual
  exterior drag cannot be optimized away; it ultimately needs a geometry model.

The example uses 30 kg/(m³/s) for a complete compressor bank. This is a declared
R&D target, with a broad sensitivity sweep, not a qualified machine. Neither a
rotor speed nor a compressor module count is selected.

## Fixed assumptions and unresolved design variables

The current implementation fixes equatorial prograde flight, perigee-noon
orientation, full geometric inbound intake, perigee timing for an installed door, uniform
compartment temperatures, a molecular-gas/iron-property proxy and the compressor
train topology. These are not freely optimized internally.

Throat shape, shock position, exchanger passage spacing and conductance, pump
mechanism/map/module count, hull shape/stability and deployable arrangements
remain real design variables that this model does not yet resolve. The program
explicitly reports those missing constraints rather than assigning a fictitious
optimum. Dry mass has no ceiling. Delivered-mass payoff still requires circular
apogee delivery and return accounting.

## Implemented search

[Optimization results](../optimization/RESULTS.md) lists the exact bounds and resulting values.
`atmo_scoops/optimization/search.py` searches 19 design coordinates, or 17 with perigee/apogee held
fixed. Machinery depth and radial clearance remain layout allowances; pumping
uses automatic sizing. Hardware, performance, process and atmosphere parameters
stay fixed. Additional search-family constraints are front bore >= mouth and
overall axial allowance <=520 m. A separate run imposes a 10% oxygen reserve.
These bounds and constraints are declared comparisons, not qualified limits.

## Mouth option controls

- `design.mouth_closure` (default true) is a discrete architecture choice. Run
  separate continuous optimizations for each option; do not interpolate it.
- Sealed recovery uses `front_residual_fraction` to size suction for `recovery_s`;
  it stops early if the inlet pressure reaches the capability floor.
- Open recovery keeps collection suction running. `front_residual_fraction`
  has no effect; `recovery_s` is a timeout, not a target run duration. Pumping
  stops at `performance.compressor_min_inlet_Pa` (default 0.1 Pa). This floor is
  a development assumption pending a pump map. A timeout above it fails a screen.
- `hardware.mouth_closure_kg_m2` (default 10) covers the door, supports, seals and
  actuators per mouth area; it is not a qualified estimate. The independent
  `compressor_bulkhead_kg_m2` (10) applies to front-chamber cross-section in both
  variants. A no-door entry shield is not implicitly included.
- `scenario.open_mouth_support_over_ram` (1) and
  `open_mouth_discharge_coefficient` (0.8) describe the provisional outbound
  boundary. They are calibration/sensitivity inputs, not optimization rewards.
  Inbound capture still uses the prescribed geometric model. Compare weaker
  support before interpreting the no-door results.
