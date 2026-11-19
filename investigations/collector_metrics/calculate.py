"""Frozen-trajectory collector boundary accounting; does not run/alter the model."""
import gzip,json,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'results/transient/plates/reference_validation/case_72.json.gz'
r=json.load(gzip.open(source,'rt'));d=r['inputs']['design'];c=r['inputs']['capabilities'];h=r['hardware'];m=h['masses_kg'];t=np.asarray(r['time_s']);hist=r['history']
stop=d['pump_stop_s'];ix=np.flatnonzero(t<=stop);tt=t[ix]
# Before plant start: load contains thrust, dive pump/idle/spin, auxiliary,
# and cryogenic holding power. Subtract thrust and holding, retain auxiliary.
assert stop<d['plant_start_s']
warm=np.asarray(hist['warm_K'])[ix]
hold=c['tank_heat_W']*np.maximum((warm+20)/70-1,0)/c['carnot_fraction']/1e6
power=np.maximum(0,np.asarray(hist['load_MW'])[ix]-np.asarray(hist['thrust_MW'])[ix]-hold)
energy=float(np.trapezoid(power,tt)/3600)
# Rating sizes to the installed four dive motors, not sampled transient maxima.
rating=sum(d['motor_MW'])+c['auxiliary_W']/1e6
usable=d['battery_initial_soc']-(1-c['battery_usable'])
capacity=energy/c['discharge_eta']/usable
battery=max(capacity*1e6/c['battery_Wh_kg'],rating*1e6/c['battery_W_kg'])
shaft=float(np.interp(stop,t,r['ledger']['shaft_MJ']))/3600
# All electrical energy not left in gas as shaft work eventually becomes heat,
# including rotor braking. No radiation credit during this one-pass accounting.
heat=(energy/c['discharge_eta']-shaft)*3.6e9
store=heat/(c['buffer_cp_J_kg_K']*(d['warm_max_K']-d['warm_initial_K']))
kept={k:m[k] for k in ['racks','rack_mechanisms','dive_compressors','pressure_vessels','hull','auxiliary']}
kept.update(battery=battery,bus=rating*1000*c['bus_kg_kW'],warm_store=store)
base=sum(kept.values());mass=base*(1+c['margin'])
i=int(ix[-1]);initial=np.asarray(r['gas_species_kg'])[0,4].sum();product=float(np.asarray(r['gas_species_kg'])[i,4].sum()-initial)
# Solar addition: recharge AFTER handoff in the saved orbit's outbound/coast
# window, using the existing eclipse function recovered from full-array output.
phase=np.where(t>(h['end_s']-h['start_s'])/2,t-(h['end_s']-h['start_s']),t)
oldex=np.clip((abs(phase)-h['safe_s'])/h['array_motion_s'],0,1)
sun=np.divide(np.asarray(hist['solar_MW'])*1e6,d['solar_area_m2']*c['solar_W_m2']*oldex,out=np.zeros_like(t),where=oldex>1e-8)
# Recharge and run controls after capture; retain battery for all compression.
coast_aux=c['auxiliary_W']*(t[-1]-stop)/3.6e9
recharge=energy/(c['discharge_eta']*c['charge_eta'])+coast_aux
# Restart deployment at handoff; stop using panel at original inward stow boundary.
def collected(area):
 motion=np.sqrt(area)/c['deployment_m_s']
 exposure=np.clip((t-max(stop,h['safe_s']))/motion,0,1)*np.clip((abs(phase)-h['safe_s'])/motion,0,1)
 return float(np.trapezoid(area*c['solar_W_m2']*exposure*sun,t)/3.6e9)
area=brentq(lambda a:collected(a)-recharge,1.,d['solar_area_m2'])
solar=area*c['solar_W_m2']/c['solar_W_kg']
result=dict(source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),endpoint_s=stop,captured_new_receiver_gas_kg=product,receiver_pressure_Pa=hist['pressure_Pa'][i][4],receiver_temperature_K=hist['gas_K'][i][4],capture_load_MWh=energy,shaft_to_gas_MWh=shaft,installed_capture_rating_MW=rating,sampled_peak_capture_MW=float(max(power)),battery_MWh=capacity,thermal_store_heat_MJ=heat/1e6,components_kg=kept,margin_fraction=c['margin'],battery_only_dry_kg=mass,battery_only_capture_kg_per_kg=product/mass,battery_only_equivalent_passes=mass/product,solar_area_m2=area,solar_mass_kg=solar,solar_recharge_MWh=recharge,solar_addition_dry_kg=(base+solar)*(1+c['margin']),solar_addition_capture_kg_per_kg=product/((base+solar)*(1+c['margin'])),solar_addition_equivalent_passes=(base+solar)*(1+c['margin'])/product,notes=['Frozen trajectory attribution, not a new feasible forward simulation.','Compressed gas at 600 s, not cryogenic liquid; upstream residual gas is excluded.','Thermal buffer sized conservatively without radiative credit; retained rack mechanisms permit external reset.','Solar variant adds electrical recharge only: thermal reset, handoff, orbit restoration and mothership mass are external.','All hull and pressure vessel mass retained; no credit for using freed volume or changing structure.'])
(ROOT/'investigations/collector_metrics/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
