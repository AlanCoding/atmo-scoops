import copy
import json
from pathlib import Path
import pytest
from investigations.reduced_optimization.run import config_at
from atmo_scoops.transient.reduced_coordinates import rack_allocation
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config

@pytest.fixture
def base():
 return json.loads(Path('results/transient/pressure_continuation/p105/selected_config.json').read_text())

def test_rack_coordinate_fixes_distribution_and_other_geometry(base):
 original=copy.deepcopy(base);c=config_at(base,[.95,0,0,0]);a=rack_allocation(base);b=rack_allocation(c)
 assert base==original
 assert b['total_kg']==pytest.approx(.95*a['total_kg'])
 assert b['fractions']==pytest.approx(a['fractions'])
 for key in ['plate_gap_m','plate_thickness_m','materials','rack_initial_K','receiver_fill_Pa','solar_area_m2']:
  assert c['design'][key]==base['design'][key]

def test_pressure_coordinate_charges_receiver_and_reserve_structure(base):
 low=config_at(base,[1,0,0,0,1]);high=config_at(base,[1,0,0,0,1.1])
 assert high['design']['receiver_fill_Pa']==pytest.approx(low['design']['receiver_fill_Pa']*1.1)
 assert high['design']['rated_pressure_Pa'][:-1]==low['design']['rated_pressure_Pa'][:-1]
 assert high['design']['rated_pressure_Pa'][-1]==pytest.approx(low['design']['rated_pressure_Pa'][-1]*1.1)
 hl=compile_hardware(*read_config(low));hh=compile_hardware(*read_config(high))
 assert hh['masses_kg']['pressure_vessels']>hl['masses_kg']['pressure_vessels']
 assert hh['gas_system']['shell_and_support_kg']>hl['gas_system']['shell_and_support_kg']
 assert hh['masses_kg']['racks']==hl['masses_kg']['racks']

def test_slsqp_uses_contiguous_objective_gradient():
 # A transposed finite-difference table has strided rows. The installed SLSQP
 # bridge reads such a gradient incorrectly; exercise the actual optimizer.
 import numpy as np
 from scipy.optimize import minimize
 from investigations.reduced_optimization.run import solver_jacobian
 j=solver_jacobian([[1., 2., 3.], [-2., 4., 5.]])
 assert j[0].flags.c_contiguous
 assert np.array_equal(j[0], [1., -2.])
 result=minimize(lambda x:x[0]-2*x[1], [0.,0.], jac=lambda x:j[0],
  method='SLSQP', bounds=[(-1.,1.),(-1.,1.)], options={'ftol':1e-10})
 assert result.success
 assert result.x==pytest.approx([-1.,1.])

def test_explicit_bounds_keep_warm_start_and_only_expand_requested_coordinates():
 from investigations.reduced_optimization.run import checked_bounds
 b=json.loads(Path('investigations/reduced_optimization/widened_bounds.json').read_text())
 old=json.loads(Path('results/transient/reduced_optimization/pressure/manifest.json').read_text())['bounds']
 x=json.loads(Path('results/transient/reduced_optimization/pressure/selected_summary.json').read_text())['x']
 assert checked_bounds(b,x)==b
 for i in (1,3,4):assert b[i]==old[i]
 for i in (0,2):assert b[i][0]<old[i][0] and b[i][1]>old[i][1]

@pytest.mark.parametrize('bounds,start', [([[1,0]],[.5]), ([[0,2]],[1]), ([[.5,2]],[3]), ([[.5,float('inf')]],[1])])
def test_invalid_search_bounds_fail_before_simulating(bounds,start):
 from investigations.reduced_optimization.run import checked_bounds
 with pytest.raises(ValueError):checked_bounds(bounds,start)

def test_propulsion_minimum_is_total_gas_not_smallest_species_or_liquid_surplus():
 from investigations.reduced_optimization.replay import propellant_inventory_metrics
 r=dict(time_s=[-100.,0.,100.],gas_reserve_species_kg=[[80,20,1],[60,30,2],[70,10,3]],margins={'reserve_kg':4})
 assert propellant_inventory_metrics(r)==dict(minimum_reserve_total_kg=83,minimum_reserve_time_s=100.)
