"""Scale drawing from a saved cycle, with explicitly proposed aft placements."""
import argparse,html,json,subprocess
from pathlib import Path
from atmo_scoops.transient.io import read_result
p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
r=read_result(a.result);h=r['hardware'];d=r['inputs']['design'];pk=h['stage_packing'];g=h['geometry'];m=h['masses_kg'];rs=pk['receiver_start_m'];hd=r['inputs']['capabilities']['head_depth_m'];S=5.;X=180.;Y=360.;H=h['outside_m']*S;mid=Y+H/2;x=lambda z:X+S*z
rack_ranges=[(s['rack_start_m'],s['rack_end_m']) for s in pk['stages']]+[(rs+hd,rs+hd+g[4]['installed_rack_depth_m'])]
# Aft placements are proposed, not optimization variables or a volumetric fit.
placements={'battery':(rs+2,rs+10),'bus':(rs+10,rs+15),'coast_compressors':(rs+15,rs+25),'refrigerator':(rs+25,rs+31),'external_exchangers':(rs+25,rs+31),'separator':(rs+25,rs+31),'liquid_tanks':(rs+27,rs+31),'warm_store':(rs+31,rs+37),'warm_radiator':(rs+31,rs+37),'gas_reserve_system':(rs+37,rs+44),'solar':(rs+44,max(rs+45,190.)),'auxiliary':(rs+2,rs+10),'thrusters':(319.,329.),'hull':(0.,317.),'pressure_vessels':(10.,317.)}
register=[]
def add(name,mass,span):register.append(dict(name=name,mass_kg=mass,x0_m=span[0],x1_m=span[1],centroid_m=sum(span)/2))
for i in range(5):add(f'Rack {i+1}',g[i]['mass_kg'],rack_ranges[i])
for i,b in enumerate(h['banks']):add(f'Compressor {i+1}',b['total_kg'],(pk['stages'][i]['compressor_start_m'],pk['stages'][i]['compressor_end_m']))
foot=sum(z['deployed_physical_m2'] for z in g)
for i in range(5):add(f'Rack mechanism {i+1}',m['rack_mechanisms']*g[i]['deployed_physical_m2']/foot,(pk['stages'][i]['hatch_start_m'],pk['stages'][i]['hatch_end_m']) if i<4 else rack_ranges[4])
for key,span in placements.items():
 if key in m:add(key,m[key],span)
subtotal=sum(z['mass_kg'] for z in register);assert abs(subtotal-(h['dry_kg']-m['margin']))<1e-5
cm=sum(z['mass_kg']*z['centroid_m'] for z in register)/subtotal
add('margin (distributed proportionally)',m['margin'],(cm,cm))
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="2000" height="1230" viewBox="0 0 2000 1230"><rect width="2000" height="1180" fill="white"/><style>text{font-family:DejaVu Sans,sans-serif;fill:#223746}</style><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#226d86"/></marker></defs>']
def txt(xx,yy,s,size=20):parts.append(f'<text x="{xx}" y="{yy}" font-size="{size}">{html.escape(s)}</text>')
def line(xx,yy,xx2,yy2,color='#6d828e',dash='',arrow=False):parts.append(f'<line x1="{xx}" y1="{yy}" x2="{xx2}" y2="{yy2}" stroke="{color}" stroke-width="2" stroke-dasharray="{dash}"'+(' marker-end="url(#a)"' if arrow else '')+'/>')
def box(lo,hi,yy,height,color,stroke='#6d828e',dash=''):parts.append(f'<rect x="{x(lo)}" y="{yy}" width="{S*(hi-lo)}" height="{height}" fill="{color}" stroke="{stroke}" stroke-dasharray="{dash}"/>')
txt(55,55,'ATMOSPHERIC SCOOP DIVER · CORRECTED THERMAL-SPACING CHECKPOINT',29)
txt(55,92,f"85 × {d['apogee_km']:,.0f} km orbit · 317 m hull · 31.7 m outside diameter · perigee, all deployables stowed",21)
txt(55,128,f"Saved cycle: {r['operating_payoff_days']:.2f} operating-orbit payoff days · {r['dry_kg']/1000:,.1f} tonnes dry",21)
txt(55,170,'Front geometry and rack sizes are numerical outputs. Aft package locations and CM are layout estimates.',19)
line(980,224,650,224,arrow=True);txt(680,209,'Motion / prograde thrust',20)
txt(55,275,f'Estimated dry CM: x = {cm:.1f} m',21);txt(55,302,'Uses proposed aft locations; not a stability calculation.',17)
box(0,317,Y,H,'#edf5f7')
for i,s in enumerate(pk['stages']):
 box(s['gas_start_m'],s['gas_end_m'],Y,H,'#f8f0de')
 box(s['rack_start_m'],s['rack_end_m'],Y,H,'#c8873d','#b66b1c')
 box(s['compressor_start_m'],s['compressor_end_m'],Y,H,'#a9bac9')
 box(s['hatch_start_m'],s['hatch_end_m'],Y,H,'#c8b6d8')
 txt(x((s['compressor_start_m']+s['compressor_end_m'])/2)-8,mid+6,f'C{i+1}',13)
parts.append(f'<rect x="{x(rs)}" y="{Y+1}" width="{(317-rs)*S}" height="{H-2}" rx="{hd*S}" fill="none" stroke="#7895a1"/>')
# Receiver rack uses its true axial thickness; placement at forward service end is a layout choice.
box(*rack_ranges[4],Y,H,'#c8873d','#b66b1c')
txt(x(cm)+35,mid-4,'SHARED AFT GAS RECEIVER',23)
txt(x(cm)+35,mid+25,'Package displacement included; isolation partition is the next checkpoint',17)
# Peripheral symbols identify retained volume budgets; no radial fit is asserted.
for key,color in [('battery','#dfc69e'),('bus','#d8d9ba'),('coast_compressors','#b2c0ce'),('refrigerator','#c7b6e0'),('warm_radiator','#9bcaba'),('solar','#91b9e1')]:
 lo,hi=placements[key]
 for yy in [Y+3,Y+H-13]:box(lo,hi,yy,10,color,dash='4 3')
# Modeled reserve: four spheres in one axial station, two obscured in side projection.
gs=h['gas_system'];reserve_x=sum(placements['gas_reserve_system'])/2;reserve_radius=gs['outer_diameter_m']*S/2
for cy in [Y+52,Y+103]:
 parts.append(f'<circle cx="{x(reserve_x)}" cy="{cy}" r="{reserve_radius}" fill="#c7e3bf" stroke="#39774c" stroke-width="2"/>')
 parts.append(f'<path d="M{x(reserve_x)-reserve_radius*.75} {cy} Q{x(reserve_x)} {cy-reserve_radius*.55} {x(reserve_x)+reserve_radius*.75} {cy}" fill="none" stroke="#39774c" stroke-dasharray="3 2"/>')
# Schematic plumbing routes; no line diameter or radial fit is implied.
line(x(rs+20),Y+15,x(rs+20),Y+52,'#39774c')
line(x(rs+20),Y+52,x(reserve_x)-reserve_radius,Y+52,'#39774c',arrow=True)
line(x(reserve_x),Y+52+reserve_radius,x(reserve_x),Y+103-reserve_radius,'#39774c')
line(x(reserve_x),Y+103+reserve_radius,x(reserve_x),Y+H-20,'#39774c')
line(x(reserve_x),Y+H-20,x(319),Y+H-20,'#39774c',arrow=True)
line(x(319),Y+H-20,x(319),Y+H+15,'#39774c')
txt(1120,Y+H-29,'Gaseous propellant feed → aft thrusters',17)
line(x(reserve_x),Y+103+reserve_radius,x(reserve_x),532,'#39774c')
line(x(reserve_x),532,350,532,'#39774c');line(350,532,350,540,'#39774c')
txt(55,556,f"Thruster reserve: {gs['tank_count']} × {gs['usable_internal_m3']/gs['tank_count']:.0f} m³ spheres · Ø {gs['outer_diameter_m']:.2f} m · two visible, two behind",18)
txt(55,582,f"{d['gas_reserve_kg']:,.0f} kg starting charge · {gs['rated_Pa']/1e5:.0f} bar rated · coast compressor + booster refill · placement proposed",18)
for yy in [Y-23,Y+H+8]:
 box(319,329,yy,14,'#9cc9b2');cy=yy+7
 parts.append(f'<path d="M{x(329)} {cy} L{x(329)+100} {cy-45} L{x(329)+100} {cy+45}Z" fill="#e3f2ed" stroke="#6c9d87" stroke-dasharray="5 4"/>')
 line(x(329),cy,x(329)+120,cy,arrow=True)
line(x(cm),Y-30,x(cm),Y+H+30,'#b48122','6 4');parts.append(f'<circle cx="{x(cm)}" cy="{mid}" r="6" fill="#b48122"/>')
for yy in [Y+45,Y+110]:line(40,yy,X-12,yy,arrow=True)
txt(35,Y+22,'Air →',18)
line(x(rs+28),Y-2,x(rs+28),305);txt(x(rs+15),298,'Coast plant / cryogenics / reserve refill',17)
lo,hi=placements['solar'];txt(x(lo)+10,330,f"Folded solar: {h['packages_m3']['solar']:,.0f} m³",18)
txt(1470,275,'Aft thrusters: proposed placement',20);txt(1470,303,'Plume is illustrative',17)
line(X,640,x(317),640)
for xx in [X,x(317)]:line(xx,632,xx,648)
txt(650,630,'317 m hull; external thrusters extend beyond it',21)
txt(55,685,'Amber: actual rack thickness · Grey: compressor bank · Purple: 1 m hatch equipment · Dashed bands: proposed packages',18)
txt(55,725,'All dimensions below are metres aft of the mouth; subpixel racks are not enlarged.',18)
for xx,s in [(55,'Stage'),(160,'Gas volume range'),(440,'Rack range'),(720,'Compressor range'),(1000,'Hatch range'),(1280,'Rack mass (t)'),(1510,'Core length (m)')]:txt(xx,766,s,18)
for i in range(5):
 yy=804+39*i
 txt(55,yy,str(i+1));span=(pk['stages'][i]['gas_start_m'],pk['stages'][i]['gas_end_m']) if i<4 else (rs,317.)
 txt(160,yy,f'{span[0]:.3f}–{span[1]:.3f}');txt(440,yy,f'{rack_ranges[i][0]:.3f}–{rack_ranges[i][1]:.3f}')
 if i<4:
  s=pk['stages'][i];txt(720,yy,f"{s['compressor_start_m']:.3f}–{s['compressor_end_m']:.3f}");txt(1000,yy,f"{s['hatch_start_m']:.3f}–{s['hatch_end_m']:.3f}")
 else:txt(720,yy,'Coast plant (proposed)');txt(1000,yy,'Receiver mechanism')
 txt(1280,yy,f"{g[i]['mass_kg']/1000:.3f}");txt(1510,yy,f"{g[i]['rack_depth_m']:.4f}")
txt(55,1033,'Stage 1 has 10 m empty inlet space. Stages 2–4 include explicit vessel heads. Rack 5 is shown at the forward receiver service port.',17)
txt(55,1068,'Aft package bands are symbols, not verified radial cross sections. Their full volume remains deducted from receiver gas volume.',17)
txt(55,1103,'The planned 125 m isolation tank and five-cycle product store are subsequent checkpoints; they are not credited in this run.',17)
txt(55,1138,'Thermal-spacing equivalence is an explicit approximation. Pressure-loss electricity does not establish hydraulic or structural feasibility.',17)
parts.append('</svg>');a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(parts)+'\n')
a.output.with_suffix('.layout.json').write_text(json.dumps(dict(source=str(a.result),dry_CM_m=cm,components=register,rack_ranges_m=rack_ranges,gas_reserve=dict(tank_count=gs['tank_count'],total_internal_m3=gs['usable_internal_m3'],outer_diameter_m=gs['outer_diameter_m'],axial_station_m=reserve_x,projected_visible_tanks=2,rated_Pa=gs['rated_Pa']),placements_status='Aft locations proposed; no radial fit or stability certification'),indent=2)+'\n')
subprocess.run(['magick','-background','white',str(a.output),str(a.output.with_suffix('.png'))],check=True)
