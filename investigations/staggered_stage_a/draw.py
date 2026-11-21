"""Equal-scale checkpoint geometry; no invented front equipment bays."""
import argparse,html,subprocess
from pathlib import Path
from atmo_scoops.transient.io import read_result
p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=read_result(a.result);h=r['hardware'];packing=h['stage_packing'];scale=4.;x0=90.;y0=170.;height=h['outside_m']*scale
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="760" viewBox="0 0 1500 760"><rect width="1500" height="760" fill="white"/><style>text{font-family:DejaVu Sans,sans-serif;fill:#233748}</style>']
def text(x,y,s,size=18):parts.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>')
def box(start,end,color):parts.append(f'<rect x="{x0+start*scale}" y="{y0}" width="{(end-start)*scale}" height="{height}" fill="{color}" stroke="#5f7785" stroke-width="0.7"/>')
text(55,45,'Combined cooler and stage-packing candidate',30);text(55,78,'Exact axial scale from the saved simulation • not the published v1.0 reference',18)
box(0,h['length_m'],'#edf5f7')
for s in packing['stages']:
 box(s['gas_start_m'],s['gas_end_m'],'#edf5f7');box(s['rack_start_m'],s['rack_end_m'],'#cd8b46');box(s['compressor_start_m'],s['compressor_end_m'],'#a5b8c8');box(s['hatch_start_m'],s['hatch_end_m'],'#bbaccf')
text(x0,y0-18,'Mouth → flow',18);text(x0+packing['receiver_start_m']*scale+30,y0+height/2,'Aft receiver: residual gas volume after equipment displacement',17)
text(55,340,'Blue-white: gas space   •   Amber: plate rack   •   Grey: compressor   •   Purple: 1 m hatch equipment',18)
text(55,373,'Front clear space: 10 m. Downstream pressure-vessel heads retain their explicit gas volume.',17)
for xx,label in [(55,'Stage'),(155,'Gas region (m)'),(430,'Rack region (m)'),(700,'Compressor (m)'),(1000,'Hatch region (m)')]:text(xx,415,label,18)
for i,s in enumerate(packing['stages']):
 yy=451+i*34
 text(55,yy,str(i+1));
 for xx,k in [(155,'gas'),(430,'rack'),(700,'compressor'),(1000,'hatch')]:text(xx,yy,f"{s[k+'_start_m']:.3f}–{s[k+'_end_m']:.3f}")
text(55,615,f"Receiver: x = {packing['receiver_start_m']:.3f}–{packing['receiver_end_m']:.3f} m. Hull OD {h['outside_m']:.1f} m; length {h['length_m']:.1f} m.",18)
text(55,650,'Other equipment volume is retained in the receiver budget; radial locations await the next checkpoint.',17)
text(55,682,'The last-125-m isolation tank, five-pass liquid storage and relocated thruster hardware are not implemented here.',17)
parts.append('</svg>');a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(parts));subprocess.run(['magick','-background','white',str(a.output),str(a.output.with_suffix('.png'))],check=True)
