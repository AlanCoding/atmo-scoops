# Combined cooler / stage geometry review

Source trajectory: `results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz`. This report does not certify optimizer termination; see the associated termination record. The prior published reference remains frozen.

| Quantity | Frozen case 72 | This candidate |
|---|---:|---:|
| Dry mass, tonnes | 13249.965 | 13249.477 |
| Useful liquid per cycle, kg | 3509.134 | 3538.125 |
| Operating-orbit payoff, days | 278.019 | 275.730 |

## Geometry

Coordinates are metres aft of the mouth. Head volumes remain explicit. The first rack has 10 m clear space ahead. Each compressor is followed by 1 m hatch equipment.

| Stage | Gas region | Rack region | Compressor region | Hatch region | Metal, t | Gap, mm | Thickness, mm |
|---|---|---|---|---|---:|---:|---:|
| 1 | 0.000–13.613 | 10.000–13.613 | 13.613–18.732 | 18.732–19.732 | 381.950 | 29.049 | 1.426 |
| 2 | 19.732–22.969 | 21.232–21.469 | 22.969–29.546 | 29.546–30.546 | 26.633 | 14.892 | 0.998 |
| 3 | 30.546–33.676 | 32.046–32.176 | 33.676–38.627 | 38.627–39.627 | 12.913 | 16.694 | 1.047 |
| 4 | 39.627–42.738 | 41.127–41.238 | 42.738–47.110 | 47.110–48.110 | 11.807 | 20.041 | 1.379 |

Receiver starts at 48.110 m and ends at 317.000 m. Its other-equipment displacement is 36277.9 m³. The separate last-125-m feed compartment is the next checkpoint; it is not in this simulation.

## Mass

| Component | tonnes |
|---|---:|
| racks | 453.880 |
| rack_mechanisms | 106.741 |
| dive_compressors | 921.760 |
| coast_compressors | 47.716 |
| refrigerator | 140.272 |
| external_exchangers | 2.250 |
| separator | 2.496 |
| solar | 3071.587 |
| battery | 2220.683 |
| bus | 827.372 |
| thrusters | 1518.257 |
| warm_store | 520.905 |
| warm_radiator | 336.178 |
| liquid_tanks | 6.000 |
| auxiliary | 5.000 |
| gas_reserve_system | 51.913 |
| pressure_vessels | 240.292 |
| hull | 126.278 |
| margin | 2649.895 |

## All five racks

Start/end are cycle endpoints. Pre-deployment is immediately before the modeled vent-and-release event (pump stop + vent duration for 1–4; plant stop + vent duration for 5). Peak temperature is included because endpoint closure alone hides the thermal excursion.

| Rack | Material | Metal t | Core length m | Installed length m | Physical gap mm | Thermal gap mm | Sheet mm | Start K | Peak K | Pre-deploy K | End K |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | sic | 381.9503 | 3.5981 | 3.6131 | 29.0487 | 6.1929 | 1.4257 | 300.0199 | 866.9440 | 866.9440 | 300.0199 |
| 2 | aluminum | 26.6326 | 0.2221 | 0.2371 | 14.8918 | 2.9741 | 0.9984 | 300.0489 | 491.5535 | 491.5535 | 300.0487 |
| 3 | aluminum | 12.9131 | 0.1146 | 0.1296 | 16.6939 | 3.3881 | 1.0472 | 300.0393 | 447.5925 | 447.5919 | 300.0362 |
| 4 | aluminum | 11.8071 | 0.0961 | 0.1111 | 20.0408 | 3.9760 | 1.3789 | 300.0331 | 405.8537 | 405.8356 | 300.0330 |
| 5 | aluminum | 20.5771 | 0.1639 | 0.1789 | 19.1123 | 3.7687 | 1.3458 | 302.6437 | 356.4098 | 324.3873 | 302.6421 |

## Hydraulic applicability screen

Maximum ratios, Re and Kn use times above 10% of each stage’s peak flow. The throughput fraction integrates the entire cycle. These ratios are diagnostics; the power-only surrogate does not enforce hydraulic feasibility.

| Volume | Inlet Pa at peak flow | Drop Pa at peak flow | Drop/inlet at peak flow | Max drop/inlet (>10% peak flow) | Throughput fraction with drop > inlet | Max Re | Max Kn |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 415.423 | 74.834 | 0.1801 | 2.3097 | 7.40% | 93.64 | 0.0194 |
| 2 | 864.400 | 3.066 | 0.0035 | 0.0335 | 0.09% | 78.69 | 0.0084 |
| 3 | 2835.347 | 0.439 | 0.0002 | 0.0011 | 0.00% | 91.30 | 0.0021 |
| 4 | 6665.584 | 0.131 | 0.0000 | 0.0001 | 0.00% | 112.98 | 0.0006 |
| 5 | 4526.675 | 0.024 | 0.0000 | 0.0006 | 0.00% | 16.30 | 0.0033 |

## Design intent and buildability

The search fixes the craft diameter, all five rack frontal areas at the full bore, four serial rows, compressor suction capacities, and the operating schedule. It optimizes effective thermal gaps, thicknesses, metal inventory and the existing power/thermal/propulsion capacities. Therefore a shallow downstream rack is partly imposed by the full-bore flow-area assumption; it is not proof that a broad thin plate assembly is the best buildable architecture.

A geometric repackaging screen below holds flow, inlet state, metal inventory, plate gaps and wetted area fixed. Using frontal-area fraction f makes core depth L/f and velocity u/f. In this surrogate both shear and row-entry drops then scale as 1/f². Heat conductance stays unchanged under the stipulated thermal-spacing law. This is **not a forward simulation, recommended final sizing, or new payoff claim**; ducts, supports, changed holdup, flow distribution and deployment need modeling.

| Rack | Illustrative active-area fraction | Equivalent diameter m | Repacked core depth m | Peak-flow drop/inlet at same state |
|---|---:|---:|---:|---:|
| 1 | 1.00 | 30.00 | 3.598 | 0.1801 |
| 2 | 0.25 | 15.00 | 0.888 | 0.0568 |
| 3 | 0.10 | 9.49 | 1.146 | 0.0155 |
| 4 | 0.10 | 9.49 | 0.961 | 0.0020 |
| 5 | 0.10 | 9.49 | 1.639 | 0.0005 |

The loss model is still a power surcharge, not a hydraulic flow limiter. Any non-negligible throughput with predicted drop above inlet pressure prevents treating the numerical optimum as a hydraulically established design. Candidate remedies are a pressure-aware compressor cutoff/control and/or additional spacing/row allocation freedom; neither is silently added to this controlled comparison.

## Validation and limits

```json
{
  "feasible": true,
  "audits": {
    "species_kg": 7.275957614183426e-11,
    "energy_MJ": 8.847564458847046e-09,
    "min_gas_kg": -2.3113892378691808e-11,
    "forward_integrations": 1,
    "rhs_evaluations": 73059
  },
  "closure": {
    "rack_enthalpy_J_kg": [
      -0.00027672850410453975,
      -0.14433855697279796,
      -2.825325368787162,
      -0.09854041303333361,
      -1.430591486103367
    ],
    "battery_MJ": -78.0539871242363,
    "warm_MJ": 17.490253903146368,
    "gas_kg": 0.0,
    "gas_MJ": 0.0,
    "rotor_MJ": 1.040550699282493e-12,
    "thrust_relative": 2.020605904817785e-14,
    "reserve_deficit_kg": [
      0.0,
      0.0,
      0.0
    ],
    "gas_reserve_species_kg": [
      -4.092726157978177e-12,
      2.9558577807620168e-12,
      1.9895196601282805e-13
    ],
    "gas_reserve_MJ": 0.5636987977220542
  },
  "margins": {
    "reserve_kg": 45.99562831373874,
    "material_K": 58.44648390796118,
    "pressure_Pa": 1110.836465425903,
    "warm_K": 12.118893012291153,
    "SOC": 0.007974428283005291,
    "liquid_kg": -1.0091091735807976e-20,
    "tank_m3": 15.936326129965419,
    "Bi": 0.09945659363392736,
    "gas_K": 1058.249787760717,
    "unmet_MJ": 1.0,
    "product_kg": 3538.125254902965,
    "periodic": 0.21946012875763699,
    "gas_buffer_Pa": 465483.6446376182,
    "gas_buffer_K": 54.735679984257274,
    "gas_buffer_inventory_kg": 12.122049368999074,
    "plate_Re": 887.0237661391168
  }
}
```

Thermal-spacing equivalence and edge-loss coefficients are provisional. Five lumped gas/solid states do not resolve individual rows. Pressure loss is still charged to compressor electricity, not solved as a hydraulic pressure field. Large loss/pressure ratios and slip-flow regimes require separate validation. This is operating-orbit payoff, not delivered circular-apogee payoff.
