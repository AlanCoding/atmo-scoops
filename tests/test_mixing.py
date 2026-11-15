from dataclasses import replace
import pytest
import numpy as np
from atmo_scoops.system import simulate
from atmo_scoops.mixing import Mixing,endpoint
from atmo_scoops.thermochemistry import gas
from atmo_scoops.nitrogen import LATENT_J_KG,BOIL_K,sensible_enthalpy


def test_mixer_conserves_enthalpy_with_nist_liquid_reference():
    g=gas();g.TPX=1000,30,'N2:0.78,O2:0.22';Y=g.Y.copy();hin=g.enthalpy_mass
    m=Mixing(ratio=.2);T,Yout,hliq,work=endpoint(g,Y,1000,m)
    g.TPY=T,30,Yout
    assert (1+m.ratio)*g.enthalpy_mass==pytest.approx(hin+m.ratio*(hliq+work),rel=1e-10)
    assert 700<T<1000
    g.TPX=298.15,1e5,'N2:1'
    assert g.enthalpy_mass-hliq==pytest.approx(sensible_enthalpy(BOIL_K,298.15)+LATENT_J_KG)


def test_zero_ratio_recovers_unmixed_cycle_without_injector_hardware():
    a=simulate(n=201);b=simulate(mixing=Mixing(ratio=0,thermal_path='fixed_inlet',injector_fixed_kg=1e6),n=201)
    for key in ('captured_kg','total_dry_kg','net_liquid_equivalent_kg','compressor_kWh'):
        assert a['outputs'][key]==b['outputs'][key]
    assert 'coolant_injection' not in a['outputs']['masses_kg']


@pytest.mark.parametrize('path',['fixed_rack','fixed_inlet'])
def test_coolant_recovery_species_mass_heat_and_no_fictitious_product(path):
    r=simulate(mixing=Mixing(ratio=.1,thermal_path=path),n=401)
    o=r['outputs'];m=o['mixing'];new=o['captured_kg'];injected=.1*new
    assert m['injected_kg']==pytest.approx(injected)
    assert new+injected==pytest.approx(o['retained_kg']+o['vent_kg'],abs=1e-6)
    assert abs(o['thermal_energy_balance_residual_J'])<.01
    assert o['net_liquid_equivalent_kg']==pytest.approx(.999*o['retained_kg']-injected-o['propellant_kg'])
    assert m['recovered_coolant_kg']+m['coolant_replacement_kg']==pytest.approx(injected)
    assert o['total_with_working_fluids_kg']==pytest.approx(o['total_dry_kg']+o['circulating_warm_fluid_kg']+injected)
    assert o['oxygen_available_kg']<.26*new # Coolant adds no oxygen.
    assert o['capture_impulse_Ns']<8100*new # Coolant has no atmospheric arrival momentum.
    assert o['masses_kg']['coolant_storage']==pytest.approx(.15*injected)


def test_cold_gas_constant_cp_cannot_reduce_suction_volume():
    # Independent limiting-case check, before real-fluid/liquid corrections.
    T=1000.;Tcold=80.;r=.2;mix=(T+r*Tcold)/(1+r)
    assert (1+r)*mix/T>1
