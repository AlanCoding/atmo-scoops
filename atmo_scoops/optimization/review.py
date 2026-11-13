"""Coupled-coordinate follow-up and high-resolution replay of saved searches."""
from dataclasses import replace
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from .search import Problem,payoff_days
from ..system import inputs_from_dict,simulate


def review(path):
    saved=json.loads(path.read_text());bounds={k:tuple(v) for k,v in saved['bounds'].items()}
    inputs=inputs_from_dict(saved['best']['inputs']);keys=saved['variable_names']
    reserve=saved.get('search_constraints',{}).get('oxygen_reserve_fraction',0.)
    p=Problem(inputs,bounds,keys,oxygen_reserve_fraction=reserve)
    d=inputs['design'];initial_days=payoff_days(saved['best']);score=p(p.encode(d));steps=[]
    def consider(candidate,label):
        nonlocal d,score
        if any(not (bounds[k][0]-1e-8<=getattr(candidate,k)<=bounds[k][1]+1e-8) for k in keys):return
        s=p(p.encode(candidate))
        if s<score-1e-10:
            score=s;d=candidate;steps.append(dict(change=label,search_payoff_days=math.exp(s)))
    for iteration in range(2):
        # Moving mouth/front/rear together avoids a coordinate-polish trap at
        # the front-bore >= mouth boundary. Preserve rear volume per mouth area.
        original=d
        for mouth in np.linspace(bounds['mouth_diameter_m'][0],bounds['mouth_diameter_m'][1],16):
            scale=mouth/original.mouth_diameter_m;newrear=original.rear_diameter_m*scale
            candidate=replace(original,mouth_diameter_m=mouth,front_diameter_m=original.front_diameter_m*scale,
                rear_diameter_m=newrear,rear_depth_m=original.rear_depth_m+(newrear-original.rear_diameter_m)/6)
            consider(candidate,'joint diameter scaling')
        # Hold metal hot endpoint fixed while decreasing gas/metal approach.
        # This is a genuinely coupled move when the material limit is active.
        approach=bounds['gas_metal_approach_K'][0]
        consider(replace(d,gas_metal_approach_K=approach,
            compressor_inlet_K=d.compressor_inlet_K-d.gas_metal_approach_K+approach),'fixed metal-hot endpoint, reduced approach')
        for key in keys:
            x=p.encode(d);index=keys.index(key)
            def fun(z):
                trial=x.copy();trial[index]=z
                return p(trial)
            result=minimize_scalar(fun,bounds=(0.,1.),method='bounded',options=dict(xatol=2e-5,maxiter=45))
            for z in (0.,1.,float(result.x)):
                trial=x.copy();trial[index]=z
                consider(p.decode(trial),'coordinate '+key)
    fine=simulate(**{**inputs,'design':d},n=1601)
    finer=simulate(**{**inputs,'design':d},n=3201)
    violation=float(max(p.violations(finer)))
    if violation>2e-5 or payoff_days(finer)>=initial_days:
        d=inputs['design'];fine=simulate(**inputs,n=1601);finer=simulate(**inputs,n=3201)
        violation=float(max(p.violations(finer)))
    assert violation<=2e-5
    audit=dict(initial_payoff_days=initial_days,steps=steps,verified_payoff_days=payoff_days(finer),
        max_normalized_violation=violation,samples=[1601,3201],
        relative_change={k:abs(fine['outputs'][k]/finer['outputs'][k]-1) for k in
            ('total_dry_kg','captured_kg','net_liquid_equivalent_kg','compressor_kWh')})
    saved['coupled_followup']=audit;saved['best']=finer;saved['best_payoff_days']=payoff_days(finer)
    saved['search_constraints']=dict(max_length_m=520,front_bore_at_least_mouth=True,oxygen_reserve_fraction=reserve)
    path.write_text(json.dumps(saved,indent=2)+'\n')
    path.with_name(path.stem+'_config.json').write_text(json.dumps(finer['inputs'],indent=2)+'\n')
    print(path.stem,initial_days,'->',saved['best_payoff_days'],'days; resolution',max(audit['relative_change'].values()),flush=True)
    return saved


def main():
    names=['fixed_orbit','free_orbit','lower_perigee','free_orbit_reserve10']
    for name in names:review(Path('results/optimization')/(name+'.json'))


if __name__=='__main__':main()
