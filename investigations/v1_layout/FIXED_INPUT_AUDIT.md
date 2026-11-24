# Fixed-input and optimizer-coordinate audit

Values are the rejected boosted candidate, not proposed new settings. This enumerates every serialized input. Inline constants require the separate checklist below. Implemented dispositions are in [the finalized version document](../../docs/publication/V1_0_1.md).

## Design inputs

| Input | Value | Existing search / disposition |
|---|---|---|
| `perigee_km` | `85.0` | Fixed; reconcile before next optimizer |
| `apogee_km` | `2000.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `inlet_ceiling_km` | `250.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `inlet_taper_km` | `50.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `bore_m` | `30.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `clearance_m` | `0.85` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `length_diameter` | `10.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rack_depth_m` | `[3.5981397857324886, 0.22209284475134566, 0.11463104840211671, 0.09610257473327685, 0.16390263791572707]` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `clear_depth_m` | `[10.0, 0.0, 0.0, 0.0]` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rack_initial_K` | `[300.0199275032805, 300.0488803377537, 300.0393319255018, 300.0331308115852, 302.6436980436782]` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `materials` | `["sic", "aluminum", "aluminum", "aluminum", "aluminum"]` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rod_radius_m` | `0.001` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rod_pitch_m` | `0.01` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `stage_pitch_m` | `[]` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `stage_radius_m` | `[]` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `plate_thickness_m` | `[0.0014256929331358244, 0.000998419610386663, 0.0010471538179568063, 0.001378867911913406, 0.0013457542026683196]` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `plate_gap_m` | `[0.02904866688045006, 0.014891822948081038, 0.016693868756743207, 0.020040781360607246, 0.019112255771788312]` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `chamber_initial_pressure_Pa` | `0.0` | Numerical / property setting; preserve provenance and validate |
| `plate_thermal_model` | `"offset_equivalent"` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `plate_rows` | `[4, 4, 4, 4, 4]` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `plate_offset_fraction` | `0.5` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `plate_row_clearance_m` | `0.005` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `explicit_stage_packing` | `1` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `stage_hatch_buffer_m` | `1.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rack_flow_layout` | `"parallel_plates"` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rack_pressure_model` | `"layout"` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `rack_loss_mode` | `"power_only"` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `propellant_storage` | `"gas"` | Fixed; reconcile before next optimizer |
| `gas_volume_m3` | `500.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_reserve_kg` | `4500.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_initial_K` | `340.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_initial_fractions` | `[0.755, 0.232, 0.013]` | Fixed; reconcile before next optimizer |
| `gas_rated_Pa` | `1500000.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_feed_min_Pa` | `100000.0` | Fixed; reconcile before next optimizer |
| `gas_feed_max_kg_s` | `5.0` | Fixed; reconcile before next optimizer |
| `gas_tank_count` | `4` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_fill_suction_m3_s` | `10.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_fill_head_J_kg` | `1500000.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_fill_motor_MW` | `5.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_fill_UA_W_K` | `50000.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `gas_thermal_UA_W_K` | `50000.0` | Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities |
| `suction_m3_s` | `[27464.0, 6207.0, 1723.0, 687.0]` | Fixed; reconcile before next optimizer |
| `head_J_kg` | `[941484.0, 1213000.0, 933924.0, 823743.0]` | Fixed; reconcile before next optimizer |
| `motor_MW` | `[30.935675916031006, 10.118923206338728, 7.95302607561776, 13.004831919223918]` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `rated_pressure_Pa` | `[2000, 10000, 30000, 6500]` | Fixed; reconcile before next optimizer |
| `coast_suction_m3_s` | `500.0` | Fixed; reconcile before next optimizer |
| `coast_suction_fractions` | `[1, 0.25, 0.0625]` | Fixed; reconcile before next optimizer |
| `coast_head_J_kg` | `5000000.0` | Fixed; reconcile before next optimizer |
| `coast_motor_MW` | `21.68086485761136` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `plant_flow_kg_s` | `1.9969731648435365` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `plant_electric_MW` | `14.638333278804772` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `precool_UA_W_K` | `200000.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `condenser_UA_W_K` | `250000.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `solar_area_m2` | `1842952.4978555685` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `battery_MWh` | `333.102397870389` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `battery_MW` | `940.1956` | Fixed; reconcile before next optimizer |
| `bus_MW` | `827.372128` | Fixed; reconcile before next optimizer |
| `warm_radiator_m2` | `33617.78707971464` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `warm_store_kg` | `520905.2752167912` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `warm_initial_K` | `340.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `warm_max_K` | `450.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `battery_initial_soc` | `0.95` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `isp_s` | `1810.2977364139306` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `burn_s` | `1234.277705116753` | Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory) |
| `liquid_tank_m3` | `20.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `reserve_kg` | `0.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `mixing_ratio` | `0.0` | Fixed; retain explicitly for controlled comparison or follow scoped review |
| `plant_start_s` | `650.0` | Fixed; reconcile before next optimizer |
| `plant_stop_s` | `4200.0` | Fixed; reconcile before next optimizer |
| `pump_stop_s` | `600.0` | Fixed; reconcile before next optimizer |
| `vent_duration_s` | `120.0` | Fixed; reconcile before next optimizer |
| `cutoff_Pa` | `0.1` | Fixed; reconcile before next optimizer |
| `compression_model` | `"HEOS"` | Numerical / property setting; preserve provenance and validate |
| `integrator` | `"BDF"` | Numerical / property setting; preserve provenance and validate |
| `atol` | `1e-10` | Numerical / property setting; preserve provenance and validate |
| `max_step_s` | `10.0` | Numerical / property setting; preserve provenance and validate |
| `integration_segment_s` | `0.0` | Numerical / property setting; preserve provenance and validate |
| `rtol` | `2e-05` | Numerical / property setting; preserve provenance and validate |
| `early_reject` | `0` | Numerical / property setting; preserve provenance and validate |
| `max_rhs_evaluations` | `250000` | Numerical / property setting; preserve provenance and validate |
| `jacobian_relative_step` | `1e-06` | Numerical / property setting; preserve provenance and validate |
| `jacobian_absolute_step` | `0.0` | Numerical / property setting; preserve provenance and validate |

## Capability assumptions

These were fixed, not optimizer decisions. They remain declared assumptions unless a mandatory restoration dependency requires a reviewed change.

| Input | Value |
|---|---|
| `plate_entrance_credit` | `1.0` |
| `plate_restart_loss_K` | `0.674` |
| `rack_loss_multiplier` | `1.0` |
| `skin_friction_coefficient` | `0.002` |
| `skin_area_multiplier` | `1.0` |
| `eta_compressor` | `0.75` |
| `eta_motor` | `0.95` |
| `eta_thruster` | `0.6` |
| `retained_thruster_loss` | `0.2` |
| `thruster_kg_kW` | `2.0` |
| `bus_kg_kW` | `1.0` |
| `solar_W_m2` | `250.0` |
| `solar_W_kg` | `150.0` |
| `battery_Wh_kg` | `150.0` |
| `battery_W_kg` | `1500.0` |
| `battery_usable` | `0.8` |
| `charge_eta` | `0.95` |
| `discharge_eta` | `0.95` |
| `buffer_cp_J_kg_K` | `2000.0` |
| `radiator_kg_m2` | `5.0` |
| `radiator_emissivity` | `0.85` |
| `radiator_view` | `0.8` |
| `rack_view` | `0.7` |
| `environment_W_m2` | `80.0` |
| `deployment_m_s` | `10.0` |
| `machinery_kg_m3` | `250.0` |
| `fill_fraction` | `0.7` |
| `margin` | `0.25` |
| `idle_fraction` | `0.01` |
| `spin_s` | `120.0` |
| `brake_s` | `30.0` |
| `vacuum_regularization_kg` | `0.001` |
| `carnot_fraction` | `0.15` |
| `separation_J_kg` | `250000.0` |
| `auxiliary_W` | `10000.0` |
| `tank_heat_W` | `1000.0` |
| `heat_pump_kg_W_equivalent` | `0.25` |
| `exchanger_UA_per_kg` | `200.0` |
| `head_depth_m` | `1.5` |
| `rack_mechanism_kg_m2` | `1.0` |
| `upper_gas_K` | `2000.0` |

## Inline constants and relationships requiring explicit review

| Source | Embedded assumption | Disposition |
|---|---|---|
| hardware.py | Reference atmosphere; fixed mixture elsewhere; 2,401 forcing samples | Recompute forcing at declared orbit; retain environment scenario and verify resolution |
| hardware.py | 200 km stow/deploy altitude; orbit must leave 300 s after processing | Replace hidden timing dependencies with declared event constraints |
| hardware.py | Compressor 0.5 m modules, 350 m/s tip, 100 m/s axial; dummy inlet rho=0.001, mu=2e-5, sound=400 | Document surrogate applicability; tie capacity sizing to required flow/states |
| hardware.py | Solar packing 40 kW/m³; radiator 0.02 m³/m²; battery 280 kWh/m³ or 1,800 kg/m³; warm store 800 kg/m³ | Keep as explicit packing capabilities; apply all packages only ahead of reserve |
| hardware.py | Vessel minimum wall 1 mm, strength 150 MPa, density 2,700 kg/m³, 1.5 factors; hull 4 kg/m² | Recompute new tank/partition surfaces without double counting; coefficients remain conditional |
| hardware.py | Liquid tank 300 kg/m³ and 20% package uplift; auxiliary 5,000 kg; separator scaling | Retain documented allowances; product storage campaign separate |
| hardware.py | Refrigerator mass sized using 380 K reference sink, 77.34 K reference cold point | Keep reduced cryogenic model for now; expose distinction from actual duty |
| gas_feed.py | 1 bar cutoff, four-sphere shell geometry, 0.2 m packaging clearance, 500 kg valves | Delete old sphere/booster geometry; replace feed boundary and physical valve allowance explicitly |
| cycle.py | Inlet coefficient 0.8; pressure-difference smoothing 0.001; leak inventory clamp 100/s | Keep numerical/port assumptions explicit; enforce full-capture requirement against incident forcing |
| cycle.py | Fixed mixture, 0.03 Pa flow offset and 0.1 Pa cutoff | Check full-capture and low-pressure applicability; no unreported collection penalty |
| cycle.py | Three equal-ratio coast blocks to 100 kPa; outlet capped at warm +20 K; UA approaches 20 K / 5 K | Retain product-only reduced process; eliminate reserve split and its priority |
| cycle.py | Reserve refill target approached over 20 s | Remove entirely with booster refill control |
| cycle.py | Reservoir thermal UA 50 kW/K; zero-stored-temperature reset not allowed | Replace with physical low-pressure compartment thermal state and periodic closure |
| cycle.py | Vent mass/10 s; forced purge after pressure <100 Pa | Main chambers only; no reserve purge; keep lost mass explicit and validate vent window |
| cycle.py | Rotor enable −500 s; coast/release fixed-time events; spin/brake times | Derive consistent event ordering; no hidden refill rotor or free standby |
| cycle.py | Battery charge target initial SOC, 20 s controller; warm/rack radiative throttles near initial temperature | Retain stated control law but verify closure/sensitivity; do not mistake controlled initial temperature for passive equilibrium |
| plate_optimize.py | Bounds tied to the old seed; 33-coordinate selection; fixed motor-only search | Build a new explicit coordinate/constraint manifest; do not reuse old bounds without review |
| plate_optimize.py | Closure tolerances: racks 500 J/kg, battery/warm 100 MJ, gas 0.1 kg, gas energy 0.01 MJ, reserve species 0.1 kg/energy 1 MJ | Reassess scale for new reserve state; do not weaken criteria just to converge |
| thermo.py / plates.py / reboost.py | Property domain, mixture approximations, thermal-spacing/entry-loss law, finite-burn orbital approximation | Preserve qualified scope and numerical gates; no unrelated model expansion in restoration |

The audit does not claim these coefficients are validated. It distinguishes fixed engineering assumptions from missing architecture dependencies so they cannot silently constrain or reshape the next design.
