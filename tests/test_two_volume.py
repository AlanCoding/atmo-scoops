import numpy as np
import pytest

from atmo_scoops.two_volume import Reference, calculate, iron_cp


@pytest.fixture(scope='module')
def reference():
    return calculate(n=801)


def test_two_compartment_mass_and_pressure_accounting(reference):
    r=reference
    assert r['captured_kg']==pytest.approx(r['retained_kg']+r['vented_front_kg'],abs=1e-10)
    assert r['retained_kg']==pytest.approx(r['transferred_before_closure_kg']+r['recovered_after_closure_kg'])
    assert r['front_at_closure_kg']>0
    assert r['vented_front_kg']==pytest.approx(.1*r['front_at_closure_kg'])
    assert r['final_front_Pa']==pytest.approx(.1*r['closure_front_Pa'])
    h=r['history'];t=np.array(h['time_s']);front=np.array(h['front_mass_kg']);rear=np.array(h['rear_mass_kg'])
    assert np.all(np.diff(rear)>=-1e-9)
    assert np.allclose(front[t>=0]+rear[t>=0],r['captured_kg'])
    assert r['max_front_over_ram']<r['inputs']['inlet_pressure_fraction']


def test_analytic_pumpdown_and_numerical_resolution(reference):
    fine=calculate(n=3201)
    for key in ('captured_kg','retained_kg','compression_electric_J','hot_store_J'):
        assert reference[key]==pytest.approx(fine[key],rel=2e-5)
    r=reference
    target=r['front_volume_m3']*np.log(10)/r['inputs']['recovery_s']
    assert r['closed_suction_m3_s']==pytest.approx(target)
    assert r['compression_end_W']<r['compression_peak_closed_W']<r['compression_peak_open_W']


def test_heat_accounting_and_metal_capacity(reference):
    assert abs(reference['through_recovery_energy_residual_J'])<.01
    assert reference['metal_mass_kg']*reference['metal_capacity_J_kg']==pytest.approx(reference['hot_store_J'])
    assert 400<iron_cp(500)<800
    assert iron_cp(900)>iron_cp(500)
    with pytest.raises(ValueError):iron_cp(1500)


def test_sunlight_and_energy_budgets(reference):
    r=reference;c=Reference()
    assert 0<r['sunlight_deployed_s']<r['deployed_coast_s']<r['orbit_period_s']
    assert r['coast_start_s']>=c.recovery_s+c.deploy_s
    for b in r['budgets']:
        delivered=b['solar_bus_W']*r['sunlight_deployed_s']*c.battery_charge_efficiency*c.battery_discharge_efficiency
        assert delivered==pytest.approx(b['total_load_energy_J'])
        assert b['battery_mass_kg']==max(b['battery_energy_mass_kg'],b['battery_power_mass_kg'])
    assert r['budgets'][1]['oxygen_balance_kg']>0
    assert r['budgets'][2]['oxygen_balance_kg']<0
    assert not r['budgets'][2]['oxygen_only_sustainable']
    assert r['budgets'][2]['all_captured_gas_mass_sufficient']
    assert r['budgets'][3]['oxygen_balance_kg']<0
