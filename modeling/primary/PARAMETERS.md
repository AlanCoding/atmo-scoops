# Independent inputs

`configs/reference.json` is a complete editable input file. It is a comparison
coordinate, not an optimum; notably the 250 m front has no selection claim.
`system.inputs_from_dict` rejects unknown fields rather than silently ignoring
them. All resolved inputs are returned with the outputs.

| Section | Independent inputs | Derived quantities |
|---|---|---|
| `compressor` thermodynamics | Real-gas/legacy mode, block counts, isentropic efficiency, interstage cooling target, minimum train ratio and maximum head ratio | HEOS mixture states, work, outlet temperatures, head-limited recovery |
| `compressor` hardware | Axial velocity, module diameter limit, hub ratio, blade geometry, tip speed/loading, material/allowable stress, casing/disk gauges, accessory/mass factors, motor specific power, spin-up time | Modules, rows, areas, bank lengths, component masses, spin energy and peak power |
| `design` geometry | Front/rear physical depths, mouth/front/rear diameters, machinery depth, radial clearance | Volumes, shell/tank dimensions, pressure, structural allowances |
| `design` orbit | Perigee/apogee, Isp, thrust-burst duration | Encounter, coast/sunlight, impulse, propellant, power |
| `design` thermal | Dry compressor-stream temperature, metal cold temperature, gas/metal approach, sheet thickness, warm radiator temperature | Rack endpoint/capacity, heat, mass, deployed areas |
| `design` compression | Intermediate pressure; nominal pressure-sizing factor or explicit suction input | Compression duties, installed banks, rear pressure |
| `controls` | Installed suction multiplier, commanded cutoff, outbound timeout | Actual pressure/history, admission, leakage, stop time |
| `mixing` design | LN2 ratio and thermal path | Mixed temperature or rack heat, circulation/replacement, compressor and cryogenic throughput |
| `mixing` capability | Tank/injector mass allowances, injection pressure, liquid density, pump efficiency/specific power | Injection hardware/work and startup inventory |
| `hardware` | Component mass, stress, packing/access and margin targets | All installed masses, hydraulic access screen |
| `performance` | Compressor/motor/propulsion efficiencies, battery/solar properties, deployment times, material radiation properties | Electricity, peak power, storage, deployed coast |
| `process` | Refrigerator fraction of Carnot, exchanger approaches/conductance, radiator properties | Cold duty, refrigeration work, exchanger/radiator mass |
| `scenario` | Atmosphere choice, additional captured-air impulse multiplier | Environmental loading and propulsion scenario |
| `flow` | Support/discharge/effective-area factors, ultimate pressure, compression ceiling, idle fraction, support lag, rejected-air impulse fraction | Conditional intake and net pumping |

Only one capacity specification should be optimized: normally hold the nominal
pressure-sizing factor fixed and search the suction multiplier. Multiplying an
explicit suction input by a free scale is redundant. The nominal size includes
the mixed stream's mass and gas properties when LN2 is enabled.

The `design.compressor_inlet_K` field is the dry-stream comparison temperature.
For `mixing.thermal_path="fixed_rack"`, actual mixed compressor temperature is
solved and returned as `outputs.compressor_inlet_K`. For `fixed_inlet`, the
specified temperature is also the actual mixed inlet, with reduced rack heat.
The mixed endpoint must stay above the warm receiver in this implementation.
Ratio zero exactly recovers the unmixed model and adds no injection hardware.

The cutoff is a control, not the hardware limit; it must exceed the larger of
ultimate floor and intermediate pressure / compression ceiling. A timeout is
not an acceptable surrogate for reaching cutoff.

Dry mass, array/radiator/sheet areas, battery mass, pressure and production are
outputs. Dry mass is unbounded. Working fluids and startup LN2 are separate.
Capabilities are fixed within design searches and varied only as explicit
scenarios. A constant mass/efficiency coefficient does not establish an actual
compressor design, film-cooling capability or material lifetime.

In default real-gas mode, the old `design.intermediate_Pa`,
`performance.isothermal_efficiency`, `hardware.compressor_kg_per_m3_s` and
`hardware.compressor_electric_W_kg` do not set compressor work or mass. They
remain legacy reproduction inputs. The intermediate-pressure search coordinate
is omitted by the real-gas optimizer CLI. `compressor.thermodynamic_samples`
controls separate property quadrature and must be convergence-checked.

The reference machinery allowance is now 100 m to accommodate resolved banks;
this is a comparison allowance, not a selected optimum. Actual bank lengths and
module-face packing are reported and screened. Material life, low-Re efficiency,
interstage heat transfer and maps still require validation.
