# Combined cooler / stage geometry review

Source trajectory: `results/transient/staggered/checkpoint_a/evacuated_start/baseline_refined.json.gz`. This report does not certify optimizer termination; see the associated termination record. The prior published reference remains frozen.

| Quantity | Frozen case 72 | This candidate |
|---|---:|---:|
| Dry mass, tonnes | 13249.965 | 13263.161 |
| Useful liquid per cycle, kg | 3509.134 | 2308.807 |
| Operating-orbit payoff, days | 278.019 | 422.979 |

## Geometry

Coordinates are metres aft of the mouth. Head volumes remain explicit. The first rack has 10 m clear space ahead. Each compressor is followed by 1 m hatch equipment.

| Stage | Gas region | Rack region | Compressor region | Hatch region | Metal, t | Gap, mm | Thickness, mm |
|---|---|---|---|---|---:|---:|---:|
| 1 | 0.000–13.601 | 10.000–13.601 | 13.601–18.719 | 18.719–19.719 | 382.828 | 29.064 | 1.435 |
| 2 | 19.719–22.957 | 21.219–21.457 | 22.957–29.534 | 29.534–30.534 | 26.629 | 14.887 | 0.997 |
| 3 | 30.534–33.679 | 32.034–32.179 | 33.679–38.630 | 38.630–39.630 | 12.907 | 17.265 | 0.950 |
| 4 | 39.630–42.738 | 41.130–41.238 | 42.738–47.109 | 47.109–48.109 | 11.800 | 17.883 | 1.272 |

Receiver starts at 48.109 m and ends at 317.000 m. Its other-equipment displacement is 36295.7 m³. The separate last-125-m feed compartment is the next checkpoint; it is not in this simulation.

## Mass

| Component | tonnes |
|---|---:|
| racks | 454.731 |
| rack_mechanisms | 107.686 |
| dive_compressors | 921.735 |
| coast_compressors | 47.708 |
| refrigerator | 140.245 |
| external_exchangers | 2.250 |
| separator | 2.495 |
| solar | 3073.912 |
| battery | 2227.967 |
| bus | 827.372 |
| thrusters | 1517.556 |
| warm_store | 521.143 |
| warm_radiator | 336.241 |
| liquid_tanks | 6.000 |
| auxiliary | 5.000 |
| gas_reserve_system | 51.913 |
| pressure_vessels | 240.297 |
| hull | 126.278 |
| margin | 2652.632 |

## Hydraulic applicability screen

Only times above 10% of each stage’s peak flow are included. These ratios are diagnostics; the power-only surrogate does not enforce hydraulic feasibility.

| Volume | Max loss / absolute pressure | Max Re | Max Kn |
|---|---:|---:|---:|
| 1 | 2.874 | 56.74 | 0.0252 |
| 2 | 0.044 | 48.37 | 0.0113 |
| 3 | 0.002 | 60.78 | 0.0026 |
| 4 | 0.000 | 67.48 | 0.0010 |
| 5 | 0.001 | 14.25 | 0.0038 |

## Validation and limits

```json
{
  "feasible": true,
  "audits": {
    "species_kg": 6.730260793119669e-11,
    "energy_MJ": 3.841705620288849e-09,
    "min_gas_kg": -9.978823634041085e-11,
    "forward_integrations": 1,
    "rhs_evaluations": 73218
  },
  "closure": {
    "rack_enthalpy_J_kg": [
      -0.00041772815166041255,
      -0.7669309084740235,
      -0.3936467443272704,
      -0.0006146605592221022,
      -0.20639765546366107
    ],
    "battery_MJ": -8.607389617245644,
    "warm_MJ": 3.0560501203872263,
    "gas_kg": 0.0,
    "gas_MJ": 0.0,
    "rotor_MJ": 9.922357154600708e-13,
    "thrust_relative": -1.1879386363489175e-14,
    "reserve_deficit_kg": [
      0.0,
      0.0,
      0.0
    ],
    "gas_reserve_species_kg": [
      -9.094947017729282e-13,
      0.0,
      -3.055333763768431e-13
    ],
    "gas_reserve_MJ": 0.2980893899664352
  },
  "margins": {
    "reserve_kg": 30.014496077712845,
    "material_K": 33.61361224170355,
    "pressure_Pa": 1133.8473278851861,
    "warm_K": 12.405234588177052,
    "SOC": 0.013948141240429535,
    "liquid_kg": -5.6842430520352646e-21,
    "tank_m3": 17.348245302764415,
    "Bi": 0.09984942811835015,
    "gas_K": 754.1612066471318,
    "unmet_MJ": 1.0,
    "product_kg": 2308.807390593315,
    "periodic": 0.7019106100335648,
    "gas_buffer_Pa": 473302.19216526905,
    "gas_buffer_K": 55.202253255261496,
    "gas_buffer_inventory_kg": 11.784224952233348,
    "plate_Re": 932.520946412209
  }
}
```

Heat-transfer restart and edge-loss coefficients are provisional. Five lumped gas/solid states do not resolve individual rows. Pressure loss is still charged to compressor electricity, not solved as a hydraulic pressure field. Large loss/pressure ratios and slip-flow regimes require separate validation. This is operating-orbit payoff, not delivered circular-apogee payoff.
