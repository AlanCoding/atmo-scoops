# Combined cooler / stage geometry review

Source trajectory: `results/transient/staggered/thermal_equivalence/seed_gate/baseline_refined.json.gz`. This report does not certify optimizer termination; see the associated termination record. The prior published reference remains frozen.

| Quantity | Frozen case 72 | This candidate |
|---|---:|---:|
| Dry mass, tonnes | 13249.965 | 13263.161 |
| Useful liquid per cycle, kg | 3509.134 | 3512.466 |
| Operating-orbit payoff, days | 278.019 | 278.031 |

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

## All five racks

Start/end are cycle endpoints. Pre-deployment is immediately before the modeled vent-and-release event (pump stop + vent duration for 1–4; plant stop + vent duration for 5). Peak temperature is included because endpoint closure alone hides the thermal excursion.

| Rack | Material | Metal t | Core length m | Installed length m | Physical gap mm | Thermal gap mm | Sheet mm | Start K | Peak K | Pre-deploy K | End K |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | sic | 382.8281 | 3.5857 | 3.6007 | 29.0640 | 6.1897 | 1.4351 | 300.0061 | 865.8329 | 865.8329 | 300.0061 |
| 2 | aluminum | 26.6290 | 0.2223 | 0.2373 | 14.8874 | 2.9740 | 0.9971 | 300.0221 | 491.5477 | 491.5476 | 300.0214 |
| 3 | aluminum | 12.9070 | 0.1296 | 0.1446 | 17.2647 | 3.6034 | 0.9503 | 300.0003 | 447.7898 | 447.7892 | 299.9998 |
| 4 | aluminum | 11.8002 | 0.0931 | 0.1081 | 17.8830 | 3.5170 | 1.2717 | 299.9999 | 406.7876 | 406.7695 | 299.9999 |
| 5 | aluminum | 20.5666 | 0.1604 | 0.1754 | 16.9939 | 3.3306 | 1.2239 | 299.9997 | 353.1794 | 321.3300 | 299.9995 |

## Hydraulic applicability screen

Only times above 10% of each stage’s peak flow are included. These ratios are diagnostics; the power-only surrogate does not enforce hydraulic feasibility.

| Volume | Inlet Pa at peak flow | Drop Pa at peak flow | Drop/inlet at peak flow | Max drop/inlet (>10% peak flow) | Throughput fraction with drop > inlet | Max Re | Max Kn |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 414.822 | 74.579 | 0.1798 | 2.3008 | 7.42% | 93.69 | 0.0194 |
| 2 | 862.066 | 3.078 | 0.0036 | 0.0334 | 0.09% | 78.66 | 0.0084 |
| 3 | 2825.502 | 0.451 | 0.0002 | 0.0012 | 0.00% | 93.92 | 0.0020 |
| 4 | 6565.305 | 0.144 | 0.0000 | 0.0001 | 0.00% | 102.16 | 0.0007 |
| 5 | 4474.610 | 0.030 | 0.0000 | 0.0008 | 0.00% | 14.75 | 0.0036 |

## Validation and limits

```json
{
  "feasible": true,
  "audits": {
    "species_kg": 2.2282620193436742e-11,
    "energy_MJ": 2.270098775625229e-09,
    "min_gas_kg": -6.479281378134073e-10,
    "forward_integrations": 1,
    "rhs_evaluations": 73733
  },
  "closure": {
    "rack_enthalpy_J_kg": [
      -0.002255325365695171,
      -0.5989608911331743,
      -0.3952258028584765,
      -0.0600003427680349,
      -0.17018277411989402
    ],
    "battery_MJ": -34.687327530933544,
    "warm_MJ": 8.930251910584047,
    "gas_kg": 0.0,
    "gas_MJ": 0.0,
    "rotor_MJ": 1.015621029919916e-12,
    "thrust_relative": 5.417888360170764e-14,
    "reserve_deficit_kg": [
      0.0,
      0.0,
      0.0
    ],
    "gas_reserve_species_kg": [
      -4.547473508864641e-13,
      0.0,
      4.263256414560601e-14
    ],
    "gas_reserve_MJ": 0.44766890342989996
  },
  "margins": {
    "reserve_kg": 45.66206046504963,
    "material_K": 58.45234418238766,
    "pressure_Pa": 1113.39939226853,
    "warm_K": 12.450039169507136,
    "SOC": 0.013818269734979738,
    "liquid_kg": -3.913385498272096e-22,
    "tank_m3": 15.965796560097484,
    "Bi": 0.09945289455775697,
    "gas_K": 1058.4964400711397,
    "unmet_MJ": 1.0,
    "product_kg": 3512.466189619208,
    "periodic": 0.5523310965701,
    "gas_buffer_Pa": 466261.30556636094,
    "gas_buffer_K": 55.139420381644356,
    "gas_buffer_inventory_kg": 11.784224952230478,
    "plate_Re": 897.8415058559741
  }
}
```

Thermal-spacing equivalence and edge-loss coefficients are provisional. Five lumped gas/solid states do not resolve individual rows. Pressure loss is still charged to compressor electricity, not solved as a hydraulic pressure field. Large loss/pressure ratios and slip-flow regimes require separate validation. This is operating-orbit payoff, not delivered circular-apogee payoff.
