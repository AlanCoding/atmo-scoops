"""Summarize reproducible conditional searches, bounds, and numerical checks."""
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from ..system import simulate,inputs_from_dict
from .search import payoff_days

NAMES=['fixed_orbit','free_orbit','free_orbit_reserve10','lower_perigee']
LABELS=['Fixed orbit optimized','Orbit adjustable, perigee ≥90 km','Same range, 10% oxygen reserve','Perigee range extended to 75 km']


def main():
    baseline=simulate(n=3201)
    studies=[json.loads(Path(f'results/optimization/{name}.json').read_text()) for name in NAMES]
    results=[baseline]+[s['best'] for s in studies];labels=['Comparison inputs']+LABELS
    best=studies[1]['best'];o=best['outputs'];d=best['inputs']['design']
    # Replay each saved input independently through the public API.
    replays=[]
    for name,s in zip(NAMES,studies):
        r=simulate(**inputs_from_dict(s['best']['inputs']),n=3201)
        assert r['constraints']['all_implemented_screens_pass']
        assert abs(payoff_days(r)/s['best_payoff_days']-1)<1e-10
        replays.append(dict(name=name,payoff_days=payoff_days(r),constraints=r['constraints']['margins']))
    Path('results/optimization/replay_audit.json').write_text(json.dumps(replays,indent=2)+'\n')
    lines=['''# Conditional multivariable optimization

The independent implemented variables are identified in `system.Design` and
[PARAMETERS.md](../primary/PARAMETERS.md). This study searches **17 design coordinates with
orbit fixed**, and **19 with orbit adjustable**, holding hardware, performance,
cryogenic process capabilities and the atmospheric scenario fixed.

The objective is **dry mass / net useful product per day in the operating orbit**.
It includes oxygen consumed replacing captured-air momentum and a complete
conditional hardware ledger. It does **not** include circular-apogee delivery,
return or external/closed-mouth drag. Accordingly these are operating mass-payoff
times, not the requested final mission payoff or a demonstrated vehicle.

## Results

| Case | Perigee × apogee | Dry mass | Intake/pass | Net product/pass | Net/day | Operating mass payoff |
|---|---:|---:|---:|---:|---:|---:|''']
    for label,r in zip(labels,results):
        x=r['outputs'];dd=r['inputs']['design']
        lines.append(f"| {label} | {dd['perigee_km']:.1f} × {dd['apogee_km']:.0f} km | {x['total_dry_kg']/1000:,.0f} t | {x['captured_kg']:,.1f} kg | {x['net_liquid_equivalent_kg']:,.1f} kg | {x['net_liquid_equivalent_kg_day']/1000:.2f} t/day | {payoff_days(r):,.1f} days |")
    lines.append(f'''
The variable-orbit search improves this objective by
{payoff_days(baseline)/payoff_days(best):.2f}× relative to the comparison inputs.
The lower-perigee extension gains only another
{100*(1-studies[3]['best_payoff_days']/studies[1]['best_payoff_days']):.1f}% in payoff
while greatly increasing batch mass and installed power at its chosen size.
There is no imposed dry-mass ceiling. These runs do not approach the 30-day
benchmark under the fixed capability targets.

Changing aperture mostly scales throughput and equipment together. It is not a
free improvement in payoff, although shell/fixed overheads give a slight incentive
to larger apertures. Absolute masses should therefore be read together with the
selected dimensions; no unique economically optimal scale has been established.

## What the oxygen reserve means

For the 90 km-and-above candidate, retained gas provides
{o['oxygen_available_kg']:.1f} kg of oxygen per pass and reboost consumes
{o['propellant_kg']:.1f} kg. Almost all oxygen becomes propellant; nitrogen and
the other useful retained gas still become product. A 10% reserve constraint
requires expelling no more than 90% of recovered oxygen, leaving one-tenth of the
oxygen unused as propellant. It is not a 10% collection loss or 10% of the whole batch.

The optimizer trades propellant against electricity: a lower exhaust velocity
uses more oxygen but less reboost energy. Leaving oxygen unused as propellant forces higher
exhaust velocity and a larger power budget. That explains the change from
{studies[1]['best_payoff_days']:.0f} to {studies[2]['best_payoff_days']:.0f} days.
The remaining oxygen counts as available product; this constraint does not
model a permanent emergency stock or substitute for exterior-drag calculation.

## A concrete result from the 90 km-and-above search

| Quantity | Calculated value |
|---|---:|
| Mouth diameter | {d['mouth_diameter_m']:.2f} m |
| Physical front depth / bore | {d['front_depth_m']:.2f} m / {d['front_diameter_m']:.2f} m |
| Physical rear depth / diameter | {d['rear_depth_m']:.2f} m / {d['rear_diameter_m']:.2f} m |
| Total axial allowance | {o['overall_length_allowance_m']:.2f} m |
| Compressor inlet gas | {d['compressor_inlet_K']:.1f} K |
| Metal cold / hot endpoints | {d['metal_cold_K']:.1f} / {o['metal_hot_K']:.1f} K |
| Gas/metal approach | {d['gas_metal_approach_K']:.1f} K |
| Metal thickness | {1000*d['foil_thickness_m']:.2f} mm |
| Intermediate pressure | {d['intermediate_Pa']/1000:.2f} kPa |
| Warm radiator temperature | {d['warm_radiator_K']:.1f} K |
| Isp | {d['isp_s']:.0f} s |
| Collection duration | {o['cycle']['collection_s']:.1f} s |
| Closed recovery duration / fraction removed | {d['recovery_s']:.0f} s / {100*(1-d['front_residual_fraction']):.1f}% |
| Whole orbit | {o['cycle']['orbit_s']/60:.1f} min |
| Fully deployed coast / sunlight | {o['cycle']['deployed_s']/60:.1f} / {o['cycle']['sunlit_s']/60:.1f} min |
| Solar panels | {o['solar_area_m2']:,.0f} m² |
| Warm radiator panels, two emitting faces | {o['warm_radiator_panel_m2']:,.0f} m² |
| Metal sheets, two emitting faces | {o['metal_panel_m2']:,.0f} m² |
| Solar generation | {o['solar_MW']:.1f} MW |
| Impulse-equivalent reboost peak | {o['reboost_peak_MW']:.0f} MW |
| Reboost energy per encounter | {o['reboost_MWh']:.1f} MWh |
| Compressor mass | {o['compressor_mass_kg']/1000:.0f} t |

The optimizer opens earlier in the inbound pressure pulse: 10% of peak ram
instead of the comparison's 50%. Collection lasts about 3.7 minutes. The
300 s thrust burst remains an impulse-equivalent sizing assumption, not an
integrated orbit-restoration trajectory. The enormous arrays still use the same
five-minute deployment target; their mechanical feasibility is unresolved.

## Bounds and independent coordinates

The following are declared search bounds, **not** verified physical limits.
Geometry is additionally constrained to front bore >= mouth and overall length
<=520 m, a search family near the stated 500 m target. Rear rounded heads must
fit. Machinery allowance (20 m), radial clearance (0.85 m), hardware targets,
process capabilities and illumination orientation are fixed. Pump sizing is
automatic, so explicit pump capacity is not searched a second time.

| Design coordinate | Bounds | 90 km-and-above result | Position |
|---|---|---:|---|''')
    for key,(lo,hi,log) in studies[1]['bounds'].items():
        value=d[key];z=np.log(value/lo)/np.log(hi/lo) if log else (value-lo)/(hi-lo)
        at='lower bound' if z<.005 else ('upper bound' if z>.995 else 'interior')
        lines.append(f'| `{key}` | {lo:g}–{hi:g} | {value:.6g} | {at} |')
    lines.append('''
The lower-perigee extension changes only its perigee search range to 75–100 km.
75 km is the atmosphere-table boundary. It does not represent a material limit.
The intended perigee envelope is set by actively cooled leading-edge heat flux,
temperature, stress, erosion and repeat-use lifetime; that engineering model
must determine how far this boundary can be pushed.
The oxygen-reserve run requires at least 10% of retained oxygen to remain after
reboost. This reserve is an explicit scenario constraint, not a new hardware
capability or calculated exterior drag.

## What the boundary results mean

- **25 m front depth:** the solver prefers the smallest allowed front chamber.
  Heat-exchanger conductance, shock accommodation and pressure loss are still
  missing constraints. This is not evidence that 25 m is sufficient.
- **298 K metal start and 50 K approach:** cooler starting metal reduces inventory,
  and a smaller approach allows better temperature utilization. The model checks
  ideal radiative recovery, but does not yet price exchanger conductance or
  passage geometry. The 298 K limit is the implemented material-property domain.
- **2 mm sheets:** increasing thickness reduces deployment area/mass. Radiation
  time is checked, but the reduced gas-side exchange area is not. A true optimum
  needs that conductance/pressure-loss relationship.
- **0.8 ram pressure target:** higher assumed acceptable pressure reduces suction
  volume. This is a prescribed control target, not a computed shock stability
  ceiling. The result cannot validate that chosen pressure.
- **300 s thrust burst:** the solver benefits from lower peak-power hardware mass.
  A finite-thrust trajectory must constrain how far this duration can increase.
- **360 K warm radiator:** higher rejection temperature trades refrigerator work
  against radiator size. The search stops at the declared temperature bound;
  the warm loop and components have not been qualified at this scale.
- **Nearly all oxygen consumed:** no-reserve cases choose Isp close to the oxygen
  balance boundary. They leave essentially no allowance for additional drag or
  other oxygen use. A separate 10% reserve result quantifies the cost without
  pretending to have calculated hull drag.

Approach, minimum front depth, sheet thickness and admissible pressure deserve
particular attention: their apparent improvements exploit costs/constraints
that the current model does not yet resolve. The output is useful for choosing
what physics to develop next, not for accepting a finished spacecraft.

## Algorithm, convergence and verification

SciPy differential evolution searches unit-normalized linear/log coordinates,
followed by bounded Powell refinement. Two random seeds are run for each study;
the second seed includes the first candidate as a warm start. A subsequent
coordinate check includes joint diameter scaling and a fixed-metal-hot-endpoint
thermal move to avoid traps at coupled constraints. Some runs reach the generation
limit; neither the seed agreement nor local checks prove a global optimum.

Search evaluations use 101 samples per phase. Winners are replayed with 1,601
and 3,201 samples, checked for constraints, and saved as standalone input files.
An exact interval update for linearly interpolated inflow replaces the adaptive
front-inventory integrator, using the same differential equation. Independent
ODE comparison tests verify it; this is a speed improvement, not changed physics.

| Search | Seed results before coupled follow-up (days) | Final (days) | Largest 1,601→3,201 relative output change |
|---|---|---:|---:|''')
    for label,s in zip(LABELS,studies):
        seeds=', '.join(f"{x['seed']}: {x['verified_payoff_days']:.3f}" for x in s['runs'])
        err=max(s['coupled_followup']['relative_change'].values())
        lines.append(f"| {label} | {seeds} | {s['best_payoff_days']:.3f} | {err:.2g} |")
    lines.append('''
These saved searches use mouth closure. The discrete mouth option and its
[mass/leakage comparison](../primary/MOUTH_CLOSURE.md) are separate from these
continuous searches. An open-mouth search omits the inactive residual-fraction
coordinate, giving 16 or 18 continuous coordinates. No open-mouth optimized
winner is presented in this report.

These resolution checks cover the numerical model, not omitted flow or hardware
physics. All final candidates pass the implemented system screens and the search
geometry/reserve constraints within the recorded numerical tolerance.

## Reproduce and modify

```sh
.venv/bin/python -m atmo_scoops.optimization.search --mode fixed_orbit --iterations 100 --seeds 11 29
.venv/bin/python -m atmo_scoops.optimization.search --mode free_orbit --iterations 120 --seeds 11 29
.venv/bin/python -m atmo_scoops.optimization.search --mode lower_perigee --seed-config results/optimization/free_orbit_config.json --iterations 120 --seeds 17 37
.venv/bin/python -m atmo_scoops.optimization.search --mode free_orbit --seed-config results/optimization/free_orbit_config.json --oxygen-reserve .1 --iterations 100 --seeds 17 37
.venv/bin/python -m atmo_scoops.optimization.review
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.optimization.report
```

`atmo_scoops/optimization/search.py` declares every bound. Saved studies contain fixed inputs,
random seeds, traces, search settings and verification. Replay a candidate with:

```sh
.venv/bin/python -m atmo_scoops --config results/optimization/free_orbit_config.json --samples 3201 --output results/optimization/replayed_system.json
```

The comparison configuration is unchanged; none of these candidates silently
replaces it as the reference. Full files are in `results/optimization/`.

![Conditional optimization comparison](../../figures/optimization_summary.png)
''')
    Path('analysis/optimization/RESULTS.md').write_text('\n'.join(lines)+'\n')
    plot(results)


def plot(results):
    names=['Comparison','Fixed orbit','Free orbit\n≥90 km','10% O₂\nreserve','Perigee\n≥75 km']
    fig,ax=plt.subplots(1,2,figsize=(13,5.8))
    days=[payoff_days(r) for r in results]
    ax[0].bar(names,days,color=['#94a3b8','#327b9f','#0f766e','#9a6db0','#c77730'])
    for i,y in enumerate(days):ax[0].text(i,y+20,f'{y:.0f}',ha='center')
    ax[0].axhline(30,color='#a12222',ls='--',label='30-day benchmark')
    ax[0].set(ylabel='Operating-orbit mass payoff (days)',title='Search results under fixed capability targets')
    ax[0].legend()
    categories=[('Propulsion + distribution',['propulsion_hardware','power_distribution']),
        ('Solar + batteries',['solar','battery']),('Compressors',['compressor_hot','compressor_warm','compressor_coast']),
        ('Other hardware',[]),('Margin',['design_margin'])]
    bottom=np.zeros(len(results));used=set(sum((keys for _,keys in categories),[]))
    colors=['#b45309','#c9a340','#327b9f','#82a994','#b6b9bd']
    for (label,keys),color in zip(categories,colors):
        vals=[]
        for r in results:
            o=r['outputs'];m=o['masses_kg']
            mass=sum(m[k] for k in keys) if keys else sum(v for k,v in m.items() if k not in used)
            vals.append(mass/o['net_liquid_equivalent_kg_day'])
        ax[1].bar(names,vals,bottom=bottom,label=label,color=color);bottom+=vals
    ax[1].set(ylabel='Component contribution to payoff (days)',title='What still determines the operating payoff')
    ax[1].legend(fontsize=8,loc='upper right')
    for a in ax:a.grid(axis='y',alpha=.2);a.set_axisbelow(True)
    fig.suptitle('Two-compartment scoop optimization • circular delivery and exterior drag excluded',fontsize=13)
    fig.text(.5,.014,'Bounds, prescribed capture and capability assumptions are explicit; these are not verified spacecraft designs or global optima.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.95))
    for ext in ('png','svg'):fig.savefig(f'figures/optimization_summary.{ext}',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
