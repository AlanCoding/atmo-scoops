"""Read frozen trajectories; publish metrics/figures without rerunning physics."""
from pathlib import Path
import gzip, json, hashlib, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atmo_scoops.orbit import Orbit, R_EARTH
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'results/transient/valve_restore/selected_refined.json.gz'
r=json.load(gzip.open(SRC,'rt'));h=r['history'];hw=r['hardware'];d=r['inputs']['design'];c=r['inputs']['capabilities'];t=np.array(r['time_s']);o=Orbit(d['perigee_km'],d['apogee_km'])
ledger={k:v[-1] for k,v in r['ledger'].items()}
def species(prefix):return sum(ledger[prefix+s] for s in ('N2','O2','Ar'))
admitted=species('in_');incident=admitted+r['closure']['missed_capture_kg'];required=2*c['eta_thruster']*hw['thrust_W']/(d['isp_s']*9.80665)**2
out=dict(source=str(SRC.relative_to(ROOT)),sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),version='1.0.1',payoff_days=r['operating_payoff_days'],dry_t=r['dry_kg']/1000,product_kg=r['net_liquid_kg'],admitted_kg=admitted,incident_kg=incident,capture_fraction=admitted/incident,lost_kg=species('lost_'),propellant_kg=species('prop_'),minimum_reserve_kg=min(h['buffer_kg']),minimum_reserve_Pa=min(h['buffer_Pa']),minimum_feed_capacity_kg_s=min(h['feed_capacity_kg_s']),full_thrust_demand_kg_s=required,thrust_relative_error=r['closure']['thrust_relative'],unresolved_exospheric_incident_kg=hw['unresolved_exospheric_incident_kg'],perigee_km=d['perigee_km'],apogee_km=d['apogee_km'],period_min=o.period/60,solar_m2=d['solar_area_m2'],warm_radiator_physical_m2=d['warm_radiator_m2'],rack_physical_m2=sum(g['deployed_physical_m2'] for g in hw['geometry']))
old=json.load(gzip.open(ROOT/'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz','rt'))
out['rejected_comparison']=dict(payoff_days=old['operating_payoff_days'],perigee_km=old['inputs']['design']['perigee_km'],dry_t=old['dry_kg']/1000,product_kg=old['net_liquid_kg'],main_receiver_gas_m3=old['hardware']['geometry'][-1]['gas_m3'],current_main_receiver_gas_m3=hw['geometry'][-1]['gas_m3'],dry_mass_ratio=r['dry_kg']/old['dry_kg'],product_ratio=r['net_liquid_kg']/old['net_liquid_kg'])
Path(__file__).with_name('metrics.json').write_text(json.dumps(out,indent=2)+'\n')
plt.rcParams.update({'svg.fonttype':'none','font.size':10})
def save(fig,name):
 if '--orbit-only' in sys.argv and name not in ('orbit','schedule'):
  plt.close(fig);return
 for ext in ['svg','png']:
  path=ROOT/f'docs/images/v1_0_1_{name}.{ext}'
  fig.savefig(path,dpi=160)
  if ext=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 plt.close(fig)
fig,ax=plt.subplots(figsize=(10,7),layout='constrained');items=sorted(hw['masses_kg'].items(),key=lambda z:z[1]);ax.barh([k.replace('_',' ') for k,v in items],[v/1000 for k,v in items],color='#247c8c');ax.set(xlabel='Dry mass (tonnes)',title='v1.0.1 mass budget — 12,840 tonnes');ax.grid(axis='x',alpha=.2);save(fig,'mass')
fig,(ax,ay)=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
ax.plot(t/60,h['buffer_kg'],label='Reserve gas');ax.set(ylabel='Reserve mass (kg)',title='v1.0.1: retained gas and finite feed capacity');ax.legend()
ay.plot(t/60,h['feed_capacity_kg_s'],label='Available feed capacity');ay.plot(t/60,np.array(h['thrust_MW'])*1e6*2*c['eta_thruster']/(d['isp_s']*9.80665)**2,label='Actual thrust gas flow');ay.set(xlabel='Minutes from perigee',ylabel='kg/s',xlim=(-12,12));ay.legend()
for a in [ax,ay]:a.grid(alpha=.2)
save(fig,'feed')
fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
for i in range(5):ax.plot(t/60,np.array(h['rack_K'])[:,i],label=f'Rack {i+1}: {d["materials"][i]}')
ax.set(xlabel='Minutes from perigee',ylabel='Solid temperature (K)',title='v1.0.1 solid coolers — capture heat, deploy, radiate, return');ax.legend();ax.grid(alpha=.2);save(fig,'coolers')
# Illustrative product-collection orbit: same apogee and apsidal orientation.
# Sharing a position does not match velocity or phase; transfer is not costed.
pickup=Orbit(1000.,d['apogee_km'])
fig,ax=plt.subplots(figsize=(9,9),layout='constrained');E=np.linspace(0,2*np.pi,600)
earth=plt.Circle((0,0),R_EARTH/1000,facecolor='#d3eff7',edgecolor='#77b5c6',lw=1.2)
ax.add_patch(earth)
# Stylized land silhouettes, not a geographical map or orbit-plane orientation.
from matplotlib.patches import Polygon
for coords in [
 [(-4700,3500),(-3200,5100),(-1200,4700),(-1700,3400),(-700,2200),(-2200,1300),(-2800,-300),(-4000,900)],
 [(-2200,-500),(-600,-1700),(-900,-3300),(-2100,-5200),(-2700,-3100),(-3000,-1300)],
 [(500,4200),(2800,4900),(5100,3200),(4300,1900),(2500,2200),(1800,400),(3100,-500),(1400,-2600),(-100,-1000),(200,1200)],
 [(3700,-2600),(5100,-2400),(5700,-3600),(4200,-4000)]]:
 land=Polygon(coords,closed=True,facecolor='#a9d8ae',edgecolor='none');land.set_clip_path(earth);ax.add_patch(land)
ax.text(0,0,'Earth',ha='center',va='center',color='#326053',fontsize=15)
ax.plot(o.a*(np.cos(E)-o.e)/1000,o.a*np.sqrt(1-o.e**2)*np.sin(E)/1000,color='#c45d16',lw=2.3,label=f'Diver: {d["perigee_km"]:.1f} × 2,000 km')
ax.plot(pickup.a*(np.cos(E)-pickup.e)/1000,pickup.a*np.sqrt(1-pickup.e**2)*np.sin(E)/1000,color='#684397',lw=2,ls='--',label='Product collection: 1,000 × 2,000 km (illustrative)')
ax.plot(o.rp/1000,0,'o',color='#c45d16',zorder=5)
ax.plot(-o.ra/1000,0,'o',color='#684397',zorder=5)
ax.set_aspect('equal');ax.set(xlim=(-11200,11200),ylim=(-10500,11200),xlabel='Orbit-plane distance (km)',ylabel='km',title=f'Operating orbit and product pickup · diver period {o.period/60:.2f} min')
ax.legend(loc='upper center',fontsize=9,frameon=True,facecolor='white')
ax.annotate('Atmospheric collection\nat diver perigee',xy=(o.rp/1000,0),xytext=(4300,-9000),ha='center',fontsize=10,arrowprops={'arrowstyle':'->','color':'#914813'},bbox={'facecolor':'white','edgecolor':'none','pad':3})
ax.annotate('Shared apogee altitude\nCandidate handoff region',xy=(-o.ra/1000,0),xytext=(-3800,-9000),ha='center',fontsize=10,arrowprops={'arrowstyle':'->','color':'#684397'},bbox={'facecolor':'white','edgecolor':'none','pad':3})
ax.text(.5,-.13,'Rendezvous requires phasing and velocity matching; delivery cost is not modeled.',transform=ax.transAxes,ha='center',fontsize=9,color='#48545b')
fig.suptitle('v1.0.1 operating and product-collection orbits\nDawn–dusk SSO intended; seasonal illumination remains unmodeled');save(fig,'orbit')

# Use the exact prescribed forcing grid from the selected configuration.
# This is inlet-support/ram pressure rho*v^2, not a resolved shock stagnation state.
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
forcing=compile_hardware(*read_config(r['inputs']))['forcing']
ft=np.asarray(forcing['time']);fp=np.asarray(forcing['pressure']);peak=float(fp.max());threshold=.1*peak
hit=np.flatnonzero(fp>=threshold);i,j=int(hit[0]),int(hit[-1])
assert 0<i<=j<len(ft)-1
assert np.all(np.diff(hit)==1), 'Expected one contiguous collection window'
def crossing(a,b):return float(ft[a]+(threshold-fp[a])*(ft[b]-ft[a])/(fp[b]-fp[a]))
left,right=crossing(i-1,i),crossing(j,j+1)
schedule=dict(pressure_definition='Prescribed inlet-support ram pressure rho*v^2; not resolved stagnation pressure',peak_Pa=peak,threshold_fraction=.1,threshold_Pa=threshold,collection_start_s=left,collection_end_s=right,collection_duration_s=right-left,reboost_duration_s=d['burn_s'],collection_over_reboost=(right-left)/d['burn_s'])
Path(__file__).with_name('schedule.json').write_text(json.dumps(schedule,indent=2)+'\n')
fig,at=plt.subplots(figsize=(12,4.6),layout='constrained')
bars=[('Reboost',-d['burn_s']/120,d['burn_s']/60,'#ba4a46'),('Collection',left/60,(right-left)/60,'#c45d16'),('Coast processing window',d['plant_start_s']/60,(d['plant_stop_s']-d['plant_start_s'])/60,'#247c8c')]
for y,(label,start,width,color) in enumerate(bars):
 at.barh(y,width,left=start,height=.48,color=color)
 at.text(start+width+.7,y,f'{width:.2f} min',va='center',fontsize=11,color='#33444b')
at.set_yticks(range(3),[b[0] for b in bars]);at.invert_yaxis();at.axvline(0,color='#606b70',ls=':',lw=1.2)
at.set(xlim=(-12,80),xlabel='Minutes from perigee',title='v1.0.1 cycle schedule')
at.grid(axis='x',alpha=.2);at.set_axisbelow(True)
at.text(.5,-.25,'Collection bar: inlet-support pressure ≥ 10% of peak. Lower-rate collection continues outside this window.',transform=at.transAxes,ha='center',fontsize=10,color='#48545b')
save(fig,'schedule')
print(json.dumps(schedule,indent=2))
