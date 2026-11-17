import json
from pathlib import Path
from dataclasses import replace
import pytest
from atmo_scoops.orbit import Orbit
from atmo_scoops.reboost import arc_restore,eclipse_start,rebudget,trajectory_check
from atmo_scoops.system import inputs_from_dict,simulate
ROOT=Path(__file__).parents[1]

def test_symmetric_arcs_restore_energy_and_angular_momentum():
 o=Orbit(85,2000)
 r=arc_restore(o,600,600)
 assert abs(r['closure_residual'])<1e-10
 assert r['impulse_multiplier']>1
 near=arc_restore(o,1,.1)
 assert near['impulse_multiplier']==pytest.approx(1,rel=1e-5)
 lower=arc_restore(o,600,600,energy_only=True)
 assert lower['impulse_multiplier']<r['impulse_multiplier']
 assert abs(lower['closure_residual'])>.01
 fine=arc_restore(o,600,600,samples=1201)
 assert fine['impulse_multiplier']==pytest.approx(r['impulse_multiplier'],rel=1e-5)
 assert 1000<eclipse_start(o)<o.period/2


def test_nitrogen_propellant_preserves_product_mass_accounting():
 a=inputs_from_dict(json.loads((ROOT/'results/ammonia_integrated/refined/solid_1601.json').read_text())['inputs'])
 a['design']=replace(a['design'],isp_s=1800.)
 a['compressor']=replace(a['compressor'],thermodynamic_samples=101)
 a['scenario']=replace(a['scenario'],allow_nitrogen_propellant=True)
 r=simulate(**a,n=101);o=r['outputs']
 assert 'oxygen_kg' not in r['constraints']['margins']
 assert o['nitrogen_used_as_propellant_kg']>0
 assert o['nitrogen_used_as_propellant_kg']+o['oxygen_used_as_propellant_kg']==pytest.approx(o['propellant_kg'])
 assert r['constraints']['margins']['nitrogen_propellant_margin_kg']>0
 assert o['net_liquid_equivalent_kg']+o['propellant_kg']<=o['retained_kg']


def test_rebudget_counts_peak_array_power_process_pause_and_buffers():
 source=json.loads((ROOT/'results/ammonia_integrated/refined/cold200_1601.json').read_text())
 raw=json.loads((ROOT/'results/reboost/ammonia_raw.json').read_text())
 r=rebudget(source,raw,3000.,800.)
 assert r['dry_kg']==pytest.approx(sum(r['masses_kg'].values()))
 assert r['solar_W']>=r['thrust_peak_W']
 assert r['available_solar_energy_J']>=r['required_solar_energy_J']*(1-1e-10)
 assert r['processing_s']==pytest.approx(r['coast_s']-1600.)
 assert r['processing_sun_s']==pytest.approx(r['sun_s']-1600.)
 assert r['propellant_kg']*3000*9.80665==pytest.approx(source['outputs']['propellant_kg']*4000*9.80665*r['arc']['impulse_multiplier'])
 assert r['warm_buffer_required_J']>=r['warm_buffer_schedule_J']
 buffered=rebudget(source,raw,3000.,800.,buffer_ammonia_rejection=True)
 assert buffered['masses_kg']['ammonia_rejection_buffer']>0
 assert buffered['ammonia_radiator_m2']<r['ammonia_radiator_m2']
 with pytest.raises(ValueError):rebudget(source,raw,3000.,2000.)


def test_independent_finite_burn_orbit_integration():
 r=trajectory_check(Orbit(85,2000),600.,900.,drag_dv=3.)
 assert abs(r['energy_residual_fraction_of_drag'])<1e-4
 assert abs(r['angular_residual_fraction_of_drag'])<1e-4
 assert abs(r['perigee_error_m'])<1.
 assert abs(r['apogee_error_m'])<1.
