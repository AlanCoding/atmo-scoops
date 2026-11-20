"""Scale side elevation from the publication register; appendages illustrative."""
from pathlib import Path
import json,html,subprocess
ROOT=Path(__file__).resolve().parents[2]
r=json.loads((ROOT/'investigations/v1_layout/results.json').read_text())
cm=next(v['CM_m'] for v in r['loaded'] if v['state']=='Perigee')
S=4.;X=300.;Y=400.;D=31.7;L=317.;bottom=Y+D*S;mid=(Y+bottom)/2
x=lambda m:X+S*m
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1050" viewBox="0 0 1800 1050" role="img" aria-labelledby="title desc">
<title id="title">Atmospheric scoop diver v1.0: scale side view at perigee</title>
<desc id="desc">The 317 metre by 31.7 metre hull uses equal horizontal and vertical scale. The mouth faces left, motion and thrust point left, incoming air and exhaust point right. The loaded perigee center of mass is 32.80 metres behind the mouth. Thruster axial spans follow the provisional register; pod dimensions and aft fins are illustrative. The Earth and altitude indicator are not to scale.</desc>
<defs>
<marker id="blue" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0L10 4L0 8Z" fill="#8fc8ff"/></marker>
<marker id="orange" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0L10 4L0 8Z" fill="#f5ae66"/></marker>
<marker id="green" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0L10 4L0 8Z" fill="#74dfb5"/></marker>
<pattern id="bay" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 12L12 0" stroke="#38536b" stroke-width="1"/></pattern>
</defs>
<rect width="1800" height="1050" fill="#0b1424"/>
<style>text{font-family:DejaVu Sans,sans-serif;fill:#edf3fa} .sub{fill:#a7bfd4} .dim{stroke:#a7bfd4;stroke-width:1.5;fill:none} .leader{stroke:#90a9c0;stroke-width:1.5;fill:none}</style>
''']
def text(a,b,s,size=22,color=None,anchor='start'):
 parts.append(f'<text x="{a:.3f}" y="{b:.3f}" font-size="{size}" text-anchor="{anchor}"'+(f' style="fill:{color}"' if color else '')+'>'+html.escape(s)+'</text>')
def line(a,b,c,d,stroke='#a7bfd4',width=2,dash=None,marker=None):
 parts.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{stroke}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' marker-end="url(#{marker})"' if marker else '')+'/>')
def rect(a,b,w,h,fill,stroke=None):
 parts.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>')
text(55,58,'ATMOSPHERIC SCOOP DIVER · v1.0 AT PERIGEE',34)
text(55,91,'Scale side elevation of the hull • all deployables stowed • nose-first attitude assumed',21,'#a7bfd4')
for a,label,value in [(55,'ALTITUDE','85 km above Earth'),(490,'INERTIAL SPEED',f'{r["orbit"]["perigee_speed_km_s"]:.2f} km/s'),(900,'ORBIT','85 × 2,000 km'),(1330,'DRY MASS','13,250 tonnes')]:
 rect(a,115,405,72,'#132338');text(a+15,139,label,14,'#a7bfd4');text(a+15,169,value,23)
line(1200,235,760,235,'#8fc8ff',4,marker='blue');text(980,217,'DIRECTION OF MOTION',21,'#8fc8ff','middle')
text(1430,231,'Radial velocity = 0 at perigee',18,'#a7bfd4','middle')
text(x(cm)-80,282,f'Perigee CM: {cm:.2f} m',24,'#ffdb71')
text(x(cm)-80,309,f'Dry CM: {r["dry_CM_m"]:.2f} m',18,'#a7bfd4')
line(650,339,405,339,'#74dfb5',3,marker='green');text(663,346,'Forward thrust',21,'#74dfb5')
# Body envelope, pressure volumes, and equipment bay strips; same scale x/y.
rect(X,Y,L*S,D*S,'#173445')
for a,b in r['equipment_bays_m']:
 rect(x(a),Y,(b-a)*S,D*S,'#25364c');rect(x(a),Y,(b-a)*S,D*S,'url(#bay)')
 # Folded solar cassettes: occupy upper/lower peripheral sectors symbolically.
 rect(x(a)+1,Y+6,max(1,(b-a)*S-2),8,'#5796bf');rect(x(a)+1,bottom-14,max(1,(b-a)*S-2),8,'#5796bf')
for a,b in r['chambers_m'][:-1]:
 rect(x(a),Y,(b-a)*S,D*S,'#5c472a')
for a,b in r['chambers_m'][1:]:line(x(a),Y+2,x(a),bottom-2,'#6ab8b7',1.5)
# Exact total outline, open inlet, symbolic aft cap within 317 m.
line(X,Y,x(L),Y,'#a9c4d8',3);line(X,bottom,x(L),bottom,'#a9c4d8',3);line(x(L),Y,x(L),bottom,'#a9c4d8',3)
line(X,mid,x(L),mid,'#8aa5b8',1,dash='10 7')
text(1060,mid-8,'AFT GAS RECEIVER',26,'#97dfd6','middle')
text(1060,mid+22,'x = 69.63–317 m · 247.37 m deep',20,'#a7bfd4','middle')
# Indicative aft stabilizer surfaces, deliberately dashed/unfilled.
for yy,outer in [(Y,Y-54),(bottom,bottom+54)]:
 parts.append(f'<path d="M{x(280)} {yy} L{x(307)} {outer} L{x(315)} {yy}" fill="none" stroke="#718da6" stroke-width="2" stroke-dasharray="7 5"/>')
# Two symmetric groups of side-mounted modules. Axial spans from the register;
# radial offsets and pod heights deliberately illustrative.
for group,(a,b) in enumerate([(28.98440010238012,38.98440010238012),(42.00768260616955,69.62720686895992)]):
 # Stagger radial offsets so an upstream group's schematic exhaust does not
 # pass through the downstream pod at the same projected radius.
 for yy in ([Y-55,bottom+41] if group==0 else [Y-32,bottom+18]):
  rect(x(a),yy,(b-a)*S,14,'#235346','#74dfb5')
  line((x(a)+x(b))/2,yy+7,(x(a)+x(b))/2,Y if yy<Y else bottom,'#74dfb5',1.5)
  line(x(b)+6,yy+7,x(b)+150,yy+7,'#74dfb5',2,dash='8 5',marker='green')
text(845,378,'Exhaust aft →',20,'#74dfb5')
# Inflow relative to the moving craft.
for yy in [Y+40,Y+83]:line(55,yy,285,yy,'#f5ae66',3,marker='orange')
text(55,Y+9,'Relative airflow',20,'#f5ae66')
text(55,bottom+27,'OPEN MOUTH',19,'#f5ae66')
# CM mark: all phases differ by less than a pixel here.
line(x(cm),Y-40,x(cm),bottom+65,'#ffdb71',2,dash='6 4')
parts.append(f'<circle cx="{x(cm)}" cy="{mid}" r="9" fill="#ffdb71" stroke="#0b1424" stroke-width="2"/>')
line(x(cm)-13,mid,x(cm)+13,mid,'#0b1424',2);line(x(cm),mid-13,x(cm),mid+13,'#0b1424',2)
# Selected callouts with separate landing zones.
line(x(10),bottom+2,320,610);text(205,642,'Forward batteries + compressors',20)
line(x(61),bottom+34,650,610);text(610,642,'Thruster groups: x ≈ 29–39 and 42–70 m',19)
line(x(300),bottom+60,1460,610);text(1310,642,'Aft stabilizers: illustrative',19,'#a7bfd4')
# Diameter dimension outside the tail.
xd=x(L)+60
line(xd,Y,xd,bottom);line(xd-9,Y,xd+9,Y);line(xd-9,bottom,xd+9,bottom)
text(xd+15,mid-4,'31.7 m',22);text(xd+15,mid+22,'hull OD',17,'#a7bfd4')
# Overall and front equipment dimensions.
for xx in [X,x(L)]:line(xx,675,xx,734,'#a7bfd4',1)
line(X,715,x(L),715);line(X,707,X,723);line(x(L),707,x(L),723)
text((X+x(L))/2,702,'317 m overall hull length · L / D = 10',23,'#edf3fa','middle')
text(X,780,'x = 0 m',18,'#a7bfd4','middle');text(x(L),755,'x = 317 m',18,'#a7bfd4','middle')
# A measurable 50 m scale bar.
rect(70,730,100,8,'#edf3fa');rect(170,730,100,8,'#5e829a');text(70,766,'0',16,'#a7bfd4');text(270,766,'50 m',16,'#a7bfd4','end')
# Perigee context below the actual drawing: intentionally broken altitude scale.
rect(55,805,1690,182,'#101f31')
text(78,838,'PERIGEE CONFIGURATION',18,'#8fc8ff')
text(78,870,'Solar arrays, warm radiators and solid coolers are stowed.',20)
text(78,900,'Batteries power compression and air-fed electric reboost.',20)
text(78,930,'Dawn–dusk SSO target: inclination ≈ 99.35°; seasonal lighting still to be modeled.',17,'#a7bfd4')
line(1510,828,1510,930,'#8fc8ff',2,marker='blue')
# Zigzag break makes clear that Earth is not 85 km away on the drawing scale.
parts.append('<path d="M1500 867L1520 876L1500 885L1520 894" stroke="#0b1424" stroke-width="9" fill="none"/><path d="M1500 867L1520 876L1500 885L1520 894" stroke="#8fc8ff" stroke-width="2" fill="none"/>')
text(1530,855,'85 km altitude',19,'#8fc8ff');text(1530,914,'Earth below',18,'#a7bfd4')
line(1395,948,1695,948,'#477da5',4);text(1510,976,'Altitude indicator not to scale',15,'#a7bfd4','middle')
text(55,1020,'Hull dimensions and CM are scaled. Internal radial layout, pod dimensions, plume cones and fins are schematic; no stability claim.',17,'#a7bfd4')
parts.append('</svg>')
out=ROOT/'docs/images/v1_perigee_scale.svg';out.write_text('\n'.join(parts)+'\n')
subprocess.run(['magick','-background','none','-density','192',str(out),str(out.with_suffix('.png'))],check=True)
subprocess.run(['magick','-background','none','-density','192',str(ROOT/'docs/images/feed_racks.svg'),str(ROOT/'docs/images/feed_racks.png')],check=True)
print(out)
