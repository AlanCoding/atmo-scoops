"""Area-faithful coast deployment illustration; arrangement is conceptual."""
from pathlib import Path
import gzip,json,math,xml.etree.ElementTree as ET
import subprocess
ROOT=Path(__file__).resolve().parents[2]
r=json.load(gzip.open(ROOT/'results/transient/valve_restore/selected_refined.json.gz','rt'))
hw=r['hardware'];d=r['inputs']['design'];S=.65; X=680;Y=820
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1740" viewBox="0 0 1600 1740">', '<title>v1.0.1 deployed spacecraft at a common scale</title>', '<rect width="1600" height="1740" fill="#fff"/>', '<style>text{font-family:DejaVu Sans,sans-serif;fill:#233d4b;paint-order:stroke;stroke:white;stroke-width:3px;stroke-linejoin:round}.link{fill:none;stroke-width:2}</style>']
def text(x,y,t,size=18):parts.append(f'<text x="{x}" y="{y}" font-size="{size}">{t}</text>')
def line(x,y,xx,yy,color='#647985',dash=''):
 parts.append(f'<path d="M{x},{y} L{xx},{yy}" class="link" stroke="{color}" stroke-dasharray="{dash}"/>')
def sheet(x,y,area,color,label,detail):
 side=math.sqrt(area)*S
 parts.append(f'<rect x="{x}" y="{y}" width="{side}" height="{side}" fill="{color}" stroke="#355968" stroke-width="1.5"/>')
 for i in range(1,8):
  line(x+side*i/8,y,x+side*i/8,y+side,'#ffffff')
 text(x,y-38,label,20);text(x,y-12,detail,16)
 return side
text(55,50,'v1.0.1 · The deployed scale',32)
text(55,84,'317 m spacecraft, solar arrays, radiators and all five cooling racks at one common scale',21)
text(55,115,'Illustrative late-coast arrangement · sheet areas from the accepted saved cycle',18)
solar=d['solar_area_m2']/2
side=math.sqrt(solar)
sheet(850,165,solar,'#8db8dd','Solar wing A',f'{side:,.0f} × {side:,.0f} m · {solar:,.0f} m²')
sheet(850,1000,solar,'#8db8dd','Solar wing B',f'{side:,.0f} × {side:,.0f} m · {solar:,.0f} m²')
# Storage anchors match the existing scale SVG's axial package strips.
solar_anchor=X+140*S
line(solar_anchor,Y,solar_anchor,850,'#397eae');line(solar_anchor,850,850,790,'#397eae');line(solar_anchor,850,850,1000,'#397eae')
rad=hw['stage_packing']['aft_packages_m3']['warm_radiator']/.02
rs=sheet(650,450,rad,'#a2c9c2','Waste-heat radiator',f'{math.sqrt(rad):.0f} × {math.sqrt(rad):.0f} m · {rad:,.0f} m²')
line(X+70*S,Y,650+rs/2,450+rs,'#368477')
positions=[(230,700),(440,430),(430,590),(450,1070),(610,1250)]
for i,(g,pos) in enumerate(zip(hw['geometry'],positions)):
 area=g['deployed_physical_m2'];x,y=pos
 material='SiC' if i==0 else 'Al'
 w=sheet(x,y,area,'#dcab66' if i==0 else '#c5cbd3',f'Rack {i+1} · {material}',f'{math.sqrt(area):.1f} × {math.sqrt(area):.1f} m · {area:,.0f} m²')
 if i<4:anchor=(hw['stage_packing']['stages'][i]['rack_start_m'] if 'rack_start_m' in hw['stage_packing']['stages'][i] else hw['stage_packing']['stages'][i]['gas_start_m']+ (10 if i==0 else 1.5))
 else:anchor=48.096794+1.5
 # Front rack comes through mouth; others connect to their chamber's extraction route.
 ax=X if i==0 else X+anchor*S
 line(ax,Y,x+w,y+w/2,'#a2773d' if i==0 else '#818b98')
# Reuse the existing scale diagram's geometry, without shrinking its annotations.
root=ET.parse(ROOT/'docs/images/v1_perigee_scale.svg').getroot()
parts.append(f'<g transform="translate({X},{Y-31.7*S/2}) scale({S/4.5}) translate(-135,-330)">')
for el in root:
 if el.tag.endswith('rect') and 330<=float(el.get('y','-1'))<=473 and float(el.get('x','0'))>=135:
  parts.append(ET.tostring(el,encoding='unicode'))
parts.append('</g>')
text(670,888,'Hull: 317 m × 31.7 m',20)
text(670,916,'Mouth ←     main receiver     reserve →',15)
text(70,1320,'Connections remain attached',21)
text(70,1350,'Lines trace each deployment back to its storage region.',16)
text(70,1376,'They are schematic supports / thermal connections.',16)
# Scale bar uses exactly the same coordinate scale as hull and deployed sheets.
line(65,1460,65+500*S,1460,'#233d4b')
for dx in [0,250*S,500*S]:line(65+dx,1452,65+dx,1468,'#233d4b')
text(65,1495,'0');text(65+250*S-20,1495,'250');text(65+500*S-30,1495,'500 m')
text(55,1660,'Area convention: one physical sheet face; two-sided radiation does not double the drawn footprint.',17)
text(55,1688,'Square sheets and two equal solar wings are area-equivalent choices, not engineered deployment mechanisms.',17)
text(55,1716,'Rack 5 deploys late in coast after receiver processing / purge. Sun pointing, shadows and boom sizing remain unresolved.',17)
parts.append('</svg>')
out=ROOT/'docs/images/v1_0_1_deployed_scale.svg';out.write_text('\n'.join(parts)+'\n')
subprocess.run(["magick", "-background", "white", str(out), str(out.with_suffix(".png"))], check=True)
