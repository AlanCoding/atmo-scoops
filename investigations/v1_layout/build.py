"""Provisional axial allocation of existing masses; no forward-model changes."""
from pathlib import Path
import gzip,json,math,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.orbit import Orbit,MU,R_EARTH
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'results/transient/plates/reference_validation/case_72.json.gz'
r=json.load(gzip.open(src,'rt'));h=r['hardware'];d=r['inputs']['design'];c=r['inputs']['capabilities'];m=h['masses_kg'];g=h['geometry'];A=math.pi*d['bore_m']**2/4
rows=[]
def add(name,key,mass,a,b,volume=0):
 rows.append(dict(name=name,category=key,mass_kg=mass,x0_m=a,x1_m=b,centroid_m=(a+b)/2,package_m3=volume))
# Interleave all existing chamber depths and all 59.62 m of equipment bay.
bay_lengths=[12.,10.,10.,h['bay_m']-32.];bays=[];chambers=[];x=0
for i,L in enumerate(bay_lengths):
 chambers.append((x,x+g[i]['depth_m']));x=chambers[-1][1];bays.append((x,x+L));x+=L
chambers.append((x,x+g[4]['depth_m']));assert abs(chambers[-1][1]-317)<1e-8
foot=[v['deployed_physical_m2'] for v in g];mechanisms=np.array(foot)/sum(foot)*m['rack_mechanisms'];capacities=[]
for i,(a,b) in enumerate(bays):
 mass=h['banks'][i]['total_kg'];vol=mass/c['machinery_kg_m3']
 assert b-a>=h['banks'][i]['bank_length_m']
 add(f'Dive compressor {i+1}','dive_compressors',mass,a,b,vol)
 mech=mechanisms[i]+(mechanisms[4] if i==3 else 0)
 add(f'Rack mechanisms {i+1}'+(' + receiver' if i==3 else ''),'rack_mechanisms',float(mech),a,b,float(mech)/c['machinery_kg_m3'])
 capacities.append(c['fill_fraction']*A-(vol+mech/c['machinery_kg_m3'])/(b-a))
# Occupy residual usable cross section sequentially. Overlap is radial sharing.
machine_keys=['coast_compressors','refrigerator','external_exchangers','separator','bus','thrusters','auxiliary']
volumes={k:m[k]/c['machinery_kg_m3'] for k in machine_keys}
volumes.update({k:v for k,v in h['packages_m3'].items() if k!='machines'})
order=[('battery',1),('bus',1),('solar',.5),('thrusters',1),('gas_reserve_system',1),('warm_store',1),('coast_compressors',1),('refrigerator',1),('external_exchangers',1),('separator',1),('solar',.5),('warm_radiator',1),('liquid_tanks',1),('auxiliary',1)]
labels={'solar':'Folded solar cassettes','bus':'Power bus / electronics','battery':'Battery modules','thrusters':'Forward external thruster pods','gas_reserve_system':'Gas propellant reserve / booster','warm_store':'Warm-loop inventory','coast_compressors':'Coast compressors','refrigerator':'Refrigerator','external_exchangers':'Cryogenic exchangers','separator':'Separator','warm_radiator':'Folded warm radiators','liquid_tanks':'Liquid product tanks','auxiliary':'Auxiliary hardware'}
bi=0;pos=bays[0][0]
for key,fraction in order:
 remaining=volumes[key]*fraction
 while remaining>1e-7:
  a,b=bays[bi];v=min(remaining,(b-pos)*capacities[bi]);end=pos+v/capacities[bi]
  add(labels[key],key,m[key]*v/volumes[key],pos,end,v);remaining-=v;pos=end
  if end>=b-1e-8 and bi<3:bi+=1;pos=bays[bi][0]
# Convert short volume-equivalent slices to plausible axial package spans.
# These share radial sectors; this is not a detailed collision/duct solution.
minimum={'gas_reserve_system':max(h['gas_system']['outer_diameter_m'],h['gas_system']['fill_bank']['bank_length_m']), 'coast_compressors':max(b['bank_length_m'] for b in h['coast_banks']), 'refrigerator':4.,'external_exchangers':2.,'separator':2.,'liquid_tanks':4.,'warm_store':6.,'auxiliary':2.,'warm_radiator':3.}
for q in rows:
 if q['category']=='thrusters':
  a,b=next((a,b) for a,b in bays if a<=q['centroid_m']<=b);q.update(x0_m=a,x1_m=b,centroid_m=(a+b)/2)
 if q['category'] in minimum:
  width=minimum[q['category']]
  if q['x1_m']-q['x0_m']<width:
   a,b=next((a,b) for a,b in bays if a-1e-7<=q['centroid_m']<=b+1e-7)
   q['x0_m']=min(max(a,q['centroid_m']-width/2),b-width);q['x1_m']=q['x0_m']+width;q['centroid_m']=(q['x0_m']+q['x1_m'])/2
# Redistribute folded solar cassettes over remaining radial sectors after
# minimum-length packages are placed. Preserve total volume; cap local use at
# 90% of the bore while retaining the original 70% aggregate fill budget.
rows[:]=[q for q in rows if q['category']!='solar'];slots=[]
for a,b in bays:
 edges=sorted({a,b,*[max(a,min(b,q[k])) for q in rows for k in ('x0_m','x1_m')]})
 for lo,hi in zip(edges[:-1],edges[1:]):
  mid=(lo+hi)/2;used=sum(q['package_m3']/(q['x1_m']-q['x0_m']) for q in rows if q['x0_m']<mid<q['x1_m'])
  assert used<A,(mid,used/A,[(q["category"],q["package_m3"]/(q["x1_m"]-q["x0_m"])) for q in rows if q["x0_m"]<mid<q["x1_m"]])
  slots.append((lo,hi,max(0,.90*A-used)*(hi-lo)))
room=sum(v for a,b,v in slots);assert room>=volumes['solar']
for a,b,v in slots:
 if v>0:add(labels['solar'],'solar',m['solar']*v/room,a,b,volumes['solar']*v/room)
for i,(a,b) in enumerate(chambers):
 start=a if i==0 else (a+c['head_depth_m'] if i==4 else b-c['head_depth_m']-g[i]['rack_depth_m'])
 add(f'Cooler {i+1} ({"SiC" if i==0 else "Al"})','racks',g[i]['mass_kg'],start,start+g[i]['rack_depth_m'])
# Attribute vessel mass by the exact existing barrel/head expression.
weights=[];rad=d['bore_m']/2;hd=c['head_depth_m']
for i in range(1,5):
 L=g[i]['depth_m'];p=d['rated_pressure_Pa'][i-1];barrel=2*math.pi*rad*(L-2*hd);heads=2*math.pi*(rad**2+hd**2);R=(rad**2+hd**2)/(2*hd)
 weights.append((barrel*max(.001,1.5*p*rad/150e6)+heads*max(.001,1.5*p*R/(2*150e6)))*2700*1.5+barrel+heads)
assert abs(sum(weights)-m['pressure_vessels'])<1e-6
for i,w in enumerate(weights,1):add(f'Pressure vessel {i+1}','pressure_vessels',w,*chambers[i])
add('Hull / thermal shell','hull',m['hull'],0,317)
base=sum(q['mass_kg'] for q in rows);cm=sum(q['mass_kg']*q['centroid_m'] for q in rows)/base
assert abs(base*(1+c['margin'])-r['dry_kg'])<1e-6
for key in m:
 if key!='margin':assert abs(sum(q['mass_kg'] for q in rows if q['category']==key)-m[key])<1e-6,key
# Screen local shared package volume against the full bore, not just totals.
edges=sorted(set([q[k] for q in rows for k in ('x0_m','x1_m')]))
local_occupancy=max(sum(q['package_m3']/(q['x1_m']-q['x0_m']) for q in rows if q['x0_m']<xx<q['x1_m'])/A for xx in [(a+b)/2 for a,b in zip(edges[:-1],edges[1:])])
assert abs(sum(q['package_m3'] for q in rows)-sum(h['packages_m3'].values()))<1e-6
assert local_occupancy<.9
# Distribute contingency proportionally to each physical entry, not as ballast.
dry=r['dry_kg'];t=np.array(r['time_s']);gas=np.maximum(0,np.array(r['gas_species_kg'])).sum(axis=2);liq=np.maximum(0,np.array(r['liquid_species_kg'])).sum(axis=1);reserve=np.maximum(0,np.array(r['gas_reserve_species_kg'])).sum(axis=1)
def centroid(key):
 a=[q for q in rows if q['category']==key];return sum(q['mass_kg']*q['centroid_m'] for q in a)/sum(q['mass_kg'] for q in a)
gasx=np.array([(a+b)/2 for a,b in chambers]);wet=(dry*cm+gas@gasx+liq*centroid('liquid_tanks')+reserve*centroid('gas_reserve_system'))/(dry+gas.sum(axis=1)+liq+reserve)
loaded=[]
for name,ti in [('Entry baseline',-1200),('Perigee',0),('Collection cutoff',600),('Processing stops',d['plant_stop_s'])]:
 j=np.argmin(abs(t-ti));loaded.append(dict(state=name,time_s=float(t[j]),CM_m=float(wet[j]),contents_kg=float(gas[j].sum()+liq[j]+reserve[j])))
o=Orbit(d['perigee_km'],d['apogee_km']);n=2*math.pi/o.period;p=o.a*(1-o.e**2);J2=.00108262668;rate=2*math.pi/(365.2422*86400);K=1.5*J2*n*(R_EARTH/p)**2;inc=math.acos(-rate/K);aps=.75*J2*n*(R_EARTH/p)**2*(5*math.cos(inc)**2-1)
result=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),peak_local_package_area_fraction=local_occupancy,dry_mass_kg=dry,dry_CM_m=cm,dry_CM_fraction_length=cm/317,chambers_m=chambers,equipment_bays_m=bays,components=rows,margin_rule='25% proportional to each component; no separate ballast',loaded=loaded,stowed_coordinate_wet_CM_range_m=[float(min(wet)),float(max(wet))],uniform_hull_margin_CM_m=(base*cm+m['margin']*158.5)/dry,all_margin_at_tail_CM_m=(base*cm+m['margin']*300)/dry,solar_shift_20m_CM_change_m=m['solar']/dry*20,orbit=dict(perigee_km=o.perigee_km,apogee_km=o.apogee_km,period_min=o.period/60,perigee_speed_km_s=o.h/o.rp/1000,J2_inclination_deg=math.degrees(inc),node_rate_deg_day=math.degrees(rate)*86400,apsidal_rate_deg_day=math.degrees(aps)*86400,equinox_dawn_dusk_beta_deg=180-math.degrees(inc),perigee_no_eclipse_beta_deg=math.degrees(math.asin(R_EARTH/o.rp))))
(ROOT/'investigations/v1_layout/results.json').write_text(json.dumps(result,indent=2)+'\n')
# Formal table grouped by subsystem but retaining disjoint intervals.
lines=['# v1.0 provisional axial mass register','','x=0 is the mouth; x=317 m is the tail. Ranges are **assigned**, masses come from the verified numerical reference. Components can share an axial span in different radial sectors. Centroids use uniform mass within each assigned span. This is a stowed layout.','',f'**Dry center of mass: x = {cm:.2f} m ({100*cm/317:.1f}% of length).** Dry mass: {dry/1000:,.2f} t.','', '| Component | Axial interval(s), m | Mass, t | Assigned centroid, m |','|---|---|---:|---:|']
for name in sorted(set(q['name'] for q in rows),key=lambda name:min(q['x0_m'] for q in rows if q['name']==name)):
 qs=[q for q in rows if q['name']==name];mass=sum(q['mass_kg'] for q in qs);xc=sum(q['mass_kg']*q['centroid_m'] for q in qs)/mass
 spans=[]
 for q in sorted(qs,key=lambda z:z['x0_m']):
  if spans and abs(spans[-1][1]-q['x0_m'])<1e-7:spans[-1][1]=q['x1_m']
  else:spans.append([q['x0_m'],q['x1_m']])
 lines.append(f'| {name} | '+ '; '.join(f'{a:.2f}–{b:.2f}' for a,b in spans)+f' | {mass/1000:,.2f} | {xc:.2f} |')
lines+= [f'| Margin (distributed proportionally) | Same spans as components | {m["margin"]/1000:,.2f} | {cm:.2f} |','', '## Loaded states (stowed axial coordinates)','','| State | Time from perigee, s | Carried gas/liquid, kg | CM, m |','|---|---:|---:|---:|']
for q in loaded:lines.append(f'| {q["state"]} | {q["time_s"]:.1f} | {q["contents_kg"]:.1f} | {q["CM_m"]:.3f} |')
lines+=['','Generated by `PYTHONPATH=. .venv/bin/python investigations/v1_layout/build.py`. See [interpretation and stability screen](README.md) for assumptions; [JSON register](results.json) contains all unrounded entries.']
(ROOT/'investigations/v1_layout/MASS_REGISTER.md').write_text('\n'.join(lines)+'\n')
# Scientific plot styles; explicit coordinate scale rather than a faux 3D model.
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','font.size':10})
fig,(ax,ac)=plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[4,1.2]},layout='constrained')
keys=[k for k in m if k!='margin'];keys.sort(key=lambda k:centroid(k));colors=plt.cm.tab20(np.linspace(0,1,len(keys)))
for y,(key,col) in enumerate(zip(keys,colors)):
 for q in rows:
  if q['category']==key:ax.broken_barh([(q['x0_m'],q['x1_m']-q['x0_m'])],(y-.32,.64),facecolors=col)
 ax.plot(centroid(key),y,'ko',ms=3)
ax.set_yticks(range(len(keys)),[f'{k.replace("_"," ")}  ({m[k]/1000:,.0f} t)' for k in keys]);ax.invert_yaxis();ax.set_xlim(0,317);ax.axvline(cm,color='#c94040',lw=2,label=f'Dry CM {cm:.1f} m');ax.set_xlabel('Distance aft from mouth, m');ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right');ax.set_title('v1.0 — assigned axial locations, not a resolved mechanical layout\nBars: stowed spans; dots: mass centroids; overlapping bars occupy different radial sectors',loc='left')
xx=np.linspace(0,317,1500);cum=sum(q['mass_kg']*np.clip((xx-q['x0_m'])/(q['x1_m']-q['x0_m']),0,1) for q in rows)/base
ac.plot(xx,100*cum,color='#247c8c',lw=2);ac.axvline(cm,color='#c94040');ac.set(xlim=(0,317),ylim=(0,102),xlabel='Distance aft from mouth, m',ylabel='Cumulative dry mass, %');ac.grid(alpha=.2)
for ext in ['svg','png']:fig.savefig(ROOT/f'docs/images/v1_axial_mass.{ext}',dpi=160)
plt.close(fig)
fig,ax=plt.subplots(figsize=(10,6),layout='constrained');items=sorted(m.items(),key=lambda z:z[1]);ax.barh([k.replace('_',' ') for k,v in items],[v/1000 for k,v in items],color='#247c8c');ax.set_xlabel('Installed dry mass, tonnes');ax.set_title('v1.0 mass budget — 13,250 tonnes\n25% contingency shown separately');ax.grid(axis='x',alpha=.2)
for ext in ['svg','png']:fig.savefig(ROOT/f'docs/images/v1_mass_budget.{ext}',dpi=160)
plt.close(fig)
# Equal-scale orbit plus a numerical timeline; no invented eclipse-free geometry.
fig,(ax,at)=plt.subplots(1,2,figsize=(13,6),gridspec_kw={'width_ratios':[1,1.15]},layout='constrained');E=np.linspace(0,2*np.pi,600);xx=o.a*(np.cos(E)-o.e)/1000;yy=o.a*np.sqrt(1-o.e**2)*np.sin(E)/1000
ax.add_patch(plt.Circle((0,0),R_EARTH/1000,color='#306eaa',alpha=.85));ax.plot(xx,yy,color='#d97536',lw=2);ax.plot(o.rp/1000,0,'o',color='#d97536');ax.annotate('85 km perigee',xy=(o.rp/1000,0),xytext=(1500,-9000),arrowprops={'arrowstyle':'->'});ax.text(-9000,9000,'2,000 km apogee',fontsize=11);ax.set_aspect('equal');ax.set(xlim=(-11000,10000),ylim=(-10000,10500),xlabel='Orbit-plane distance, km',ylabel='km');ax.set_title(f'85 × 2,000 km; period {o.period/60:.2f} min\nDawn–dusk SSO target: inclination {math.degrees(inc):.2f}°')
labels=['Reboost','Dive compressors enabled','Coast processing','Intermediate hatches released','Receiver hatch released'];at.barh(0,d['burn_s']/60,left=-d['burn_s']/120,color='#ba4a46');at.barh(1,(d['pump_stop_s']+500)/60,left=-500/60,color='#dc9840');at.barh(2,(d['plant_stop_s']-d['plant_start_s'])/60,left=d['plant_start_s']/60,color='#247c8c');at.plot(12,3,'o',color='#247c8c');at.plot(72,4,'o',color='#247c8c');at.set_yticks(range(5),labels);at.invert_yaxis();at.set(xlim=(-22,87),xlabel='Minutes from perigee');at.axvline(0,color='gray',ls=':');at.grid(axis='x',alpha=.2);at.set_title('Saved cycle timings\nSSO seasonal illumination is not yet in this run');fig.suptitle('v1.0 orbit and operating sequence',fontsize=16)
for ext in ['svg','png']:fig.savefig(ROOT/f'docs/images/v1_orbit_cycle.{ext}',dpi=160)
plt.close(fig)
print(json.dumps({k:v for k,v in result.items() if k not in ['components','source_sha256']},indent=2))
# Publish histories from this exact reference, never the earlier rod study.
tt=np.asarray(r['time_s'])/60;history=r['history'];fig,axs=plt.subplots(3,1,figsize=(12,9),layout='constrained')
P=np.asarray(history['pressure_Pa']);TM=np.asarray(history['rack_K']);gas=np.asarray(r['gas_species_kg']).sum(axis=2);liq=np.asarray(r['liquid_species_kg']).sum(axis=1)
for i,(name,col) in enumerate(zip(['Front / SiC','Stage 2 / Al','Stage 3 / Al','Stage 4 / Al','Receiver / Al'],['#b34a32','#d59b24','#6e71b2','#4c9f78','#247c8c'])):
 axs[0].plot(tt,np.maximum(P[:,i],1e-6),label=name,color=col,lw=1.5);axs[1].plot(tt,TM[:,i],color=col,lw=1.5,label=name)
axs[0].set(yscale='log',ylim=(.01,40000),xlim=(-3,12),ylabel='Chamber pressure, Pa',xlabel='Minutes from perigee — dive detail');axs[0].legend(ncol=3,fontsize=9);axs[0].set_title('v1.0 cycle — finite gas volumes and reusable heat stores',loc='left')
axs[1].set(xlim=(-3,86),ylabel='Cooler temperature, K',xlabel='Minutes from perigee');axs[1].legend(ncol=3,fontsize=9)
axs[2].plot(tt,gas[:,4]/1000,label='Gas in aft receiver',color='#247c8c');axs[2].plot(tt,liq/1000,label='Liquid product inventory',color='#6e71b2');axs[2].plot(tt,np.asarray(r['gas_reserve_species_kg']).sum(axis=1)/1000,label='Propellant reserve (includes preloaded gas)',color='#b34a32');axs[2].set(xlim=(-3,86),ylabel='Inventory, tonnes',xlabel='Minutes from perigee');axs[2].legend(fontsize=9)
for ax in axs:ax.grid(alpha=.2);ax.axvline(0,color='gray',ls=':',lw=1)
for ext in ['svg','png']:fig.savefig(ROOT/f'docs/images/v1_cycle_history.{ext}',dpi=160)
plt.close(fig)
# Preserve historical artwork; update copied schematic wording for publication.
for old,new in [('spacecraft_overview','v1_overview'),('thermal_cycle','v1_thermal_cycle')]:
 s=(ROOT/f'docs/images/{old}.svg').read_text().replace('oxygen propulsion','air-propellant propulsion').replace('Oxygen electric thrust','Air-fed electric thrust').replace('compressors + air-propellant propulsion','compressors + air-fed thrusters').replace('Sheets retract into the front rack before entry.','Sheets retract into their cooling chambers before entry.').replace('Solid precooling rack','SiC / Al plate coolers').replace('Compressor wall','Staged compressors').replace('Attached metal sheets','Attached solid-cooler plates').replace('SOLID METAL ABSORBER','SOLID HEAT ABSORBER').replace('Energy stored in the metal','Energy stored in the solid').replace('Metal stays attached','Cooler stays attached')
 (ROOT/f'docs/images/{new}.svg').write_text(s)
