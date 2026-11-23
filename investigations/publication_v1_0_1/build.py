"""Read frozen trajectories; publish metrics/figures without rerunning physics."""
from pathlib import Path
import gzip, json, hashlib
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
fig,(ax,at)=plt.subplots(1,2,figsize=(13,6),layout='constrained');E=np.linspace(0,2*np.pi,600)
ax.add_patch(plt.Circle((0,0),R_EARTH/1000,color='#306eaa',alpha=.85));ax.plot(o.a*(np.cos(E)-o.e)/1000,o.a*np.sqrt(1-o.e**2)*np.sin(E)/1000,color='#d97536');ax.plot(o.rp/1000,0,'o',color='#d97536');ax.set_aspect('equal');ax.set(xlabel='Orbit-plane distance (km)',ylabel='km',title=f'{d["perigee_km"]:.3f} × 2,000 km; {o.period/60:.2f} min')
ax.annotate('Collection at perigee',xy=(o.rp/1000,0),xytext=(-1000,-6500),arrowprops={'arrowstyle':'->'})
at.barh(0,d['burn_s']/60,left=-d['burn_s']/120,color='#ba4a46');at.barh(1,(d['plant_stop_s']-d['plant_start_s'])/60,left=d['plant_start_s']/60,color='#247c8c');at.scatter(max(d['pump_stop_s'],d['burn_s']/2)/60,2,color='#397c49')
for ev in r['events']:at.scatter(ev['time_s']/60,3 if ev['chamber']<4 else 4,color='#dc9840')
at.set_yticks(range(5),['Reboost','Coast processing window','Reserve isolates','Front rack hatch events','Receiver rack hatch event']);at.invert_yaxis();at.axvline(0,color='gray',ls=':');at.set(xlabel='Minutes from perigee',title='Saved-cycle schedule');at.grid(axis='x',alpha=.2)
fig.suptitle('v1.0.1 orbit and cycle\nDawn–dusk SSO is intended; seasonal illumination remains unmodeled');save(fig,'orbit')
print(json.dumps(out,indent=2))
