"""Compare bound continuations, with search limits separate from path constraints."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'results/transient/reduced_optimization'
NAMES=['pressure','pressure_wide_mass_reserve','pressure_wide_refined','pressure_wide_closed']
records=[]
for name in NAMES:
 folder=BASE/name
 if not (folder/'termination.json').exists():continue
 t=json.loads((folder/'termination.json').read_text())
 r=json.loads((folder/'selected_summary.json').read_text()) if (folder/'selected_summary.json').exists() else None
 v=json.loads((folder/'replay_summary.json').read_text()) if (folder/'replay_summary.json').exists() else None
 m=json.loads((folder/'manifest.json').read_text())
 records.append((name,t,r,v,m))
lines=['# Widening the rack-mass and reserve-inventory bounds','','These are continuations of the [previous constrained searches](RESULTS.md), using the same five fixed rack mass fractions and one forward cycle per candidate. The accepted v1.0.1 publication remains unchanged.','',
'Only total rack mass and initial reserve gas inventory ranges are widened in the first continuation. Compressor, plant, solar, battery-energy and thermal-store capacities retain their existing sizes. Thrust hardware and bus/discharge ratings remain derived costs. Original physical constraints and closure tolerances remain enforced.','',
'| Search | Solver success | Iterations | Configurations | Replay feasible | Payoff days | Artificial bounds reached |',
'|---|---|---:|---:|---|---:|---|']
for name,t,r,v,m in records:
 lines.append(f'| {name} | {t["success"]} | {t.get("nit","—")} | {t.get("cycles","—")} | {v["feasible"] if v else "Not run"} | '+(f'{v["days"]:.4f}' if v else (f'{r["days"]:.4f} (search only)' if r else '—'))+' | '+(', '.join(t.get('bound_hits',[])) or 'none')+' |')
for name,t,r,v,m in records:
 if name=='pressure_wide_closed' and t['success']:
  lines+=['','## Result','',
  'The actual five-variable SLSQP search terminated successfully with the rack and initial-reserve bounds inactive. **Perigee reaches its artificial lower search bound, 85.09807 km.** Receiver pressure and initial reserve temperature also remain inside their search ranges. This therefore does not yet establish an altitude optimum limited by hardware or material physics.',
  'The final restart took one SLSQP iteration and nine evaluated configurations, including derivative probes; this excludes the two interrupted attempts and explicit seed correction documented below. The unchanged stopping tolerance is 0.005 days. The result is a local solver-converged point on a fairly flat rack-mass trade, not a certification of global optimality or a uniquely determined rack mass.',
  'The low-metal trial below reveals a cooling/suction-throughput limitation, but that capture constraint is not active at the final point. Installed compressor capabilities remain fixed, so changing those capabilities could move this trade. No physical constraint was relaxed to obtain convergence.']
  if v:lines.append(f'The independent replay uses rtol=1e-9 and a 2.5 s maximum time step, versus rtol=1e-8 and 5 s in the search. It passes all original constraints: **{v["feasible"] and not v["failed"]}**. Operating-orbit payoff is **{v["days"]:.3f} days**, compared with **289.571 days** before widening these two bounds.')
for name,t,r,v,m in records:
 lines+=['',f'## {name}','',f'Termination: **{t.get("message",t.get("error",t.get("status")))}**.']
 if not r:continue
 d=r['inputs']['design'];b=m['base']['design']
 # The stage masses scale together, so the reference total follows exactly.
 base_rack=sum(r['rack_kg'])/r['x'][0]
 transforms=[(base_rack/1000,0,'Total racks','t'),(1,b['perigee_km'],'Perigee','km'),(1000,b['gas_reserve_kg'],'Initial reserve gas','kg'),(100,b['gas_initial_K'],'Initial reserve temperature','K'),(b['receiver_fill_Pa']/1000,0,'Receiver target','kPa')]
 lines+=['','### Artificial search bounds','','| Coordinate | Lower | Selected | Upper | Unit | At bound? |','|---|---:|---:|---:|---|---|']
 for i,(scale,offset,label,unit) in enumerate(transforms):
  lo,hi=m['bounds'][i];x=r['x'][i];hit=m['coordinates'][i] in t.get('bound_hits',[])
  lines.append(f'| {label} | {lo*scale+offset:.4f} | {x*scale+offset:.4f} | {hi*scale+offset:.4f} | {unit} | {"YES" if hit else "no"} |')
 lines+=['','These intervals are exploration safeguards, not material limits. Initial reserve gas mass and temperature are periodic-state coordinates; the reserve tank geometry is fixed. Receiver/reserve structural rating follows target pressure at a fixed ratio, with its mass charged.']
 if v:
  cl=v['closure'];margin=v['margins'];cap=100*(1-d['capture_tolerance']+margin['full_capture'])
  lines+=['','### Independent tighter replay','',f'Dry mass **{v["dry_kg"]/1000:,.3f} t**; net liquid **{v["liquid_kg"]:,.3f} kg/orbit**; operating-orbit payoff **{v["days"]:.5f} days**. Capture **{cap:.5f}%**. Minimum total propulsion-gas inventory **{v["minimum_reserve_total_kg"]:.3f} kg** at **{v["minimum_reserve_time_s"]:.3f} s** from perigee.',f'Fill residual **{cl["receiver_fill_Pa"]:.6f} Pa**; reserve species residuals **{[round(z,6) for z in cl["gas_reserve_species_kg"]]} kg**; reserve energy residual **{cl["gas_reserve_MJ"]:.6f} MJ**. Failed original constraints: `{v["failed"]}`.',f'Payoff change from search: **{v["days"]-r["days"]:+.6f} days**.','',
  '| Modeled constraint | Remaining margin | Interpretation |','|---|---:|---|',
  f'| Rack material temperature | {margin["material_K"]:.6f} K | Smallest allowance below a material temperature limit |',
  f'| Chamber pressure rating | {margin["pressure_Pa"]:.6f} Pa | Smallest pressure-rating allowance among compressed chambers |',
  f'| Warm-loop temperature | {margin["warm_K"]:.6f} K | Allowance below configured warm-loop maximum |',
  f'| Battery usable-energy floor | {100*margin["SOC"]:.6f} percentage points | Minimum state of charge minus the usable-energy floor |',
  f'| Liquid tank capacity | {margin["tank_m3"]:.6f} m³ | Unused liquid-storage volume at peak inventory |',
  f'| Full-capture tolerance | {100*margin["full_capture"]:.6f} percentage points | Allowance before the permitted lost fraction is exceeded |',
  f'| Plate Reynolds-number validity | {margin["plate_Re"]:.6f} | Allowance below the configured Re=1000 applicability limit |',
  f'| Gas temperature capability | {margin["gas_K"]:.6f} K | Allowance below the modeled gas-temperature ceiling |']
 lines+=['',f'- [Manifest and numerical settings](../../results/transient/reduced_optimization/{name}/manifest.json).',f'- [Exact selected inputs](../../results/transient/reduced_optimization/{name}/selected_config.json).',f'- [Termination](../../results/transient/reduced_optimization/{name}/termination.json).',f'- [Evaluation history](../../results/transient/reduced_optimization/{name}/evaluations.json).']
 if v:lines.append(f'- [Replay and audits](../../results/transient/reduced_optimization/{name}/replay_summary.json).')
trial_folder=BASE/'pressure_wide_mass_reserve'
if (trial_folder/'low_rack_trial.json.gz').exists():
 import numpy as np
 from atmo_scoops.transient.io import read_result
 trial=read_result(trial_folder/'low_rack_trial.json.gz');prior=read_result(BASE/'pressure/replay.json.gz')
 h=trial['history'];i=int(np.argmax(np.array(h['incident_kg_s'])-h['admitted_kg_s']));time=trial['time_s'][i]
 rows=[]
 for label,r in [('Prior accepted case',prior),('Rejected lower-metal trial',trial)]:
  j=int(np.argmin(abs(np.array(r['time_s'])-time)));h=r['history']
  rows.append(dict(label=label,time_s=r['time_s'][j],gas_K=h['gas_K'][j][0],front_pressure_Pa=h['pressure_Pa'][j][0],incident_kg_s=h['incident_kg_s'][j],admitted_kg_s=h['admitted_kg_s'][j],first_pump_kg_s=h['pump_kg_s'][j][0]))
 from atmo_scoops.transient.thermo import properties
 d=trial['inputs']['design'];c=trial['inputs']['capabilities'];h=trial['history'];mass=np.array(trial['gas_species_kg'][i][0]);R=float(mass/mass.sum()@properties().R)
 flow=h['pump_kg_s'][i][0];work=h['stage_compression_base_MW'][i][0]*1e6*c['eta_motor']/flow
 nominal=d['suction_m3_s'][0]*(h['pressure_Pa'][i][0]-.03)/(R*h['gas_K'][i][0]);factor=max(0,1-(work/d['head_J_kg'][0])**2)
 pump=dict(nominal_full_speed_suction_kg_s=nominal,head_derating=factor,full_speed_flow_after_head_kg_s=nominal*factor,actual_flow_kg_s=flow,approx_electric_MW=h['stage_compression_base_MW'][i][0]+h['rack_loss_MW'][i][0]+c['idle_fraction']*d['motor_MW'][0],motor_MW=d['motor_MW'][0])
 (trial_folder/'low_rack_diagnostic.json').write_text(json.dumps(dict(snapshots=rows,first_pump_screen=pump),indent=2)+'\n')
 cap=100*(1-trial['inputs']['design']['capture_tolerance']+trial['margins']['full_capture'])
 rack=sum(g['mass_kg'] for g in trial['hardware']['geometry'])/1000
 lines+=['','## A rejected low-metal trial shows the throughput limit','',f'A trial with **{rack:.3f} t** of racks admitted only **{cap:.4f}%** of the incident batch. It also failed reserve/fill closure and is not an alternative payoff result. Material-temperature margin remained **{trial["margins"]["material_K"]:.2f} K**, and usable battery margin **{100*trial["margins"]["SOC"]:.3f} percentage points**.','', '| Case near maximum intake deficit | Time s | Front gas K | Front pressure Pa | Arriving kg/s | Admitted kg/s | First pump kg/s |','|---|---:|---:|---:|---:|---:|---:|']
 for row in rows:lines.append('| '+row['label']+' | '+' | '.join(f'{row[k]:.3f}' for k in ['time_s','gas_K','front_pressure_Pa','incident_kg_s','admitted_kg_s','first_pump_kg_s'])+' |')
 lines+=['',f'At that point, the first compressor has nominal full-speed suction capacity **{nominal:.3f} kg/s**, reduced to about **{nominal*factor:.3f} kg/s** by the modeled head-capability factor (actual flow **{flow:.3f} kg/s**). Estimated compression, friction and idle draw is **{pump["approx_electric_MW"]:.3f} MW** against a **{pump["motor_MW"]:.3f} MW** motor. Thus this snapshot points to suction-density/head capability rather than instantaneous motor power saturation. The full-speed calculation is a diagnostic upper estimate; the integrated rotor state determines actual flow.']
 lines+=['','The maximum deficit occurs after perigee, while atmospheric support is declining. The model couples gas temperature to suction density and compression work, limits compressor volume/head/power, and reduces admission when front pressure approaches inlet support. This is a cooling/throughput limitation with the installed compressor capabilities, not evidence that the metal has reached its temperature limit. The two trials also differ in perigee and reserve state; this comparison is diagnostic, not an isolated rack-mass derivative.','', '- [Rejected trial inputs](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_trial_config.json).','- [Saved time history](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_trial.json.gz).','- [Extracted comparison](../../results/transient/reduced_optimization/pressure_wide_mass_reserve/low_rack_diagnostic.json).']
coarse_path=BASE/'pressure_wide_mass_reserve/evaluations.json';fine_path=BASE/'pressure_wide_refined/evaluations.json'
if fine_path.exists():
 import numpy as np
 coarse=json.loads(coarse_path.read_text());fine=json.loads(fine_path.read_text())
 if len(coarse)>=33 and len(fine)>=6:
  comparison=[]
  for label,group,steps in [('2.55 t probe, rtol=1e-7',coarse[27:33],[.005,.005,.002,.002,.002]),('0.255 t probe, rtol=1e-8',fine[:6],[.0005,.005,.002,.002,.002])]:
   first=group[0];f=np.r_[first['days'],first['eq']]
   J=np.column_stack([(np.r_[r['days'],r['eq']]-f)/h for r,h in zip(group[1:],steps)])
   controls=[2,3,4];response=np.linalg.solve(J[1:,controls],-J[1:,0]);slope=float(J[0,0]+J[0,controls]@response)
   comparison.append(dict(label=label,payoff_days_per_one_percent_rack_mass=.01*slope,reserve_mass_residual_kg_per_one_percent_rack_mass=float(J[2,0]),scaled_closure_jacobian_condition=float(np.linalg.cond(J[1:,controls]))))
  (BASE/'pressure_wide_refined/derivative_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
  lines+=['','## Numerical refinement at the same inputs','','The first widened attempt was stopped during backtracking; its history contains completed configurations and some in-flight work was deliberately discarded. It is not reported as converged. The refinement uses the same ranges and physical constraints, with a smaller rack-mass derivative probe and tighter integration.','', '| Derivative calculation | Local payoff slope, days per +1% rack mass | Scaled closure-matrix condition |','|---|---:|---:|']
  for z in comparison:lines.append(f'| {z["label"]} | {z["payoff_days_per_one_percent_rack_mass"]:+.6f} | {z["scaled_closure_jacobian_condition"]:.3f} |')
  lines+=['','These slopes eliminate the linearized fill/reserve mass/reserve energy residuals using initial reserve mass, initial reserve temperature and target pressure, while holding perigee fixed. They diagnose derivative resolution near the capture transition; they are not substitute simulation results or a new payoff model.','', '- [Derivative comparison](../../results/transient/reduced_optimization/pressure_wide_refined/derivative_comparison.json).']
seed_folder=BASE/'pressure_wide_closed'
if (seed_folder/'seed_summary.json').exists():
 seed=json.loads((seed_folder/'seed_summary.json').read_text());meta=json.loads((seed_folder/'seed_restoration.json').read_text());cl=seed['closure']
 lines+=['','## Explicit feasible-seed construction','', 'The fine-gradient run still backtracked from a slightly unclosed initial state and was stopped. Its already-measured Jacobian supplied one Newton correction to initial reserve mass, initial reserve temperature and receiver target. Rack mass and perigee were held fixed for this seed correction only. One fresh forward cycle verified it; the subsequent constrained optimizer again frees all five coordinates under the same widened bounds.',f'The seed is physically feasible: **{seed["feasible"]}**. Fill residual **{cl["receiver_fill_Pa"]:.6f} Pa** (targeted 20 Pa within the guarded band), summed reserve mass residual **{sum(cl["gas_reserve_species_kg"]):.9f} kg**, reserve energy residual **{cl["gas_reserve_MJ"]:.9f} MJ**. Seed payoff **{seed["days"]:.6f} days**. This is initialization, not a substitute for the subsequent optimizer termination.', '', '- [Measured-Jacobian correction](../../results/transient/reduced_optimization/pressure_wide_closed/seed_restoration.json).','- [Verified seed](../../results/transient/reduced_optimization/pressure_wide_closed/seed_summary.json).','- [Reproduction script](restore_seed.py).']
lines+=['','## Interpretation and scope','','A model constraint is not necessarily a fundamental physical limit: installed power/processing capacities and material capabilities are fixed assumptions in this experiment. A search-bound hit is not a physical limit at all. Closure and receiver-fill tolerance boundaries are numerical acceptance conditions, not hardware failures.','',
'The complete collection, propellant availability, thermal, electrical, geometric, pressure-rating, applicability and conservation checks remain active. Leading-edge lifetime, calibrated compressor maps and resolved inlet aerodynamics are not established by optimizer convergence. These payoffs end in the operating orbit; delivery/circularization has not been added.','',
'## Reporting correction','','The previous report labeled `margins.reserve_kg` as minimum propulsion inventory. That field is the smallest liquid-species surplus. This report and the corrected earlier report instead sum the three species in the saved propulsion-gas reservoir at every time and take the minimum. The earlier 289.57-day case had **2,404.075 kg** minimum total propulsion gas, not 44.8 kg. This correction changes neither the trajectory nor its constraints or payoff.']
lines+=['','## Code validation','','The complete test suite passes **181 tests**. The model audit passes eight cycle resolution/conservation cases and the Kepler energy/angular-momentum checks. The rack allocation fractions match the preceding selected case to floating-point roundoff. The forward physics implementation was unchanged in this bound-continuation experiment.']
Path(__file__).with_name('WIDENED_BOUNDS.md').write_text('\n'.join(lines)+'\n')
