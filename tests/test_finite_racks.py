from dataclasses import replace
import math
import numpy as np
import pytest
from atmo_scoops.racks import Racks,geometry,conductance,Metal
from atmo_scoops.compressor import Compressor,RealAir,evaluate_train_history
from atmo_scoops.system import Design,simulate
from atmo_scoops.packaging import Packaging


def test_lattice_volume_area_and_thinning_are_distinct():
    s=Racks();g=geometry(787.,7870.,10.,s)
    assert g['solid_m3']==pytest.approx(.1)
    assert g['envelope_m3']==pytest.approx(.1/(math.pi*.05**2))
    assert g['gas_m3']+g['solid_m3']==pytest.approx(g['envelope_m3'])
    thin=geometry(787.,7870.,10.,replace(s,wire_radius_m=s.wire_radius_m/2))
    assert thin['envelope_m3']==g['envelope_m3']
    assert thin['wetted_m2']==2*g['wetted_m2']
    assert thin['deployed_physical_m2']==2*g['deployed_physical_m2']
    dense=geometry(787.,7870.,10.,replace(s,radius_over_pitch=.1))
    assert dense['envelope_m3']==pytest.approx(g['envelope_m3']/4)


def test_rarefaction_reduces_conductance_and_reports_scale():
    s=Racks();g=geometry(787.,7870.,10.,s)
    high,d=conductance(1000.,600.,1.,10.,g,s)
    low,e=conductance(.001,600.,1e-6,10.,g,s)
    assert low<high
    assert e['Kn']>d['Kn']*1e5
    zero,_=conductance(0.,600.,0.,10.,g,s)
    assert zero<1e-20


def train(factor=1.,mass=100.):
    s=Racks(heat_transfer_factor=factor,mass_factors=(1.,1.,1.,1.))
    geoms=[geometry(mass,7870.,2.,s) for _ in range(4)]
    context=dict(spec=s,geometries=geoms,metal=Metal(500.))
    times=np.linspace(0.,10.,101)
    return evaluate_train_history(RealAir(),Compressor(),np.full(101,1000.),600.,np.full(101,10000.),
        np.ones(101),times,4,600.,.95,rack_context=context)


def test_finite_racks_recover_adiabatic_limit_and_capacity_trade():
    dry=train(1e-20)
    cold=train(mass=1000.)
    small=train(mass=10.)
    assert sum(abs(x) for x in dry['rack_heat_J'])<1e-5
    assert cold['electricity_J']<dry['electricity_J']
    assert cold['electricity_J']<small['electricity_J']
    assert cold['rack_max_metal_K'][1]<small['rack_max_metal_K'][1]
    assert cold['stage_temperature_history'][-1]['inlets_K'][1]>500.


def test_system_volume_conservation_and_deployment_feedback():
    d=replace(Design(),front_depth_m=1.)
    r=simulate(d,n=201);o=r['outputs'];g=o['racks'][0]
    actual=math.pi*d.front_diameter_m**2/4*o['front_depth_m']
    assert actual>=g['envelope_m3']*(1-1e-12)
    assert o['front_gas_volume_m3']==pytest.approx(actual-g['solid_m3'])
    assert o['captured_kg']+1e-9==pytest.approx(o['retained_kg']+o['vent_kg'],abs=1e-5)
    assert abs(o['thermal_energy_balance_residual_J'])<1e-7*o['hot_absorbed_GJ']*1e9
    assert o['interstage_vent_kg']>0
    assert sum(o['masses_kg'].values())==pytest.approx(o['total_dry_kg'])
    slow=simulate(d,packaging=Packaging(deployment_speed_m_s=2.),n=201)['outputs']
    assert slow['cycle']['deploy_s']>o['cycle']['deploy_s']
    assert slow['cycle']['deployed_s']<o['cycle']['deployed_s']
    assert slow['solar_MW']>o['solar_MW']
    # No arbitrary bay length survives in the active calculation.
    arbitrary=simulate(replace(d,machinery_depth_m=10000.),n=201)['outputs']
    assert arbitrary['overall_length_allowance_m']==pytest.approx(o['overall_length_allowance_m'])
    assert arbitrary['total_dry_kg']==pytest.approx(o['total_dry_kg'])
