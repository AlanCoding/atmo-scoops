"""Resolution, conservation and orbital-invariant audit of the active system."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from .system import Design,Scenario,simulate
from .orbit import Orbit,MU


def main():
    cases=[Design(),replace(Design(),compressor_inlet_K=650),replace(Design(),compressor_inlet_K=750),
           replace(Design(),compressor_inlet_K=1100),replace(Design(),front_depth_m=25,rear_depth_m=10),
           replace(Design(),front_depth_m=400,rear_depth_m=100)]
    cases=[(d,Scenario()) for d in cases]+[
        (replace(Design(),mouth_closure=False),Scenario()),
        (replace(Design(),mouth_closure=False),Scenario(open_mouth_support_over_ram=.3))]
    rows=[]
    for d,scenario in cases:
        coarse=simulate(d,scenario=scenario,n=401);fine=simulate(d,scenario=scenario,n=1601)
        a=coarse['outputs'];b=fine['outputs']
        errors={k:abs(a[k]/b[k]-1) for k in ('captured_kg','retained_kg','total_dry_kg','compressor_kWh','hot_absorbed_GJ')}
        assert max(errors.values())<2e-4,errors
        assert abs(b['thermal_energy_balance_residual_J'])<.01
        assert abs(b['captured_kg']-b['retained_kg']-b['vent_kg'])<1e-9
        assert abs(sum(b['masses_kg'].values())-b['total_dry_kg'])<1e-7
        rows.append(dict(design=fine['inputs']['design'],scenario=fine['inputs']['scenario'],relative_resolution_errors=errors,
            thermal_residual_J=b['thermal_energy_balance_residual_J']))
    o=Orbit(100,2000);_,_,r,_,vr,vt=o.eccentric_grid(1001)
    energy=(vr*vr+vt*vt)/2-MU/r;angular=r*vt
    assert np.max(np.abs(energy/(-MU/(2*o.a))-1))<1e-12
    assert np.max(np.abs(angular/o.h-1))<1e-12
    report=dict(status='passed',cycle_cases=rows,orbit_energy_angular_invariants='passed',
        scope='Current lumped cycle conservation and resolution; not a thrust trajectory, inlet CFD or hardware validation')
    Path('results/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Passed {len(rows)} cycle resolution/conservation cases and Kepler energy/angular-momentum checks.')


if __name__=='__main__':main()
