"""Generate the finite-rack investigation and scientific comparison figure."""
from pathlib import Path
import json,math,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/finite_rack_limits'

def main():
 rows=json.loads((DATA/'reference_1mm/summary.json').read_text())
 ref=json.loads((DATA/'reference_1mm/apogee_2000.json').read_text());o=ref['outputs'];pack=o['packaging'];A=math.pi*30**2/4
 radius=json.loads((DATA/'radius_trade/summary.json').read_text())
 sensitivity=json.loads((DATA/'packaging_sensitivity.json').read_text())
 long=json.loads((DATA/'long_rear.json').read_text())['outputs']
 table=['| Apogee km | Perigee km | Rear depth m | Total length m | Storage bar | Dry tonnes | Net tonnes/pass | Operating payoff days |', '|---:|---:|---:|---:|---:|---:|---:|---:|']
 for x in rows:table.append(f"| {x['apogee_km']:,.0f} | {x['perigee_km']:.2f} | {x['rear_depth_m']:.2f} | {x['length_m']:.2f} | {x['pressure_Pa']/1e5:.3f} | {x['dry_t']:,.0f} | {x['net_kg_pass']/1000:.3f} | {x['payoff_days']:.1f} |")
 lines=['# Finite metal racks and the constrained reference','',
 '**Scope:** current reduced model, L/D ≤ 10 and rear storage ≤ 110 kPa. These are conditional package/thermal screens, not demonstrated flight feasibility or a global optimization. Payoff is in the operating orbit; circular-apogee delivery remains unimplemented.','',
 '## What changed','',
 'The front chamber now integrates gas and metal energy with finite convection. Each of the three interstage racks has independent mass, finite heat capacity, convection, pore volume and residual gas loss. The lattice sets minimum chamber dimensions. Pressure loss through the metal is intentionally omitted. Compressor blocks use real-fluid isentropic-efficiency states at the resulting time-dependent inlet temperatures. Folded hardware contributes explicit volume; deployment and retraction take finite time at 10 m/s. The fixed machinery bay is gone.','',
 'Equations, assumptions and approximation limits: [finite racks](../../modeling/metal_coolers/FINITE_RACK_MODEL.md), [folded volume/timing](../../modeling/deployment/IMPLEMENTED_VOLUME.md), [compressor mass evidence](../../modeling/compressor/COMPARABLE_SYSTEMS.md).','',
 '## Constraint-driven cases','',
 'Common geometry: 30 m inner/mouth diameter, 31.7 m outer diameter, maximum length 317 m. Radius/pitch = 0.10, so metal occupies 3.14% of each lattice envelope. These cases use 1 mm wire radius, selected from the discrete comparison below. Four rack masses use the explicit capacity-based sizing rule and independent multipliers of 1.5. Each is overridable through `racks.masses_kg`.','',
 'For each of three fixed apogees, the search varied perigee and rear depth toward the simultaneous length and storage-pressure boundaries. Final cases step slightly inside the boundaries and are re-evaluated with 801 samples. All implemented screens pass. No material survivability boundary has been supplied; the altitude limits here arise from the stated numerical hardware/packaging assumptions.','',*table,'',
 'Higher apogee allows a somewhat deeper pass, but does not improve payoff in these samples. The rate of useful production per day falls with the longer orbit while power hardware remains expensive. Neither a globally best apogee nor a fully optimized rack allocation is claimed.','',
 '## The long rear tank is still available','',
 f"A separate **85 × 2,000 km** case fits a **95 m physical rear vessel** into **{long['overall_length_allowance_m']:.2f} m total length**, with storage at **{long['rear_pressure_Pa']/1000:.2f} kPa**. It yields **{long['net_liquid_equivalent_kg']/1000:.3f} tonnes/pass**, weighs **{long['total_dry_kg']/1000:,.0f} tonnes dry**, and gives **{long['operating_mass_payoff_days']:.1f} days** operating payoff. All implemented screens pass. Warm storage below the nitrogen triple-point pressure is allowed because the coast compressor subsequently feeds the separate approximately 1 bar liquefaction train.",'',
 'Thus the short rear vessel in the deepest cases is a result of this particular boundary objective and package allocation, not an imposed 100 m equipment bay. A longer rear vessel and shallower pass have almost the same payoff under these coefficients.','',
 '## Wire thickness has an actual thermal trade','',
 'Fixed 85 × 2,000 km orbit, 16 m rear depth, the same mass-sizing rule and r/p. Holding r/p fixes metal fraction and working envelope at a given metal mass; changing radius changes surface area, heat transfer, deployment footprint and cooler radiation time.','',
 '| Wire radius mm | Peak pumping inlet K | Dry tonnes | Net tonnes/pass | Payoff days |', '|---:|---:|---:|---:|---:|']
 for x in radius:
  if 'error' not in x:lines.append(f"| {x['radius_m']*1000:g} | {x['gas_peak_K']:.0f} | {x['dry_t']:,.0f} | {x['net_kg_pass']/1000:.3f} | {x['payoff_days']:.1f} |")
 lines += ['', 'Very fine wires give excellent cooling but require a much larger deployed mesh footprint and more deployment hardware under the current area-based mechanism allowance. At 3 mm, gas heating and reduced collection offset the remaining mass saving. A 1 mm radius is the best of these four samples, not a fitted universal optimum.','',
 '## Detailed 2,000 km-apogee boundary case','',
 f"The orbit lasts **{o['cycle']['orbit_s']/60:.1f} minutes**. Full deployment takes **{o['cycle']['deploy_s']:.1f} s**; the fully deployed coast interval is **{o['cycle']['deployed_s']/60:.1f} min**. Retraction takes the same time. Strong collection follows the atmospheric pulse; the program does not impose a rectangular one-minute scoop.",'',
 '| Allocation | Physical/equivalent depth m |', '|---|---:|',
 f"| Front working rack/chamber | {pack['front_depth_m']:.2f} |",
 f"| Three interstage rack chambers, total | {pack['interstage_rack_depth_m']:.2f} |",
 f"| Equipment packages plus installation space | {pack['equipment_equivalent_depth_m']:.2f} |",
 f"| Rear tank including heads | {pack['rear_depth_m']:.2f} |",'',
 'Equipment equivalent depth is volume divided by bore area, not a CAD-certified axial arrangement. Each rack chamber contains gas in its pores, not an empty space added on top of the rack envelope.','',
 '| Deployed system | Physical footprint m² | Travel time s |','|---|---:|---:|',
 f"| Solar | {o['solar_area_m2']:,.0f} | {pack['deployment_travel_s']['solar']:.1f} |",
 f"| Warm radiator | {o['warm_radiator_panel_m2']:,.0f} | {pack['deployment_travel_s']['warm_radiator']:.1f} |",
 f"| Metal wire planes | {o['metal_panel_m2']:,.0f} | {pack['deployment_travel_s']['metal_racks']:.1f} |",'',
 'Solar generation is withheld until all systems finish the conservative common deployment schedule. This charges no benefit for partial unfolding. Metal footprint includes gaps between wires; effective emitting area is separately calculated from wire surface and view factor.','',
 '| Rack | Metal tonnes | Working depth m | End temperature K | Peak-flow Re | Peak-flow Kn |', '|---|---:|---:|---:|---:|---:|']
 for i,x in enumerate(o['racks']):
  h=x['convection_at_peak_flow'];lines.append(f"| {i} | {x['mass_kg']/1000:,.2f} | {x['depth_m']:.3f} | {x['final_metal_K']:.1f} | {h['Re']:.2f} | {h['Kn']:.4g} |")
 lines += ['', 'Front-rack properties are at peak admission; intermediate properties are at peak gross compressor flow. Rarefaction matters at the wire scale even though the craft is much larger than the mean free path. Axial temperature gradients and mesh-bank correlations remain unvalidated.','',
 '| Compressor block | Inlet Pa | Inlet K | Outlet Pa | Outlet K | Installed tonnes | Peak electric MW |', '|---|---:|---:|---:|---:|---:|---:|']
 dive=o['compressor_analysis']['dive']
 for i,(b,x) in enumerate(zip(dive['banks'],dive['peak_flow_states'])):
  lines.append(f"| {i+1} | {x['inlet']['p_Pa']:,.1f} | {x['inlet']['T_K']:.1f} | {x['outlet']['p_Pa']:,.1f} | {x['outlet']['T_K']:.1f} | {b['total_kg']/1000:,.1f} | {b['design_electric_W']/1e6:.1f} |")
 lines += ['', 'State columns are at the common peak-flow instant. Bank mass and motor columns use each bank’s time-envelope maxima, which need not occur simultaneously. The existing NASA-inspired blade/disk/case accounting now sees the calculated finite-cooling states; this is not a new empirical validation of low-density compressor mass or maps.','',
 f"Total dive plus coast compressor mass is **{o['compressor_mass_kg']/1000:,.1f} tonnes**, versus **{o['total_dry_kg']/1000:,.0f} tonnes dry** overall. Peak reboost electric power is **{o['reboost_peak_MW']/1000:.2f} GW** over the declared 300 s burst; solar bus power is **{o['solar_MW']/1000:.2f} GW**.",'',
 '| Mass contribution | Tonnes |', '|---|---:|']
 for k,v in sorted(o['masses_kg'].items(),key=lambda x:-x[1]):lines.append(f"| {k.replace('_',' ')} | {v/1000:,.1f} |")
 lines += ['', 'The large mass is principally an electric-propulsion/power-system result, not a condenser or compressor result. The retained assumptions include 2 kg/kW of thruster hardware, 1 kg/kW of distribution, and 1.5 kW/kg battery power capability. These are explicit unvalidated scoop-system capability assumptions. Short, high-power reboost makes them expensive.','',
 '## How much of the length limit is a packaging assumption?','',
 'Keep the boundary design and all mass/power coefficients fixed, but change the provisional bulk envelope density used for plant, motors, propulsion/distribution and deployment packages. These are sensitivity scenarios, not three proven hardware options.','',
 '| Bulk envelope density kg/m³ | Total length m | Operating payoff days |','|---:|---:|---:|']
 for x in sensitivity:lines.append(f"| {x['density_kg_m3']:.0f} | {x['length_m']:.1f} | {x['payoff_days']:.1f} |")
 lines += ['', 'This large length variation means the nominal deepest perigee is **not established independently of package design**. The 250 kg/m³ coefficient must not acquire the authority of the discarded 100 m bay. It is visible, adjustable, and bracketed here. Solar packing has a published reference; folded radiator stack pitch and complete plant/propulsion envelopes still need component designs.','',
 'Intermediate gas is explicitly accounted for, but only in a small-holdup approximation: current series-flow states do not optimize independent compressor schedules or significant storage in intermediate chambers. Cases above 1% maximum intermediate hold-up are rejected from this reduced-model family. Full transient stage matching, shock stability, reusable heating limits, structural/hatch design, and circular-orbit export remain unresolved.','',
 '## Reproduction and verification','',
 '```sh', '.venv/bin/python -m atmo_scoops --config configs/finite_rack_reference.json',
 '.venv/bin/python -m atmo_scoops.studies.rack_radius_trade', '.venv/bin/python -m atmo_scoops.studies.finite_rack_limits',
 '.venv/bin/python -m atmo_scoops.studies.refresh_finite_racks', '.venv/bin/python -m atmo_scoops.studies.long_rear_reference',
 '.venv/bin/python -m atmo_scoops.studies.finite_rack_validation',
 'MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.finite_rack_report',
 '.venv/bin/python -m pytest -q', '.venv/bin/python -m atmo_scoops.audit', '```','',
 'Saved JSON contains exact inputs, states, component budgets and constraint margins. See [results](../../results/finite_rack_limits/reference_1mm/summary.json) and [additional convergence checks](../../results/finite_rack_limits/verification.json). The general audit retains its strict conservation/resolution checks; new tests cover lattice geometry, rarefaction, the zero-conductance limit, finite capacity, gas displacement, deployment feedback and removal of the arbitrary bay.','',
 '![Finite rack trade and conditional boundary cases](../../docs/images/finite_rack_trade.png)','']
 (ROOT/'investigations/altitude_sensitivity/FINITE_RACK_LIMITS.md').write_text('\n'.join(lines))
 mech=ROOT/'investigations/altitude_sensitivity/MECHANISM.md';s=mech.read_text();marker='<!-- finite-rack-update -->';s=s.split(marker)[0].rstrip()
 mech.write_text(s+'\n\n'+marker+'\n\n## Current finite-rack and package-constrained cases\n\nThe fixed 100 m bay is replaced by finite convection, working lattice volumes, equipment envelopes and area-dependent deployment. Detailed equations, the radius trade, mass drivers and packaging uncertainty are in the [finite-rack investigation](FINITE_RACK_LIMITS.md). These are conditional operating-orbit payoffs, not circular-delivery or survivability results.\n\n'+'\n'.join(table)+f"\n\nA longer-tank alternative at 85 × 2,000 km fits a **95 m rear tank**, **{long['overall_length_allowance_m']:.1f} m total length**, and yields **{long['operating_mass_payoff_days']:.1f} days**.\n")
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained')
 good=[x for x in radius if 'error' not in x]
 axes[0].semilogx([x['radius_m']*1000 for x in good],[x['payoff_days'] for x in good],'o-',color='#16697a')
 axes[0].set(xlabel='Wire radius (mm)',ylabel='Operating payoff (days)',title='Fixed 85 × 2,000 km orbit')
 axes[1].plot([x['apogee_km'] for x in rows],[x['payoff_days'] for x in rows],'o-',color='#c75b39')
 axes[1].set(xlabel='Apogee altitude (km)',ylabel='Operating payoff (days)',title='L/D and pressure boundary cases')
 labels=['Front rack','Interstage racks','Equipment','Rear tank'];vals=[pack['front_depth_m'],pack['interstage_rack_depth_m'],pack['equipment_equivalent_depth_m'],pack['rear_depth_m']]
 axes[2].barh(labels,vals,color=['#16697a','#3f9c9c','#c75b39','#64748b']);axes[2].invert_yaxis()
 axes[2].set(xlabel='Physical / volume-equivalent depth (m)',title='2,000 km-apogee allocation')
 fig.suptitle('Finite metal racks: conditional model results — operating orbit only',fontsize=14)
 fig.savefig(ROOT/'docs/images/finite_rack_trade.png',dpi=160)
 plt.close(fig)
 (DATA/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'atmo_scoops').rglob('*.py')},indent=2)+'\n')

if __name__=='__main__':main()
