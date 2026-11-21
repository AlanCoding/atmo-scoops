# Independent coordinates at constrained termination

All values use SI units except the explicitly named MW/MWh quantities. `solid_depth` means solid material volume divided by full bore area; it is not the physical rack length. Thermal gaps, thicknesses and solid inventories determine physical gaps and rack lengths.

| Coordinate | Lower | Selected | Upper | At a bound? |
|---|---:|---:|---:|---|
| thermal_gap_m:0 | 0.0005 | 0.006192897 | 0.03 | no |
| thermal_gap_m:1 | 0.0005 | 0.002974141 | 0.03 | no |
| thermal_gap_m:2 | 0.0005 | 0.003388102 | 0.03 | no |
| thermal_gap_m:3 | 0.0005 | 0.003976044 | 0.03 | no |
| thermal_gap_m:4 | 0.0005 | 0.003768748 | 0.03 | no |
| plate_thickness_m:0 | 0.0002 | 0.001425693 | 0.005 | no |
| plate_thickness_m:1 | 0.0002 | 0.0009984196 | 0.005 | no |
| plate_thickness_m:2 | 0.0002 | 0.001047154 | 0.005 | no |
| plate_thickness_m:3 | 0.0002 | 0.001378868 | 0.005 | no |
| plate_thickness_m:4 | 0.0002 | 0.001345754 | 0.005 | no |
| solid_depth:0 | 0.08435997 | 0.1683331 | 0.3374399 | no |
| solid_depth:1 | 0.006976363 | 0.01395459 | 0.02790545 | no |
| solid_depth:2 | 0.003381423 | 0.006766033 | 0.01352569 | no |
| solid_depth:3 | 0.003091457 | 0.006186504 | 0.01236583 | no |
| solid_depth:4 | 0.005388121 | 0.01078173 | 0.02155248 | no |
| rack_initial_K:0 | 300 | 300.0199 | 400 | no |
| rack_initial_K:1 | 300 | 300.0489 | 400 | no |
| rack_initial_K:2 | 300 | 300.0393 | 400 | no |
| rack_initial_K:3 | 300 | 300.0331 | 400 | no |
| rack_initial_K:4 | 300 | 302.6437 | 400 | no |
| solar_area_m2 | 1383261 | 1842952 | 2766521 | no |
| battery_MWh | 250.6463 | 333.1024 | 501.2926 | no |
| warm_store_kg | 390857.2 | 520905.3 | 781714.5 | no |
| warm_radiator_m2 | 25218.06 | 33617.79 | 50436.12 | no |
| plant_flow_kg_s | 1.497271 | 1.996973 | 2.994543 | no |
| plant_electric_MW | 10.9766 | 14.63833 | 21.9532 | no |
| motor_MW:0 | 18.55456 | 30.93568 | 49.47883 | no |
| motor_MW:1 | 6.068631 | 10.11892 | 16.18302 | no |
| motor_MW:2 | 4.769882 | 7.953026 | 12.71969 | no |
| motor_MW:3 | 7.799607 | 13.00483 | 20.79895 | no |
| coast_motor_MW | 13.00338 | 21.68086 | 34.67568 | no |
| isp_s | 1200 | 1810.298 | 3000 | no |
| burn_s | 800 | 1234.278 | 2000 | no |

Fixed for this comparison: 85 × 2,000 km orbit; 30 m bore; 31.7 m outer diameter and 317 m hull; full-bore rack frontal areas; four serial rows per rack; SiC first, aluminum downstream; 10 m front empty depth; 1 m hatch buffers; compressor suction and head ratings; gas reserve hardware; collection/plant cutoff schedule; 0.1 Pa compressor cutoff; capability coefficients. Receiver free volume is derived after subtracting chambers and equipment. Pressure and gas temperature are simulated states, not independent input coordinates.

See `search.json` for exact fixed settings, `selected_summary.json` for every individual constraint residual, and `termination.json` for solver status. Geometry bounds are study bounds, not material qualification limits.
