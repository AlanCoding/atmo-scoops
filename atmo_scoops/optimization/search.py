"""Bounded conditional design search using the public spacecraft API.

Objective is OPERATING-ORBIT mass payoff, never delivered circular-apogee payoff.
Hardware capabilities stay fixed. All bounds and optimization traces are saved.
"""
import argparse
from dataclasses import asdict,replace
import json
import math
import multiprocessing as mp
from pathlib import Path
import time

import numpy as np
from scipy.optimize import differential_evolution,minimize

from ..system import Design,simulate,inputs_from_dict

# Engineering search bounds, not validated feasibility limits. Log coordinates
# improve scale coverage for positive quantities spanning orders of magnitude.
BOUNDS={
    'front_depth_m':(25.,450.,True),
    'rear_depth_m':(10.,100.,True),
    'mouth_diameter_m':(10.,30.,False),
    'front_diameter_m':(10.,36.,False),
    'rear_diameter_m':(6.,36.,False),
    'perigee_km':(90.,120.,False),
    'apogee_km':(500.,10000.,True),
    'opening_ram_fraction':(.1,.8,False),
    'compressor_inlet_K':(420.,1200.,False),
    'metal_cold_K':(298.,600.,False),
    'gas_metal_approach_K':(50.,200.,False),
    'foil_thickness_m':(.0001,.002,True),
    'inlet_pressure_fraction':(.4,.8,False),
    'intermediate_Pa':(100.,10000.,True),
    'recovery_s':(300.,600.,False),
    'front_residual_fraction':(.01,.3,True),
    'warm_radiator_K':(280.,360.,False),
    'thrust_burst_s':(60.,300.,False),
    'isp_s':(3200.,6000.,False),
}


def payoff_days(result):
    o=result['outputs']
    return o['total_dry_kg']/o['net_liquid_equivalent_kg_day']


class Problem:
    def __init__(self,inputs,bounds,keys,n=101,oxygen_reserve_fraction=0.):
        self.inputs=inputs;self.bounds=bounds;self.keys=keys;self.n=n
        self.oxygen_reserve_fraction=oxygen_reserve_fraction

    def decode(self,x):
        values={}
        for z,key in zip(x,self.keys):
            lo,hi,log=self.bounds[key]
            values[key]=math.exp(math.log(lo)+z*math.log(hi/lo)) if log else lo+z*(hi-lo)
        return replace(self.inputs['design'],**values)

    def encode(self,d):
        out=[]
        for key in self.keys:
            lo,hi,log=self.bounds[key];v=getattr(d,key)
            z=math.log(v/lo)/math.log(hi/lo) if log else (v-lo)/(hi-lo)
            out.append(float(np.clip(z,0,1)))
        return np.array(out)

    def evaluate(self,x,n=None):
        d=self.decode(x)
        return simulate(**{**self.inputs,'design':d},n=n or self.n)

    def violations(self,result):
        o=result['outputs'];d=result['inputs']['design'];m=result['constraints']['margins']
        # A subset of plausible layouts: no bore contraction immediately behind
        # the collecting mouth; total length limited to the user's ~500 m target.
        values=[-m['front_pressure_ratio']/d['inlet_pressure_fraction'],
            -m['compressor_access_m2']/o['available_compressor_open_area_m2'],
            self.oxygen_reserve_fraction-m['oxygen_kg']/max(o['oxygen_available_kg'],1e-6),
            -m['metal_radiation_time_s']/o['cycle']['deployed_s'],
            -m['positive_production_kg']/max(o['captured_kg'],1e-6),
            (o['overall_length_allowance_m']-520)/520,
            (d['mouth_diameter_m']-d['front_diameter_m'])/d['mouth_diameter_m']]
        if 'open_pump_pressure_floor_Pa' in m:
            values.append(-m['open_pump_pressure_floor_Pa']/result['inputs']['performance']['compressor_min_inlet_Pa'])
            values.append(-m['inbound_support_ratio']/result['inputs']['scenario']['open_mouth_support_over_ram'])
        return np.maximum(values,0.)

    def __call__(self,x):
        try:
            result=self.evaluate(x)
            v=self.violations(result)
            if np.max(v)>1e-8:return 10000.+100000.*float(np.sum(v*v))+1000.*float(np.sum(v))
            return math.log(payoff_days(result))
        except (ValueError,RuntimeError,OverflowError,ZeroDivisionError):return 1e7


def search(label,inputs,bounds,keys,seeds,iterations,popsize,workers,initial=None,oxygen_reserve_fraction=0.):
    problem=Problem(inputs,bounds,keys,oxygen_reserve_fraction=oxygen_reserve_fraction)
    runs=[];best=None;best_value=float('inf');start=time.monotonic()
    folder=Path('results/optimization');folder.mkdir(parents=True,exist_ok=True)
    for seed in seeds:
        trace=[]
        def callback(xk,convergence):
            score=problem(xk)
            trace.append(dict(generation=len(trace)+1,payoff_days=math.exp(score) if score<100 else None,
                elapsed_s=time.monotonic()-start))
            if len(trace)%20==0:
                print(label,'seed',seed,'generation',len(trace),'best days',trace[-1]['payoff_days'],flush=True)
            (folder/f'{label}_progress.json').write_text(json.dumps(dict(seed=seed,trace=trace),indent=2)+'\n')
        x0=problem.encode(initial or inputs['design'])
        with mp.get_context('spawn').Pool(workers) as pool:
            result=differential_evolution(problem,[(0,1)]*len(keys),seed=seed,maxiter=iterations,
                popsize=popsize,tol=.002,atol=0.,mutation=(.5,1.),recombination=.8,
                x0=x0,callback=callback,polish=False,workers=pool.map,updating='deferred')
        # Derivative-free bounded local follow-up; the model contains max() and
        # discretized illumination boundaries, so smooth gradients are unreliable.
        local=minimize(problem,result.x,method='Powell',bounds=[(0,1)]*len(keys),
                       options=dict(maxiter=12,maxfev=1600,xtol=1e-4,ftol=1e-5))
        x=local.x if local.fun<result.fun else result.x
        score=problem(x)
        if score>=100:raise RuntimeError(f'{label}: no feasible point found')
        fine=problem.evaluate(x,n=1601)
        violations=problem.violations(fine)
        runs.append(dict(seed=seed,de_success=bool(result.success),de_message=str(result.message),
            generations=int(result.nit),de_evaluations=int(result.nfev),local_evaluations=int(local.nfev),
            search_payoff_days=math.exp(score),verified_payoff_days=payoff_days(fine),
            max_normalized_violation=float(max(violations)),trace=trace,design=fine['inputs']['design']))
        if max(violations)<=2e-5 and payoff_days(fine)<best_value:
            best=fine;best_value=payoff_days(fine);initial=problem.decode(x)
        if best is None:
            # Keep an inspectable result; do not label a failed fine-grid point feasible.
            raise RuntimeError(f'{label}: candidate fails verification: {violations}')
        output=dict(label=label,objective='Operating-orbit dry-mass payoff days; circular delivery excluded',
            variable_names=keys,bounds={k:list(bounds[k]) for k in keys},fixed_inputs={
                **{k:asdict(v) for k,v in inputs.items() if k!='design'},
                'design':{k:v for k,v in asdict(inputs['design']).items() if k not in keys}},
            optimizer=dict(method='Differential evolution + bounded Powell',population_multiplier=popsize,
                max_generations=iterations,search_samples=101,verification_samples=1601),
            search_constraints=dict(max_length_m=520,front_bore_at_least_mouth=True,
                oxygen_reserve_fraction=oxygen_reserve_fraction),
            runs=runs,best=best,best_payoff_days=best_value,elapsed_s=time.monotonic()-start)
        (folder/f'{label}.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
        (folder/f'{label}_config.json').write_text(json.dumps(best['inputs'],indent=2)+'\n')
        print(label,'seed',seed,'verified days',payoff_days(fine),'mass t',fine['outputs']['total_dry_kg']/1000,flush=True)
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['fixed_orbit','free_orbit','lower_perigee'],required=True)
    p.add_argument('--config',type=Path,default=Path('configs/reference.json'))
    p.add_argument('--seed-config',type=Path)
    p.add_argument('--seeds',nargs='+',type=int,default=[11,29])
    p.add_argument('--iterations',type=int,default=100)
    p.add_argument('--popsize',type=int,default=6)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--oxygen-reserve',type=float,default=0.,help='Required unspent fraction of retained oxygen')
    p.add_argument('--mouth-closure',action=argparse.BooleanOptionalAction,default=None)
    a=p.parse_args();inputs=inputs_from_dict(json.loads(a.config.read_text()))
    if a.mouth_closure is not None:
        inputs['design']=replace(inputs['design'],mouth_closure=a.mouth_closure)
    bounds=dict(BOUNDS)
    if a.mode=='lower_perigee':bounds['perigee_km']=(75.,100.,False)
    keys=[k for k in bounds if a.mode!='fixed_orbit' or k not in ('perigee_km','apogee_km')]
    if not inputs['design'].mouth_closure:keys.remove('front_residual_fraction')
    initial=inputs_from_dict(json.loads(a.seed_config.read_text()))['design'] if a.seed_config else None
    if not 0<=a.oxygen_reserve<1:p.error('Oxygen reserve must be in [0,1)')
    label=a.mode+(f'_reserve{100*a.oxygen_reserve:g}' if a.oxygen_reserve else '')
    if not inputs['design'].mouth_closure:label+='_open_mouth'
    search(label,inputs,bounds,keys,a.seeds,a.iterations,a.popsize,a.workers,initial,a.oxygen_reserve)


if __name__=='__main__':main()
