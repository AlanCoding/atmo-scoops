"""Proposed packaging revision; frozen cycle results are not recalculated."""
from pathlib import Path
import json, html, subprocess
ROOT=Path(__file__).resolve().parents[2]
r=json.loads((ROOT/'investigations/v1_layout/results.json').read_text())
# Relocate complete mass categories; all other masses, including margin, stay put.
cm=r['dry_CM_m']
for category,new_x in [('thrusters',324.),('solar',132.5),('coast_compressors',80.),('refrigerator',80.),('external_exchangers',80.),('separator',80.),('liquid_tanks',85.)]:
 rows=[c for c in r['components'] if c['category']==category]
 cm+=sum(c['mass_kg']*(new_x-c['centroid_m']) for c in rows)/r['dry_mass_kg']
S=4.;X=230.;Y=370.;L=317.;D=31.7;B=Y+D*S;M=(Y+B)/2
x=lambda v:X+S*v
p=['''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1040" viewBox="0 0 1800 1040" role="img" aria-labelledby="title desc">
<title id="title">Atmospheric scoop diver: proposed perigee packaging</title>
<desc id="desc">Equal-scale 317 metre hull, aft thrusters, solar stowage alongside the forward receiver, and a 125 metre isolated aft propellant compartment. This is a proposed layout, not a rerun of the v1.0 cycle.</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#236b87"/></marker></defs>
<rect width="1800" height="1040" fill="#ffffff"/>
<style>text{font-family:DejaVu Sans,sans-serif;fill:#203344}line,path,rect{stroke-linejoin:round}</style>''']
def text(a,b,s,size=20,color='#203344',anchor='start'):
 p.append(f'<text x="{a}" y="{b}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
def line(a,b,c,d,color='#64798a',width=2,dash='',arrow=False):
 p.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def rect(a,b,w,h,fill,stroke='#64798a'):
 p.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
text(55,55,'ATMOSPHERIC SCOOP DIVER · PROPOSED PACKAGING',32)
text(55,89,'v1.0 geometry • revised stowage and propellant partition • numerical cycle update pending',21)
text(55,135,'85 km perigee   |   85 × 2,000 km reference orbit   |   all deployables stowed',23)
line(1050,190,650,190,'#236b87',4,arrow=True);text(850,174,'Motion and forward thrust',22,anchor='middle')
text(55,247,f'Illustrative relocated dry CM: {cm:.1f} m',23,'#996300')
text(55,274,'Existing masses relocated only; larger liquid tanks not yet re-budgeted.',17)
# Existing machinery and pressure-volume positions remain provisional.
rect(X,Y,L*S,D*S,'#e9f4f5')
for a,b in r['equipment_bays_m']:rect(x(a),Y,(b-a)*S,D*S,'#dce2e8')
rack_depths=[.8964235337918296,.055570427084493626,.03240614150379688,.023282503789430302]
for i,((a,b),depth) in enumerate(zip(r['chambers_m'][:-1],rack_depths)):
 rect(x(a),Y,(b-a)*S,D*S,'#f6eddc')
 start=a if i==0 else b-1.5-depth
 # Preserve true plate-bank thickness, even where subpixel in this overview.
 p.append(f'<rect x="{x(start)}" y="{Y}" width="{depth*S}" height="{D*S}" fill="#b66f20"/>')
# Rounded pressure vessels; constant barrel radius, heads illustrative.
# Main tank 24 m diameter leaves peripheral equipment space inside 30 m bore.
p.append(f'<rect x="{x(69.63)}" y="{M-48}" width="{(192-69.63)*S}" height="96" rx="16" fill="#e9f4f5" stroke="#426b7a" stroke-width="2"/>')
p.append(f'<rect x="{x(192)}" y="{M-60}" width="{125*S}" height="120" rx="16" fill="#d9ede1" stroke="#366c50" stroke-width="2"/>')
# Valve icon across bulkhead, connection is internal.
p.append(f'<path d="M{x(192)-12} {M-9} L{x(192)+12} {M+9} L{x(192)+12} {M-9} L{x(192)-12} {M+9} Z" fill="#fff" stroke="#366c50" stroke-width="2"/>')
# Solar stowage in opposing peripheral sectors, avoiding forward rack exits.
for yy in [Y+4,B-16]:
 rect(x(90),yy,85*S,12,'#96bfe8','#416a97')
 rect(x(70),yy,20*S,12,'#c8b7e1','#785a98')
# Product tank marker in the same peripheral service zone.
rect(x(82),Y+4,6*S,12,'#f1d297','#9f792f')
text(x(130),M-3,'MAIN RECEIVER',21,anchor='middle')
text(x(130),M+22,'24 m barrel diameter',17,anchor='middle')
text(x(254),M-6,'PROPELLANT RESERVE',21,anchor='middle')
text(x(254),M+20,'125 m · 30 m barrel diameter',19,anchor='middle')
# Modest cryogenic package marker; callout, not detailed internals.
# Cryogenic plant is now in the receiver peripheral zone, not the front bays.
# Tail pods occupy last 10 m; motor head/PPU split is unresolved.
for yy,sign in [(Y-23,-1),(B+7,1)]:
 rect(x(319),yy,10*S,16,'#a3cdb8','#366c50')
 cy=yy+8
 p.append(f'<path d="M{x(329)} {cy} L{x(329)+110} {cy-64} L{x(329)+110} {cy+64} Z" fill="#d7eee5" fill-opacity="0.65" stroke="#459476" stroke-dasharray="6 4"/>')
 line(x(329),cy,x(329)+125,cy,'#236b87',2,arrow=True)
# Conceptual fins; not a stability result.
for yy,outer in [(Y,Y-50),(B,B+50)]:
 p.append(f'<path d="M{x(280)} {yy} L{x(302)} {outer} L{x(307)} {yy}" fill="none" stroke="#7e8c97" stroke-width="2" stroke-dasharray="6 4"/>')
line(X,Y,x(L),Y,'#354c5c',3);line(X,B,x(L),B,'#354c5c',3);line(x(L),Y,x(L),B,'#354c5c',3)
line(x(cm),Y-35,x(cm),B+35,'#b77a00',2,'6 4')
p.append(f'<circle cx="{x(cm)}" cy="{M}" r="7" fill="#b77a00"/>')
for yy in [Y+40,Y+85]:line(55,yy,X-12,yy,'#236b87',3,arrow=True)
text(55,Y+12,'Incoming air',18);text(55,B+25,'Open mouth',18)
# Top and bottom labels, separated from the hull.
line(x(132.5),Y+3,x(132.5),318);text(x(132.5),310,'Folded solar: x = 90–175 m · 11,527 m³',19,anchor='middle')
text(1110,273,'Tail-mounted electric thrusters',22)
text(1110,302,'30° plume half-angle shown for screening',18)
line(1430,310,x(324),Y-23)
line(x(80),B,550,583);text(290,611,'Cryogenic plant wraps forward receiver',19)
text(290,637,'60 m³ liquid capacity ≈ 15 passes (provisional)',17)
line(x(192),B,1050,583);text(880,611,'Separate rounded reserve + isolation valve',19)
text(880,637,'Opens when collection pressure catches reserve pressure',17)
# Dimensions.
for a,b,yy,label in [(0,317,700,'317 m overall · 31.7 m hull OD · L/D = 10'),(192,317,755,'125 m reserved aft length')]:
 line(x(a),yy,x(b),yy)
 for q in [a,b]:line(x(q),yy-7,x(q),yy+7)
 text((x(a)+x(b))/2,yy-12,label,21,anchor='middle')
text(X,735,'x = 0',16);text(x(192),787,'x = 192 m',16,anchor='middle');text(x(317),787,'x = 317 m',16,anchor='middle')
rect(55,820,1690,170,'#f0f4f7','#d6e0e6')
text(78,849,'FRONT COOLERS · SAVED REFERENCE DIMENSIONS',20)
text(78,879,'Rack depths: SiC 0.896 m  |  Al 0.0556 m  |  Al 0.0324 m  |  Al 0.0233 m',20)
text(78,908,'Chamber axial envelopes: 0.896 m  |  3.056 m  |  3.032 m  |  3.023 m (downstream includes vessel heads)',18)
text(78,939,'Coast: isolate reserve. Pre-dive: draw it down. Reopen when collection pressure catches reserve pressure.',18)
text(78,969,'Front chamber positions retained from reference; 12 / 10 / 10 / 27.62 m machinery bays remain provisional.',17)
text(55,1020,'317 m hull excludes aft thrusters (x = 319–329 m). Tank heads and radial packaging provisional; cycle update pending.',17)
p.append('</svg>')
out=ROOT/'docs/images/v1_perigee_scale.svg';out.write_text('\n'.join(p)+'\n')
subprocess.run(['magick','-background','white','-density','120',str(out),str(out.with_suffix('.png'))],check=True)
print(f'{out}\nRelocated dry CM: {cm:.3f} m')
