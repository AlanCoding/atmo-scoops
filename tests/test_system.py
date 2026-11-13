from dataclasses import replace
import json
import subprocess
import sys

import pytest

from atmo_scoops.system import Design,Hardware,Performance,Scenario,defaults,inputs_from_dict,simulate
from atmo_scoops.process import ProcessTargets


@pytest.fixture(scope='module')
def baseline():
    return simulate(n=401)


def test_complete_config_round_trip_and_typo_rejection():
    config=defaults()
    parsed=inputs_from_dict(json.loads(json.dumps(config)))
    assert parsed['design']==Design()
    with pytest.raises(ValueError,match='Unknown design'):
        inputs_from_dict({'design':{'front_dept_m':100}})
    with pytest.raises(ValueError,match='Unknown configuration'):
        inputs_from_dict({'dry_mass':200000})


def test_precooling_trade_preserves_intake_and_counts_deployment(baseline):
    cooler=simulate(replace(Design(),compressor_inlet_K=750),n=401)
    a=baseline['outputs'];b=cooler['outputs']
    assert b['captured_kg']==pytest.approx(a['captured_kg'])
    assert b['compressor_mass_kg']<a['compressor_mass_kg']
    assert b['masses_kg']['hot_metal']>a['masses_kg']['hot_metal']
    assert b['masses_kg']['hot_sheet_deployment']>a['masses_kg']['hot_sheet_deployment']
    assert b['total_dry_kg']<a['total_dry_kg']
    assert b['metal_hot_K']==650
    assert abs(b['thermal_energy_balance_residual_J'])<.01
    # Same material, density and gauge: area ratio must equal metal mass ratio.
    assert b['metal_panel_m2']/a['metal_panel_m2']==pytest.approx(b['masses_kg']['hot_metal']/a['masses_kg']['hot_metal'])


@pytest.mark.parametrize('change',[{'compressor_inlet_K':600},{'metal_cold_K':250},
    {'front_depth_m':-1},{'front_depth_m':float('nan')},{'rear_depth_m':5},
    {'opening_ram_fraction':1},{'pump_suction_m3_s':0}])
def test_invalid_domains_rejected(change):
    with pytest.raises(ValueError):simulate(replace(Design(),**change),n=101)


def test_explicit_pump_and_capability_constraints_are_not_capture_claims(baseline):
    weak=simulate(replace(Design(),pump_suction_m3_s=1000),n=401)
    assert weak['constraints']['margins']['front_pressure_ratio']<0
    assert not weak['constraints']['all_implemented_screens_pass']
    assert weak['outputs']['captured_kg']==pytest.approx(baseline['outputs']['captured_kg'])
    narrow=simulate(hardware=replace(Hardware(),compressor_open_fraction=.1),n=401)
    assert narrow['constraints']['margins']['compressor_access_m2']<0
    drag=simulate(scenario=Scenario(total_impulse_over_capture=2),n=401)
    assert drag['outputs']['propellant_kg']==pytest.approx(2*baseline['outputs']['propellant_kg'])
    assert drag['constraints']['margins']['oxygen_kg']<0


def test_dimensions_and_refrigerator_parameters_reach_system(baseline):
    wider=simulate(replace(Design(),rear_diameter_m=20),n=401)
    assert wider['outputs']['rear_pressure_Pa']<baseline['outputs']['rear_pressure_Pa']
    assert wider['resolved_cycle_inputs']['outside_diameter_m']==pytest.approx(21.7)
    efficient=simulate(process=replace(ProcessTargets(),carnot_fraction=.3),n=401)
    assert efficient['outputs']['cryoplant_electric_kW']==pytest.approx(baseline['outputs']['cryoplant_electric_kW']/2)
    assert efficient['outputs']['total_dry_kg']<baseline['outputs']['total_dry_kg']


def test_cli_outputs_resolved_inputs_and_constraints(tmp_path):
    config=tmp_path/'design.json';out=tmp_path/'result.json'
    config.write_text(json.dumps({'design':{'front_depth_m':100,'compressor_inlet_K':750}}))
    p=subprocess.run([sys.executable,'-m','atmo_scoops','--config',str(config),'--rear-depth','50',
        '--samples','101','--output',str(out)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    result=json.loads(out.read_text())
    assert result['inputs']['design']['front_depth_m']==100
    assert result['inputs']['design']['rear_depth_m']==50
    assert result['outputs']['metal_hot_K']==650
    assert result['constraints']['unresolved']
