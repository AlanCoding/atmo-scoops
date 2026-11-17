"""L/D<=10, storage<=1.1 bar: finite-rack / folded-package boundary study."""
from pathlib import Path
from dataclasses import replace
import json, math, hashlib
from scipy.optimize import root,brentq
from ..system import inputs_from_dict,simulate
from ..racks import Racks
from ..orbit import Orbit

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'results/finite_rack_limits/reference_1mm'

def main():
    DEST.mkdir(parents=True,exist_ok=True)
    base=inputs_from_dict(json.loads((ROOT/'configs/limit_case_reference.json').read_text()))
    base['design']=replace(base['design'],front_depth_m=1.,machinery_depth_m=0.)
    base['performance']=replace(base['performance'],deploy_s=0.,retract_s=0.)
    base['racks']=Racks(wire_radius_m=.001,radius_over_pitch=.1)
    base['compressor']=replace(base['compressor'],minimum_train_ratio=100.,thermodynamic_samples=201)
    rows=[]
    for apogee in (2000.,6000.,10000.):
        trials=[];cache={}
        def evaluate(h,depth,n=201):
            key=(float(h),float(depth),n)
            if key not in cache:
                args={**base,'design':replace(base['design'],perigee_km=float(h),apogee_km=apogee,rear_depth_m=float(depth)),
                    'controls':replace(base['controls'],max_after_perigee_s=min(1200.,Orbit(h,apogee).time_at_altitude(999.))),
                    'compressor':replace(base['compressor'],thermodynamic_samples=n)}
                r=simulate(**args,n=n);cache[key]=r;o=r['outputs']
                trials.append(dict(perigee_km=h,rear_depth_m=depth,pressure_Pa=o['rear_pressure_Pa'],length_m=o['overall_length_allowance_m'],payoff_days=o['operating_mass_payoff_days']))
                print(apogee,trials[-1],flush=True)
            return cache[key]
        def residual(x):
            h=float(x[0]);depth=float(x[1])
            if not 65<h<110 or depth<15:raise ValueError('Boundary root left physical search bracket')
            o=evaluate(h,depth)['outputs']
            return [(o['overall_length_allowance_m']-317.)/317.,math.log(o['rear_pressure_Pa']/110000.)]
        guess={2000.:[83.2,19.],6000.:[81.,19.],10000.:[81.,19.]}[apogee]
        sol=root(residual,guess,options={'eps':1e-5,'xtol':1e-5})
        if not sol.success or max(abs(v) for v in residual(sol.x))>.002:
            raise ValueError(str(sol.message))
        hroot,depthroot=map(float,sol.x)
        # Small interior step and finer resolution; no failing root called feasible.
        r=evaluate(hroot+.05,depthroot+.1,801)
        name=f'apogee_{apogee:.0f}.json';(DEST/name).write_text(json.dumps(r,indent=2)+'\n')
        (DEST/f'trials_{apogee:.0f}.json').write_text(json.dumps(trials,indent=2)+'\n')
        o=r['outputs'];row=dict(apogee_km=apogee,perigee_km=r['inputs']['design']['perigee_km'],rear_depth_m=o['rear_depth_m'],
            pressure_Pa=o['rear_pressure_Pa'],length_m=o['overall_length_allowance_m'],dry_t=o['total_dry_kg']/1000,
            compressor_t=o['compressor_mass_kg']/1000,net_kg_pass=o['net_liquid_equivalent_kg'],payoff_days=o['operating_mass_payoff_days'],
            period_h=o['cycle']['orbit_s']/3600,screens=r['constraints']['all_implemented_screens_pass'],file=name)
        rows.append(row);print('RESULT',row,flush=True)
        (DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    (DEST/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'atmo_scoops').rglob('*.py')},indent=2)+'\n')

if __name__=='__main__':main()
