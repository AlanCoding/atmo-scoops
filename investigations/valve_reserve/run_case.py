import argparse,json,time
from pathlib import Path
from atmo_scoops.transient.cycle import simulate
from atmo_scoops.transient.io import write_trajectory
from atmo_scoops.transient.search import summary
p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('output');a=p.parse_args()
t=time.monotonic();r=simulate(json.loads(Path(a.config).read_text()),samples=301)
write_trajectory(Path(a.output),r)
s=summary(r);s['seconds']=time.monotonic()-t
Path(a.output).with_suffix('.summary.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps(s,indent=2))
