"""Valve-only layout from the validated current forward cycle."""
import json,html,subprocess,sys
from pathlib import Path
from atmo_scoops.transient.io import read_result
ROOT=Path(__file__).resolve().parents[2]
a=json.loads(Path(__file__).with_name('VALVE_ALGEBRA.json').read_text());z=a['cases'][0]
r=read_result(ROOT/'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz');stages=r['hardware']['stage_packing']['stages']
if len(sys.argv)==1: sys.argv.append(str(ROOT/'results/transient/valve_restore/selected_refined.json.gz'))
solved=True
if solved:
 r=read_result(sys.argv[1]);h=r['hardware'];g=h['geometry'][-1];v=h['gas_system'];pack=h['stage_packing'];stages=pack['stages']
 a=dict(head_depth_m=r['inputs']['capabilities']['head_depth_m'],main_start_m=pack['receiver_start_m'],split_m=pack['reserve_start_m'],main_radius_m=pack['receiver_radius_m'],reserve_radius_m=v['internal_radius_m'],main_length_m=g['depth_m'],receiver_rack_core_m=g['rack_depth_m'],retained_package_displacement_m3=pack['aft_displacement_m3'])
 j=max(range(len(r['time_s'])),key=lambda j:r['history']['pressure_Pa'][j][-1])
 z=dict(perigee_km=r['inputs']['design']['perigee_km'],target_pressure_Pa=r['history']['pressure_Pa'][j][-1],temperature_K=r['history']['gas_K'][j][-1],main_mass_kg=sum(r['gas_species_kg'][j][-1]),reserve_mass_kg=sum(r['gas_reserve_species_kg'][0]))
S=4.5;X=135;Y=330;H=31.7*S;mid=Y+H/2;x=lambda m:X+S*m
p=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="850" viewBox="0 0 1800 850"><title>v1.0.1 working valve-connected reserve layout</title><rect width="1800" height="850" fill="white"/><style>text{font-family:DejaVu Sans,sans-serif;fill:#243b48}</style><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#286f82"/></marker></defs>']
def text(xx,yy,s,size=19):p.append(f'<text x="{xx}" y="{yy}" font-size="{size}">{html.escape(s)}</text>')
def line(xx,yy,ex,ey,color='#6d858e',arrow=False):p.append(f'<line x1="{xx}" y1="{yy}" x2="{ex}" y2="{ey}" stroke="{color}" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def rect(lo,hi,yy,hh,fill,rx=0):p.append(f'<rect x="{x(lo)}" y="{yy}" width="{S*(hi-lo)}" height="{hh}" rx="{rx}" fill="{fill}" stroke="#6d858e"/>')
text(45,48,'v1.0.1 WORKING DESIGN · VALVE-CONNECTED AFT RESERVE',29)
text(45,85,f"{'Simulated orbit:' if solved else 'Algebraic starting orbit:'} {z['perigee_km']:.2f} × 2,000 km · 317 m hull · 31.7 m outer diameter",21)
text(45,118,('Forward-cycle geometry; valve-connected reserve. See numerical report for optimizer termination and validation.' if solved else 'Planning geometry only: revised simulation, mass budget, CM and payoff are pending review and implementation.'),18)
text(45,149,f"Fill screen: {z['target_pressure_Pa']/1000:.3f} kPa at {z['temperature_K']:.1f} K · {'main receiver peak from trajectory' if solved else 'equal tank temperature assumed for this calculation'}",18)
line(850,210,550,210,arrow=True);text(580,194,'Motion / prograde thrust',18)
rect(0,317,Y,H,'#eff4f6')
for i,s in enumerate(stages):
 for k,col in [('gas','#fbf3df'),('rack','#cd8b35'),('compressor','#a7bac9'),('hatch','#c4b4d1')]:rect(s[k+'_start_m'],s[k+'_end_m'],Y,H,col)
 text(x((s['compressor_start_m']+s['compressor_end_m'])/2)-7,mid+4,f'C{i+1}',11)
rs=a['main_start_m'];split=a['split_m'];mr=a['main_radius_m'];rr=a['reserve_radius_m']
rect(rs,split,mid-mr*S,2*mr*S,'#e3f0f6',a['head_depth_m']*S)
rect(split,317,mid-rr*S,2*rr*S,'#e3f2e3',a['head_depth_m']*S)
# Retain metal inventory while reducing receiver rack area to the main barrel.
rect(rs+1.5,rs+1.5+a['receiver_rack_core_m']+.015,mid-mr*S,2*mr*S,'#cd8b35')
for lo,hi,col in [(rs+2,rs+15,'#dfc89b'),(rs+15,rs+37,'#c5b5df'),(rs+44,190,'#93b8db')]:
 for yy in [Y+3,Y+H-12]:rect(lo,hi,yy,9,col)
text(x(rs)+45,mid-14,'MAIN RECEIVER',22);text(x(rs)+45,mid+13,f"{a['main_length_m']:.1f} m long · Ø {2*mr:.2f} m",18)
text(x(rs)+45,mid+38,f"{z['main_mass_kg']/1000:.2f} t gas at fill target",17)
text(x(split)+45,mid-14,'THRUSTER RESERVE',22);text(x(split)+45,mid+13,'125 m long · Ø 30 m',18)
text(x(split)+45,mid+38,f"{z['reserve_mass_kg']/1000:.2f} t retained working inventory",17)
# Valve is the only inter-tank transfer connection; icon is symbolic.
vx=x(split);vy=Y+25
line(vx-28,vy,vx+28,vy,'#397c49')
p.append(f'<path d="M{vx-9} {vy-8}L{vx+9} {vy+8}L{vx+9} {vy-8}L{vx-9} {vy+8}Z" fill="white" stroke="#397c49" stroke-width="2"/>')
line(vx,vy-9,vx,270);text(vx-100,255,'Isolation / equalization valve',17)
text(x(rs)+10,285,'Coast compressors / cryogenics',17);line(x(rs+25),290,x(rs+25),Y+3)
text(x(rs+55),312,'Folded solar panels around main receiver',16)
# Product processing is connected only to the main receiver while isolated.
line(x(rs+30),mid-mr*S+28,x(rs+30),Y+10,arrow=True)
line(x(308),mid,x(322),mid,arrow=True);text(x(252),Y+H+44,'Gaseous feed; low-pressure interface to verify',16)
for yy in [Y-20,Y+H+9]:
 rect(320,330,yy,12,'#9cc6b3');line(x(330),yy+6,x(330)+90,yy+6,arrow=True)
text(1450,285,'Aft thrusters',18)
for yy in [Y+42,Y+100]:line(30,yy,X-8,yy,arrow=True)
text(30,Y+20,'Air →',17)
line(X,550,x(317),550)
for xx in [X,x(317)]:line(xx,542,xx,558)
text(610,538,'317 m hull · geometry drawn at common scale',19)
text(45,615,'Valve sequence: reserve feeds pre-entry thrust → open when receiver pressure catches reserve → shared feeding → isolate for coast.',17)
text(45,660,f"Main-tank packages: {a['retained_package_displacement_m3']:,.0f} m³ equivalent displacement, all ahead of x = 192 m; radial sectors remain provisional.",17)
text(45,705,f"Receiver rack: Al plates within the narrowed tank; {a['receiver_rack_core_m']:.3f} m core depth.",17)
text(45,750,('Low-pressure thruster feed remains a development assumption; no updated CM is claimed.' if solved else 'No new payoff or CM is claimed. Model validation is pending.'),17)
p.append('</svg>');out=ROOT/'docs/images/v1_perigee_scale.svg';out.write_text('\n'.join(p)+'\n');subprocess.run(['magick','-background','white',str(out),str(out.with_suffix('.png'))],check=True)
out.with_suffix('.layout.json').write_text(json.dumps(dict(status='forward-cycle valve layout' if solved else 'working valve-only planning layout; not simulated',source=sys.argv[1] if solved else 'VALVE_ALGEBRA.json',geometry=a,front_stages=stages,CM=None,payoff=r.get('operating_payoff_days') if solved else None),indent=2)+'\n')
