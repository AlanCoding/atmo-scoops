import subprocess,sys,json
from pathlib import Path
py=sys.executable;folder='results/transient/staggered/thermal_equivalence/optimization'
for batch in range(40):
 subprocess.run([py,'investigations/staggered_stage_a/replay.py',folder],check=True)
 r=json.loads((Path(folder)/'replay_audit.json').read_text())
 if not r['next_x']:break
 result=subprocess.run([py,'investigations/staggered_stage_a/prefill_probes.py',folder,'--workers','4','--from-replay','--count','4'])
 if result.returncode:break
subprocess.run([py,'-m','atmo_scoops.transient.plate_optimize','--config','configs/transient_staggered_thermal_seed.json','--output',folder,'--maxiter','300','--tol','.01','--rhobeg','.03','--seconds','300'],check=True)
