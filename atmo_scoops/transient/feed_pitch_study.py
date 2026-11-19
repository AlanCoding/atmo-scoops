"""Declared feed/pitch comparison grid; hardware fixed before each forward solve."""
import copy,json,argparse,multiprocessing
from dataclasses import asdict
from .inputs import read_config
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from .search import run_case,summary
from .io import read_result

def proposals():
    base=json.loads(Path('configs/transient_skin_reference.json').read_text())
    cases={}
    x=copy.deepcopy(base);x['design'].update(rack_flow_layout='outlet_planes',stage_pitch_m=[.01]*5)
    cases['layout_only']=x
    for label,pitches,depths in [
        ('wide',[.02]*5,[5.42,.4,.18,.2,.32]),
    ]:
        x=copy.deepcopy(base);x['design'].update(rack_flow_layout='outlet_planes',stage_pitch_m=pitches,rack_depth_m=depths,propellant_storage='gas',reserve_kg=0.)
        x['capabilities']['rack_loss_multiplier']=1.;cases[label]=x
    x=json.loads(Path('configs/transient_gas_reference.json').read_text())
    x['design'].update(rack_flow_layout='outlet_planes',stage_pitch_m=[.01]*5)
    x['capabilities']['rack_loss_multiplier']=1.;cases['joint_dense']=x
    x=json.loads(Path('configs/transient_gas_reference.json').read_text())
    x['design'].update(plant_electric_MW=20.,plant_flow_kg_s=2.)
    cases['gas_smaller_plant']=x
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('results/transient/feed_pitch'));p.add_argument('--workers',type=int,default=2);p.add_argument('--cases',nargs='+');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    cases=proposals()
    if a.cases:cases={name:cases[name] for name in a.cases}
    (a.output/'proposals.json').write_text(json.dumps(proposals(),indent=2)+'\n')
    old=json.loads((a.output/'comparison.json').read_text()) if (a.output/'comparison.json').exists() else []
    rows={row['case']:row for row in old};pending={}
    for name,x in cases.items():
        path=a.output/f'cycle_{name}.json'
        if path.exists() or path.with_suffix('.json.gz').exists():
            saved=read_result(path);d,c=read_config(x)
            expected=dict(design=asdict(d),capabilities=asdict(c))
            if json.dumps(saved['inputs'],sort_keys=True)!=json.dumps(expected,sort_keys=True):
                raise ValueError(f'Saved inputs differ for {name}; use a new output folder')
            rows[name]=dict(case=name,**summary(saved))
        else:pending[name]=x
    (a.output/'comparison.json').write_text(json.dumps(list(rows.values()),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('fork')) as pool:
        fs={pool.submit(run_case,(name,x,str(a.output))):name for name,x in pending.items()}
        for f in as_completed(fs):
            row=f.result();rows[row['case']]=row;(a.output/'comparison.json').write_text(json.dumps(list(rows.values()),indent=2)+'\n');print({k:row.get(k) for k in ['case','feasible','operating_payoff_days','error']},flush=True)
if __name__=='__main__':main()
