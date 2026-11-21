"""Build the checkpoint review from saved trajectories; never re-simulate."""
import argparse,json
from pathlib import Path
import numpy as np
from atmo_scoops.transient.io import read_result
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,default=Path(__file__).with_name('REVIEW.md'));a=p.parse_args()
 r=read_result(a.result);old=read_result(ROOT/'results/transient/plates/reference_validation/case_72.json.gz');h=r['hardware'];d=r['inputs']['design'];rows=['# Combined cooler / stage geometry review','','Source trajectory: `'+str(a.result)+'`. This report does not certify optimizer termination; see the associated termination record. The prior published reference remains frozen.','','| Quantity | Frozen case 72 | This candidate |','|---|---:|---:|']
 for label,key,scale in [('Dry mass, tonnes','dry_kg',1000),('Useful liquid per cycle, kg','net_liquid_kg',1),('Operating-orbit payoff, days','operating_payoff_days',1)]:
  rows.append(f'| {label} | {old[key]/scale:.3f} | {r[key]/scale:.3f} |' if r[key] is not None else f'| {label} | {old[key]/scale:.3f} | unresolved/infeasible |')
 rows+=['','## Geometry','','Coordinates are metres aft of the mouth. Head volumes remain explicit. The first rack has 10 m clear space ahead. Each compressor is followed by 1 m hatch equipment.','','| Stage | Gas region | Rack region | Compressor region | Hatch region | Metal, t | Gap, mm | Thickness, mm |','|---|---|---|---|---|---:|---:|---:|']
 for i,s in enumerate(h['stage_packing']['stages']):
  def span(k):return f"{s[k+'_start_m']:.3f}–{s[k+'_end_m']:.3f}"
  rows.append(f"| {i+1} | {span('gas')} | {span('rack')} | {span('compressor')} | {span('hatch')} | {h['geometry'][i]['mass_kg']/1000:.3f} | {d['plate_gap_m'][i]*1000:.3f} | {d['plate_thickness_m'][i]*1000:.3f} |")
 rows += ['',f"Receiver starts at {h['stage_packing']['receiver_start_m']:.3f} m and ends at {h['length_m']:.3f} m. Its other-equipment displacement is {h['stage_packing']['aft_displacement_m3']:.1f} m³. The separate last-125-m feed compartment is the next checkpoint; it is not in this simulation.",'','## Mass','','| Component | tonnes |','|---|---:|']
 rows += [f'| {k} | {v/1000:.3f} |' for k,v in h['masses_kg'].items()]
 flows=np.column_stack([np.array(r['history']['pump_kg_s']),r['history']['coast_kg_s']]);pressure=np.array(r['history']['pressure_Pa']);drop=np.array(r['history']['rack_drop_Pa'])
 temps=np.array(r['history']['rack_K']);times=np.array(r['time_s']);rack_rows=[]
 rows+=['','## All five racks','','Start/end are cycle endpoints. Pre-deployment is immediately before the modeled vent-and-release event (pump stop + vent duration for 1–4; plant stop + vent duration for 5). Peak temperature is included because endpoint closure alone hides the thermal excursion.','','| Rack | Material | Metal t | Core length m | Installed length m | Physical gap mm | Thermal gap mm | Sheet mm | Start K | Peak K | Pre-deploy K | End K |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for i,g in enumerate(h['geometry']):
  release=(d['pump_stop_s'] if i<4 else d['plant_stop_s'])+d['vent_duration_s']
  vals=dict(stage=i+1,material=d['materials'][i],mass_t=g['mass_kg']/1000,core_m=g['rack_depth_m'],installed_m=g.get('installed_rack_depth_m',g['rack_depth_m']),physical_gap_mm=g['gap_m']*1000,thermal_gap_mm=g.get('thermal_gap_m',g['gap_m'])*1000,thickness_mm=g['thickness_m']*1000,start_K=temps[0,i],peak_K=temps[:,i].max(),predeploy_K=np.interp(release,times,temps[:,i]),end_K=temps[-1,i])
  rack_rows.append(vals)
  rows.append('| '+ ' | '.join(str(vals[k]) if k in ('stage','material') else f'{vals[k]:.4f}' for k in vals)+' |')
 rows+=['','## Hydraulic applicability screen','','Maximum ratios, Re and Kn use times above 10% of each stage’s peak flow. The throughput fraction integrates the entire cycle. These ratios are diagnostics; the power-only surrogate does not enforce hydraulic feasibility.','','| Volume | Inlet Pa at peak flow | Drop Pa at peak flow | Drop/inlet at peak flow | Max drop/inlet (>10% peak flow) | Throughput fraction with drop > inlet | Max Re | Max Kn |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for i in range(5):
  mask=flows[:,i]>.1*flows[:,i].max()
  if mask.any():
   peak=int(np.argmax(flows[:,i]));ratio=drop[:,i]/np.maximum(pressure[:,i],1e-30);fraction=float(np.trapezoid(flows[:,i]*(ratio>1),times)/max(np.trapezoid(flows[:,i],times),1e-30))
   rack_rows[i].update(inlet_at_peak_Pa=float(pressure[peak,i]),drop_at_peak_Pa=float(drop[peak,i]),ratio_at_peak=float(ratio[peak]),max_meaningful_ratio=float(ratio[mask].max()),throughput_fraction_above_unity=fraction)
   rows.append(f"| {i+1} | {pressure[peak,i]:.3f} | {drop[peak,i]:.3f} | {ratio[peak]:.4f} | {ratio[mask].max():.4f} | {fraction:.2%} | {np.max(np.array(r['history']['rack_Re'])[mask,i]):.2f} | {np.max(np.array(r['history']['rack_Kn'])[mask,i]):.4f} |")
 a.output.with_suffix('.racks.json').write_text(json.dumps(rack_rows,indent=2)+'\n')
 rows+=['','## Design intent and buildability','','The search fixes the craft diameter, all five rack frontal areas at the full bore, four serial rows, compressor suction capacities, and the operating schedule. It optimizes effective thermal gaps, thicknesses, metal inventory and the existing power/thermal/propulsion capacities. Therefore a shallow downstream rack is partly imposed by the full-bore flow-area assumption; it is not proof that a broad thin plate assembly is the best buildable architecture.','','A geometric repackaging screen below holds flow, inlet state, metal inventory, plate gaps and wetted area fixed. Using frontal-area fraction f makes core depth L/f and velocity u/f. In this surrogate both shear and row-entry drops then scale as 1/f². Heat conductance stays unchanged under the stipulated thermal-spacing law. This is **not a forward simulation, recommended final sizing, or new payoff claim**; ducts, supports, changed holdup, flow distribution and deployment need modeling.','','| Rack | Illustrative active-area fraction | Equivalent diameter m | Repacked core depth m | Peak-flow drop/inlet at same state |','|---|---:|---:|---:|---:|']
 for i,f in enumerate([1.,.25,.1,.1,.1]):
  z=rack_rows[i];rows.append(f"| {i+1} | {f:.2f} | {d['bore_m']*f**.5:.2f} | {z['core_m']/f:.3f} | {z.get('ratio_at_peak',0)/f**2:.4f} |")
 rows+=['','The loss model is still a power surcharge, not a hydraulic flow limiter. Any non-negligible throughput with predicted drop above inlet pressure prevents treating the numerical optimum as a hydraulically established design. Candidate remedies are a pressure-aware compressor cutoff/control and/or additional spacing/row allocation freedom; neither is silently added to this controlled comparison.']
 rows+=['','## Validation and limits','','```json',json.dumps(dict(feasible=r['feasible'],audits=r['audits'],closure=r['closure'],margins=r['margins']),indent=2),'```','','Thermal-spacing equivalence and edge-loss coefficients are provisional. Five lumped gas/solid states do not resolve individual rows. Pressure loss is still charged to compressor electricity, not solved as a hydraulic pressure field. Large loss/pressure ratios and slip-flow regimes require separate validation. This is operating-orbit payoff, not delivered circular-apogee payoff.']
 a.output.write_text('\n'.join(rows)+'\n')
if __name__=='__main__':main()
