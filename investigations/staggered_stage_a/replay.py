"""Audit actual COBYLA requests from exact cached cycles, without simulating."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,Bounds
from atmo_scoops.transient.plate_optimize import encode
class Missing(RuntimeError):pass
p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();m=json.loads((a.folder/'search.json').read_text());rows=json.loads((a.folder/'evaluations.json').read_text());cache={tuple(r['x']):r for r in rows};used=[];pending=[]
def get(x):
 key=tuple(float(z) for z in x)
 if key not in cache:pending.append(list(key));raise Missing('Next requested point has not completed')
 r=cache[key]
 if r['index'] not in used:used.append(r['index'])
 if r.get('error'):raise Missing('Requested point has an unresolved forward solve')
 return r
s=m['coordinates']
try:
 result=minimize(lambda x:get(x)['diagnostic_payoff_days']/300.,encode(m['base'],s),method='COBYLA',bounds=Bounds(np.zeros(len(s)),np.ones(len(s))),constraints=[dict(type='ineq',fun=lambda x:np.array(get(x)['constraints']))],options=m['options']);status=str(result.message)
except Missing as exc:status=str(exc)
r=dict(status=status,requested_evaluation_indices=used,requested_count=len(used),unused_cached_count=len(rows)-len(used),next_x=pending[0] if pending else None)
(a.folder/'replay_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('requested_evaluation_indices','next_x')}))
