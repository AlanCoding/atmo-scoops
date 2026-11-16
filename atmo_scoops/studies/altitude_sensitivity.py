"""Fixed geometry altitude sensitivity; dependent equipment is resized, not optimized."""
from dataclasses import replace
from pathlib import Path
import json, hashlib, argparse
from ..system import inputs_from_dict, simulate


def main():
    root=Path(__file__).resolve().parents[2]
    out=root/'results/altitude_sensitivity';out.mkdir(exist_ok=True)
    base=inputs_from_dict(json.loads((root/'results/compressor_refinement/candidate_real_compact.json').read_text())['inputs'])
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true',help='Compare saved 60/80 km cases at 1601 samples')
    if parser.parse_args().verify:
        checks=[]
        for altitude in (60,80):
            old=json.loads((out/f'{altitude}km.json').read_text())
            args=inputs_from_dict(old['inputs'])
            args['compressor']=replace(args['compressor'],thermodynamic_samples=1601)
            result=simulate(**args,n=1601)
            (out/f'{altitude}km_fine.json').write_text(json.dumps(result,indent=2)+'\n')
            checks.append(dict(altitude_km=altitude,relative_payoff_change=result['outputs']['operating_mass_payoff_days']/old['outputs']['operating_mass_payoff_days']-1))
        (out/'convergence.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(checks)
        return
    rows=[]
    for altitude in range(50,151,10):
        inputs={**base,'design':replace(base['design'],perigee_km=float(altitude))}
        try:
            result=simulate(**inputs,n=401)
            (out/f'{altitude}km.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
            o=result['outputs'];c=result['constraints']
            row=dict(altitude_km=altitude,payoff_days=o['operating_mass_payoff_days'],dry_t=o['total_dry_kg']/1000,
                compressor_t=o['compressor_mass_kg']/1000,net_kg_pass=o['net_liquid_equivalent_kg'],
                screens_pass=c['all_implemented_screens_pass'],failed_margins={k:v for k,v in c['margins'].items() if v< -1e-8})
        except ValueError as exc:
            from dataclasses import asdict
            row=dict(altitude_km=altitude,error=str(exc),inputs={k:asdict(v) for k,v in inputs.items()})
        rows.append(row);print({k:v for k,v in row.items() if k!='inputs'},flush=True)
        (out/'summary.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    sources=list((root/'atmo_scoops').rglob('*.py'))
    (out/'manifest.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')

if __name__=='__main__':main()
