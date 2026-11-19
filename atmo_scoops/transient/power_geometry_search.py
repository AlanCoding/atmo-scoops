"""Feasibility-first blocked pattern search of power-only rack geometry and hardware.

Geometry coordinates preserve nominal solid inventory. No candidate sizes itself
from its trajectory. Completion of a finite poll is not convergence certification.
"""
import argparse
import copy
import json
import math
from pathlib import Path
from .staged_search import batch

def geometry(base,ratios=None,radii=None):
    c=copy.deepcopy(base);d=c['design'];old_r=d.get('stage_radius_m') or [d['rod_radius_m']]*5
    old_p=d.get('stage_pitch_m') or [d['rod_pitch_m']]*5
    old_a=[p/r for p,r in zip(old_p,old_r)]
    ratios=ratios or old_a;radii=radii or old_r
    ratios=[min(40.,max(4.01,a)) for a in ratios]
    radii=[min(.005,max(.0002,r)) for r in radii]
    d['stage_radius_m']=radii;d['stage_pitch_m']=[r*a for r,a in zip(radii,ratios)]
    d['rack_depth_m']=[z*(a/b)**2 for z,a,b in zip(d['rack_depth_m'],ratios,old_a)]
    return c

def geometry_proposals(base,stage,round_id):
    d=base['design'];r=d.get('stage_radius_m') or [d['rod_radius_m']]*5
    p=d.get('stage_pitch_m') or [d['rod_pitch_m']]*5;a=[x/y for x,y in zip(p,r)]
    out={};steps=(.7,1.4) if round_id==0 else (.9,1.1)
    for i in range(5):
        for scale in steps:
            aa=a.copy();aa[i]*=scale;out[f'pitch_{i}_{scale:g}']=geometry(base,ratios=aa)
    if round_id==0:
        for ratio in (4.01,6.,8.,12.,16.):out[f'all_pitch_ratio_{ratio:g}']=geometry(base,ratios=[ratio]*5)
    if stage=='radius':
        for i in range(5):
            for scale in ((.5,2.) if round_id==0 else (.8,1.25)):
                rr=r.copy();rr[i]*=scale;out[f'radius_{i}_{scale:g}']=geometry(base,radii=rr)
        if round_id==0:
            for radius in (.0002,.0005,.002,.005):out[f'all_radius_{radius:g}']=geometry(base,radii=[radius]*5)
    return out

def hardware_proposals(base):
    out={}
    bounds=dict(isp_s=(1200.,5000.),burn_s=(800.,1800.),solar_area_m2=(1e6,5e6),battery_MWh=(180.,1200.),battery_MW=(450.,2500.),bus_MW=(450.,2500.),warm_store_kg=(200000.,1500000.),warm_radiator_m2=(20000.,150000.),plant_flow_kg_s=(.5,4.),plant_electric_MW=(5.,40.))
    for key,(lo,hi) in bounds.items():
        for sign in (-1,1):
            c=copy.deepcopy(base);c['design'][key]=min(hi,max(lo,c['design'][key]*(1+sign*.06)));out[f'{key}_{sign}']=c
    for i in range(4):
        for sign in (-1,1):
            c=copy.deepcopy(base);c['design']['motor_MW'][i]*=1+sign*.15;out[f'motor_{i}_{sign}']=c
    for sign in (-1,1):
        c=copy.deepcopy(base);c['design']['coast_motor_MW']*=1+sign*.15;out[f'coast_motor_{sign}']=c
    return out

def choose(rows):
    good=[r for r in rows if r.get('feasible')]
    return min(good,key=lambda r:r['operating_payoff_days']) if good else None

def combine_geometry(seed,best,rows):
    """Test coordinated independent geometry moves on the selected hardware."""
    d=seed['inputs']['design'];r=d.get('stage_radius_m') or [d['rod_radius_m']]*5
    p=d.get('stage_pitch_m') or [d['rod_pitch_m']]*5;a=[x/y for x,y in zip(p,r)]
    rr=list(r);aa=list(a)
    for i in range(5):
        for kind in ('pitch','radius'):
            good=[z for z in rows if z['name'].startswith(f'r0_{kind}_{i}_') and z.get('feasible') and z['operating_payoff_days']<seed['operating_payoff_days']*(1-1e-5)]
            winner=choose(good)
            if winner:
                w=winner['inputs']['design'];wr=w['stage_radius_m'][i];wp=w['stage_pitch_m'][i]
                if kind=='radius':rr[i]=wr
                else:aa[i]=wp/wr
    # Use the seed's nominal solid inventory, with the winner's installed hardware.
    c=copy.deepcopy(best['inputs']);g=geometry(seed['inputs'],ratios=aa,radii=rr)['design']
    for key in ('stage_radius_m','stage_pitch_m','rack_depth_m'):c['design'][key]=g[key]
    return c

def headroom(c,lean=False):
    c=copy.deepcopy(c);d=c['design']
    if lean:
        d['motor_MW'][0]*=1.15;d['warm_store_kg']*=1.12;d['warm_radiator_m2']*=1.06
        return c
    d['motor_MW'][0]*=1.5;d['warm_store_kg']*=1.25;d['warm_radiator_m2']*=1.15
    d['solar_area_m2']*=1.02;d['battery_MWh']*=1.02;d['bus_MW']*=1.05
    return c

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stage',choices=['pitch','radius'],required=True);p.add_argument('--rounds',type=int,default=1);p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=int,default=300);p.add_argument('--finish-combination',action='store_true');a=p.parse_args()
    base=json.loads(a.config.read_text());assert base['design']['rack_loss_mode']=='power_only'
    a.output.mkdir(parents=True,exist_ok=True)
    manifest=dict(base=base,stage=a.stage,rounds=a.rounds,algorithm='geometry poll, then hardware poll; feasible selection; finite budget',radius_bounds_m=[.0002,.005],pitch_radius_ratio_bounds=[4.01,40.],fixed_nominal_solid_inventory=True)
    path=a.output/'search.json'
    if path.exists() and json.loads(path.read_text())!=manifest:raise ValueError('Changed search; use another directory')
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    if a.finish_combination:
        rows=json.loads((a.output/'evaluations.json').read_text());best=json.loads((a.output/'best_summary.json').read_text());seed=next(r for r in rows if r['name']=='seed')
        combined=combine_geometry(seed,best,rows)
        cases={'geometry_combined':combined}
        for ratio in (4.01,6.,8.):cases[f'joint_pitch_{ratio:g}']=headroom(geometry(best['inputs'],ratios=[ratio]*5))
        for ratio in (4.01,6.):cases[f'lean_joint_pitch_{ratio:g}']=headroom(geometry(best['inputs'],ratios=[ratio]*5),lean=True)
        if a.stage=='radius':
            for radius in (.0002,.0005):cases[f'joint_radius_{radius:g}']=headroom(geometry(best['inputs'],radii=[radius]*5))
        fresh=batch(cases,a.output,a.workers,a.seconds)
        best=choose([best,*fresh]);(a.output/'best_config.json').write_text(json.dumps(best['inputs'],indent=2)+'\n');(a.output/'best_summary.json').write_text(json.dumps(best,indent=2)+'\n')
        done=json.loads((a.output/'done.json').read_text());done.update(best=best['name'],payoff_days=best['operating_payoff_days'],evaluations=len(json.loads((a.output/'evaluations.json').read_text())),geometry_combination_checked=True)
        (a.output/'done.json').write_text(json.dumps(done,indent=2)+'\n');return
    best=choose(batch({'seed':base},a.output,a.workers,a.seconds))
    if best is None:raise RuntimeError('No feasible seed; do not rank infeasible payoff')
    for rd in range(a.rounds):
        proposals={f'r{rd}_{k}':c for k,c in geometry_proposals(best['inputs'],a.stage,rd).items()}
        rows=batch(proposals,a.output,a.workers,a.seconds);best=choose([best,*rows])
        center=copy.deepcopy(best['inputs'])
        proposals={f'r{rd}_hw_{k}':c for k,c in hardware_proposals(center).items()}
        rows=batch(proposals,a.output,a.workers,a.seconds)
        # Combine favorable independent hardware changes, then solve anew.
        combined=copy.deepcopy(center)
        for key in list(hardware_proposals(center)):
            if not key.endswith('_-1'):continue
            prefix=f'r{rd}_hw_{key[:-3]}_'
            candidates=[r for r in rows if r['name'].startswith(prefix) and r.get('feasible') and r['operating_payoff_days']<best['operating_payoff_days']]
            winner=choose(candidates)
            if winner:
                for field,value in winner['inputs']['design'].items():
                    if value!=center['design'].get(field):
                        if field=='motor_MW':
                            for i,v in enumerate(value):
                                if v!=center['design'][field][i]:combined['design'][field][i]=v
                        else:combined['design'][field]=value
        if combined!=center:rows+=batch({f'r{rd}_combined':combined},a.output,a.workers,a.seconds)
        best=choose([best,*rows])
        (a.output/'best_config.json').write_text(json.dumps(best['inputs'],indent=2)+'\n')
        (a.output/'best_summary.json').write_text(json.dumps(best,indent=2)+'\n')
    rows=json.loads((a.output/'evaluations.json').read_text())
    (a.output/'done.json').write_text(json.dumps(dict(best=best['name'],payoff_days=best['operating_payoff_days'],evaluations=len(rows),convergence_certified=False,termination='finite search budget'),indent=2)+'\n')

if __name__=='__main__':main()
