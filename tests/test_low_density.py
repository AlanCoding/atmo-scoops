import CoolProp.CoolProp as CP
import pytest
from atmo_scoops.low_density import gas_update


def fluid():
    f=CP.AbstractState('HEOS','Nitrogen&Oxygen&Argon');f.set_mass_fractions([.755,.232,.013]);f.specify_phase(CP.iphase_gas);return f


def test_previously_failed_state_matches_prescribed_pressure():
    f=fluid();gas_update(f,.00798698,872.028)
    assert f.p()==pytest.approx(.00798698,rel=1e-11)
    assert f.hmass()>0 and f.cpmass()>0


@pytest.mark.parametrize('T',[200.,300.,872.,1500.,2000.])
@pytest.mark.parametrize('p',[.01,.1,1.,10.,99.,100.])
def test_density_update_preserves_heos_properties(p,T):
    f=fluid();ref=fluid();ref.update(CP.PT_INPUTS,p,T);gas_update(f,p,T)
    assert f.p()==pytest.approx(p,rel=1e-11)
    assert f.hmass()==pytest.approx(ref.hmass(),rel=1e-10)
    assert f.smass()==pytest.approx(ref.smass(),rel=1e-10)


@pytest.mark.parametrize('fractions',[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[.8,.2,0.]])
def test_exact_zero_species_use_physical_reduced_backend(fractions):
    f=fluid();f.set_mass_fractions(fractions)
    result=gas_update(f,.016850440236404217,820.8305965530261)
    assert len(result.fluid_names())==sum(z>0 for z in fractions)
    assert result.p()==pytest.approx(.016850440236404217,rel=1e-11)
    assert result.cpmass()>0


def test_transient_pure_nitrogen_compression():
    import numpy as np
    from atmo_scoops.transient.thermo import properties
    from atmo_scoops.compressor import RealAir
    r=RealAir();r.mass_fractions=[1.,0.,0.];r.fluid.set_mass_fractions(r.mass_fractions)
    expected=r.compress(.016850440236404217,820.8305965530261,.05,.75)['shaft_J_kg']
    assert properties().compression(820.8305965530261,.016850440236404217,.05,np.array([1.,0.,0.]),.75)==pytest.approx(expected,rel=2e-7)
