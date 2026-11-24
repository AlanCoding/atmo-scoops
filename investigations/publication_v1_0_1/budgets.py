"""Additive stowed volume and electrical budgets from the frozen design."""
from pathlib import Path
import json,gzip,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];r=json.load(gzip.open(ROOT/'results/transient/valve_restore/selected_refined.json.gz','rt'));hw=r['hardware'];d=r['inputs']['design'];c=r['inputs']['capabilities'];m=hw['masses_kg'];pack=hw['stage_packing'];A=math.pi*d['bore_m']**2/4
PACKAGE_LABELS = {
 'solar': 'Folded solar arrays', 'warm_radiator': 'Folded waste-heat radiators',
 'battery': 'Batteries', 'warm_store': 'Waste-heat buffer',
 'machines': 'Cryogenic plant, power electronics and machinery',
 'liquid_tanks': 'Liquid-product tanks',
 'gas_reserve_system': 'Reserve valve and feed hardware (tank excluded)',
}
def package_label(key): return PACKAGE_LABELS.get(key, key.replace('_', ' '))
rows=[]
def row(label,volume,where,kind='additive envelope'):rows.append(dict(component=label,volume_m3=volume,location=where,kind=kind))
for i,(g,s,b) in enumerate(zip(hw['geometry'][:4],pack['stages'],hw['banks'])):
 row(f'Volume {i+1}: free gas',g['gas_m3'],f'{s["gas_start_m"]:.3f}–{s["gas_end_m"]:.3f} m')
 row(f'Rack {i+1}: solid',g['solid_m3'],'Inside corresponding gas chamber')
 row(f'Volume {i+1}: head/shape allowance',A*g['depth_m']-g['gross_m3'],'Same chamber envelope')
 row(f'Compressor {i+1}: axial envelope',A*b['bank_length_m'],f'{s["compressor_start_m"]:.3f}–{s["compressor_end_m"]:.3f} m')
 row(f'Hatch equipment {i+1}: envelope',A*d['stage_hatch_buffer_m'],f'{s["hatch_start_m"]:.3f}–{s["hatch_end_m"]:.3f} m')
g=hw['geometry'][4]
row('Main receiver free gas',g['gas_m3'],'48.097–192 m; narrowed barrel')
row('Receiver rack solid',g['solid_m3'],'Inside main receiver')
for k,v in pack['aft_packages_m3'].items():row(package_label(k),v,'Around main receiver, before x=192 m')
row('Aft packing clearance',pack['aft_displacement_m3']-sum(pack['aft_packages_m3'].values()),'Around main receiver')
row('Main receiver head/shape allowance',A*g['depth_m']-g['gross_m3']-pack['aft_displacement_m3'],'Main receiver ends')
row('Thruster reserve free gas',hw['gas_system']['usable_internal_m3'],'192–317 m; full bore')
row('Reserve head/shape allowance',A*d['reserve_depth_m']-hw['gas_system']['usable_internal_m3'],'Reserve ends')
assert abs(sum(x['volume_m3'] for x in rows)-A*hw['length_m'])<1e-6
assert min(x['volume_m3'] for x in rows)>-1e-6
machines={k:m[k]/c['machinery_kg_m3'] for k in ['coast_compressors','refrigerator','external_exchangers','separator','bus','auxiliary']}
machines['receiver_rack_mechanisms']=hw['geometry'][4]['deployed_physical_m2']*c['rack_mechanism_kg_m2']/c['machinery_kg_m3']
assert abs(sum(machines.values())-pack['aft_packages_m3']['machines'])<1e-6
energy=json.loads((ROOT/'investigations/subsystem_payoff/results.json').read_text())['energy']
result=dict(volume_rows=rows,aft_package_m3=pack['aft_packages_m3'],aft_machinery_detail_m3=machines,internal_bore_envelope_m3=A*hw['length_m'],external_hull_envelope_m3=math.pi*hw['outside_m']**2/4*hw['length_m'],energy=energy)
Path(__file__).with_name('budgets.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# v1.0.1 folded volume and cycle energy budgets','', 'Derived from the same frozen trajectory as the current scale drawing. Reproduce with `PYTHONPATH=. .venv/bin/python investigations/subsystem_payoff/calculate.py` then `.venv/bin/python investigations/publication_v1_0_1/budgets.py`.','', '## Additive stowed envelope','', f'The 30 m bore × 317 m hull gives **{A*hw["length_m"]:,.1f} m³** of internal cylindrical envelope. The 31.7 m external cylinder is **{result["external_hull_envelope_m3"]:,.1f} m³**; the difference is the radial hull/clearance zone, not available tank space. The following rows sum to the internal envelope.','', '| Item | Volume m³ | Location / drawing region |','|---|---:|---|']
for x in rows:lines.append(f'| {x["component"]} | {x["volume_m3"]:,.2f} | {x["location"]} |')
lines+=['','Rack **solid volume** is additive; the porous rack envelope contains gas already counted in free gas volume. Do not add its full envelope again. Compressor/hatch rows are installed axial envelopes, not solid metal volumes. Vessel-head/shape allowances are geometrical residuals, not additional gas. Detailed shell/support occupation remains a reduced-model allowance rather than a collision-free CAD inventory.','', '## Folded equipment around the main receiver','', 'The waste-heat buffer absorbs equipment heat pending radiator rejection; it is not stored warmth for a heating service. Reserve valve/feed hardware excludes the 87,301 m³ reserve gas volume, which is counted separately above. These packages are included in the additive table, not extra volume. The model divides their sum by 0.7 to allow packing/service clearance; this narrows the receiver once. Symbols in the scale picture identify sectors, but their drawn strip lengths do not individually encode these volumes. Use the table for 3D sizing, not the thickness of a symbolic strip.','', '| Package | Stowed volume m³ |','|---|---:|']
for k,v in pack['aft_packages_m3'].items():lines.append(f'| {package_label(k)} | {v:,.2f} |')
lines+=['', 'The machinery package breaks down as follows:','','| Machinery | m³ |','|---|---:|']
for k,v in machines.items():lines.append(f'| {k.replace("_"," ")} | {v:,.2f} |')
lines+=['','Solar volume uses 40 kW/m³ of rated output; warm radiator uses 0.02 m³ per physical m²; machinery uses 250 kg/m³. These are capability allowances, not measured package designs. Liquid tanks occupy 24 m³ including a 20% packaging factor around 20 m³ rated liquid capacity. Thrusters are external: no internal gas displacement is charged to them. Mass contingency has no standalone volume; general packing clearance is separately explicit.','', '## Electrical energy per orbit','', '| Load/source | MWh/orbit |','|---|---:|']
labels=[('Thrust','thrust_electric_MWh'),('Dive motors, spinup, idle and channel-loss surcharge','dive_motors_spin_idle_loss_MWh'),('Coast compression, liquefaction and separation','coast_compression_liquefaction_separation_MWh'),('Cryogenic holding','cryo_holding_MWh'),('Auxiliary electrical load','auxiliary_MWh'),('Total delivered electrical load','load_integral_MWh'),('Battery conversion losses','battery_loss_MWh'),('Solar energy actually used (integrated ledger)','solar_used_ledger_MWh')]
for label,key in labels:lines.append(f'| {label} | {energy[key]:.6f} |')
lines+=['','Battery charging and discharge are transfers, not extra end-use loads: charge input **%.3f MWh**, discharge output **%.3f MWh**. Their difference is the conversion loss above, with negligible net stored-energy change. Do not add charging again to the delivered loads.'%(energy['battery_charge_input_MWh'],energy['battery_output_MWh']), '', '## Thermal and mechanical energy — separate ledger views','', f'Warm-loop radiation: **{energy["warm_radiated_MWh"]:.3f} MWh**; direct solid-rack radiation: **{energy["solid_radiated_MWh"]:.3f} MWh**. Total gas-compression shaft work: **{energy["shaft_work_MWh"]:.3f} MWh**. Rack-friction electricity: **{energy["rack_friction_electric_MWh"]:.3f} MWh**, already included in compressor/processing loads. These are not additional electrical demands to add to the table. Thermal energy includes captured-gas enthalpy as well as dissipated electrical work.', '', 'Timing matters: these are integrated energies, not installed power or battery capacity. The frozen battery is 332.778 MWh and the bus is 760 MW; neither equals an energy-per-cycle row. Shared-hardware attribution is explained in the [subsystem payoff study](../subsystem_payoff/README.md).','', '![Folded packages](../../docs/images/v1_0_1_folded_volume.svg)','', '![Electrical energy](../../docs/images/v1_0_1_energy.svg)']
Path(__file__).with_name('BUDGETS.md').write_text('\n'.join(lines)+'\n')
plt.rcParams['svg.fonttype']='none'
def save(fig,name):
 for ext in ['png','svg']:
  p=ROOT/f'docs/images/v1_0_1_{name}.{ext}';fig.savefig(p,dpi=160)
  if ext=='svg':p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
 plt.close(fig)
# One additive chart for the complete internal envelope.
groups = {
 'Thruster reserve: gas space': hw['gas_system']['usable_internal_m3'],
 'Main receiver: gas space': g['gas_m3'],
 'Four front chambers: gas space': sum(x['gas_m3'] for x in hw['geometry'][:4]),
 'Compressors': sum(A*b['bank_length_m'] for b in hw['banks']),
 **{package_label(k):v for k,v in pack['aft_packages_m3'].items()},
 'Packing / service clearance': pack['aft_displacement_m3']-sum(pack['aft_packages_m3'].values()),
 'All cooling-rack solids': sum(x['solid_m3'] for x in hw['geometry']),
 'Hatch equipment envelopes': 4*A*d['stage_hatch_buffer_m'],
}
groups['Tank heads / shape allowances'] = A*hw['length_m']-sum(groups.values())
assert abs(sum(groups.values())-sum(x['volume_m3'] for x in rows)) < 1e-6
fig,ax=plt.subplots(figsize=(13,8),layout='constrained')
items=sorted(groups.items(),key=lambda item:item[1])
bars=ax.barh([k for k,v in items],[v for k,v in items],color='#247c8c')
ax.bar_label(bars,labels=[f'{v:,.0f} m³' for k,v in items],padding=4,fontsize=9)
ax.set(xlabel='Allocated volume (m³)',
 title='v1.0.1 stowed spacecraft volume — 224,074 m³ internal envelope',
 xlim=(0,max(groups.values())*1.24))
ax.grid(axis='x',alpha=.2)
save(fig,'folded_volume')
fig,ax=plt.subplots(figsize=(10,5),layout='constrained');items=[(l,energy[k]) for l,k in labels[:5]]+[('Battery conversion losses',energy['battery_loss_MWh'])];ax.barh([k for k,v in items],[v for k,v in items],color='#b76327');ax.set(xlabel='Electrical energy (MWh per orbit)',title='v1.0.1 electrical energy budget');ax.grid(axis='x',alpha=.2);save(fig,'energy')
print(json.dumps({k:v for k,v in result.items() if k not in ('volume_rows','energy')},indent=2))
