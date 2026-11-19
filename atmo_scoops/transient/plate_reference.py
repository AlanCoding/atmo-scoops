"""Validate a closure-reserved reference from actual COBYLA evaluations.

No parameters are hand-adjusted. Retain the lowest-payoff recorded feasible
point with a declared battery closure reserve, and verify at three resolutions.
"""
import json
from pathlib import Path
from .staged_search import batch,resolution,numerical_gate


def main():
    root=Path('results/transient/plates');src=root/'cobyla_stable'
    rows=json.loads((src/'evaluations.json').read_text());good=sorted((r for r in rows if r['feasible']),key=lambda r:r['operating_payoff_days'])
    reserve=20.
    chosen=next(r for r in good if r['closure']['battery_MJ']>=-100+reserve)
    nearest=next(r for r in good if r['closure']['battery_MJ']>=-90.)
    cases={}
    for r in [chosen,nearest]:
        c=r['inputs'];name=f'case_{r["index"]}'
        cases[name]=c;cases[name+'_refined']=resolution(c);cases[name+'_finer']=resolution(resolution(c))
    folder=root/'reference_validation';fresh=batch(cases,folder,4,300);byname={r['name']:r for r in fresh};checks={}
    for r in [chosen,nearest]:
        name=f'case_{r["index"]}'
        a,b,c=[byname[name+s] for s in ('','_refined','_finer')]
        checks[name]=dict(coarse_to_refined=numerical_gate([a,b]),refined_to_finer=numerical_gate([b,c]),payoffs=[z['operating_payoff_days'] for z in [a,b,c]],battery_MJ=[z['closure']['battery_MJ'] for z in [a,b,c]])
    (folder/'gates.json').write_text(json.dumps(checks,indent=2)+'\n')
    check=checks[f'case_{chosen["index"]}']
    if not all(check[k]['passed'] for k in ['coarse_to_refined','refined_to_finer']):raise RuntimeError('Reserved reference failed verification; do not promote')
    result=dict(source_index=chosen['index'],battery_closure_reserve_MJ=reserve,rule='Lowest payoff in the actual optimizer history with at least 20 MJ nominal reserve inside the unchanged 100 MJ battery closure tolerance',nominal=chosen,validation=check,trajectory=byname[f'case_{chosen["index"]}']['trajectory'])
    (root/'reference_selection.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(reference_index=chosen['index'],validation=check)),flush=True)

if __name__=='__main__':main()
