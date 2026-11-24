"""Inventory current candidate inputs for restoration review; no model changes."""
import json
from pathlib import Path
from atmo_scoops.transient.plate_optimize import specs
ROOT=Path(__file__).resolve().parents[2]
c=json.loads((ROOT/'docs/design_archive/v1.0.1_rejected_boosted/inputs.json').read_text())
coords=specs(c);free={s['key'].split(':')[0] for s in coords};free.add('rack_depth_m');free.add('plate_gap_m')
remove={'gas_volume_m3','gas_reserve_kg','gas_initial_K','gas_rated_Pa','gas_tank_count','gas_fill_suction_m3_s','gas_fill_head_J_kg','gas_fill_motor_MW','gas_fill_UA_W_K','gas_thermal_UA_W_K'}
reconcile={'perigee_km','suction_m3_s','head_J_kg','rated_pressure_Pa','coast_suction_m3_s','coast_suction_fractions','coast_head_J_kg','battery_MW','bus_MW','gas_feed_min_Pa','gas_feed_max_kg_s','plant_start_s','plant_stop_s','pump_stop_s','vent_duration_s','cutoff_Pa','gas_initial_fractions','propellant_storage'}
num={'integrator','atol','max_step_s','integration_segment_s','rtol','early_reject','max_rhs_evaluations','jacobian_relative_step','jacobian_absolute_step','chamber_initial_pressure_Pa','compression_model'}
lines=['# Fixed-input and optimizer-coordinate audit','','Values are the rejected boosted candidate, not proposed new settings. This enumerates every serialized input. Inline constants require the separate checklist below. Implemented dispositions are in [the finalized version document](../../docs/publication/V1_0_1.md).','','## Design inputs','','| Input | Value | Existing search / disposition |','|---|---|---|']
for k,v in c['design'].items():
 if k in remove:status='Remove boosted subsystem; cyclic reserve states/geometry replace applicable quantities'
 elif k in reconcile:status='Fixed; reconcile before next optimizer'
 elif k in num:status='Numerical / property setting; preserve provenance and validate'
 elif k in free:status='Optimized (rack physical gaps/depths derived from thermal gaps/thickness/solid inventory)'
 else:status='Fixed; retain explicitly for controlled comparison or follow scoped review'
 lines.append(f'| `{k}` | `{json.dumps(v)}` | {status} |')
lines+=['','## Capability assumptions','','These were fixed, not optimizer decisions. They remain declared assumptions unless a mandatory restoration dependency requires a reviewed change.','','| Input | Value |','|---|---|']
for k,v in c['capabilities'].items():lines.append(f'| `{k}` | `{json.dumps(v)}` |')
lines+=['','## Inline constants and relationships requiring explicit review','','| Source | Embedded assumption | Disposition |','|---|---|---|',
'| hardware.py | Reference atmosphere; fixed mixture elsewhere; 2,401 forcing samples | Recompute forcing at declared orbit; retain environment scenario and verify resolution |',
'| hardware.py | 200 km stow/deploy altitude; orbit must leave 300 s after processing | Replace hidden timing dependencies with declared event constraints |',
'| hardware.py | Compressor 0.5 m modules, 350 m/s tip, 100 m/s axial; dummy inlet rho=0.001, mu=2e-5, sound=400 | Document surrogate applicability; tie capacity sizing to required flow/states |',
'| hardware.py | Solar packing 40 kW/m³; radiator 0.02 m³/m²; battery 280 kWh/m³ or 1,800 kg/m³; warm store 800 kg/m³ | Keep as explicit packing capabilities; apply all packages only ahead of reserve |',
'| hardware.py | Vessel minimum wall 1 mm, strength 150 MPa, density 2,700 kg/m³, 1.5 factors; hull 4 kg/m² | Recompute new tank/partition surfaces without double counting; coefficients remain conditional |',
'| hardware.py | Liquid tank 300 kg/m³ and 20% package uplift; auxiliary 5,000 kg; separator scaling | Retain documented allowances; product storage campaign separate |',
'| hardware.py | Refrigerator mass sized using 380 K reference sink, 77.34 K reference cold point | Keep reduced cryogenic model for now; expose distinction from actual duty |',
'| gas_feed.py | 1 bar cutoff, four-sphere shell geometry, 0.2 m packaging clearance, 500 kg valves | Delete old sphere/booster geometry; replace feed boundary and physical valve allowance explicitly |',
'| cycle.py | Inlet coefficient 0.8; pressure-difference smoothing 0.001; leak inventory clamp 100/s | Keep numerical/port assumptions explicit; enforce full-capture requirement against incident forcing |',
'| cycle.py | Fixed mixture, 0.03 Pa flow offset and 0.1 Pa cutoff | Check full-capture and low-pressure applicability; no unreported collection penalty |',
'| cycle.py | Three equal-ratio coast blocks to 100 kPa; outlet capped at warm +20 K; UA approaches 20 K / 5 K | Retain product-only reduced process; eliminate reserve split and its priority |',
'| cycle.py | Reserve refill target approached over 20 s | Remove entirely with booster refill control |',
'| cycle.py | Reservoir thermal UA 50 kW/K; zero-stored-temperature reset not allowed | Replace with physical low-pressure compartment thermal state and periodic closure |',
'| cycle.py | Vent mass/10 s; forced purge after pressure <100 Pa | Main chambers only; no reserve purge; keep lost mass explicit and validate vent window |',
'| cycle.py | Rotor enable −500 s; coast/release fixed-time events; spin/brake times | Derive consistent event ordering; no hidden refill rotor or free standby |',
'| cycle.py | Battery charge target initial SOC, 20 s controller; warm/rack radiative throttles near initial temperature | Retain stated control law but verify closure/sensitivity; do not mistake controlled initial temperature for passive equilibrium |',
'| plate_optimize.py | Bounds tied to the old seed; 33-coordinate selection; fixed motor-only search | Build a new explicit coordinate/constraint manifest; do not reuse old bounds without review |',
'| plate_optimize.py | Closure tolerances: racks 500 J/kg, battery/warm 100 MJ, gas 0.1 kg, gas energy 0.01 MJ, reserve species 0.1 kg/energy 1 MJ | Reassess scale for new reserve state; do not weaken criteria just to converge |',
'| thermo.py / plates.py / reboost.py | Property domain, mixture approximations, thermal-spacing/entry-loss law, finite-burn orbital approximation | Preserve qualified scope and numerical gates; no unrelated model expansion in restoration |',
'', 'The audit does not claim these coefficients are validated. It distinguishes fixed engineering assumptions from missing architecture dependencies so they cannot silently constrain or reshape the next design.']
Path(__file__).with_name('FIXED_INPUT_AUDIT.md').write_text('\n'.join(lines)+'\n')
print('Registered',len(c['design']),'design fields and',len(c['capabilities']),'capability fields.')
