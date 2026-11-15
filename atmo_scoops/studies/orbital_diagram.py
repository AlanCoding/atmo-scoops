"""Orbit geometry and operating sequence, drawn from the public cycle inputs."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from ..system import inputs_from_dict, simulate
from ..inlet import EncounterControls
from ..orbit import Orbit,R_EARTH
from ..encounter import orbit_state
from ..atmosphere import make_profile


def main():
    inputs=inputs_from_dict(json.loads(Path('configs/reference.json').read_text()))
    inputs['controls']=EncounterControls(suction_scale=.7853937968247334,cutoff_Pa=.032293173704872453)
    result=simulate(**inputs,n=1601)
    d=inputs['design'];cycle=result['outputs']['cycle']
    orbit=Orbit(d.perigee_km,d.apogee_km);atm=make_profile(inputs['scenario'].atmosphere_name)
    def xy(t):
        t=np.asarray(t);M=2*np.pi*t/orbit.period;E=M.copy()
        for _ in range(12):E-=(E-orbit.e*np.sin(E)-M)/(1-orbit.e*np.cos(E))
        return orbit.a*np.sqrt(1-orbit.e**2)*np.sin(E)/R_EARTH,-orbit.a*(np.cos(E)-orbit.e)/R_EARTH
    bg='#0b1424';white='#eef5ff';muted='#a9bfd3';blue='#76b7ff';teal='#75e4d0';orange='#ffad70';purple='#c8b5ff'
    plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans','text.color':white,
        'axes.labelcolor':muted,'xtick.color':muted,'ytick.color':muted,'axes.edgecolor':muted})
    fig=plt.figure(figsize=(15,10),facecolor=bg)
    fig.text(.045,.95,'ONE ORBIT: COLLECT, RECOVER, REPEAT',fontsize=24,weight='bold')
    fig.text(.045,.91,f'{d.perigee_km:g} × {d.apogee_km:,.0f} km comparison orbit • {orbit.period/60:.1f} min / revolution • mouth remains open',fontsize=14,color=muted)
    ax=fig.add_axes([.035,.255,.51,.625],facecolor=bg)
    ax.set_aspect('equal');ax.set(xlim=(-1.65,1.65),ylim=(-1.65,1.7));ax.axis('off')
    ax.add_patch(Circle((0,0),(R_EARTH+200000)/R_EARTH,color='#3f6074',alpha=.65))
    ax.add_patch(Circle((0,0),1,color='#173a55'))
    for yy in (-.6,0,.6):
        xx=np.sqrt(1-yy*yy);ax.plot([-xx,xx],[yy,yy],color='#274b63',lw=.7)
    ax.text(0,.08,'EARTH',ha='center',fontsize=19,weight='bold');ax.text(0,-.1,'Planet at the ellipse focus',ha='center',fontsize=10,color=muted)
    ax.add_patch(Circle((0,0),orbit.ra/R_EARTH,fill=False,edgecolor=purple,ls=(0,(5,5)),lw=1.5))
    t=np.linspace(0,orbit.period,2001);ax.plot(*xy(t),color=blue,lw=2.5)
    ax.plot(*xy(np.linspace(cycle['deploy_complete_s'],cycle['retract_start_s'],900)),color=teal,lw=4)
    ax.plot(*xy(np.linspace(-cycle['collection_s'],cycle['recovery_s'],200)),color=orange,lw=4)
    for f in (.20,.70):
        x0,y0=xy(orbit.period*f);x1,y1=xy(orbit.period*(f+.018))
        ax.annotate('',(x1,y1),(x0,y0),arrowprops={'arrowstyle':'-|>','color':teal,'lw':2,'mutation_scale':14})
    ax.scatter([0,0],[-orbit.rp/R_EARTH,orbit.ra/R_EARTH],s=35,color=[orange,teal],zorder=5)
    ax.annotate(f'Apogee: {d.apogee_km:,.0f} km',xy=(0,orbit.ra/R_EARTH),xytext=(-.8,1.53),fontsize=12,color=teal,
                arrowprops={'arrowstyle':'-','color':teal})
    ax.annotate(f'Perigee: {d.perigee_km:g} km\nCollection + reboost',xy=(0,-orbit.rp/R_EARTH),xytext=(-1.55,-1.48),fontsize=12,color=orange,
                arrowprops={'arrowstyle':'-','color':orange})
    ax.annotate('Circular delivery orbit\nat apogee altitude',xy=(orbit.ra/R_EARTH*.83,-orbit.ra/R_EARTH*.55),xytext=(.35,-1.48),fontsize=10,color=purple,
                arrowprops={'arrowstyle':'-','color':purple})
    ax.text(-1.62,1.12,'Distance scale preserved',fontsize=10,color=muted)
    ax.text(-1.62,.99,'Thin band: 0–200 km',fontsize=10,color=muted)
    ax.text(-1.62,.87,'Not a hard atmosphere edge',fontsize=9,color=muted)
    # Local-altitude inset makes the short low-altitude arc visible without
    # drawing an exaggerated, misleadingly eccentric main orbit.
    zoom=fig.add_axes([.61,.57,.34,.265],facecolor='#101e30')
    ti=np.linspace(-480,480,1201);state=orbit_state(orbit,ti,atm)
    zoom.axvspan(-cycle['collection_s']/60,cycle['recovery_s']/60,color=orange,alpha=.18)
    zoom.axhline(200,color=muted,ls='--',lw=1)
    zoom.plot(ti/60,state['altitude_km'],color=blue,lw=2)
    zoom.axvline(0,color=muted,lw=.8,ls=':')
    zoom.set(xlim=(-8,8),ylim=(80,260),xlabel='Minutes from perigee',ylabel='Altitude (km)')
    zoom.set_title('The atmospheric pass, enlarged',loc='left',color=white,fontsize=14,pad=12)
    zoom.text(-7.5,208,'200 km deployment gate (assumption)',fontsize=9,color=muted)
    zoom.text(.3,245,'Perigee',fontsize=10,color=white)
    zoom.text(-.4,117,'Pumping window',fontsize=10,color=orange)
    zoom.grid(alpha=.12)
    fig.text(.61,.495,f'Inbound collection begins: −{cycle["collection_s"]/60:.2f} min',fontsize=12,color=orange)
    fig.text(.61,.463,f'Open-mouth compressor cutoff: +{cycle["recovery_s"]/60:.2f} min',fontsize=12,color=orange)
    fig.text(.61,.431,f'Fully deployed coast: {cycle["deployed_s"]/60:.1f} min; sunlit: {cycle["sunlit_s"]/60:.1f} min',fontsize=12,color=teal)
    fig.text(.61,.389,'Radiate stored heat • liquefy gas • recharge',fontsize=12,color=teal,weight='bold')
    fig.text(.61,.345,f'Circularization at apogee: ideal Δv ≈ {orbit.circularization_dv:.0f} m/s',fontsize=12,color=purple)
    fig.text(.61,.285,'A circular orbit no longer dives. Delivery / return\nhardware and energy remain outside current payoff.',fontsize=10,color=muted,linespacing=1.5)
    # Time-proportional one-orbit strip, t=0 to next perigee.
    line=fig.add_axes([.08,.12,.84,.075],facecolor=bg)
    line.set(xlim=(0,orbit.period/60),ylim=(0,1),yticks=[],xlabel='Minutes after perigee')
    for side in ('left','right','top'):line.spines[side].set_visible(False)
    line.broken_barh([(0,orbit.period/60)],(.28,.38),facecolors='#33445a')
    for start,end,col in [(0,cycle['recovery_s'],orange),
            (cycle['deploy_complete_s']-cycle['deploy_s'],cycle['deploy_complete_s'],blue),
            (cycle['deploy_complete_s'],cycle['retract_start_s'],teal),
            (cycle['retract_start_s'],cycle['retract_start_s']+cycle['retract_s'],blue),
            (orbit.period-cycle['collection_s'],orbit.period,orange)]:
        line.broken_barh([(start/60,(end-start)/60)],(.28,.38),facecolors=col)
    line.axvline(orbit.period/120,color=white,lw=1,alpha=.7)
    line.text(orbit.period/120,.88,'Apogee',ha='center',fontsize=11)
    line.set_xticks([0,20,40,60,80,100,orbit.period/60]);line.set_xticklabels(['0','20','40','60','80','100',f'{orbit.period/60:.1f}'])
    fig.text(.08,.224,'ONE CYCLE',fontsize=12,weight='bold')
    fig.text(.27,.224,'■ Pumping',fontsize=11,color=orange);fig.text(.40,.224,'■ Deploy / retract',fontsize=11,color=blue)
    fig.text(.58,.224,'■ Deployed coast',fontsize=11,color=teal);fig.text(.76,.224,'■ Stowed / waiting',fontsize=11,color=muted)
    fig.text(.045,.035,'Kepler reference geometry; finite-thrust restoration is not integrated. Lighting omitted from orbit view. Cutoff and deployment are model assumptions.',fontsize=9,color=muted)
    path=Path('docs/images/orbital_cycle.svg');fig.savefig(path,facecolor=bg)
    fig.savefig('/tmp/atmo-orbital-cycle.png',facecolor=bg,dpi=130);plt.close(fig)
    # A machine-readable account prevents caption numbers drifting from inputs.
    Path('results/orbital_diagram.json').write_text(json.dumps(dict(inputs=result['inputs'],cycle=cycle,
        ideal_apogee_circularization_m_s=orbit.circularization_dv,geometry='Kepler, no finite thrust',
        source='Active reference geometry with displayed control settings',
        controls=result['inputs']['controls'],samples=result['numerics']['samples']),indent=2)+'\n')
    # Accessible document description in addition to the visible title.
    svg=path.read_text();pos=svg.index('>',svg.index('<svg'))+1
    svg=svg[:pos]+'\n<title>Atmospheric scoop orbit and operating cycle</title><desc>Earth and the 100 by 2000 kilometre scoop orbit at equal scale, with a circular delivery orbit, an enlarged atmospheric pass and a time-proportional cycle strip. The open-mouth comparison cycle has a 106.2 minute period.</desc>'+svg[pos:]
    path.write_text(svg)
    print(path,cycle)

if __name__=='__main__':main()
