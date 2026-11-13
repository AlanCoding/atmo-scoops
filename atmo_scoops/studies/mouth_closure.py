"""Compare optional mouth closure and reduced outbound-boundary sensitivities."""
from dataclasses import replace
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..system import inputs_from_dict, simulate
from ..two_volume import Reference, calculate
from ..atmosphere import make_profile
from ..orbit import Orbit
from ..encounter import orbit_state


def main():
    cases=[('Comparison inputs','configs/reference.json'),
           ('90 km search candidate','results/optimization/free_orbit_config.json'),
           ('90 km / 10% oxygen reserve candidate','results/optimization/free_orbit_reserve10_config.json')]
    runs=[];audits=[]
    for label,path in cases:
        inputs=inputs_from_dict(json.loads(Path(path).read_text()))
        for closed in (True,False):
            current={**inputs,'design':replace(inputs['design'],mouth_closure=closed)}
            coarse=simulate(**current,n=1601);fine=simulate(**current,n=3201)
            errors={k:abs(coarse['outputs'][k]/fine['outputs'][k]-1) for k in
                    ('captured_kg','retained_kg','total_dry_kg','compressor_kWh')}
            assert max(errors.values())<2e-4
            o=fine['outputs']
            assert abs(o['captured_kg']-o['retained_kg']-o['vent_kg'])<1e-6
            assert abs(o['thermal_energy_balance_residual_J'])<.01
            audits.append(dict(case=label,closure=closed,relative_resolution_errors=errors,
                               energy_residual_J=o['thermal_energy_balance_residual_J']))
            runs.append(dict(case=label,result=fine))
    base=inputs_from_dict(json.loads(Path(cases[1][1]).read_text()))
    sensitivity=[]
    for support in (1.,.8,.6,.3):
        for floor in (.1,1.,10.):
            r=simulate(**{**base,'design':replace(base['design'],mouth_closure=False),
                'scenario':replace(base['scenario'],open_mouth_support_over_ram=support),
                'performance':replace(base['performance'],compressor_min_inlet_Pa=floor)},n=1601)
            sensitivity.append(r)
    doors=[]
    for coefficient in (10.,100.,1000.):
        doors.append(simulate(**{**base,'hardware':replace(base['hardware'],mouth_closure_kg_m2=coefficient)},n=1601))
    output=dict(scope='Fixed-input architecture comparison; no open-mouth reoptimization or CFD validation',
                runs=runs,support_and_floor_sensitivity=sensitivity,door_mass_sensitivity=doors,audit=audits)
    Path('results/mouth_closure.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    lines=['''# Mouth closure comparison

Mouth closure is an explicit design option. The same inlet, physical depths,
compressor capacity and capability targets are used for each paired comparison;
dependent tank, heat, propulsion, solar and battery requirements are recalculated.
Consequently these are redesigned hardware budgets at fixed independent inputs,
not a claim that an installed vehicle can process twice its rated batch.
The open variant has **not** been reoptimized. Circular delivery is excluded.

The closed variant ends admission at perigee, then pumps residuals. The open
variant keeps its collection suction running into the outbound atmosphere until
its inlet reaches 0.1 Pa. The pressure floor is a capability assumption, not a
measured pump map. The timeout is the input recovery duration; a timeout above
the floor fails a screen. Rear tanks are isolated when the pump stops.

## Cycle and hardware comparison

| Input set | Mouth | Admitted / pass | Stored / pass | Lost / pass | Dry mass | Net product / day | Operating payoff | System screens |
|---|---|---:|---:|---:|---:|---:|---:|---|''']
    for row in runs:
        r=row['result'];o=r['outputs'];closed=r['inputs']['design']['mouth_closure']
        lines.append(f"| {row['case']} | {'Closes' if closed else 'Stays open'} | {o['captured_kg']:.2f} kg | {o['retained_kg']:.2f} kg | {o['vent_kg']:.3f} kg | {o['total_dry_kg']/1000:,.1f} t | {o['net_liquid_equivalent_kg_day']/1000:.3f} t | {o['operating_mass_payoff_days']:.1f} days | {'pass' if r['constraints']['all_implemented_screens_pass'] else 'FAIL'} |")
    lines.append('''
Lost mass includes outward leakage during pumping and the final front residual.
The open mouth admits more mass because collection continues after perigee.
Any apparent payoff benefit combines that longer collection window and removal
of the door; it is not solely the door's mass saving. A closure-equipped design
could also close later: closure time is not yet a searched coordinate.

The nominal boundary uses support pressure equal to `rho*u²` and discharge
coefficient 0.8. In these nominal cases, pumping keeps the plenum below the
assumed support until the pressure floor: reverse flow is zero. That is a
conditional result of this reduced boundary, not proof against inlet unstart
or three-dimensional spillage. The weaker-support cases below show reverse flow.

### 90 km search candidate: component outputs

| Quantity | Closes at perigee | Stays open |
|---|---:|---:|''')
    a=runs[2]['result']['outputs'];b=runs[3]['result']['outputs']
    for label,key,scale,unit in [('Front depth','front_depth_m',1,'m'),('Rear depth','rear_depth_m',1,'m'),
            ('Compressors','compressor_mass_kg',.001,'t'),('Solar panels','solar_area_m2',1,'m²'),
            ('Warm radiator panels','warm_radiator_panel_m2',1,'m²'),('Metal sheets','metal_panel_m2',1,'m²'),
            ('Propellant per pass','propellant_kg',1,'kg'),('Recovered oxygen per pass','oxygen_available_kg',1,'kg'),
            ('Oxygen remaining per pass','oxygen_mass_margin_kg',1,'kg')]:
        lines.append(f"| {label} | {a[key]*scale:,.2f} {unit} | {b[key]*scale:,.2f} {unit} |")
    lines.append(f"| Post-perigee pumping duration | {a['cycle']['recovery_s']:.1f} s | {b['cycle']['recovery_s']:.1f} s |")
    lines.append(f"| Closure hardware, before margin | {a['masses_kg']['mouth_closure']/1000:.2f} t | 0 t |")
    lines.append('''
Physical radiator/sheet areas have two emitting faces; solar area is collecting
area. The post-perigee duration is a result for the open case. Both retain the
compressor wall and rear isolation hardware.

## Pressure support and pump-floor sensitivity

These change only the 90 km search candidate's outbound boundary and pressure
floor, with no door. Inbound full-capture assumptions remain prescribed. This
is a boundary sensitivity, not a self-consistent fluid prediction of either leg.
Weak-support rows below the inbound plenum/ram ratio also fail the inbound
support screen. They deliberately start from the same prescribed inbound state;
their leakage is predominantly a short initial pressure-relaxation burst, not
proof of a late-outbound instability. Their inflow/outflow curves are diagnostic
boundary tests, not self-consistent complete passes. A negative oxygen balance
also fails the oxygen-only reboost screen. Failed-row payoff arithmetic is shown
only for diagnosis.

| Support / ram | Pump floor | Stop after perigee | Reverse leak | Final residual | Net kg/pass | Oxygen margin | Payoff | Screens |
|---|---:|---:|---:|---:|---:|---:|---:|---|''')
    for r in sensitivity:
        o=r['outputs'];i=r['inputs']
        lines.append(f"| {i['scenario']['open_mouth_support_over_ram']:.1f} | {i['performance']['compressor_min_inlet_Pa']:g} Pa | {o['cycle']['recovery_s']:.1f} s | {o['mouth_leakage_kg']:.3f} kg | {o['final_front_vent_kg']:.3f} kg | {o['net_liquid_equivalent_kg']:.1f} | {o['oxygen_mass_margin_kg']:.3f} kg | {o['operating_mass_payoff_days']:.1f} days | {'pass' if r['constraints']['all_implemented_screens_pass'] else 'FAIL'} |")
    lines.append('''
## Closure mass sensitivity

The door allowance covers skin, supports, seals and actuation. It is separate
from the permanent compressor bulkhead. No detailed closure design supports
these coefficients yet. The following holds the closed candidate unchanged:

| Door specific mass | Installed door, before margin | Whole dry mass | Operating payoff |
|---|---:|---:|---:|''')
    for r in doors:
        o=r['outputs'];h=r['inputs']['hardware']
        lines.append(f"| {h['mouth_closure_kg_m2']:g} kg/m² | {o['masses_kg']['mouth_closure']/1000:.2f} t | {o['total_dry_kg']/1000:,.1f} t | {o['operating_mass_payoff_days']:.1f} days |")
    lines.append('''
The default 10 kg/m² is a target, not evidence that such a large reusable cooled
door can be built at that mass. Open-mouth protection, early-entry heating and
drag are also missing design costs. Those omissions prevent selecting a winner.

## Validation and reproduction

Both variants are checked for mass/energy conservation and 1,601→3,201-sample
convergence. The port helper has an independent analytic vacuum-leak/pump test,
including its sonic limit. These verify the implementation, not the support
coefficient or real shock behavior. Saved inputs and all signed margins are in
`results/mouth_closure.json`.

```sh
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.mouth_closure
.venv/bin/python -m atmo_scoops --config configs/reference.json --no-mouth-closure --output results/open_mouth.json
```

See [model equations](MODEL.md), [independent inputs](PARAMETERS.md),
[fluid analysis](../fluid/README.md) and the
[improvement list](../../docs/MODEL_IMPROVEMENTS.md).

![Post-perigee open-mouth pressure and mass flow](../../figures/mouth_closure.png)
''')
    Path('analysis/primary/MOUTH_CLOSURE.md').write_text('\n'.join(lines)+'\n')
    plot(base)
    for row in runs:
        r=row['result'];o=r['outputs']
        print(row['case'],r['inputs']['design']['mouth_closure'],round(o['operating_mass_payoff_days'],2),
              'days; oxygen margin',round(o['oxygen_mass_margin_kg'],3),'kg; screens',r['constraints']['all_implemented_screens_pass'])


def plot(inputs):
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for support,color in [(1.,'#0f766e'),(.3,'#c77730')]:
        inp={**inputs,'design':replace(inputs['design'],mouth_closure=False),
             'scenario':replace(inputs['scenario'],open_mouth_support_over_ram=support)}
        resolved=simulate(**inp,n=1601)
        raw=calculate(Reference(**resolved['resolved_cycle_inputs']),n=1601,process_targets=inputs['process'])
        h=raw['history'];t=np.array(h['time_s']);keep=t>=0
        tt=t[keep];p=np.array(h['front_pressure_Pa'])[keep]
        state=orbit_state(Orbit(inputs['design'].perigee_km,inputs['design'].apogee_km),tt,
                          make_profile(inputs['scenario'].atmosphere_name))
        axes[0].plot(tt,p,color=color,label=f'Plenum, support={support:g} ram')
        axes[0].plot(tt,support*state['ram_Pa'],color=color,ls='--',label=f'Assumed support={support:g} ram')
        axes[1].plot(tt,np.array(h['intake_mass_flow_kg_s'])[keep],color=color,label=f'Admission, {support:g} ram')
        axes[1].plot(tt,np.array(h['leakage_mass_flow_kg_s'])[keep],color=color,ls='--',label=f'Reverse leak, {support:g} ram')
    axes[0].axhline(.1,color='#666',ls=':',label='Pump floor 0.1 Pa')
    axes[0].set(yscale='log',ylabel='Pressure (Pa)',title='Reduced pressure boundary')
    axes[1].set(ylabel='Mass flow (kg/s)',title='Admission and outward leakage')
    axes[1].set_xscale('symlog',linthresh=.1)
    axes[1].set_xlim(0,None)
    for ax in axes:
        ax.set_xlabel('Seconds after perigee');ax.grid(alpha=.2);ax.legend(fontsize=8)
    axes[1].set_xlabel('Seconds after perigee (log scale beyond 0.1 s)')
    fig.suptitle('Open-mouth 90 km candidate • coefficient sensitivity, not CFD')
    fig.tight_layout()
    for ext in ('png','svg'):fig.savefig(f'figures/mouth_closure.{ext}',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
