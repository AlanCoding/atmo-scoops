"""Controlled LN2-ratio sweep; optimize equal controls for every ratio.

No calibrated temperature-dependent pump map is claimed. Compare conditional
thermal paths and expose the component savings needed to reverse the result.
"""
from dataclasses import replace
import argparse,json,math,time
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from scipy.optimize import minimize_scalar
from ..system import inputs_from_dict,simulate
from ..inlet import EncounterControls
from ..mixing import Mixing

RATIOS=(0.,.01,.03,.1,.25,.5,1.)
ROOT=Path('results/incremental_mixing')


def solve(task,scenario="nominal"):
    path,ratio,thermal_free=task
    inp=inputs_from_dict(json.loads(Path('configs/reference.json').read_text()))
    if scenario=='heavy_compressors':inp['hardware']=replace(inp['hardware'],compressor_kg_per_m3_s=100.)
    if scenario=='efficient_cryo':inp['process']=replace(inp['process'],carnot_fraction=.3)
    inp['mixing']=replace(inp['mixing'],ratio=ratio,thermal_path=path)
    cache={};best=None;trace=[]
    def evaluate(T,S,cut):
        nonlocal best
        key=tuple(round(float(x),7) for x in (T,S,cut))
        if key in cache:return cache[key]
        args={**inp,'design':replace(inp['design'],compressor_inlet_K=T),
              'controls':replace(inp['controls'],suction_scale=S,cutoff_Pa=cut)}
        try:
            r=simulate(**args,n=201)
            feasible=r['constraints']['all_implemented_screens_pass']
            score=r['outputs']['operating_mass_payoff_days'] if feasible else 1e9
            if feasible and (best is None or score<best['outputs']['operating_mass_payoff_days']):best=r
            reason=None if feasible else r['constraints']['margins']
        except (ValueError,RuntimeError,ZeroDivisionError) as e:score=1e9;reason=str(e)
        cache[key]=score
        trace.append(dict(dry_K=T,suction_scale=S,cutoff_Pa=cut,payoff_days=score if score<1e9 else None,failure=reason))
        return score
    temperatures=(650.,800.,1000.,1100.) if thermal_free else (1000.,)
    for T in temperatures:
        for S in (.65,.9,1.2):
            for p in (.04,.1,1.):evaluate(T,S,p)
    if best is not None:
        for _ in range(2):
            keys=['T','S','cut'] if thermal_free else ['S','cut']
            for key in keys:
                point={'T':best['inputs']['design']['compressor_inlet_K'],
                       'S':best['inputs']['controls']['suction_scale'],
                       'cut':best['inputs']['controls']['cutoff_Pa']}
                bounds={'T':(601.,1142.),'S':(.5,1.5),'cut':(math.log(.0315),math.log(10.))}[key]
                def objective(z):
                    q=dict(point);q[key]=math.exp(z) if key=='cut' else z
                    return evaluate(q['T'],q['S'],q['cut'])
                rr=minimize_scalar(objective,bounds=bounds,method='bounded',options={'maxiter':11,'xatol':.001})
                for z in (bounds[0],rr.x,bounds[1]):objective(z)
        args=inputs_from_dict(best['inputs'])
        fine=simulate(**args,n=1601);finer=simulate(**args,n=3201)
        errors={k:abs(fine['outputs'][k]/finer['outputs'][k]-1) for k in ('captured_kg','retained_kg','total_dry_kg','compressor_kWh')}
        if max(errors.values())>3e-4:raise RuntimeError(errors)
        if not finer['constraints']['all_implemented_screens_pass']:raise RuntimeError(finer['constraints'])
        best=finer
    else:errors={}
    return dict(scenario=scenario,thermal_path=path,ratio=ratio,thermal_free=thermal_free,
        search=dict(method='paired coarse grid + two bounded coordinate passes',global_optimum_claim=False,
            dry_stream_K=[601,1142] if thermal_free else [1000,1000],suction_scale=[.5,1.5],cutoff_Pa=[.0315,10.],
            evaluations=len(trace),samples=201,verification_samples=[1601,3201]),
        best=best,verification=errors,trace=trace)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--sensitivity',action='store_true',help='Paired r=0 and r=0.1 thermal/control searches under two capability scenarios')
    parser.add_argument('--quick',action='store_true',help='Only fixed 1000 K rack endpoint; full run additionally optimizes thermal endpoint')
    args=parser.parse_args();ROOT.mkdir(parents=True,exist_ok=True)
    tasks=[(path,r,free) for free in ((False,) if args.quick else (False,True))
           for path in ('fixed_rack','fixed_inlet') for r in RATIOS if not (r==0 and path=='fixed_inlet')]
    jobs=[(t,'nominal') for t in tasks]
    if args.sensitivity:
        jobs=[(('fixed_rack',r,True),scenario) for scenario in ('heavy_compressors','efficient_cryo') for r in (0.,.1)]
    start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=mp.get_context("spawn")) as pool:
        futures={pool.submit(solve,t,scenario):(t,scenario) for t,scenario in jobs}
        for f in as_completed(futures):
            (path,r,free),scenario=futures[f];result=f.result();label=(scenario+'_' if scenario!='nominal' else '')+f'{"free" if free else "fixed"}_{path}_{r:g}'
            (ROOT/f'{label}.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
            best=result['best'];print(label,'payoff',None if best is None else best['outputs']['operating_mass_payoff_days'],
                'elapsed',round(time.monotonic()-start),flush=True)

if __name__=='__main__':main()
