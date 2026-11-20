"""Original editorial schematics, not reproductions or trajectory simulations."""
from pathlib import Path
from html import escape
import math, subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/images/refueling_precedents'
OUT.mkdir(parents=True, exist_ok=True)
BG='#ffffff'; PANEL='#f0f4f8'; INK='#172b40'; MUT='#536779'; BLUE='#1965a3'; GREEN='#13785c'; ORANGE='#a7530c'; RED='#b23e49'
class Fig:
 def __init__(self,title,subtitle,height=960):
  self.height=height
  self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img"><title>{escape(title)}</title><desc>{escape(subtitle)}</desc><defs>']
  for col in [BLUE,GREEN,ORANGE,RED,MUT]:
   self.p.append(f'<marker id="a{col[1:]}" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto"><path d="M0 0L9 3.5L0 7Z" fill="{col}"/></marker>')
  self.p+=['</defs>',f'<rect width="1440" height="{height}" fill="{BG}"/>']
  self.text(54,63,title,32);self.text(54,99,subtitle,19,MUT)
 def text(self,x,y,s,size=19,col=INK,anchor='start'):
  self.p.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{col}" text-anchor="{anchor}">{escape(s)}</text>')
 def lines(self,x,y,ss,size=19,col=MUT):
  for i,s in enumerate(ss):self.text(x,y+i*(size+10),s,size,col)
 def rect(self,x,y,w,h,fill=PANEL,stroke='none',rx=9):
  self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
 def path(self,d,col=BLUE,width=3,fill='none',dash='',arrow=False):
  self.p.append(f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(f' marker-end="url(#a{col[1:]})"' if arrow else '')+'/>')
 def line(self,x,y,X,Y,col=BLUE,width=3,arrow=False,dash=''):
  self.path(f'M{x} {y}L{X} {Y}',col,width,dash=dash,arrow=arrow)
 def circle(self,x,y,r,col,stroke='none',w=2):
  self.p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="{stroke}" stroke-width="{w}"/>')
 def earth(self,x,y,r):
  self.circle(x,y,r+5,'none','#b6d2e8',6);self.circle(x,y,r,'#e0eff9',BLUE)
  self.path(f'M{x-r*.6} {y-r*.3}q{r*.5} {-r*.4} {r*.9} 0t{-r*.2} {r*.7}t{-r*.5} {-r*.5}', '#80b5a0',1,'#b9d8c9')
  self.text(x,y+7,'EARTH',18,INK,'middle')
 def box(self,x,y,w,title,lines,col=BLUE):
  self.rect(x,y,w,48+len(lines)*29);self.text(x+18,y+29,title,20,col);self.lines(x+18,y+61,lines,18)
 def save(self,name,source):
  self.text(54,self.height-35,source,15,MUT);self.p.append('</svg>');p=OUT/(name+'.svg');p.write_text('\n'.join(self.p)+'\n')
  subprocess.run(['magick','-background',BG,'-density','144',str(p),str(p.with_suffix('.png'))],check=True)
  print(p)

def orbit(f,fx,fy,rp,ra,k,col,dash=''):
 a=(rp+ra)/2*k;b=math.sqrt(rp*ra)*k;cx=fx+(ra-rp)/2*k
 f.p.append(f'<ellipse cx="{cx}" cy="{fy}" rx="{a}" ry="{b}" fill="none" stroke="{col}" stroke-width="3" stroke-dasharray="{dash}"/>')
 return cx,a,b

def min_orbit():
 f=Fig('MINOVITCH · 1988 | Capture while descending','A nuclear-electric transfer vehicle collects air as atmospheric drag lowers its return-orbit apogee.')
 fx,fy,k=310,430,85/6371
 # Reference return ellipses: common perigee is schematic, not propagated.
 for ha,col,dash in [(35786,BLUE,''),(18000,MUT,'9 7'),(7000,MUT,'9 7'),(200,ORANGE,'')]:orbit(f,fx,fy,6421,6371+ha,k,col,dash)
 f.earth(fx,fy,85);f.circle(fx,fy,6571*k,'none',GREEN)
 f.text(650,177,'GEO departure → atmospheric return',22,BLUE,'middle')
 f.line(873,430,873,500,BLUE,3,True);f.text(900,428,'GEO',21,BLUE)
 f.text(900,458,'35,786 km',17,MUT)
 f.circle(224,430,7,ORANGE);f.line(220,446,112,566,ORANGE,2)
 f.lines(56,598,['Atmospheric capture','50 km perigee in the','single-dive example'],19,ORANGE)
 f.line(600,333,488,350,MUT,3,True);f.text(540,310,'Apogee decreases',19,MUT)
 f.line(399,431,399,495,GREEN,3,True);f.lines(458,431,['Final burn at low apogee','raises perigee → circular LEO'],17,GREEN)
 f.box(1010,160,375,'1  Powered transfer',['Onboard nuclear-electric engine','takes the vehicle from LEO to GEO.','Payload is delivered there.'])
 f.box(1010,320,375,'2  Return and collect',['Lower perigee into atmosphere.','Capture drag brakes the craft;','no restoration of high apogee.'],ORANGE)
 f.box(1010,480,375,'3  Finish in low orbit',['After capture, raise perigee','with an onboard engine burn','near the new, low apogee.'],GREEN)
 f.box(55,710,1330,'REFUELING DURING A TRANSFER — NOT A FIXED COLLECTION ELLIPSE',[
 'The description allows several decelerating passes. Its worked numerical example uses one dive near 50 km.',
 'Dashed ellipses illustrate falling apogee; they are not calculated intermediate trajectories. Outbound spiral omitted.',
 'Earth and the example return ellipses share a distance scale. Atmospheric thickness and event markers are exaggerated.'],ORANGE)
 f.save('minovitch_1988_orbit','Source: US 4,754,601 · description of Fig. 9 and Earth-return example. Original schematic; powered maneuvers are retained.')

def min_craft():
 f=Fig('MINOVITCH · 1988 | Nuclear-electric collector / transport','Capture phase emphasized below; radiators shown in dotted lines will unfurl in the coast phase.',height=780)
 f.line(430,190,120,190,BLUE,4,True);f.text(120,168,'Vehicle motion',19,BLUE)
 x,y=150,440
 # 4 px/m: overall 250m; inlet22m, body14m; diffuser48m.
 f.path('M150 396L342 412L1150 412L1150 468L342 468L150 484',MUT,2,'#edf2f7')
 f.line(150,396,150,484,BLUE,4)
 f.path('M150 404L320 430L385 430 M150 476L320 450L385 450',ORANGE,3)
 for a in [68,105]:f.line(a,440,a+48,440,BLUE,3,True)
 f.rect(365,415,100,50,'#fae0c7',ORANGE,2);f.rect(475,415,110,50,'#e2e8ef',MUT,2)
 for a in [598,624,650]:f.rect(a,416,18,48,'#d9eee5',GREEN,2)
 f.rect(685,415,95,50,'#dcebf9',BLUE,18)
 f.rect(798,415,110,50,'#f4dfb9',ORANGE,2)
 f.rect(930,415,165,50,'#e3eaf2',MUT,3)
 f.path('M1095 418L1150 410L1150 470L1095 462',BLUE,2,'#dbeaf8')
 f.rect(950,414,40,52,'#dcebf9',BLUE,12)
 f.rect(950,437,40,6,BG,BLUE,0)
 f.path('M990 450L1190 510',BLUE,2)
 f.lines(1110,550,['LN₂ tank 149','1,000,000 kg','10 m × 13 m','Toroidal; access tunnel'],17,BLUE)
 # Schematic radiator wings: dashed deployed, solid stowed.
 for a,b in [(800,910),(947,1060)]:
  f.path(f'M{a} 412L{a-30} 270L{b+30} 270L{b} 412',ORANGE,2,dash='7 6')
  f.path(f'M{a} 468L{a-30} 610L{b+30} 610L{b} 468',ORANGE,2,dash='7 6')
  f.rect(a,402,b-a,7,'#c58f50',rx=0);f.rect(a,471,b-a,7,'#c58f50',rx=0)
 f.lines(75,340,['22 m inlet','48 m diffuser'],18,BLUE);f.line(188,369,222,409,BLUE,2)
 f.lines(270,245,['Hypervelocity intake and','radiative cooling chamber','Gas cooled to ~1,600 K'],19,ORANGE);f.line(420,319,420,413,ORANGE,2)
 f.lines(490,355,['Tank 52','Hot-gas buffer: 500 m³'],17,MUT);f.line(530,389,530,413,MUT,2)
 # Hypothetical isolation valve; explicitly NOT attributed to the patent.
 f.path('M460 430L480 450L480 430L460 450Z',RED,2,BG)
 f.text(470,416,'?',25,RED,'middle');f.path('M470 452L420 510L350 510',RED,2)
 f.lines(100,540,['Isolation valve ?','Not specified in the patent'],18,RED)
 f.lines(550,550,['Compression + cooling','Liquefier → cryogenic tanks'],18,GREEN);f.line(636,474,636,518,GREEN,2)
 f.lines(760,214,['3,500 MW nuclear-electric plant','Folding power-plant radiators'],18,ORANGE);f.line(845,258,845,269,ORANGE,2)
 f.lines(1100,305,['Onboard microwave /','ECR accelerator','and its radiators'],17,BLUE);f.line(1130,374,1125,409,BLUE,2)
 f.text(1080,650,'Processing continues after the atmospheric pass',17,MUT,'end')
 f.line(150,680,1150,680,MUT,2);f.line(150,668,150,692,MUT,2);f.line(1150,668,1150,692,MUT,2)
 f.text(650,711,'250 m overall',20,INK,'middle')
 f.save('minovitch_1988_craft','Source: US Patent 4,754,601')

def slough_orbit():
 f=Fig('SLOUGH · 2022 | Refueling Orbital Navigator','Repeated collection with perigee drag compensation — a different design from the 2026 Space Gas Station.')
 fx,fy,k=395,445,245/6371
 orbit(f,fx,fy,6521,7321,k,BLUE);f.earth(fx,fy,245)
 # circle ring is atmosphere context, not a second orbit
 f.circle(fx,fy,6521*k,'none','#c2d0db',1)
 px=fx-6521*k;ax=fx+7321*k
 f.circle(px,fy,8,ORANGE);f.circle(ax,fy,6,BLUE)
 f.lines(60,160,['PERIGEE','150 km nominal','151 km worked case'],18,ORANGE);f.line(143,238,px,422,ORANGE,2)
 f.line(px,445,px,365,GREEN,4,True);f.line(px,453,px,510,ORANGE,3,True)
 f.text(66,550,'Thrust ↑',17,GREEN);f.text(66,579,'Drag ↓',17,ORANGE)
 f.line(ax-5,445,ax-5,505,BLUE,3,True);f.lines(700,425,['APOGEE','950 km'],20,BLUE)
 f.box(900,155,485,'1  Perigee: collect + reboost',['Scoop → compressors → gas tank.','Batteries supply the Hall thruster.','Some collected gas offsets drag.'],ORANGE)
 f.box(900,340,485,'2  Coast: recharge',['Solar supply replenishes batteries.','Net collected gas remains in storage.','Return to the collection pass.'],GREEN)
 f.box(900,525,485,'3  After refueling',['Leave the collection orbit to perform','the next servicing / debris mission.'],BLUE)
 f.box(55,755,1330,'REPEATED REFUELING IS EXPLICIT IN THE 2022 PAPER',[
 'The paper proposes maintaining the collection orbit with perigee thrust, rather than letting apogee decay each pass.',
 'Earth and orbit are drawn at the same scale: 150 × 950 km is only modestly eccentric (e ≈ 0.058).',
 'Arrows show force directions at perigee, not a calculated thrust profile; exact orbit closure is not independently verified here.'],GREEN)
 f.save('slough_2022_orbit','Source: Slough, RON (IEEE Aerospace 2022), pp. 5–6, mission stage 3 and Fig. 9. Original explanatory schematic.')

def solar(f,x,y,w,h):
 f.rect(x,y,w,h,'#d9e9f8',BLUE,2)
 for a in range(int(x)+25,int(x+w),25):f.line(a,y,a,y+h,'#94b4d1',1)
 for b in range(int(y)+20,int(y+h),20):f.line(x,b,x+w,b,'#94b4d1',1)

def slough_craft():
 f=Fig('SLOUGH · 2022 | Scoop, pumps, gas tank and Hall thruster','Functional side cutaway • collected gas is stored under pressure, rather than processed into cryogenic liquid.')
 f.line(460,195,160,195,BLUE,4,True);f.text(160,171,'Motion / perigee thrust',19,BLUE)
 # Frontal silhouette boundaries and panels inside that silhouette.
 f.line(200,290,1190,290,MUT,1,False,'5 7');f.line(200,610,1190,610,MUT,1,False,'5 7')
 solar(f,630,310,380,68);solar(f,630,522,380,68)
 f.path('M200 290L570 412L610 412L610 488L570 488L200 610',BLUE,4,'#e8f1f8')
 # Sectional dividers suggest the multiple-cone collector; not a cone-count specification.
 for yy in [310,365,420,475,530,585]:
  end=450+(yy-450)*.12
  f.path(f'M215 {yy}L560 {end}',MUT,2)
 for xx,yy in [(300,323),(360,344),(420,366)]:
  f.path(f'M{xx} {yy}q-10 -12 0 -24t0 -24l0 -15',ORANGE,2,arrow=True)
 f.text(90,232,'Passive radiation to space',18,ORANGE)
 f.line(200,290,200,610,BLUE,5)
 for yy in [375,450,525]:f.line(65,yy,265,yy,BLUE,3,True)
 f.rect(610,410,140,80,'#d6eee3',GREEN,3)
 for xx in [630,666,702]:
  f.path(f'M{xx} 425l16 25l-16 25 M{xx+10} 425l16 25l-16 25',GREEN,2)
 f.rect(775,405,230,90,'#dcebf9',BLUE,42);f.line(750,450,775,450,GREEN,4,True)
 f.rect(615,380,150,25,'#f4dfb9',ORANGE,4);f.text(690,398,'Batteries',15,INK,'middle')
 f.line(765,391,1055,391,ORANGE,2);f.line(1055,391,1055,418,ORANGE,2,True)
 f.rect(1030,420,55,60,'#e0eaf4',BLUE,4)
 f.path('M1085 426L1240 395L1240 505L1085 474',BLUE,2,'#e9f2fa')
 f.line(1005,450,1030,450,GREEN,3,True)
 f.text(1190,540,'Exhaust →',19,BLUE,'middle');f.line(1140,565,1250,565,BLUE,3,True)
 f.lines(150,680,['Multi-cone intake / passive cooler','3.5 m reference diameter'],18,BLUE);f.line(390,624,390,554,BLUE,2)
 f.lines(600,235,['5 kW solar panels inside the scoop silhouette','No panel folding sequence assumed'],18,BLUE);f.line(830,265,830,308,BLUE,2)
 f.lines(530,670,['Multi-stage','pumping / compression'],18,GREEN);f.line(600,620,655,490,GREEN,2)
 f.lines(810,728,['Gas tank: 1,000 psi (~69 bar)','Nitrogen-bearing atmospheric propellant'],18,BLUE)
 f.lines(1120,300,['30 kW','Hall thruster'],20,BLUE);f.line(1150,343,1060,418,BLUE,2)
 f.box(55,775,650,'COLLECTION PASS',['Gas enters from the left; captured material feeds storage.','The battery-backed thruster provides forward drag makeup.'],GREEN)
 f.box(730,775,655,'COAST',['Solar energy restores the electrical reserve for later passes.','Tank and machinery placement are schematic, not scaled.'],BLUE)
 f.save('slough_2022_craft','Source: Slough, RON (2022), pp. 5–6, Table III and Fig. 20. Original schematic; no 2026 ion grid or cold head included.')

if __name__=='__main__':
 min_orbit();min_craft();slough_orbit();slough_craft()
