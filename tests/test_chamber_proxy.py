"""Accounting and rejection checks for the explicitly approximate search metric."""
import json,copy
from pathlib import Path
import pytest
from atmo_scoops.chambers.proxy import evaluate
ROOT=Path(__file__).parents[1]
def inputs():
 r=json.loads((ROOT/'results/chamber_optimization/baseline.json').read_text())
 a=json.loads((ROOT/'results/reboost/solid_isp_optimum_1601.json').read_text())
 return r,a,r['ledger']['shaft_work_MJ'][-1]
def test_proxy_charges_propellant_and_receiver_purge():
 r,a,w=inputs();p=evaluate(r,a,w)
 initial=sum(r['gas_mass_kg'][0])
 available=r['ledger']['withdrawn_kg'][-1]+r['gas_mass_kg'][-1][-1]-initial
 assert p['net_product_kg']==pytest.approx(available-p['receiver_vent_reserve_kg']-p['propellant_kg'])
 assert p['compression_adjustment_kg']==0
 assert p['motor_uprating_kg']>0
 assert len(p['compressor_electric_peaks_W'])==4
 assert p['estimated_reset_s']>0
 assert p['proxy_dry_kg']>p['fixed_hardware_kg']
def test_pressure_rejection_and_declared_heat_weight():
 r,a,w=inputs();p=evaluate(r,a,w);q=evaluate(r,a,w,processing_kg_MJ=20)
 assert q['proxy_days']>p['proxy_days']
 r=copy.deepcopy(r);r['pressure_Pa'][10][-1]=120000
 assert not evaluate(r,a,w)['feasible']

def test_deployment_travel_uses_area_not_mechanism_mass():
 r,a,w=inputs();p=evaluate(r,a,w)
 heavier=copy.deepcopy(a);heavier['inputs']['hardware']['sheet_deployment_kg_m2']*=100
 q=evaluate(r,heavier,w)
 assert q['deployment_kg']==pytest.approx(100*p['deployment_kg'])
 assert q['estimated_reset_s']==pytest.approx(p['estimated_reset_s'])
 assert q['proxy_dry_kg']>p['proxy_dry_kg']
