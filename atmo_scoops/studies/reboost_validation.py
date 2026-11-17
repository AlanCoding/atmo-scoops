"""Re-evaluate selected arc cases and independently integrate orbit closure."""
from pathlib import Path
import json
from ..reboost import rebudget,arc_restore,trajectory_check
from ..orbit import Orbit
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'results/reboost'
def main():
 paths={'solid':'results/ammonia_integrated/refined/solid_1601.json','ammonia':'results/ammonia_integrated/refined/cold200_1601.json','warm_ammonia':'results/ammonia_integrated/refined/warm280_1601.json'}
 checks=[]
 for label,path in paths.items():
  source=json.loads((ROOT/path).read_text());raw=json.loads((DEST/f'{label}_raw.json').read_text())
  orbit=Orbit(source['inputs']['design']['perigee_km'],source['inputs']['design']['apogee_km'])
  for suffix in ('closed_orbit','energy_only','closed_orbit_buffered'):
   file=DEST/f'{label}_direct_{suffix}_best.json'
   if not file.exists():continue
   saved=json.loads(file.read_text())
   r=rebudget(source,raw,saved['isp_s'],saved['window_each_s'],energy_only=suffix=='energy_only',buffer_ammonia_rejection='buffered' in suffix)
   r['source_result']=path;file.write_text(json.dumps(r,indent=2)+'\n')
   assert r['screens'];assert abs(r['dry_kg']-sum(r['masses_kg'].values()))<1e-5
   assert r['available_solar_energy_J']>=r['required_solar_energy_J']*(1-1e-10)
   row=dict(name=file.stem,solar_energy_margin_J=r['available_solar_energy_J']-r['required_solar_energy_J'])
   if suffix!='energy_only':
    fine=arc_restore(orbit,r['burn_start_after_perigee_s'],r['window_each_s'],samples=1201)
    row['arc_multiplier_relative_resolution_change']=fine['impulse_multiplier']/r['arc']['impulse_multiplier']-1
    working=source['outputs']['total_with_working_fluids_kg']-source['outputs']['total_dry_kg']
    impulse=source['outputs']['propellant_kg']*source['inputs']['design']['isp_s']*9.80665
    row['trajectory']=trajectory_check(orbit,r['burn_start_after_perigee_s'],r['window_each_s'],impulse/(r['dry_kg']+working))
   checks.append(row);print(row,flush=True)
 (DEST/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
if __name__=='__main__':main()
