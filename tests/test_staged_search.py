import copy,json
import pytest
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.porous import suction_pressure
from atmo_scoops.racks import Racks,conductance

@pytest.mark.parametrize('seconds',[-1.,.5,float('nan')])
def test_invalid_numerical_restart_interval_rejected(seconds):
    c=json.load(open('configs/transient_active.json'))
    c['design']['integration_segment_s']=seconds
    with pytest.raises(ValueError):
        compile_hardware(*read_config(c))

def test_pressure_stage_preserves_fixed_geometry_heat_and_hardware():
    a=json.load(open('configs/transient_gas_reduced_plant.json'))
    b=copy.deepcopy(a);b['design']['rack_pressure_model']='inline_laminar';b['capabilities']['rack_loss_multiplier']=1.
    ha=compile_hardware(*read_config(a));hb=compile_hardware(*read_config(b))
    assert ha['dry_kg']==pytest.approx(hb['dry_kg'])
    for ga,gb in zip(ha['geometry'],hb['geometry']):
        for k in ('gas_m3','mass_kg','wetted_m2','wire_radius_m','pitch_m'):
            assert ga[k]==pytest.approx(gb[k])
        ua,_=conductance(500,500,10,ga['frontal_m2'],ga,Racks())
        ub,_=conductance(500,500,10,gb['frontal_m2'],gb,Racks())
        assert ua==pytest.approx(ub)
        assert suction_pressure(1.,500.,500.,287.,gb)[0]<500.
