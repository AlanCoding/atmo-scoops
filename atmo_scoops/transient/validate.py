"""Independent post-run thermodynamic and closure checks (no resizing/shooting)."""
import argparse,json
from pathlib import Path
import numpy as np
from ..compressor import RealAir
from .thermo import properties,Y
from .io import read_result


def check(r):
    th=properties();th.table_enabled=r['inputs']['design'].get('compression_model','HEOS')=='HEOS_table'
    real=RealAir();T=np.asarray(r['history']['gas_K']);p=np.asarray(r['history']['pressure_Pa'])
    masses=np.asarray(r['gas_species_kg']);flow=np.asarray(r['history']['pump_kg_s'])
    indices=np.unique(np.r_[np.linspace(0,len(T)-1,101,dtype=int),np.argmax(p,axis=0),np.argmax(flow,axis=0)])
    zerr=0.;workerr=0.;outlet=0.;domain_failures=[]
    for j in indices:
        for k in range(5):
            m=masses[j,k];total=m.sum()
            if total<.01:continue
            yy=m/total;real.fluid.set_mass_fractions(yy.tolist());real.mass_fractions=yy.tolist()
            try:
                state=real.state(p[j,k],T[j,k]);zerr=max(zerr,abs(state['Z']-1))
                if k<4 and flow[j,k]>.001:
                    ps=r['history'].get('compressor_suction_Pa',p[:,:4])[j][k]
                    expected=real.compress(ps,T[j,k],max(ps,p[j,k+1]),r['inputs']['capabilities']['eta_compressor'])
                    w=th.compression(T[j,k],ps,p[j,k+1],yy,r['inputs']['capabilities']['eta_compressor'])
                    workerr=max(workerr,abs(w-expected['shaft_J_kg'])/max(expected['shaft_J_kg'],1.))
                    outlet=max(outlet,expected['outlet']['T_K'])
            except ValueError as exc:domain_failures.append(dict(index=int(j),stage=k,error=str(exc)))
    if r['inputs']['design'].get('propellant_storage')=='gas':
        for j in indices:
            m=np.asarray(r['gas_reserve_species_kg'][j]);real.fluid.set_mass_fractions((m/m.sum()).tolist())
            try:zerr=max(zerr,abs(real.state(r['history']['buffer_Pa'][j],r['history']['buffer_K'][j])['Z']-1))
            except ValueError as exc:domain_failures.append(dict(index=int(j),stage='gas_buffer',error=str(exc)))
    return dict(max_abs_Z_minus_one=zerr,max_compressor_work_relative_error=workerr,
                max_audited_compressor_outlet_K=outlet,domain_failures=domain_failures,
                low_density_chamber_EOS_screen_passed=zerr<.01 and not domain_failures,
                note='HEOS compressor work; low-density chamber EOS checked at 101 times plus extrema. This is not a nonideal mixture chamber solver or physical validation.')


def main():
    a=argparse.ArgumentParser();a.add_argument('result',type=Path);args=a.parse_args()
    r=check(read_result(args.result));path=args.result.with_suffix('.validation.json');path.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
