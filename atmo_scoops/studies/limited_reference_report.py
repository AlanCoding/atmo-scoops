"""Append the constrained reference to the existing altitude mechanism document."""
from pathlib import Path
import json

MARKER='## Limit-case reference: L/D and storage pressure'

def section(root):
 dest=root/'results/altitude_sensitivity/limited_reference'
 rows=json.loads((dest/'summary.json').read_text())
 first=json.loads((dest/rows[0]['file']).read_text());o=first['outputs'];d=first['inputs']['design']
 lines=[MARKER,'','**Packing status correction:** this is a preserved assumption study, not a geometry-feasible reference. The 25 m front and 100 m machinery allocations were not derived from component volumes; independent interstage chambers and stowed equipment are missing. See [close-pass volume accounting](../../modeling/deployment/CLOSE_PASS_VOLUME.md) and the [reference packing screen](../../modeling/deployment/PACKING_SCREEN.md). The stated perigee boundary is not a validated L/D-limited vehicle result.','',
 'This case adopts the requested limits explicitly: **length/diameter ≤10** and **warm rear storage pressure ≤110,000 Pa absolute**. “Ten diameters long” is the interpretation of the requested ratio. The bore/mouth remains 30 m; with the existing 0.85 m radial allowance, outside diameter is 31.7 m and total permitted length is 317 m. No dry-mass ceiling is imposed.','',
 'The pressure is 10% above the existing numerical process feed of 1 bar, not 10% above the nitrogen triple-point pressure. One bar is a conventional low-pressure liquefaction benchmark, not a universal thermodynamic minimum or a complete mixed-air process specification. The pure products liquefy near 77 K (nitrogen) and 90 K (oxygen) at about atmospheric pressure; see [NIST phase data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=5) and [NIST boiling-point compilation](https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2126.pdf). At 1.10 bar, CoolProp gives saturated pure-liquid temperatures of 78.06 K for N2 and 90.98 K for O2. Separation, finite exchanger approaches and pressure losses still require process development. The numerical plant retains its existing 1-bar N2-equivalent duty.','',
 '| Longitudinal allocation | Length |','|---|---:|',
 '| Front collection/precooling chamber | 25 m |','| Compressor/intercooler machinery allowance | 100 m |','| Rear tank, including two end heads | 192 m |','| Total | 317 m |','',
 'Rear bore is enlarged from the earlier 20.778 m to 30 m. Its two ellipsoidal heads are 7.5 m deep each, leaving a 177 m cylindrical barrel. Usable geometric gas volume is 132,183 m³; expressed as a same-bore flat cylinder it is 187 m deep. At 380 K and 1.10 bar this holds approximately 133 tonnes of gas. The front/machinery allocations are inherited allowances, not optimized minimum lengths; this is a geometric envelope, not a solved packing layout for all the huge deployed systems.','',
 'The artificial minimum overall compressor ratio is changed from 100 to **1**. Discharge follows required receiver pressure; there is no imposed 100:1 startup overcompression. The four-bank architecture, 75% efficiency, compact module geometry, automatic suction sizing, 0.1 Pa inlet cutoff and 300 s reboost remain unchanged. Their masses are recalculated. We do not silently remove a bank or claim a calibrated stage-bypass map.','',
 'For each listed apogee, solve for the perigee at which the complete encounter fills the tank to its pressure ceiling. Then move 0.01 km upward and recompute with 1,601 encounter and thermodynamic samples to remain just inside the boundary. Final rear pressure is the peak in this model because tank inventory increases monotonically during collection. All provided results are subject to the existing local constraints, including oxygen supply.','',
 '| Apogee (km) | Perigee just inside cap (km) | Rear pressure (bar abs.) | Orbit (h) | Dry mass (t) | Compressor mass (t) | Net liquid (kg/pass) | Operating payoff (days) | Screens |','|---:|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in rows:
  lines.append(f"| {r['apogee_km']:,.0f} | {r['perigee_km']:.3f} | {r['storage_Pa']/1e5:.5f} | {r['period_h']:.3f} | {r['dry_t']:,.0f} | {r['compressor_t']:,.0f} | {r['net_kg_pass']:,.0f} | {r['payoff_days']:,.1f} | {'Pass' if r['passes'] else 'FAIL: '+', '.join(r['failed_margins'])} |")
 lines+=['','The 937 km apogee row is the direct limit-case reference against the previous fixed-apogee study. Larger apogees are separate diagnostics that permit a deeper complete pass before reaching the same storage capacity. They are not an apogee optimization. A lower pressure at perigee is not itself proof of better payoff: per-pass impulse, oxygen demand and orbit period change with eccentricity.','',
 '### Reference cycle and deployed equipment','',
 '| Quantity, 937 km apogee | Result |','|---|---:|']
 for title,k,scale,unit in [('Stored gas','retained_kg',1,'kg/pass'),('Reboost propellant','propellant_kg',1,'kg/pass'),('Front pressure near perigee','front_pressure_Pa',1,'Pa'),('Nominal compressor suction','hot_suction_m3_s',1,'m³/s'),('Compressor electricity','compressor_kWh',1,'kWh/pass'),('Reboost electricity','reboost_MWh',1,'MWh/pass'),('Solar collecting area','solar_area_m2',1,'m²'),('Warm radiator physical panel area','warm_radiator_panel_m2',1,'m²'),('Metal cooler physical panel area','metal_panel_m2',1,'m²')]:
  lines.append(f"| {title} | {o[k]*scale:,.2f} {unit} |")
 lines+=['','Panel areas are physical areas, not doubled emitting-face areas. Metal coolers still use sensible storage; no PCM credit is included.','',
 '| Major dry-mass term, 937 km apogee | Tonnes |','|---|---:|']
 for k in ('propulsion_hardware','solar','battery','power_distribution','compressor_hot','compressor_warm','compressor_coast','hot_metal','rear_tank_and_supports','design_margin'):
  lines.append(f"| {k.replace('_',' ')} | {o['masses_kg'][k]/1000:,.1f} |")
 lines+=['','### What “as low as possible” means here','',
 'This is the **lowest full-encounter perigee allowed by tank capacity for each tested apogee and retained collection policy**. It is not a universal minimum altitude. If compressors stop earlier when the tank fills, collection is throttled or the admitted window shrinks, still lower perigees could respect the same tank cap. Exterior/rejected-air drag, heating and recovery would then need to be integrated for that changed policy. This calculation intentionally does not count an overflowing tank or truncate its inventory after the fact.','',
 'The larger tank prevents the previous multi-megapascal receiver from driving the result, and removing the minimum ratio lets the compressor respond to the lower required discharge. The still-large installed masses remain consequences of the inherited propulsion, battery and array capabilities. A pressure/geometry cap does not by itself constrain their mass or demonstrate that their stowed volumes fit. These are limits on a numerical reference, not structural or thermal flight qualification. Circular-apogee export remains excluded.','',
 'Reproduce with `.venv/bin/python -m atmo_scoops.studies.limited_reference` and `.venv/bin/python -m atmo_scoops.studies.limited_reference_report`. [Complete inputs, solver evaluations and summaries](../../results/altitude_sensitivity/limited_reference/summary.json) retain pressure/length margins and ordinary constraint failures. Source hashes are saved alongside the results.','']
 if (dest/'joint_boundary.json').exists():
  joint=json.loads((dest/'joint_boundary.json').read_text());z=joint['outputs'];jd=joint['inputs']['design']
  search=json.loads((dest/'joint_boundary_search.json').read_text())
  lines+=['### Coupled pressure and oxygen boundary','',
   f"Solving tank pressure = 110,000 Pa and oxygen balance = 0 simultaneously gives **{search['boundary_perigee_km']:.3f} km perigee / {search['boundary_apogee_km']:,.1f} km apogee**. This is the lowest-perigee boundary found along the fixed-design, full-encounter pressure-limit family before the oxygen-only reboost constraint fails. It is a local boundary calculation, not a proof of a global optimum across all control schedules or hardware.", '',
   f"The saved reference moves 20 m upward in perigee and 10 km downward in apogee, and is reevaluated at 1,601 samples: **{jd['perigee_km']:.3f} × {jd['apogee_km']:,.1f} km**. Rear pressure is **{z['rear_pressure_Pa']/1e5:.5f} bar absolute**, and the oxygen margin is only **{z['oxygen_mass_margin_kg']:.2f} kg/pass**. This deliberately approaches zero reserve; it is a numerical limit case, not a robust operating point.", '',
   '| Deepest boundary reference | Result |','|---|---:|',
   f"| Orbit period | {z['cycle']['orbit_s']/3600:.3f} h |",
   f"| Stored warm gas | {z['retained_kg']/1000:.3f} t/pass |",
   f"| Net useful liquid | {z['net_liquid_equivalent_kg']/1000:.3f} t/pass |",
   f"| Total dry mass | {z['total_dry_kg']/1000:,.0f} t |",
   f"| Compressors | {z['compressor_mass_kg']/1000:,.0f} t |",
   f"| Front pressure near perigee | {z['front_pressure_Pa']:,.1f} Pa |",
   f"| Operating payoff | {z['operating_mass_payoff_days']:,.1f} days |", '',
   'The approximately 69.14 km perigee / 937 km apogee case gives a much shorter payoff (~506 days) while staying within the same two new limits. Choosing the deepest permissible pass does not minimize payoff under the retained fixed-burst propulsion and electrical capabilities. Both results are retained rather than calling the deeper one an economic optimum.', '',
   'Runnable reference: [configs/limit_case_reference.json](../../configs/limit_case_reference.json). Use `.venv/bin/python -m atmo_scoops --config configs/limit_case_reference.json`. The ordinary CLI reports its existing constraints; the additional investigation pressure/length limits are checked and stored in [joint_boundary.json](../../results/altitude_sensitivity/limited_reference/joint_boundary.json). Reproduce the coupled solve with `.venv/bin/python -m atmo_scoops.studies.limited_reference_boundary`, after the fixed-apogee cases, then regenerate this section.','']
 return '\n'.join(lines)


def main():
 root=Path(__file__).resolve().parents[2];p=root/'investigations/altitude_sensitivity/MECHANISM.md'
 p.write_text(p.read_text().split(MARKER)[0].rstrip()+'\n\n'+section(root))

if __name__=='__main__':main()
