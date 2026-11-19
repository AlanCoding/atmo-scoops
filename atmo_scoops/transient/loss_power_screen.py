"""Frozen-history, linear hydraulic-power charge. No forward solve or property flash."""
import argparse
import gzip
import json
from pathlib import Path
import numpy as np
from .porous import laminar_bank_coefficient, viscosity

def charge(mdot,p,T,rho,g,eta):
    if g.get("lattice")=="parallel_plates":
        from .plates import charge as plate_charge
        return plate_charge(mdot,p,T,rho,g,eta)
    if mdot<=0:
        return 0.,0.
    if min(p,T,rho,eta)<=0:
        raise ValueError('Positive flowing-state properties and efficiency required')
    beta=1-2*g['wire_radius_m']/g['pitch_m']
    flux=mdot/g['frontal_m2']
    Re=flux*2*g['wire_radius_m']/(beta*viscosity(T))
    a=g['pitch_m']/(2*g['wire_radius_m'])
    K=(g['row_count']*laminar_bank_coefficient(Re,a,a)+(1-beta)**2)/beta**2
    dp=K*flux**2/(2*rho)
    return dp*(mdot/rho)/eta,2*dp/p

def analyze(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt') as f:r=json.load(f)
    t=np.array(r['time_s']);h=r['history'];m=np.maximum(r['gas_species_kg'],0)
    # Density comes directly from saved inventory and chamber gas volume.
    # No EOS, real-fluid property call or temperature inversion is performed.
    rho=m.sum(axis=2)/np.array([g['gas_m3'] for g in r['hardware']['geometry']])
    flow=np.column_stack([h['pump_kg_s'],h['coast_kg_s']])
    eta=r['inputs']['capabilities']['eta_compressor']*r['inputs']['capabilities']['eta_motor']
    power=np.zeros_like(flow);chi=np.zeros_like(flow)
    for j,g in enumerate(r['hardware']['geometry']):
        for i in range(len(t)):
            power[i,j],chi[i,j]=charge(flow[i,j],h['pressure_Pa'][i][j],h['gas_K'][i][j],rho[i,j],g,eta)
    baseline=r['ledger']['shaft_MJ'][-1]/r['inputs']['capabilities']['eta_motor']/3600
    stages=np.trapezoid(power,t,axis=0)/3.6e9
    cases=[]
    for alpha in [.01,.1,1.]:
        cases.append(dict(multiplier=alpha,added_MWh=float(alpha*stages.sum()),
            percent_of_baseline=float(100*alpha*stages.sum()/baseline),
            peak_added_MW=float(alpha*power.sum(axis=1).max()/1e6),
            stage_added_MWh=(alpha*stages).tolist(),
            transported_mass_fraction_beyond_pressure_limit=np.divide(np.trapezoid(flow*(alpha*chi>=1),t,axis=0),np.trapezoid(flow,t,axis=0)).tolist(),
            max_linear_dp_over_p=(alpha*chi.max(axis=0)/2).tolist()))
    return dict(source=str(path),baseline_compression_electric_MWh=baseline,
                baseline_total_load_MWh=float(np.trapezoid(h['load_MW'],t)/3600),
                source_loss_multiplier=r['inputs']['capabilities']['rack_loss_multiplier'],cases=cases)

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('results/transient/staged/bypass_verify/check_refined.json.gz'))
    p.add_argument('--output',type=Path,default=Path('results/transient/loss_power_screen.json'));a=p.parse_args()
    result=analyze(a.input);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
