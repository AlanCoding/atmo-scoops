"""Concept schematic for planned serial offset plates, not a CFD result."""
from pathlib import Path
import html, subprocess
ROOT=Path(__file__).resolve().parents[2]
p=['''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="title desc"><title id="title">Longer staggered plate cooler: serial flow</title><desc id="desc">A short dense reference stack is compared with four successive wider-pitch rows holding the same material. All gas flows through all four rows. Transverse spacing is magnified; this is not a full spacecraft elevation.</desc><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#167e97"/></marker></defs><rect width="1600" height="1050" fill="white"/><style>text{font-family:DejaVu Sans,sans-serif;fill:#243748}</style>''']
def text(x,y,s,size=20):p.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>')
def line(x,y,a,b,col='#80929c',arrow=False,dash=''):
 p.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"'+(' marker-end="url(#a)"' if arrow else '')+'/>')
def rect(x,y,w,h,fill,stroke='none'):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
text(50,55,'SAME COOLER MATERIAL · WIDER PITCH · LONGER SERIAL FLOW PATH',29)
text(50,90,'Proposed staggered plates — geometry study, not a simulated performance result',21)
text(50,135,'A. Reference: one dense, uninterrupted plate stack',24)
# 16 original strips, each same drawn material area as 4 strips in 4 rows below.
x0=220;length=240;top=165
rect(x0,top,length,220,'#eef5f7','#849aa6')
for i in range(16):rect(x0,top+11+i*13, length,4,'#b57639')
for yy in [top+35,top+100,top+165]:line(70,yy,205,yy,'#167e97',True);line(475,yy,580,yy,'#167e97',True)
text(650,205,'Front SiC reference',23)
text(650,242,'Plate thickness: 1.435 mm')
text(650,274,'Pitch: 7.625 mm  |  clear gap: 6.190 mm')
text(650,306,'Material: 382.83 tonnes  |  wetted area: 166,207 m²')
text(650,338,'Axial flow depth: 0.896 m')
line(220,407,460,407);text(278,432,'0.896 m',18)
text(50,480,'B. Four successive rows: 4× pitch, ¼ as many sheets per row',24)
top=510
# Rendering row gaps are intentional schematic separators, not modeled dimensions.
for row in range(4):
 xx=x0+row*260
 rect(xx,top,length,220,'#eef5f7','#849aa6')
 offset=row*13
 for j in range(4):rect(xx,top+11+offset+j*52,length,4,'#b57639')
 text(xx+80,top+249,f'Row {row+1}',18)
 # arrows at representative channel centers, no imposed winding trajectory
 for j in [0,2]:
  yy=top+38+offset+j*52
  line(xx+35,yy,xx+200,yy,'#167e97',True)
for yy in [top+65,top+165]:line(70,yy,205,yy,'#167e97',True);line(1250,yy,1430,yy,'#167e97',True)
text(1270,top+112,'To compressor',18)
line(220,796,1240,796);text(420,825,'Total plate-bearing length = 3.586 m (4 × 0.896 m)',21)
text(50,866,'All gas traverses all four rows. Each row shifts by ¼ of the wide pitch; four phases sample the original spacing.',21)
text(50,902,'Pitch: 30.499 mm  |  clear gap: 29.064 mm  |  thickness, material mass and broad-face area unchanged.',20)
text(50,938,'Model: wide hydraulic gap, original effective thermal gap; edge/turning losses remain charged.',20)
text(50,978,'Schematic slice: transverse spacing/thickness magnified; plate count illustrative. Same axial scale in A and B.',17)
text(50,1008,'Visible row separations are illustrative; real row clearance adds length and must be budgeted. Thermal equivalence assumed; flow validation remains needed.',17)
p.append('</svg>')
out=ROOT/'docs/images/staggered_plate_cooler.svg';out.write_text('\n'.join(p)+'\n')
subprocess.run(['magick','-background','white',str(out),str(out.with_suffix('.png'))],check=True)
