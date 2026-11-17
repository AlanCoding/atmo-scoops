import numpy as np
import pytest
from dataclasses import replace
from atmo_scoops.chambers import Chamber,Pump,Schedule,Boundary,simulate

EMPTY=Boundary([0,1000],[0,0],[0,0],[0,0],0)
def settings(**kw):return replace(Schedule(start_s=0,end_s=100,withdrawal_kg_s=0,max_step_s=1),**kw)
def audit(r):
 assert r['checks']['max_mass_residual_kg']<1e-5
 assert r['checks']['max_energy_residual_MJ']<1e-5
 assert r['checks']['min_gas_mass_kg']>0
 assert not r['checks']['caloric_table_boundary_reached']

def test_sealed_rack_equilibration_conserves_mass_and_energy():
 c=Chamber('sealed',1,1,.1,initial_gas_K=700,initial_pressure_Pa=1e5)
 r=simulate([c],[],EMPTY,settings(),101);audit(r)
 T=np.array(r['gas_temperature_K'])[:,0];m=np.array(r['metal_temperature_K'])[:,0]
 assert T[-1]<T[0] and m[-1]>m[0] and T[-1]>=m[-1]-1e-4
 assert r['pressure_Pa'][-1][0]/r['pressure_Pa'][0][0]==pytest.approx(T[-1]/T[0],rel=1e-7)
 assert r['density_kg_m3'][-1][0]==pytest.approx(r['density_kg_m3'][0][0])

def test_withdrawal_removes_enthalpy_and_cools_empty_tank():
 c=Chamber('tank',1,1,initial_gas_K=600,initial_pressure_Pa=1e5)
 r=simulate([c],[],EMPTY,settings(withdrawal_start_s=0,withdrawal_kg_s=.002),101);audit(r)
 assert r['gas_temperature_K'][-1][0]<600
 assert r['ledger']['withdrawn_kg'][-1]>0
 assert r['ledger']['withdrawn_enthalpy_MJ'][-1]>0

def test_compressor_work_is_added_to_total_energy():
 a=Chamber('a',1,1,initial_pressure_Pa=1e5,initial_gas_K=400)
 b=replace(a,name='b',initial_pressure_Pa=1e4)
 r=simulate([a,b],[Pump(.02,2e5)],EMPTY,settings(end_s=20),101);audit(r)
 assert r['ledger']['shaft_work_MJ'][-1]>0
 assert sum(r['gas_mass_kg'][-1])==pytest.approx(sum(r['gas_mass_kg'][0]))
 assert r['ledger']['total_internal_MJ'][-1]-r['ledger']['total_internal_MJ'][0]==pytest.approx(r['ledger']['shaft_work_MJ'][-1],abs=1e-7)

def test_radiation_uses_explicit_area_and_geometry_rejects_overfill():
 c=Chamber('radiating',1,1,.1,initial_gas_K=600,initial_metal_K=600,initial_pressure_Pa=1e5,external_emitting_m2=2)
 r=simulate([c],[],EMPTY,settings(radiation_start_s=0),101);audit(r)
 assert r['ledger']['radiated_MJ'][-1]>0
 assert r['metal_temperature_K'][-1][0]<600
 with pytest.raises(ValueError):replace(c,rack_depth_m=2).geometry()
