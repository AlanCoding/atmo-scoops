"""Material energy/geometry and independent mixed-rack conservation checks."""
from dataclasses import replace
import numpy as np
import pytest
from atmo_scoops.chambers import Chamber,Pump,Schedule,Boundary,simulate
from atmo_scoops.chambers.materials import material

@pytest.mark.parametrize('name,delta',[('iron',280399),('sic',503678),('aluminum',524531)])
def test_integrated_heat_capacity_reference(name,delta):
 m=material(name)
 assert m.energy(813)-m.energy(298)==pytest.approx(delta,rel=2e-4)
 assert m.temperature(m.energy(650))==pytest.approx(650)

def test_equal_geometry_displaces_equal_gas_but_not_equal_mass():
 a=Chamber('a',1,1,.2);b=replace(a,material='aluminum')
 assert a.geometry()['gas_m3']==b.geometry()['gas_m3']
 assert b.geometry()['mass_kg']/a.geometry()['mass_kg']==pytest.approx(2700/7870)
 with pytest.raises(ValueError):replace(a,material='unknown').geometry()

def test_mixed_racks_conserve_energy_and_reach_caloric_equilibrium():
 chambers=[Chamber(name,1,1,.02,material=name,initial_gas_K=700,initial_pressure_Pa=1e5) for name in ('fecral','sic','aluminum')]
 boundary=Boundary([0,100],[0,0],[0,0],[0,0],0)
 r=simulate(chambers,[Pump(.01,2e5,stop_s=0)]*2,boundary,Schedule(start_s=0,end_s=100,withdrawal_kg_s=0,max_step_s=1),101)
 assert r['checks']['max_energy_residual_MJ']<1e-7
 assert r['checks']['max_mass_residual_kg']<1e-8
 assert len(set(np.round(r['metal_temperature_K'][-1],1)))==3
 assert all(x>298 for x in r['metal_temperature_K'][-1])

def test_reset_requires_net_radiation_and_material_capacity():
 g=Chamber('a',1,1,.2,material='aluminum').geometry();m=material('aluminum')
 assert 0<m.cooldown(500,298,g,.8)<1e5
 assert m.cooldown(500,298,g,.1)==1e30
 assert m.cooldown(600,298,g,.8)==1e30
 assert m.cooldown(500,298,g,.5)>m.cooldown(500,298,g,.8)
