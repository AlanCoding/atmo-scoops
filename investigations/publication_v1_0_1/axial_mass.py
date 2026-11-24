"""Stowed axial attribution of frozen v1.0.1 masses; no cycle rerun."""
from pathlib import Path
import gzip,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
r=json.load(gzip.open(ROOT/'results/transient/valve_restore/selected_refined.json.gz','rt'))
h=r['hardware'];d=r['inputs']['design'];c=r['inputs']['capabilities'];m=h['masses_kg'];p=h['stage_packing'];g=h['geometry'];rows=[]
def add(name,key,mass,a,b):rows.append(dict(name=name,category=key,mass_kg=mass,x0_m=a,x1_m=b,centroid_m=(a+b)/2))
for i,s in enumerate(p['stages']):
 add(f'Compressor {i+1}','dive_compressors',h['banks'][i]['total_kg'],s['compressor_start_m'],s['compressor_end_m'])
 add(f'Rack {i+1}','racks',g[i]['mass_kg'],s['rack_start_m'],s['rack_end_m'])
 add(f'Rack mechanism {i+1}','rack_mechanisms',g[i]['deployed_physical_m2']*c['rack_mechanism_kg_m2'],s['hatch_start_m'],s['hatch_end_m'])
a=p['receiver_start_m'];b=p['receiver_end_m'];hd=c['head_depth_m']
add('Receiver rack','racks',g[4]['mass_kg'],a+hd,a+hd+g[4]['rack_depth_m'])
# Uniform packing capacity along narrowed receiver, assign heavy packages forward.
packages=p['aft_packages_m3'];capacity=sum(packages.values())/(b-a);pos=a
machine_keys=['bus','coast_compressors','refrigerator','external_exchangers','separator','auxiliary']
items=[('battery',m['battery'],packages['battery'])]
items += [(k,m[k],m[k]/c['machinery_kg_m3']) for k in machine_keys]
mech=g[4]['deployed_physical_m2']*c['rack_mechanism_kg_m2']
items += [('rack_mechanisms',mech,mech/c['machinery_kg_m3'])]
items += [(k,m[k],packages[k]) for k in ['warm_store','liquid_tanks','gas_reserve_system','warm_radiator','solar']]
for k,mass,vol in items:
 end=pos+vol/capacity;add(k,k,mass,pos,end);pos=end
assert abs(pos-b)<1e-6
# Whole thruster mass placed at tail; remote power electronics remain in bus above.
add('Aft thruster assemblies','thrusters',m['thrusters'],317,322)
for i in range(1,5):
 radius=p['receiver_radius_m'] if i==4 else d['bore_m']/2
 L=g[i]['depth_m'];rating=d['rated_pressure_Pa'][i-1]
 barrel=2*math.pi*radius*(L-2*hd);heads=2*math.pi*(radius**2+hd**2);R=(radius**2+hd**2)/(2*hd)
 mass=(barrel*max(.001,1.5*rating*radius/150e6)+heads*max(.001,1.5*rating*R/(2*150e6)))*2700*1.5+barrel+heads
 lo=a if i==4 else p['stages'][i]['gas_start_m']
 add(f'Vessel {i+1}','pressure_vessels',mass,lo,lo+L)
add('Reserve shell','pressure_vessels',h['gas_system']['shell_and_support_kg'],192,317)
add('Hull','hull',m['hull'],0,317)
for k,v in m.items():
 if k!='margin':assert abs(sum(q['mass_kg'] for q in rows if q['category']==k)-v)<1e-5,k
base=sum(q['mass_kg'] for q in rows);cm=sum(q['mass_kg']*q['centroid_m'] for q in rows)/base
assert abs(base+m['margin']-r['dry_kg'])<1e-5
labels={'racks':'Cooling racks','rack_mechanisms':'Rack deployment mechanisms','dive_compressors':'Dive compressors','coast_compressors':'Coast compressors','refrigerator':'Refrigeration plant','external_exchangers':'Cryogenic heat exchangers','separator':'Separator','bus':'Power electronics / bus','thrusters':'Aft thrusters','warm_store':'Waste-heat buffer','warm_radiator':'Folded waste-heat radiators','solar':'Folded solar arrays','battery':'Batteries','liquid_tanks':'Liquid-product tanks','auxiliary':'Auxiliary hardware','gas_reserve_system':'Reserve valve / feed hardware','pressure_vessels':'Pressure-vessel shells','hull':'Hull'}
def center(k):return sum(q['mass_kg']*q['centroid_m'] for q in rows if q['category']==k)/m[k]
keys=sorted(labels,key=center)
fig,(ax,ac)=plt.subplots(2,1,figsize=(13,10),gridspec_kw={'height_ratios':[4,1]},layout='constrained')
for y,k in enumerate(keys):
 for q in rows:
  if q['category']==k:ax.broken_barh([(q['x0_m'],q['x1_m']-q['x0_m'])],(y-.32,.64),facecolors=plt.cm.tab20(y/20))
 ax.plot(center(k),y,'ko',ms=3)
ax.set_yticks(range(len(keys)),[f'{labels[k]} ({m[k]/1000:,.0f} t)' for k in keys]);ax.invert_yaxis()
ax.axvline(cm,color='#c94040',label=f'Dry CM: {cm:.1f} m');ax.legend(loc='lower right');ax.set_xlim(0,325);ax.grid(axis='x',alpha=.2)
ax.set_title('v1.0.1 · Stowed axial mass distribution\nBars: assigned spans; dots: subsystem centroids. Equipment positions remain provisional.',loc='left')
xx=np.linspace(0,325,2000);cum=sum(q['mass_kg']*np.clip((xx-q['x0_m'])/(q['x1_m']-q['x0_m']),0,1) for q in rows)/base
ac.plot(xx,cum*100,color='#247c8c');ac.axvline(cm,color='#c94040');ac.set(xlim=(0,325),ylim=(0,102),xlabel='Distance aft from mouth (m)',ylabel='Cumulative dry mass (%)');ac.grid(alpha=.2)
for stem in ['v1_0_1_axial_mass','v1_axial_mass']:
 for ext in ['svg','png']:
  out=ROOT/f'docs/images/{stem}.{ext}';fig.savefig(out,dpi=160)
  if ext=='svg':out.write_text('\n'.join(x.rstrip() for x in out.read_text().splitlines())+'\n')
report=dict(source='results/transient/valve_restore/selected_refined.json.gz',dry_kg=r['dry_kg'],dry_CM_m=cm,rows=rows)
Path(__file__).with_name('axial_mass.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# v1.0.1 stowed axial mass allocation','',f'Dry CM **{cm:.2f} m from the mouth ({100*cm/317:.1f}% of hull length)**. Dry mass **{r["dry_kg"]/1000:,.2f} t**. This is an assigned packaging estimate, not an optimized CM or aerodynamic stability result.','', 'Masses and chamber/compressor/rack locations use the accepted frozen cycle. Receiver equipment is placed sequentially forward-to-aft within 48.097–192 m using its modeled package volumes and uniform available packing capacity: batteries, power electronics and processing machinery first; solar cassettes last. This refines the symbolic equipment strips in the scale drawing; those strip lengths were not measured package dimensions. The entire thruster mass is assigned to 317–322 m, an illustrative external hardware span. Actual separation of thruster heads and remote electronics needs engineering.','', 'Vessel shell masses use the model barrel/head expression, distributed uniformly over each vessel. Hull mass is uniform; 25% margin follows component masses proportionally and does not shift CM. Rack mechanisms use deployed area to allocate mass. No wet inventory or deployed position is included.','', 'This moves CM aft relative to the obsolete forward-pod layout. Stability still requires an aerodynamic center behind CM with adequate restoring derivatives; this mass calculation alone cannot establish that. A 10 m shift of all thruster hardware moves CM by %.2f m under the proportional-margin convention.'%(m['thrusters']/base*10),'','| Component | Mass (t), before margin | Axial span (m) |','|---|---:|---|']
for q in rows:lines.append(f'| {labels[q["category"]]} / {q["name"]} | {q["mass_kg"]/1000:,.2f} | {q["x0_m"]:.2f}–{q["x1_m"]:.2f} |')
lines+=['', 'Reproduce: `.venv/bin/python investigations/publication_v1_0_1/axial_mass.py`. Component sums are asserted against every frozen mass category.','', '![Axial mass](../../docs/images/v1_0_1_axial_mass.svg)']
Path(__file__).with_name('AXIAL_MASS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(CM_m=cm,solar_span=[q for q in rows if q['category']=='solar']),indent=2))
