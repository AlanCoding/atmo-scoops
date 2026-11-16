"""Generate the incremental-mixing conclusion and its capability thresholds."""
from dataclasses import replace
from pathlib import Path
import json,math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from ..system import inputs_from_dict,simulate

ROOT=Path('results/incremental_mixing')
DEST=Path('investigations/incremental_mixing')


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    runs={p.stem:json.loads(p.read_text()) for p in ROOT.glob('*.json')}
    ratios=[0.,.01,.03,.1,.25,.5,1.]
    def run(free,path,r):
        if r==0:path='fixed_rack'
        return runs[f'{"free" if free else "fixed"}_{path}_{r:g}']['best']
    baseline=run(True,'fixed_rack',0);base=baseline['outputs'];base_days=base['operating_mass_payoff_days']
    thresholds=[]
    for ratio in (.01,.1,.25,.5,1.):
        r=run(True,'fixed_rack',ratio);o=r['outputs'];inp=inputs_from_dict(r['inputs'])
        saving=o['total_dry_kg']-base_days*o['net_liquid_equivalent_kg_day']
        margin=1+inp['hardware'].design_margin
        def excess(eta):
            args={**inp,'performance':replace(inp['performance'],isothermal_efficiency=eta)}
            result=simulate(**args,n=801)
            return result['outputs']['operating_mass_payoff_days']-base_days
        eta=None
        if excess(.8)<0:
            eta=brentq(excess,.5,.8,xtol=2e-6)
        thresholds.append(dict(ratio=ratio,additional_dry_mass_saving_kg=saving,
            additional_hot_compressor_mass_saving_fraction=saving/margin/o['masses_kg']['compressor_hot'],
            train_isothermal_efficiency_break_even=eta,
            scope='Fixed searched controls; extra improvement only in mixed case; alternatives, not simultaneous credits'))
    # Finer independent environmental grid for the near-neutral sensitivity.
    fine_checks=[]
    for ratio in (0.,.1):
        result=runs[f'heavy_compressors_free_fixed_rack_{ratio:g}']['best']
        fine=simulate(**inputs_from_dict(result['inputs']),n=6401)
        fine_checks.append(dict(ratio=ratio,payoff_3201=result['outputs']['operating_mass_payoff_days'],
            payoff_6401=fine['outputs']['operating_mass_payoff_days'],
            mass_balance_residual_kg=fine['outputs']['mixing']['cycle_mass_residual_kg']))
    Path('results/mixing_thresholds.json').write_text(json.dumps(dict(thresholds=thresholds,heavy_case_resolution=fine_checks),indent=2)+'\n')
    plt.rcParams.update({'svg.fonttype':'none','font.size':10})
    fig,axs=plt.subplots(1,3,figsize=(16,5.4),layout='constrained')
    for path,color,label in [('fixed_rack','#087e8b','Solve mixed temperature'),('fixed_inlet','#d06a24','Hold mixed temperature')]:
        ys=[run(True,path,r)['outputs']['operating_mass_payoff_days']-base_days for r in ratios]
        axs[0].plot(ratios,ys,'o-',color=color,label=label)
    axs[0].set_yscale('symlog',linthresh=2)
    axs[0].set(xlabel='Injected LN₂ / new air (kg/kg)',ylabel='Change in payoff (days; symlog scale)',title='Nominal capabilities: mixing penalty')
    axs[0].axhline(0,color='#777',lw=.8);axs[0].legend(fontsize=8)
    axs[1].plot(ratios,[run(True,'fixed_rack',r)['outputs']['compressor_inlet_K'] for r in ratios],'o-',color='#087e8b',label='Mixed compressor gas')
    axs[1].plot(ratios,[run(True,'fixed_rack',r)['inputs']['design']['compressor_inlet_K'] for r in ratios],'--',color='#777',label='Dry stream after rack')
    axs[1].set(xlabel='Injected LN₂ / new air (kg/kg)',ylabel='Temperature (K)',title='Much colder gas; more circulating mass');axs[1].legend(fontsize=8)
    mixed=run(True,'fixed_rack',.1)['outputs'];a=base['masses_kg'];b=mixed['masses_kg']
    groups={'Hot compressors':['compressor_hot'],'Warm + coast pumps':['compressor_warm','compressor_coast'],
        'Metal + deployment':['hot_metal','hot_sheet_deployment'],'Cold plant':['refrigerator','product_heat_exchangers'],
        'Solar + battery':['solar','battery'],'Warm radiator/buffer':['warm_radiator','warm_buffer','warm_aftercooler'],
        'Other + margin':[]}
    deltas=[sum(b.get(k,0)-a.get(k,0) for k in keys)/1000 for keys in groups.values()]
    deltas[-1]=(mixed['total_dry_kg']-base['total_dry_kg'])/1000-sum(deltas[:-1])
    axs[2].barh(list(groups),deltas,color=['#087e8b' if v<0 else '#d06a24' for v in deltas])
    axs[2].axvline(0,color='#777',lw=.8);axs[2].set(xlabel='Mass change (tonnes)',title='r = 0.1: component trade');axs[2].invert_yaxis()
    for ax in axs:ax.grid(alpha=.15)
    fig.suptitle('Incremental LN₂ mixing — fixed geometry, reoptimized thermal endpoint and pumping\nConditional inlet and compressor capabilities; recycled nitrogen is not new product',fontsize=13)
    fig.savefig(DEST/'mixing_trade.svg');fig.savefig(DEST/'mixing_trade.png',dpi=150);plt.close(fig)
    lines=['# Incremental LN₂ mixing','',
        '**Decision: retain mixing support in the active model.** Compressor physics remains a major unresolved item; the current study does not rule out benefits under realistic compressor capabilities. Zero injection is a reference setting, not a decision to eliminate mixing.','',
        '**Nominal result: incremental mixing does not improve payoff in the tested reference design, but its penalty can be very small. The compressor capability assumptions can reverse that sign.** Keep zero optional injection as the nominal numerical baseline; this is not a rejection of film cooling required for material survival. A flight mixing ratio needs the real thermal and compressor maps.','',
        '## What was compared','',
        'The reference geometry is an 18.3 m mouth/front/rear bore, a 250 m front and 25 m rear, in a 100 × 2,000 km orbit with 4,000 s Isp. Dry mass is an output, with no ceiling. Ratios r = 0, 0.01, 0.03, 0.1, 0.25, 0.5 and 1 mean **kg of injected LN₂ per kg of newly admitted atmospheric gas**, not coolant fraction of the total mixture.','',
        '- **Fixed rack endpoint:** precool the new air to a specified dry-stream temperature, then mix LN₂ and solve the colder compressor-inlet temperature from enthalpy. The metal endpoint remains tied to the dry stream.','- **Fixed mixed inlet:** hold the compressor-inlet temperature while injection replaces part of the metal cooling duty. Total compressed mass rises without a compensating gas-temperature reduction.','',
        'The first search family holds the thermal endpoint at 1,000 K. The second also searches it from 601 to 1,142 K, with metal cold temperature 500 K and approach 100 K. Every ratio gets the same suction-scale range 0.5–1.5 and cutoff range 0.0315–10 Pa. Both paths include actual admission/reverse flow, finite-backflow pumping and automatic hardware resizing. Geometry, orbit, staging, Isp and other capabilities stay fixed. These are coarse grids plus two bounded coordinate passes, **not a whole-vehicle or global optimum**.','',
        '## Payoff versus injected ratio','',
        '| LN₂ / new air | Fixed rack, 1,000 K dry stream | Fixed mixed inlet, 1,000 K | Rack endpoint also searched | Mixed inlet also searched |',
        '|---:|---:|---:|---:|---:|']
    for ratio in ratios:
        values=[run(free,path,ratio)['outputs']['operating_mass_payoff_days'] for free,path in ((False,'fixed_rack'),(False,'fixed_inlet'),(True,'fixed_rack'),(True,'fixed_inlet'))]
        lines.append(f'| {ratio:g} | '+' | '.join(f'{v:,.3f} d' for v in values)+' |')
    lines += ['', 'All are operating-orbit dry-mass payoffs, before circular-apogee delivery. All saved winners pass the implemented screens. A failed point is not ranked as a feasible improvement. The broad geometry optimizer has not been rerun with these changes.','',
        f"With thermal endpoint and pumping free, the unmixed control is **{base_days:.3f} days**. At r = 0.1 the result is **{mixed['operating_mass_payoff_days']:.3f} days**, a penalty of **{mixed['operating_mass_payoff_days']-base_days:.3f} day ({100*(mixed['operating_mass_payoff_days']/base_days-1):.3f}%)**. The mixed gas is much colder, but coolant mass also passes through the warm compressor and cryogenic plant.",'',
        '![Incremental mixing payoff, temperatures and component mass changes](mixing_trade.svg)','',
        '### Cycle inventory and compressor behavior','',
        '| Ratio | Dry stream → mixed gas | New air admitted | LN₂ injected | Coolant replacement | Net new liquid | Hot suction | Total compressor mass |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|']
    for ratio in ratios:
        r=run(True,'fixed_rack',ratio);o=r['outputs'];m=o['mixing']
        lines.append(f"| {ratio:g} | {m['dry_stream_K']:.1f} → {m['mixed_K']:.1f} K | {o['captured_kg']:.3f} kg | {m['injected_kg']:.3f} kg | {m['coolant_replacement_kg']:.4f} kg | {o['net_liquid_equivalent_kg']:.3f} kg | {o['hot_suction_m3_s']:,.0f} m³/s | {o['compressor_mass_kg']/1000:.3f} t |")
    lines += ['', 'All masses in this table are per pass except installed compressor mass. Replacement includes reverse/front losses and the 0.1% coast-feed residual. It is reserved from captured nitrogen. Oxygen propulsion is checked against retained atmospheric oxygen, not diluted mixture mass.','',
        '### r = 0.1 versus no mixing: component budgets','',
        '| Quantity | No mixing | r = 0.1 | Change |','|---|---:|---:|---:|']
    rows=[('Whole dry mass','total_dry_kg',.001,'t'),('Hot compressor bank',('masses_kg','compressor_hot'),.001,'t'),
        ('Warm compressor bank',('masses_kg','compressor_warm'),.001,'t'),('Metal rack',('masses_kg','hot_metal'),.001,'t'),
        ('Refrigerator package',('masses_kg','refrigerator'),.001,'t'),('Solar area','solar_area_m2',1,'m²'),
        ('Warm radiator panel area','warm_radiator_panel_m2',1,'m²'),('Metal sheet area','metal_panel_m2',1,'m²'),
        ('Compression electricity','compressor_kWh',1,'kWh/pass'),('Cryoplant electric power','cryoplant_electric_kW',1,'kW')]
    for label,key,scale,unit in rows:
        get=lambda o:o[key] if isinstance(key,str) else o[key[0]][key[1]]
        a=get(base)*scale;b=get(mixed)*scale
        lines.append(f'| {label} | {a:,.3f} {unit} | {b:,.3f} {unit} | {b-a:+,.3f} {unit} |')
    lines += ['', 'The warm radiator and metal-sheet areas are physical panels with two emitting faces. The hot-bank mass saving is real within the declared volume-rate model, but the warm-bank throughput, refrigeration, heat rejection and other costs consume it. The metal mass changes slightly because its endpoint is reoptimized; it is not held fixed in this table.','',
        '## What compressor improvement would make mixing worthwhile?','',
        'The model holds effective compression efficiency at 0.5 and volume-rate mass target at 30 kg/(m³/s). Those assumptions do not capture a real machine becoming lighter or more efficient at a lower inlet temperature. The following thresholds hold each searched mixed policy fixed and compare against the optimized unmixed control. They are required **additional** gains, beyond the volume-flow savings already counted. They are alternatives, not cumulative credits.','',
        '| Ratio | Additional whole-dry-mass saving needed | Equivalent extra hot-bank mass reduction before margin | Train efficiency needed instead of 0.5 |',
        '|---:|---:|---:|---:|']
    for r in thresholds:
        eta='not reached ≤0.8' if r['train_isothermal_efficiency_break_even'] is None else f"{r['train_isothermal_efficiency_break_even']:.4f}"
        lines.append(f"| {r['ratio']:g} | {r['additional_dry_mass_saving_kg']:,.1f} kg | {100*r['additional_hot_compressor_mass_saving_fraction']:.3f}% | {eta} |")
    lines += ['', 'The efficiency threshold changes the effective hot/warm compression efficiency only in the mixed case; it does not assert a measured temperature response. The coast-feed and refrigerator efficiencies retain their separate assumptions. A measured benefit of this size could change the decision; applying it without a map would manufacture a conclusion.','',
        '### Reoptimized capability scenarios','',
        'These change the same capability for both r = 0 and r = 0.1, and repeat the thermal/suction/cutoff search.','',
        '| Shared capability | No mixing | r = 0.1 | Difference |','|---|---:|---:|---:|']
    for prefix,label in (('heavy_compressors','Compressor target 100 instead of 30 kg/(m³/s)'),('efficient_cryo','Refrigerator 30% instead of 15% of Carnot')):
        a=runs[f'{prefix}_free_fixed_rack_0']['best']['outputs']['operating_mass_payoff_days']
        b=runs[f'{prefix}_free_fixed_rack_0.1']['best']['outputs']['operating_mass_payoff_days']
        lines.append(f'| {label} | {a:.3f} d | {b:.3f} d | {b-a:+.3f} d |')
    lines += ['', 'The heavier-compressor scenario reverses the sign, but by only about an hour on a multi-year payoff. This is a near tie, not engineering evidence for a preferred ratio. A 6,401-sample replay checks the numerical sign separately; bounded coordinate searches still do not certify a global minimum. These capability scenarios are not changes to the reference configuration.','',
        '## Physical explanation and balances','',
        'Cooling lowers temperature, but suction capacity depends on **total mass × specific gas constant × temperature**. For the same new-air rate and inlet pressure:', '',
        '```text\nS_mixed / S_dry = (1+r) (R_mixed/R_dry) (T_mixed/T_dry)\n```','',
        'For equal-Cp ideal gases, cold gas alone satisfies `(1+r)T_mix = T_hot + r T_cold`; total suction volume increases despite the temperature drop. At 1,000 K hot gas, 80 K cold gas and r = 0.1, temperature becomes about 916 K but total suction volume is 1.008 times the original. This limiting result does not include LN2 latent heat.','',
        'LN2 absorbs roughly 200 kJ/kg through vaporization as well as sensible heat. That can lower the required hot-bank suction volume, as the calculated table shows. It also adds warm-stage throughput and a coolant-restoration duty. Recovered nitrogen must be reliquefied and reserved for the next orbit; nitrogen lost from the loop must be replaced.','',
        '```text\nFixed-rack mixing: h_air(T_dry) + r [h_LN2 + w_injection]\n                   = (1+r) h_mix(T_mixed)\nMass: new_air + injected_LN2 = stored_mixture + reverse_leak + final_front\nNet new liquid: 0.999 stored_mixture − injected_LN2 − propulsion\n```','',
        'Liquid enthalpy is anchored to the gas enthalpy reference at 298.15 K using NIST sensible/latent heat, rather than extrapolating gas polynomials into the liquid domain. The actual molecular mixture determines R and heat capacity; atmospheric oxygen is transported separately. Injection is proportional to new admission, so coolant is never assigned atmospheric arrival momentum.','',
        'Both comparison branches route all compressor heat to the warm loop. A mixed stream can be colder than the metal rack, so assigning isothermal compressor heat to the hotter rack would be invalid. This shared thermal-accounting change means the unmixed control is recomputed here; numbers from the frozen prior decision study are not silently reused.','',
        '## Inputs, limitations and next decision','',
        'The injector/storage allowances are explicit: 0.15 kg of storage hardware per kg of startup LN2, 25 kg fixed injection hardware, 10 kg per kg/s peak injection flow, 1 MPa pressure work, 806 kg/m³ density proxy, 60% pump efficiency and 500 W/kg pump specific power. No added hardware is charged at r = 0. Dry mass excludes the circulating LN2 itself; it is reported separately with warm-loop inventory. These allowances are scenario targets, not qualified tanks or atomizers.','',
        'The reduced model assumes complete mixing/vaporization, a uniform molecular endpoint and a nitrogen-equivalent cryogenic plant. It does not resolve injector location, atomization, film heat transfer, rack conductance/pressure loss, pump thermal clearances or non-equilibrium chemistry. The fixed-inlet path uses the mixed-gas endpoint to set its conservative metal endpoint; it does not give a free hotter exchanger. The fixed-rack path represents injection after the rack has performed its assigned dry-stream cooling. Neither path establishes leading-edge cooling performance. Admission conductance is evaluated at the lumped cooled mixture state; the upstream diffuser/rack flow and injector location are not spatially resolved. Those inlet uncertainties can exceed the small nominal payoff differences.','',
        'The actionable result is that **optional bulk mixing needs little additional compressor benefit to break even**, while using injection merely to replace solid cooling at unchanged compressor temperature is substantially more expensive. Required film cooling must be evaluated against material survival and hardware saved, rather than rejected because a thermal-protection-free model prefers r = 0.','',
        '## Verification and reproduction','',
        'Tests cover the exact r = 0 limit, liquid-reference and mixer enthalpy, mass/species accounting, coolant replacement, no fictitious product or arrival momentum, hydraulic access, cutoff, and full thermal/power accounting. Winners are replayed at 1,601 and 3,201 environmental samples. Exact inputs, unsuccessful search points, margins and numerical errors are retained in [results/incremental_mixing](../../results/incremental_mixing/); [thresholds and finer checks](../../results/mixing_thresholds.json) are separate.','',
        '```sh\n.venv/bin/python -m atmo_scoops.studies.incremental_mixing --workers 4\n.venv/bin/python -m atmo_scoops.studies.incremental_mixing --sensitivity --workers 4\nMPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.mixing_report\n```','',
        'A frozen [source, inputs and results snapshot](reproduction.tar.gz), with [checksum](SHA256.txt), preserves this experiment independently of later model changes. Extract it into a separate directory, create a local venv in `snapshot/`, install `requirements-lock.txt`, and run the commands above there.','',
        'The implementation is [mixing.py](../../atmo_scoops/mixing.py) with the shared [cycle kernel](../../atmo_scoops/two_volume.py) and [continuous inlet](../../atmo_scoops/inlet.py). The same optional mixing inputs work through the public API and JSON configurations.','',
        'Sources: [NIST nitrogen gas heat capacity](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Units=SI&Mask=1), [NIST nitrogen phase data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Units=SI&Mask=4), and [Leybold pump operating principles](https://www.leybold.com/en-us/knowledge/vacuum-fundamentals/vacuum-generation/how-does-a-roots-pump-work). The latter supports the need for backing-pressure/internal-backflow and thermal operating maps; it does not validate the scoop compressor. [Source qualifications](../../docs/SOURCES.md) and the [remaining engineering plan](../../docs/DESIGN_STUDIES_PLAN.md) distinguish evidence from targets.','']
    (DEST/'ANALYSIS.md').write_text('\n'.join(lines))
    print('Wrote mixing conclusion, thresholds and figures.',thresholds,flush=True)

if __name__=='__main__':main()
