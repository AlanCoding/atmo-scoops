"""Regenerate comparison, trajectory plots and concept geometry from saved runs."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .io import read_result

def main():
    folder=Path('results/transient/feed_pitch');out=Path('investigations/feed_pitch');out.mkdir(exist_ok=True)
    records=json.loads((folder/'comparison.json').read_text())
    cases={'gas_reference':read_result('results/transient/gas_trial.json'),'dense_rack':read_result('results/transient/rack_trial.json')}
    for row in records:
        if 'error' not in row:cases[row['case']]=read_result(folder/f'cycle_{row["case"]}.json')
    lines=['# Gas reserve and independently spaced racks','',
    'These are declared candidate comparisons, not a joint global optimum. All retain the 85 × 2,000 km orbit, 30 m bore, 317 m hull, 1,766 s Isp, 1,200 s symmetric burn, and effective external skin coefficient 0.002. Hardware is compiled once before each forward integration. Payoffs below end in the **operating orbit**, not circular-apogee delivery.','',
    'Gas bypass supports a smaller installed liquefier and gives a modest mass/payoff improvement in the zero-rack-loss comparison. The original dense transverse front rack is a much stronger concern: nominal resistance eliminates net liquid production in its completed liquid-feed comparison. This is evidence of sensitivity to the assumed rack geometry/law, not experimental evidence against passive cooling. A wider-spacing full-cycle result remains numerically unresolved; no optimized spacing or combined improved payoff is claimed.','',
    '## Coupled results','',
    '| Case | Dry mass (t) | Net liquid (kg/orbit) | Accepted payoff (days) | Constraint failures |',
    '|---|---:|---:|---:|---|']
    for name,r in cases.items():
        pay=r['operating_payoff_days'];fails=', '.join(k for k,v in r['margins'].items() if v< -1e-6)
        if not r['feasible'] and not fails:fails='audit/property/hatch check'
        lines.append(f'| {name} | {r["dry_kg"]/1000:,.1f} | {r["net_liquid_kg"]:,.1f} | {f"{pay:.2f}" if pay else "Rejected"} | {fails or "None"} |')
    for row in records:
        if 'error' in row:lines.append(f'| {row["case"]} | — | — | Unresolved | {row["error"]} |')
    pending=set(json.loads((folder/'proposals.json').read_text()))-set(cases)
    if pending:lines+=['','Additional saved proposals are not completed results: '+', '.join(sorted(pending))+'. No payoff or physical rejection is assigned to them.']
    if 'joint_dense' in cases:
        joint=cases['joint_dense'];deficit=-sum(joint['closure']['gas_reserve_species_kg'])
        lines+=['',f'The combined dense-rack/gas-feed case makes {joint["net_liquid_kg"]:.1f} kg of liquid but finishes {deficit:.1f} kg short of its initial gas reserve. Its positive liquid output is therefore **not a sustainable payoff**. The refill booster can bottleneck while the product branch continues; even redirecting all that liquid-equivalent mass would not recover the total reserve shortfall. The periodic inventory constraint correctly rejects it.']
    lines+=['','`layout_only` is the liquid-feed checkpoint with outlet-plane geometry but zero resistance. `gas_reference` changes only feed architecture. `gas_smaller_plant` additionally proposes 20 MW / 2 kg/s liquefaction instead of 40 MW / 4 kg/s before integration. `dense_rack` retains liquid feed with 10 mm pitch and nominal resistance. `wide` combines gas feed with 20 mm pitch and nominal resistance; `joint_dense` combines gas feed with 10 mm pitch and nominal resistance. Only completed trajectories have geometry/results rows below.','',
    'The liquid-feed reference is favorable to liquid storage: it does not resolve a vaporizer/regulator assembly. Gas feed is credited only for avoided processing and is charged for its own reserve hardware. The gas case also consumes its small argon fraction, whereas the historical liquid-feed case retains argon as product.','',
    '## Rack and volume geometry','',
    '| Case | Pitches (mm) | Actual rack depths (m) | Material mass (t) | Receiver depth (m) |',
    '|---|---|---|---:|---:|']
    for name,r in cases.items():
        g=r['hardware']['geometry'];lines.append(f'| {name} | '+', '.join(f'{z["pitch_m"]*1000:g}' for z in g)+' | '+', '.join(f'{z["rack_depth_m"]:.2f}' for z in g)+f' | {sum(z["mass_kg"] for z in g)/1000:.1f} | {g[-1]["depth_m"]:.2f} |')
    lines+=['','Wider pitch at unchanged depth also removes metal and heat-transfer surface; it is not an isolated pressure-loss improvement. Rod radius remains 1 mm. The additional fixed-mass case, when present, scales front depth with pitch squared.','',
    '## Gas-feed physical specification','',
    'The reserve contains unseparated gas, with no cryogenic or separation duty on its branch. Its four 6.25 m outer-diameter spheres have 500 m³ combined internal volume and 1.5 MPa design pressure. A 10 m³/s, 5 MW booster and aftercooler refill them during coast. The existing warm loop supplies/absorbs tank heat; the burn uses the previous cycle\'s reserve. The branch hardware weighs 51.9 t before margin and occupies 1,099 m³ of package envelope before general packing clearance.','',
    '![Reserve and flow traces](../../docs/images/feed_pitch_histories.png)','',
    '## Hydraulic interpretation and limits','',
    'Pressure loss is placed at the compressor suction and coupled to the finite map, not charged afterward as a wattage penalty. Each volume remains a blended thermal inventory. The outlet-plane layout uses actual withdrawal for forced convection; it does not assume inlet flow circulates through the receiver rack before withdrawal.','',
    'The independent-cylinder resistance law is a **provisional screening assumption**, not a validated multirow, rarefied-array correlation. Its nominal coefficient must not be interpreted as data establishing that a rack design succeeds or fails. Re, Kn and pore Mach are saved; the accepted-cycle low-Mach screen is 0.3. In particular, rod-scale slip can matter despite continuum flow on the spacecraft scale. See [equations and primary references](../../modeling/metal_coolers/TRANSVERSE_PLANES.md).','',
    '## Verification and reproduction','',
    'Full trajectories retain species/energy ledgers, path constraints, per-stage suction/loss states and gas-reserve closure. Conservation checks are numerical evidence, not validation of the component correlations. Gas reserve closure checks each species within 0.1 kg and energy within 1 MJ.','',
    '```bash\nOPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient --config configs/transient_gas_reference.json --output results/transient/gas_trial.json --samples 401\nOPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient --config configs/transient_rack_reference.json --output results/transient/rack_trial.json --samples 401\nOPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.feed_pitch_study --workers 3\n.venv/bin/python -m atmo_scoops.transient.feed_pitch_report\n```','',
    'Geometry exports contain actual chamber/rack dimensions, bank envelopes and package volumes. They are a **concept-model specification**, not resolved mechanical packing: frame details, pressure-hatch placement, plumbing and global structure remain deferred. The selected gas reference export is not represented as a pressure-loss-optimized craft.','',
    'Future priority requested by the owner: integrate the cryogenic process with existing compressors, thermal loops, recuperators and propellant routing. Other proposed penalty refinements remain deferred.']
    hydraulic=['','## States at each stage’s peak withdrawal','',
      '| Case / stage | Flow (kg/s) | Bulk pressure (Pa) | Rack drop (Pa) | Rod Re | Rod Kn |',
      '|---|---:|---:|---:|---:|---:|']
    for name,r in cases.items():
        if not r['inputs']['capabilities'].get('rack_loss_multiplier',0):continue
        h=r['history'];flows=np.c_[h['pump_kg_s'],h['coast_kg_s']]
        for j in range(5):
            i=int(np.argmax(flows[:,j]));hydraulic.append(f'| {name} / {j+1} | {flows[i,j]:.2f} | {h["pressure_Pa"][i][j]:.2f} | {h["rack_drop_Pa"][i][j]:.2f} | {h["rack_Re"][i][j]:.2f} | {h["rack_Kn"][i][j]:.4f} |')
    lines+=hydraulic
    if 'layout_only' in cases:
        import copy
        from .inputs import read_config
        from .hardware import compile_hardware
        from .porous import pump_flow
        from .thermo import properties,Y
        base=cases['layout_only'];i=int(np.argmax(np.array(base['history']['pump_kg_s'])[:,0]));h=base['history'];th=properties()
        screen=[]
        lines+=['','## Controlled local hydraulic screen','',
          'These are **local pump calculations at the checkpoint peak first-stage state**, not full-cycle payoffs. Bulk pressure, temperature, discharge pressure and compressor hardware are held fixed. The fixed-metal comparison increases depth with pitch squared; it separates hydraulic geometry from removing thermal storage. Half/nominal/double resistance are illustrative coefficient variations, not confidence bounds.','',
          '| Front pitch (mm) | Allocation | Actual depth (m) | Flow at 0.5× loss (kg/s) | Flow at 1× (kg/s) | Flow at 2× (kg/s) |','|---:|---|---:|---:|---:|---:|']
        for pitch in [.01,.02,.03]:
            for fixed in [False,True]:
                if pitch==.01 and fixed:continue
                x=copy.deepcopy(base['inputs']);x['design']['stage_pitch_m'][0]=pitch
                if fixed:x['design']['rack_depth_m'][0]*=(pitch/.01)**2
                d,c=read_config(x);g=compile_hardware(d,c)['geometry'][0];ff=[]
                for factor in [.5,1.,2.]:
                    f,*_=pump_flow(h['pressure_Pa'][i][0],h['gas_K'][i][0],h['pressure_Pa'][i][1],float(Y@th.R),Y,g,d.suction_m3_s[0],d.head_J_kg[0],d.motor_MW[0]*1e6,c.eta_motor,c.eta_compressor,th,d.cutoff_Pa,factor);ff.append(f)
                label='fixed metal' if fixed else 'fixed envelope'
                lines.append(f'| {pitch*1000:g} | {label} | {g["rack_depth_m"]:.2f} | '+ ' | '.join(f'{f:.2f}' for f in ff)+' |')
                screen.append(dict(pitch_m=pitch,allocation=label,geometry=g,flows_kg_s=ff))
        (folder/'local_hydraulic_screen.json').write_text(json.dumps(screen,indent=2)+'\n')
    resolution_path=folder/'gas_resolution.json'
    if resolution_path.exists() or resolution_path.with_suffix('.json.gz').exists():
        rr=read_result(resolution_path);ref=cases['gas_smaller_plant']
        lines+=['','## Resolution check','',f'The reduced-plant gas case was repeated with max step {rr["inputs"]["design"]["max_step_s"]:g} s, relative tolerance {rr["inputs"]["design"]["rtol"]:g}, and Jacobian differencing step {rr["inputs"]["design"]["jacobian_relative_step"]:g}. Feasible: {rr["feasible"]}. Net-product change: {rr["net_liquid_kg"]-ref["net_liquid_kg"]:.4f} kg; diagnostic payoff change: {rr["diagnostic_payoff_days"]-ref["diagnostic_payoff_days"]:.4f} days. Only numerical settings change; hardware and physical coefficients are identical.','',
        'Reproduce from the complete `inputs` object in `results/transient/feed_pitch/gas_resolution.json.gz` (or the uncompressed CLI output). Two additional attempts at rtol=1e-5 (Jacobian steps 1e-6 and 1e-4) were stopped while making negligible time progress at small gas inventory. They are unresolved numerical trials, not physically rejected designs. The completed check halves the maximum time step at unchanged rtol; stronger tolerance-convergence evidence remains future work.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    r=cases.get('gas_smaller_plant',cases['gas_reference']);hw=r['hardware']
    manifest=dict(status='concept envelopes; reduced-plant gas reference when available; rack resistance disabled in this reference',inputs=r['inputs'],hull=dict(length_m=hw['length_m'],outside_m=hw['outside_m'],bore_m=30),chambers=hw['geometry'],compressor_banks=hw['banks'],coast_banks=hw['coast_banks'],gas_reserve=hw['gas_system'],packages_m3=hw['packages_m3'],bay_m=hw['bay_m'],flow_paths=['inlet -> rack0 -> compressor0 -> rack1 -> compressor1 -> rack2 -> compressor2 -> rack3 -> compressor3 -> receiver rack -> coast train','coast train -> product plant -> liquid tanks','coast train -> gas booster/aftercooler -> reserve spheres -> regulator -> thrusters','reserve jackets / aftercooler -> existing warm loop'])
    (folder/'geometry.json').write_text(json.dumps(manifest,indent=2)+'\n')
    fig,ax=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
    t=np.array(r['time_s'])/60;h=r['history']
    ax[0,0].plot(t,np.array(h['buffer_kg'])/1000);ax[0,0].set_ylabel('Propellant gas (tonnes)')
    ax[0,1].plot(t,np.array(h['buffer_Pa'])/1e5);ax[0,1].set_ylabel('Reserve pressure (bar)')
    ax[1,0].plot(t,h['gas_fill_kg_s'],label='Gas reserve refill');ax[1,0].plot(t,h['liquefaction_kg_s'],label='Liquid production');ax[1,0].set_ylabel('Coast flow (kg/s)');ax[1,0].legend()
    for name in ['layout_only','dense_rack','wide','joint_dense']:
        if name in cases:
            a=cases[name];ax[1,1].plot(np.array(a['time_s'])/60,np.array(a['history']['pump_kg_s'])[:,0],label=name)
    ax[1,1].set_xlim(-3,5);ax[1,1].set_ylabel('First-block flow (kg/s)');ax[1,1].legend(fontsize=8)
    for a in ax.flat:a.set_xlabel('Minutes from perigee');a.grid(alpha=.25)
    fig.savefig('docs/images/feed_pitch_histories.png',dpi=160);plt.close(fig)
    (folder/'audits.json').write_text(json.dumps({n:{k:r[k] for k in ['audits','closure','thermodynamic_audit']} for n,r in cases.items()},indent=2)+'\n')
if __name__=='__main__':main()
