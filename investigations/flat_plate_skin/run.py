"""No cycle optimization: matched-geometry orbital shear and compiler comparison."""
from pathlib import Path
import copy,json,math
import numpy as np
from atmo_scoops.atmosphere import make_profile
from atmo_scoops.orbit import Orbit
from atmo_scoops.encounter import orbit_state
from atmo_scoops.transient.drag import flat_plate_laminar
from atmo_scoops.transient.inputs import read_config
from atmo_scoops.transient.hardware import compile_hardware
BASE=Path('results/transient/reduced_optimization/pressure_wide_closed/selected_config.json')
OUT=Path('results/transient/flat_plate_skin');OUT.mkdir(exist_ok=True,parents=True)
cfg=json.loads(BASE.read_text());d=cfg['design'];atm=make_profile();D=d['bore_m']+2*d['clearance_m'];L=D*d['length_diameter'];A=math.pi*d['bore_m']**2/4
rows=[]
for altitude in [50,60,70,80,d['perigee_km'],90,100,120,150]:
 for wall in [300,600,1000]:
  # Same ±1200 s support as the compiler's pre-pass start; no CFD or re-sizing.
  t=np.linspace(-1200,1200,4801);s=orbit_state(Orbit(altitude,d['apogee_km']),t,atm)
  z=flat_plate_laminar(t,s['density_kg_m3'],s['speed_m_s'],s['temperature_K'],D,L,wall)
  J=float(np.trapezoid(A*s['density_kg_m3']*s['speed_m_s']**2,t))
  z.update(perigee_km=altitude,skin_to_incident_impulse=z['impulse_Ns']/J,
    incident_impulse_Ns=J,incident_mass_kg=float(np.trapezoid(A*s['density_kg_m3']*s['speed_m_s'],t)))
  rows.append(z)
comparison=[]
for mode in ['constant','flat_plate_laminar']:
 x=copy.deepcopy(cfg);x['capabilities'].update(skin_model=mode,skin_wall_K=600.)
 h=compile_hardware(*read_config(x));comparison.append(dict(model=mode,skin=h['skin_friction'],
   total_drag_impulse_Ns=h['total_drag_impulse_Ns'],thrust_W=h['thrust_W'],
   propellant_reference_kg=h['propellant_reference_kg'],masses_kg=h['masses_kg']))
 if mode=='flat_plate_laminar':(OUT/'candidate_config.json').write_text(json.dumps(x,indent=2)+'\n')
(OUT/'screen.json').write_text(json.dumps(dict(source=str(BASE),diameter_m=D,length_m=L,rows=rows,compiled_comparison=comparison),indent=2)+'\n')
for r in rows:
 if r['wall_K']==600:print(r['perigee_km'],r['peak_dynamic_state'],100*r['skin_to_incident_impulse'])
print('compiled',[(r['model'],r['propellant_reference_kg'],r['thrust_W']/1e6) for r in comparison])
