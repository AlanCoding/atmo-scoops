import json
import pytest
from atmo_scoops.transient.loss_continuation import proposals
from atmo_scoops.transient.hardware import compile_hardware
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.porous import suction_pressure

def test_multiplier_preserves_inputs_and_scales_squared_pressure_drop():
    base=json.load(open('configs/transient_staged_bypass.json'))
    cases=proposals(base,[0.,.01,.1,1.])
    assert base['capabilities']['rack_loss_multiplier']==0
    g=compile_hardware(*read_config(cases['loss_1']))['geometry'][0]
    p=1000.
    full=suction_pressure(1.,p,500.,287.,g,1.)[0]
    for c in cases.values():
        alpha=c['capabilities']['rack_loss_multiplier']
        ps,_=suction_pressure(1.,p,500.,287.,g,alpha)
        assert p*p-ps*ps==pytest.approx(alpha*(p*p-full*full),abs=1e-9)
        assert c['design']['rod_radius_m']==base['design']['rod_radius_m']
        assert c['design']['rod_pitch_m']==base['design']['rod_pitch_m']
        assert c['design']['rack_depth_m']==base['design']['rack_depth_m']
    with pytest.raises(ValueError):proposals(base,[-.1])
