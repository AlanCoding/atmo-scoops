# Valve-reserve constrained coordinates

The search has **46 independent scalar coordinates**. Values below come from `selected_config.json` in `results/transient/valve_restore/cobyla_scaled`.

| Coordinate | Lower bound | Selected / baseline | Upper bound |
|---|---:|---:|---:|
| `thermal_gap_m:0` | 0.0005 | 0.006165098 | 0.03 |
| `thermal_gap_m:1` | 0.0005 | 0.002974314 | 0.03 |
| `thermal_gap_m:2` | 0.0005 | 0.00338651 | 0.03 |
| `thermal_gap_m:3` | 0.0005 | 0.003964433 | 0.03 |
| `thermal_gap_m:4` | 0.0005 | 0.003760681 | 0.03 |
| `plate_thickness_m:0` | 0.0002 | 0.001431814 | 0.005 |
| `plate_thickness_m:1` | 0.0002 | 0.0009893193 | 0.005 |
| `plate_thickness_m:2` | 0.0002 | 0.001047309 | 0.005 |
| `plate_thickness_m:3` | 0.0002 | 0.001379406 | 0.005 |
| `plate_thickness_m:4` | 0.0002 | 0.001345447 | 0.005 |
| `solid_depth:0` | 0.08416653 | 0.1680457 | 0.3366661 |
| `solid_depth:1` | 0.006977296 | 0.01395421 | 0.02790918 |
| `solid_depth:2` | 0.003383016 | 0.006766751 | 0.01353207 |
| `solid_depth:3` | 0.003093252 | 0.006176928 | 0.01237301 |
| `solid_depth:4` | 0.005390863 | 0.01077205 | 0.02156345 |
| `rack_initial_K:0` | 300 | 300.0311 | 400 |
| `rack_initial_K:1` | 300 | 300.0973 | 400 |
| `rack_initial_K:2` | 300 | 300.0511 | 400 |
| `rack_initial_K:3` | 300 | 300.0224 | 400 |
| `rack_initial_K:4` | 300 | 302.489 | 400 |
| `solar_area_m2` | 1382214 | 1839621 | 2764429 |
| `battery_MWh` | 249.8268 | 332.7783 | 499.6536 |
| `warm_store_kg` | 390679 | 520950.2 | 781357.9 |
| `warm_radiator_m2` | 25213.34 | 33618 | 50426.68 |
| `plant_flow_kg_s` | 1.49773 | 1.996643 | 2.99546 |
| `plant_electric_MW` | 10.97875 | 14.63841 | 21.9575 |
| `motor_MW:0` | 18.56141 | 30.85559 | 49.49708 |
| `motor_MW:1` | 6.071354 | 10.12728 | 16.19028 |
| `motor_MW:2` | 4.771816 | 7.960064 | 12.72484 |
| `motor_MW:3` | 7.802899 | 13.01131 | 20.80773 |
| `coast_motor_MW` | 13.00852 | 21.69421 | 34.68938 |
| `isp_s` | 1200 | 1811.985 | 3000 |
| `burn_s` | 800 | 1235.139 | 2000 |
| `perigee_km` | 80 | 85.80446 | 100 |
| `gas_reserve_kg` | 1500 | 3513.831 | 8000 |
| `gas_initial_K` | 200 | 343.9879 | 490 |
| `suction_m3_s:0` | 10985.6 | 27352.43 | 68660 |
| `suction_m3_s:1` | 2482.8 | 6207.258 | 15517.5 |
| `suction_m3_s:2` | 689.2 | 1719.954 | 4307.5 |
| `suction_m3_s:3` | 274.8 | 687.5317 | 1717.5 |
| `head_J_kg:0` | 376593.6 | 940518 | 2353710 |
| `head_J_kg:1` | 485200 | 1217370 | 3032500 |
| `head_J_kg:2` | 373569.6 | 932193.1 | 2334810 |
| `head_J_kg:3` | 329497.2 | 822446.9 | 2059358 |
| `coast_suction_m3_s` | 200 | 501.1123 | 1250 |
| `coast_head_J_kg` | 2000000 | 4874370 | 1.25e+07 |

Indices are zero-based. `solid_depth` multiplied by the fixed full-bore area gives metal volume. `thermal_gap_m` is effective thermal spacing: physical gap = rows × (effective gap + thickness) − thickness. Main receiver rack depth is recomputed at its narrower area while preserving metal inventory.

Fixed: 30 m bore, 31.7 m external diameter, 317 m hull, 125 m reserve length, 2,000 km apogee, SiC then Al materials, four staggered plate rows, 10 m/s deployment speed, receiver pressure target 4,766.83 Pa and 6,500 Pa rating. Valve and feed passage areas are capability assumptions, not optimizer controls.

Derived before each cycle: main receiver radius and volume after packages; reserve volume including heads; total dry mass; installed bus and battery discharge power; gas and product processing schedules. Receiver operating temperature is an integrated state, not a prescribed fill temperature.

Constraints include reserve species/energy closure, rack enthalpy closure, battery/warm energy closure, gas/rotor residuals, full thrust, pressure/material/electrical limits, rack regime/fit, storage capacity, capture ≥99.9%, and receiver peak pressure within 50 Pa of target. Search-only safety buffers tighten reserve closure and receiver matching for subsequent resolution validation.

The objective is dry mass / net new useful liquid per cycle × orbital period. It is operating-orbit mass payoff; circular-apogee delivery is not implemented.
