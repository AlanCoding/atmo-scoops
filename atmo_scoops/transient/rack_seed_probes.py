import copy,json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import multiprocessing
from atmo_scoops.transient.global_search import coordinates,encode,evaluate
from atmo_scoops.transient.io import write_trajectory

def main():
 b=json.load(open('configs/transient_low_re_search.json'));spec=coordinates(b);tasks=[]
 for i,r in enumerate([.0005,.001,.002,.003]):
  c=copy.deepcopy(b);d=c['design'];d['isp_s']=2800.;d['burn_s']=1800.;d['apogee_km']=3500.
  for k in ['solar_area_m2','battery_MWh','battery_MW','bus_MW','warm_store_kg','warm_radiator_m2']:d[k]*=1.65
  d['stage_radius_m']=[r,.001,.001,.001,.0002];d['stage_pitch_m']=[4*v for v in d['stage_radius_m']]
  tasks.append((i,encode(c,spec).tolist(),b,spec,480))
 out=Path('results/transient/rack_seed_probes');out.mkdir(exist_ok=True);rows=[]
 with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
  for f in as_completed([pool.submit(evaluate,t) for t in tasks]):
   row,r=f.result();rows.append(row)
   if r:write_trajectory(out/f"case_{row['case']}.json",r)
   (out/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n');print(row['case'],row.get('feasible'),row.get('violation'),row.get('error'),flush=True)
if __name__=='__main__':main()
