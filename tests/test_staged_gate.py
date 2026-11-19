import copy
from atmo_scoops.transient.staged_search import numerical_gate

def row():
    return dict(feasible=True,audits=dict(species_kg=1e-8,energy_MJ=1e-6,min_gas_kg=-1e-8),net_liquid_kg=3000.,admitted_kg=7000.,lost_kg=500.,propellant_kg=3500.)

def test_stage_release_requires_resolution_and_inventory_checks():
    a=row();b=row();assert numerical_gate([a,b])['passed']
    b['net_liquid_kg']*=1.01;assert not numerical_gate([a,b])['passed']
    b=row();b['audits']['min_gas_kg']=-.001;assert not numerical_gate([a,b])['passed']
    assert not numerical_gate([a,dict(error='failed')])['passed']

def test_physical_infeasibility_can_be_numerically_repeatable_but_not_promoted():
    a=row();b=row();a['feasible']=False;b['feasible']=False
    assert numerical_gate([a,b],require_feasible=False)['passed']
    assert not numerical_gate([a,b])['passed']

def test_resolution_checks_always_tighten_the_supplied_settings():
    from atmo_scoops.transient.staged_search import resolution
    c=dict(design=dict(max_step_s=5.,rtol=1e-5,atol=1e-8))
    tighter=resolution(c)['design']
    assert tighter['max_step_s']<c['design']['max_step_s']
    assert tighter['rtol']<c['design']['rtol']
    assert tighter['atol']<c['design']['atol']
