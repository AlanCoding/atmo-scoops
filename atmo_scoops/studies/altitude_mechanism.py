"""Explain saved altitude/apogee runs through pressure and component ledgers."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
 root=Path(__file__).resolve().parents[2]
 outputs={h:json.loads((root/f'results/altitude_sensitivity/{h}km.json').read_text())['outputs'] for h in (60,80,90,100,140)}
 lines=['# Why the altitude sweep plateaus, and what apogee changes','',
 'This explains the [altitude sweep](ANALYSIS.md), not a universal optimum. The previous sweep held apogee at 937.191 km, kept front/rear geometry and temperature/control choices fixed, and resized dependent equipment. The additional apogee runs change apogee alone. Neither experiment jointly optimizes chamber volumes, stage maps, cooling, thrust duration and orbit.','',
 '## The low-pressure bank does not see a fixed downstream pressure','',
 'The current model accumulates the larger captured batch in the same rear volume at the same receiver temperature. Consequently rear pressure rises approximately in proportion to atmospheric density, as does front pressure. The four block pressures are allocated between those endpoints; they are not fixed absolute intermediate-pressure targets. The historical `intermediate_Pa` field is inactive for real-gas compression.','',
 '| Perigee | Front pressure near perigee | Final rear pressure | Rear/front ratio* | Nominal suction | First-bank Re |','|---:|---:|---:|---:|---:|---:|']
 for h,o in outputs.items():
  lines.append(f"| {h} km | {o['front_pressure_Pa']:,.3f} Pa | {o['rear_pressure_Pa']:,.1f} Pa | {o['rear_pressure_Pa']/o['front_pressure_Pa']:.1f} | {o['hot_suction_m3_s']:,.0f} m³/s | {o['compressor_analysis']['dive']['banks'][0]['inlet_Re']:,.0f} |")
 lines+=['','*Front perigee and final rear pressure are different-time diagnostics, not an instantaneous compressor pressure ratio. Saved `peak_flow_states` supply simultaneous block states. At peak flow the first bank is approximately 144→464 Pa at 90 km versus 14,411→47,278 Pa at 60 km: nearly the same bank ratio.','',
 'For a similar capture fraction and cooled temperature, `m_dot ~ rho_inf A v`, while `p_front ~ C rho_inf v²` and `rho_front ~ p_front/(R T)`. Therefore `Q_front = m_dot/rho_front ~ A R T/(C v)`. Density cancels. The first bank handles far more kilograms at lower altitude, but almost the same cubic metres per second. That explains the nearly unchanged annulus requirement. It is not evidence that higher inlet pressure is useless.','',
 'With fixed downstream pressure, higher inlet pressure really would lower head and could eliminate earlier banks. To preserve downstream pressure while collecting the larger batch, the rear volume must grow, or the collection window/mouth area/batch must change. A jointly designed machine could also use different stage counts, speeds and bank bypasses. None is allowed in this sweep.','',
 'Two additional modeling restrictions matter: (1) installed first-bank volume flow is bounded below by the computed nominal suction even when realized flow is lower; (2) a minimum overall compression ratio of 100 is imposed at startup and excess pressure throttled. The bank masses are sized from maximum flow/head/power over the entire pass, so the low-pressure recovery tail can set head. This is not adaptive stage selection. These are explicit engineering assumptions to revisit, not first-principles requirements.','',
 'The first-bank Reynolds number improves from about 466 at 90 km to 46,727 at 60 km. Yet efficiency remains 75% in both cases. The model therefore does not credit improved aerodynamic efficiency or a different viable rotor design at higher density. Conversely, it has not established that 75% is possible at the lower Re. That uncertainty can change the comparison.','',
 '## Where the dry mass goes','',
 '![Component contributions to payoff](../../docs/images/altitude_mass_drivers.svg)','',
 '| Component | 90 km mass (t) | 60 km mass (t) | 90 km payoff contribution (days) | 60 km contribution (days) |','|---|---:|---:|---:|---:|']
 groups={'All compressors':['compressor_hot','compressor_warm','compressor_coast'],'Perigee thrusters':['propulsion_hardware'],'Solar arrays':['solar'],'Batteries':['battery'],'Power distribution':['power_distribution'],'Front metal':['hot_metal'],'Warm radiator/buffer':['warm_radiator','warm_buffer'],'Design margin':['design_margin']}
 for label,keys in groups.items():
  m=[sum(outputs[h]['masses_kg'][k] for k in keys) for h in (90,60)]
  days=[m[i]/outputs[h]['total_dry_kg']*outputs[h]['operating_mass_payoff_days'] for i,h in enumerate((90,60))]
  lines.append(f'| {label} | {m[0]/1000:,.1f} | {m[1]/1000:,.1f} | {days[0]:.1f} | {days[1]:.1f} |')
 lines+=['','A component contribution is its mass divided by net production/day, so contributions add to total payoff when every component is included. The table groups the major terms; smaller terms are omitted. Compressor fraction falls from ~3.19% to ~0.124% of dry mass. The first bank dominates compressor mass at 90 km, not whole-craft mass; at 60 km even the later banks collectively outweigh the first.','',
 'The specific mechanism is the reboost budget. The implemented equations are `J ~ m_air v`, `m_prop = J/v_e`, `E_prop = J v_e/(2 eta)`, and `P_prop = E_prop/t_burn`. At 4,000 s Isp the exhaust is 39.23 km/s; a representative 8 km/s encounter with eta=0.6 requires about 262 MJ (72.6 kWh) per kg of intercepted air for capture-only restoration. Extra impulse and leakage affect actual values.','',
 'With a 300 s burn and thruster mass 2 kg/kW, the pulse requires about 1,743 kg of thruster hardware per kg of captured air. This is the model coefficient propagated through the impulse and energy balance, not a measured mass for this spacecraft. Power distribution adds 1 kg/kW. A battery at 150 Wh/kg, 80% usable and 95% discharge efficiency needs about 637 kg per kg of captured air just for that example reboost energy. A larger batch multiplies these hardware masses almost linearly.','',
 'In the saved runs, reboost electricity rises from 294 MWh/pass at 90 km to 32,032 MWh/pass at 60 km; compressor electricity is only 3.18 and 271 MWh/pass respectively. The fixed 300 s window makes the corresponding thruster powers 3.53 GW and 384 GW. These conditional pulse-power assumptions, not the compressor, dominate the deep-dive payoff. Finite-thrust trajectory integration and validated propulsion specific mass are therefore central next steps.','',
 'Mathematically, if `M_dry ≈ M_fixed + alpha * m_batch` and net product is `beta * m_batch`, then `payoff ≈ period * [M_fixed/(beta*m_batch) + alpha/beta]`. The first term improves as collection rises; the second reaches a density-independent floor for fixed period and capabilities. That is the plateau in this sweep.','',
 '## Apogee: more energy per installed solar area, fewer passes','',
 'The prior sweep did hold apogee fixed. It was not an altitude/apogee optimization. The model compensates for deeper dives by adding arrays, not by requiring a longer orbit. Increasing coast duration is an alternative way to supply per-pass energy and reduce processing power. It does not by itself shrink the energy the battery must deliver while stowed or the thrust required in the same 300 s window.','',
 '| Perigee | Apogee | Orbit (h) | Deployed sunlight (h) | Dry mass (t) | Net product (kg/pass) | Payoff (days) | Screens |','|---:|---:|---:|---:|---:|---:|---:|---|']
 apo=json.loads((root/'results/altitude_sensitivity/apogee/summary.json').read_text())
 for h in (60,80,90):
  o=outputs[h];lines.append(f"| {h} | 937 | {o['cycle']['orbit_s']/3600:.3f} | {o['cycle']['sunlit_s']/3600:.3f} | {o['total_dry_kg']/1000:,.0f} | {o['net_liquid_equivalent_kg']:,.0f} | {o['operating_mass_payoff_days']:,.1f} | Pass |")
  for r in [r for r in apo if r['perigee_km']==h]:
   if 'error' in r:lines.append(f"| {h} | {r['apogee_km']} | — | — | — | — | — | {r['error']} |")
   else:lines.append(f"| {h} | {r['apogee_km']:,} | {r['period_h']:.3f} | {r['sunlight_h']:.3f} | {r['dry_t']:,.0f} | {r['net_kg_pass']:,.0f} | {r['payoff_days']:,.1f} | {'Pass' if r['screens_pass'] else 'FAIL oxygen'} |")
 lines+=['','For example, at 80 km, moving apogee from 937 to 10,000 km reduces solar mass from 29,743 to 3,140 t and total mass from 145,503 to 59,345 t. However, net collection per pass falls from 18,945 to 8,049 kg and the period grows from 1.580 to 3.373 h. The more eccentric orbit crosses the dense altitude band faster and its higher encounter speed raises impulse/energy per captured kg. Per-pass collection is an integrated atmospheric column, not simply peak density times an unchanged minute.','',
 'The larger apogee does help array and coast-plant sizing, just not enough to offset the other terms in these fixed-design cases. At 35,786 km apogee the oxygen balance also fails at fixed Isp, so those arithmetic payoff values are not sustainable-cycle predictions. Nothing here rules out a better joint solution with different throat/mouth, receiver volumes, cooling, thrust policy and compressor maps.','',
 'An idealized solar-only term illustrates the trade: `M_solar ~ E_pass/(specific_power * sunlight_per_orbit)`. Multiplying by orbital period for payoff largely cancels the benefit of longer coast when sunlight fraction is unchanged. A better sunlight fraction can still help; eclipse geometry and deploy/retract dead time are included in these runs. Pulse hardware and storage terms generally do not enjoy that cancellation.','',
 '## Reproduction and scope','',
 'Run `.venv/bin/python -m atmo_scoops.studies.apogee_diagnostic`, then `.venv/bin/python -m atmo_scoops.studies.altitude_mechanism`. The [saved apogee cases](../../results/altitude_sensitivity/apogee/summary.json) retain complete inputs and constraints. Their integration horizon is limited to the 999 km atmosphere altitude when necessary; every reported completed case reaches pressure cutoff before that horizon. No density above the atmosphere table is extrapolated.','',
 'The apogee diagnostics use 401 samples and are screening runs, not a globally optimized or independently converged family. The original altitude convergence checks remain in the main report. No model physics or capability coefficients were changed for this investigation. Operating-orbit payoff excludes circular-apogee delivery. PCM coolers are a separate [design investigation](../../docs/PHASE_CHANGE_COOLERS.md), with no numerical credit here.','']
 report='\n'.join(lines)
 if (root/'results/altitude_sensitivity/limited_reference/summary.json').exists():
  from .limited_reference_report import section
  report+='\n\n'+section(root)
 (root/'investigations/altitude_sensitivity/MECHANISM.md').write_text(report)
 fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained');bottom=[0.,0.]
 for name,keys in groups.items():
  vals=[sum(outputs[h]['masses_kg'][k] for k in keys)/outputs[h]['total_dry_kg']*outputs[h]['operating_mass_payoff_days'] for h in (90,60)]
  ax.bar(['90 km','60 km'],vals,bottom=bottom,label=name);bottom=[a+b for a,b in zip(bottom,vals)]
 vals=[outputs[h]['operating_mass_payoff_days']-bottom[i] for i,h in enumerate((90,60))];ax.bar(['90 km','60 km'],vals,bottom=bottom,label='Other')
 ax.set_ylabel('Contribution to operating payoff (days)');ax.set_title('Why deeper collection reaches a plateau\nFixed 937 km apogee; 300 s reboost; resized hardware');ax.legend(loc='upper left',bbox_to_anchor=(1,1),fontsize=9)
 for ext in ('png','svg'):fig.savefig(root/f'docs/images/altitude_mass_drivers.{ext}',dpi=160)
 plt.close(fig)

if __name__=='__main__':main()
