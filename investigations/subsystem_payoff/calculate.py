"""Frozen v1.0.1 attribution and continuous-duty paper screen; no new cycle."""
from pathlib import Path
import gzip,json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
src=ROOT/'results/transient/valve_restore/selected_refined.json.gz'
r=json.load(gzip.open(src,'rt'));h=r['history'];hw=r['hardware'];d=r['inputs']['design'];c=r['inputs']['capabilities'];m=hw['masses_kg'];t=np.array(r['time_s']);period=hw['end_s']-hw['start_s'];led={k:v[-1] for k,v in r['ledger'].items()}
integ=lambda v:float(np.trapezoid(v,t)/3600)
load=np.array(h['load_MW']);thr=np.array(h['thrust_MW']);solar=np.array(h['solar_MW']);warm=np.array(h['warm_K'])
thrust_energy=hw['thrust_W']/1e6*d['burn_s']/3600
plant=led['plant_MJ']/3600
hold=c['tank_heat_W']*np.maximum((warm+20)/70-1,0)/c['carnot_fraction']/1e6
aux=c['auxiliary_W']/1e6*period/3600
# All other delivered power includes four dive motors, spinup, idle, channel loss.
dive=integ(load)-thrust_energy-plant-integ(hold)-aux
fraction=np.divide(thr,load,out=np.zeros_like(thr),where=load>0)
discharge=np.maximum(load-solar,0)
battery_fraction=integ(discharge*fraction)/integ(discharge)
# Charge/discharge losses from stored energy changes; no summing available solar as used.
batE=np.array(h['SOC'])*d['battery_MWh'];delta=np.diff(batE)
battout=-float(delta[delta<0].sum())*c['discharge_eta'];chargein=float(delta[delta>0].sum())/c['charge_eta']
battloss=chargein-battout-(batE[-1]-batE[0])
source=led['solar_MJ']/3600
source_prop=thrust_energy+battloss*battery_fraction
solar_fraction=source_prop/source
bus_fraction=hw['thrust_W']/1e6/d['bus_MW']
phase=np.where(t>period/2,t-period,t)
ex=np.clip((np.abs(phase)-hw['safe_s'])/hw['radiator_motion_s'],0,1)
qr=ex*2*d['warm_radiator_m2']*np.maximum(0,c['radiator_emissivity']*c['radiator_view']*5.670374419e-8*warm**4-c['environment_W_m2'])*np.clip((warm-d['warm_initial_K'])/.5,0,1)/1e6
warm_heat=integ(qr)+(warm[-1]-warm[0])*d['warm_store_kg']*c['buffer_cp_J_kg_K']/3.6e9
prop_heat=thrust_energy*(1-c['eta_thruster'])*c['retained_thruster_loss']+battloss*battery_fraction
thermal_fraction=prop_heat/warm_heat
fractions=dict(solar=solar_fraction,battery=battery_fraction,bus=bus_fraction,warm_store=thermal_fraction,warm_radiator=thermal_fraction,hull=d['reserve_depth_m']/hw['length_m'],pressure_vessels=hw['gas_system']['shell_and_support_kg']/m['pressure_vessels'],thrusters=1.,gas_reserve_system=1.)
alloc=[]
for k,v in m.items():
 if k=='margin':continue
 f=fractions.get(k,0.);assert 0<=f<=1,(k,f)
 alloc.append(dict(component=k,total_kg=v,propulsion_kg=v*f,collection_kg=v*(1-f),propulsion_fraction=f))
mp=sum(x['propulsion_kg'] for x in alloc);mc=sum(x['collection_kg'] for x in alloc)
alloc.append(dict(component='margin',total_kg=m['margin'],propulsion_kg=mp*c['margin'],collection_kg=mc*c['margin'],propulsion_fraction=mp/(mp+mc)))
mp*=1+c['margin'];mc*=1+c['margin'];assert abs(mp+mc-r['dry_kg'])<1e-6
rate=r['net_liquid_kg']*86400/period
# Requested minimal paper adjustment: replace pulse-rated thrusters by average
# power at same Isp/efficiency and same impulse per accounting cycle; delete
# attributed battery. Keep ALL other allocated masses, including bus and arrays.
duty=d['burn_s']/period
new_thr=m['thrusters']*duty
battery_prop=m['battery']*battery_fraction
mp_cont=mp-(battery_prop+m['thrusters']-new_thr)*(1+c['margin'])
assert mp_cont>0
energy=dict(thrust_electric_MWh=thrust_energy,dive_motors_spin_idle_loss_MWh=dive,coast_compression_liquefaction_separation_MWh=plant,cryo_holding_MWh=integ(hold),auxiliary_MWh=aux,load_integral_MWh=integ(load),battery_charge_input_MWh=chargein,battery_output_MWh=battout,battery_loss_MWh=battloss,solar_used_ledger_MWh=source,electrical_closure_difference_MWh=source-(integ(load)+battloss+batE[-1]-batE[0]),warm_heat_input_MWh=warm_heat,warm_radiated_MWh=integ(qr),solid_radiated_MWh=led['radiated_MJ']/3600-integ(qr),shaft_work_MWh=led['shaft_MJ']/3600,rack_friction_electric_MWh=sum(led[f'rack_loss_{i}_MJ'] for i in range(5))/3600)
result=dict(source=str(src.relative_to(ROOT)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),denominator='same net new useful liquid production for all payoff contributions',product_rate_kg_day=rate,energy=energy,allocation_fractions=fractions,mass_allocation=alloc,propulsion_dry_kg=mp,collection_dry_kg=mc,propulsion_payoff_days=mp/rate,collection_payoff_days=mc/rate,combined_payoff_days=(mp+mc)/rate,continuous_screen=dict(isp_s=d['isp_s'],same_impulse_Ns=hw['required_impulse_Ns'],period_s=period,duty_factor=duty,pulsed_power_MW=hw['thrust_W']/1e6,continuous_power_MW=hw['thrust_W']/1e6*duty,removed_battery_kg=battery_prop,old_thruster_kg=m['thrusters'],continuous_thruster_kg=new_thr,propulsion_dry_kg=mp_cont,propulsion_payoff_days=mp_cont/rate,collection_plus_continuous_days=(mp_cont+mc)/rate,other_hardware='retained without resizing, including allocated solar, bus, reserve and thermal hardware; 25% margin reapplied'))
assert abs(energy['electrical_closure_difference_MWh'])<.01
assert dive>=0 and abs(result['combined_payoff_days']-r['operating_payoff_days'])<1e-8
Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='mass_allocation'},indent=2))
