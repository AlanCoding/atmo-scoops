from dataclasses import replace
import math
import pytest
from atmo_scoops.pcm import MATERIALS,Cell
from atmo_scoops.racks import Racks,geometry


def spec():return Racks(pcm_material='nitrate_eutectic',wire_radius_m=.01,radius_over_pitch=.1)


def test_phase_plateau_and_reversible_latent_energy():
 p=MATERIALS['nitrate_eutectic'];h=p.enthalpy(p.melt_K)
 for f in (0.,.1,.5,.9,1.):
  assert p.temperature(h+f*p.latent_J_kg)==p.melt_K
  assert p.melt_fraction(h+f*p.latent_J_kg)==pytest.approx(f)
 assert p.temperature(p.enthalpy(610.))==pytest.approx(610.)


def test_casing_ullage_displace_gas_and_all_mass_is_charged():
 s=spec();s.validate(4);g=geometry(100.,7870.,10.,s)
 assert g['shell_and_fin_kg']+g['pcm_kg']==pytest.approx(100.)
 assert g['material_m3']+g['sealed_void_m3']==pytest.approx(g['solid_m3'])
 assert g['gas_m3']+g['solid_m3']==pytest.approx(g['envelope_m3'])
 assert g['liquid_fill_fraction']<1
 thicker=geometry(100.,7870.,10.,replace(s,pcm_wall_m=.001))
 assert thicker['core_mass_fraction']<g['core_mass_fraction']
 with pytest.raises(ValueError,match='expansion'):replace(s,pcm_material='sodium_nitrate',pcm_fill_fraction=.95).validate(4)


def test_internal_conduction_conserves_energy_and_does_not_instantly_melt():
 s=spec();m=Cell(298.,s,7870.);g=geometry(100.,7870.,10.,s)
 total=m.enthalpy(430.)
 # Load energy into the shell first: the core cannot acquire latent heat for free.
 core=m.hcore_cold
 new=m.advance_core(total,core,.1,g)
 assert m.pcm.melt_fraction(new)==0
 assert m.surface_temperature(total,new)>m.pcm.temperature(new)
 hs=m.shell.enthalpy(m.surface_temperature(total,new))
 assert (1-m.f)*hs+m.f*new==pytest.approx(total,rel=1e-9)
 eq=m.advance_core(total,core,1e8,g)
 assert m.surface_temperature(total,eq)==pytest.approx(m.pcm.temperature(eq),abs=.01)


def test_latent_cooldown_recovers_core_not_just_skin():
 s=spec();m=Cell(298.,s,7870.);g=geometry(100.,7870.,10.,s)
 r=m.cooldown_state(m.enthalpy(600.),m.pcm.enthalpy(600.),g,.8,s)
 assert 0<r['cooldown_s']<2e5
 assert r['recovered_melt_fraction']==0
 assert r['coast_end_core_K']<=298.10001
 assert r['coast_end_shell_K']<=298.10001
 assert r['rejected_coast_J']==pytest.approx(100*(m.enthalpy(600.)-m.enthalpy(298.)),rel=.001)
 zero=replace(s,pcm_latent_fraction=0.)
 z=Cell(298.,zero,7870.)
 rz=z.cooldown_state(z.enthalpy(600.),z.pcm.enthalpy(600.),g,.8,zero)
 assert r['cooldown_s']>rz['cooldown_s']


def test_per_stage_material_radius_inputs():
 s=replace(spec(),pcm_materials=('none','tin','nitrate_eutectic','sodium_nitrate'),wire_radii_m=(.001,.005,.01,.02))
 s.validate(4)
 assert s.for_stage(0).pcm_material=='none'
 assert s.for_stage(2).wire_radius_m==.01
 with pytest.raises(ValueError,match='cold start'):Cell(500.,spec(),7870.)
