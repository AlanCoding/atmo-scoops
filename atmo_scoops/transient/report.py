"""Render current coupled-cycle results and exact numerical tables."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .search import summary
from .validate import check
from .io import read_result

ROOT=Path('results/transient');DOC=Path('investigations/transient')

def main():
    DOC.mkdir(parents=True,exist_ok=True)
    reference=json.loads((ROOT/'reference.json').read_text());rows=[dict(label='Reference',path=ROOT/'reference.json',**summary(reference))]
    for name in ('search','sizing'):
        path=ROOT/name/'comparison.json'
        if path.exists():
            for row in json.loads(path.read_text()):rows.append(dict(label=f'{name} {row["case"]}',path=ROOT/name/f'cycle_{row["case"]}.json',**row))
    feasible=[r for r in rows if r['feasible']];best=min(feasible,key=lambda r:r['operating_payoff_days'])
    r=read_result(best['path']);audit=check(r)
    if not audit['low_density_chamber_EOS_screen_passed']:raise ValueError('Selected trajectory failed independent property audit')
    (ROOT/'best.json').write_text(json.dumps(r,allow_nan=False)+'\n');(ROOT/'best_config.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
    (ROOT/'best.validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    t=np.array(r['time_s'])/60;h=r['history'];colors=plt.cm.viridis(np.linspace(.05,.9,5));labels=['Front SiC','Al 1','Al 2','Al 3','Receiver Al']
    fig,axes=plt.subplots(4,2,figsize=(13,14),sharex=True,constrained_layout=True)
    mass=np.array(r['gas_species_kg']).sum(axis=2);vol=np.array([g['gas_m3'] for g in r['hardware']['geometry']])
    for i in range(5):
        for ax,key,title in [(axes[0,0],'pressure_Pa','Gas pressure (Pa)'),(axes[0,1],'gas_K','Gas temperature (K)'),(axes[1,0],'rack_K','Rack temperature (K)')]:
            values=np.asarray(h[key])[:,i].copy()
            if key!='rack_K':values[mass[:,i]<.01]=np.nan
            ax.plot(t,values,color=colors[i],label=labels[i],lw=1.3);ax.set_title(title)
        axes[1,1].plot(t,np.where(mass[:,i]>.01,mass[:,i]/vol[i],np.nan),color=colors[i]);axes[1,1].set_title('Gas density (kg/m³)')
        axes[3,1].plot(t,mass[:,i],color=colors[i]);axes[3,1].set_title('Gas inventory (kg)')
    axes[0,0].set_yscale('log');axes[1,1].set_yscale('log');axes[0,0].legend(fontsize=8,ncol=2)
    for key,label in [('solar_MW','Available solar'),('load_MW','Electrical load'),('thrust_MW','Thrusters')]:axes[2,0].plot(t,h[key],label=label)
    axes[2,0].set_title('Electrical power (MW)');axes[2,0].legend(fontsize=8)
    axes[2,1].plot(t,h['SOC'],color='tab:blue',label='Battery SOC');axes[2,1].set_title('Battery reserve / warm-store temperature');axes[2,1].set_ylim(0,1)
    twin=axes[2,1].twinx();twin.plot(t,h['warm_K'],color='tab:red');twin.set_ylabel('Warm store (K)',color='tab:red')
    liquid=np.asarray(r['liquid_species_kg'])
    for i,label in enumerate(('LN₂','LOX','Liquid Ar')):axes[3,0].plot(t,liquid[:,i],label=label)
    axes[3,0].set_title('Liquid inventory, including initial reserve (kg)');axes[3,0].legend(fontsize=8)
    for ax in axes.flat:ax.axvline(0,color='black',lw=.6);ax.grid(alpha=.2);ax.set_xlim(t[0],t[-1])
    for ax in axes[-1]:ax.set_xlabel('Minutes from perigee')
    fig.suptitle(f'Coupled cycle: {best["label"]} — {r["operating_payoff_days"]:.1f} days operating-orbit payoff\nFixed hardware; one forward integration; not a global optimum',fontsize=14)
    fig.savefig(DOC/'cycle.png',dpi=150);plt.close(fig)
    items=sorted(r['hardware']['masses_kg'].items(),key=lambda x:x[1]);fig,ax=plt.subplots(figsize=(10,7),layout='constrained');ax.barh([k.replace('_',' ') for k,v in items],[v/1000 for k,v in items]);ax.set_xlabel('Dry mass (tonnes)');ax.set_title(f'Coupled reference mass: {r["dry_kg"]/1000:,.0f} tonnes');fig.savefig(DOC/'mass.png',dpi=150);plt.close(fig)
    lines=['# Coupled-cycle numerical results','', 'Generated with `python -m atmo_scoops.transient.report`. Payoff is in the operating orbit; circular-apogee delivery is not included. Feasible means the declared reduced-model constraints pass, not that hardware is qualified.','', '| Case | Isp (s) | Burn (min) | Dry mass (t) | Net liquid/orbit (kg) | Payoff (days) | Accepted? |','|---|---:|---:|---:|---:|---:|---|']
    rejected=[]
    for a in rows:
        d=a['inputs']['design'];value=a.get('operating_payoff_days');pay=f'{value:.2f}' if value else '—'
        lines.append(f'| {a["label"]} | {d["isp_s"]:.0f} | {d["burn_s"]/60:.2f} | — | — | — | Unresolved |' if a.get('error') else f'| {a["label"]} | {d["isp_s"]:.0f} | {d["burn_s"]/60:.2f} | {a["dry_kg"]/1000:,.0f} | {a["net_liquid_kg"]:,.1f} | {pay} | {a["feasible"]} |')
        if not a['feasible']:rejected.extend(['',f'{a["label"]} rejected: '+str(a.get('error') or {k:v for k,v in a.get('margins',{}).items() if v<0})+'.',''])
    lines+=rejected
    d=r['inputs']['design'];hw=r['hardware'];s=summary(r)
    lines+=['',f'## Best tested case: {best["label"]}','',f'**{r["operating_payoff_days"]:.2f} days**, {r["dry_kg"]/1000:,.1f} t dry, {r["net_liquid_kg"]:,.1f} kg net liquid per { (hw["end_s"]-hw["start_s"])/60:.2f}-minute orbit. This is the best tested candidate, not a converged all-variable optimum.','',f'Admission {s["admitted_kg"]:,.2f} kg; gross liquid {s["gross_liquid_kg"]:,.2f} kg; propulsion {s["propellant_kg"]:,.2f} kg; total leaked/vented {s["lost_kg"]:,.2f} kg. Initial liquid reserve is restored before surplus counts.','',f'Physical chamber depths, front to receiver: **'+', '.join(f'{g["depth_m"]:.2f} m' for g in hw['geometry'])+f'**. Equipment bay {hw["bay_m"]:.2f} m; total 317 m.','',f'Solar {d["solar_area_m2"]:,.0f} m²; warm radiator {d["warm_radiator_m2"]:,.0f} m² physical / {2*d["warm_radiator_m2"]:,.0f} m² emitting; metal-rack footprint {sum(g["deployed_physical_m2"] for g in hw["geometry"]):,.0f} m². Motion at 10 m/s is included.','',f'Battery {d["battery_MWh"]:.1f} MWh; bus {d["bus_MW"]:.1f} MW; thrust {hw["thrust_W"]/1e6:.1f} MW. Finite-burn impulse penalty {hw["arc"]["impulse_multiplier"]:.5f}.','', '![Cycle histories](cycle.png)','', '![Dry mass breakdown](mass.png)','', '| Component | Dry mass (t) |','|---|---:|']
    lines += [f'| {k.replace("_"," ")} | {v/1000:,.2f} |' for k,v in reversed(items)]
    lines+=['','## Numerical checks','',f'Maximum species-ledger error {r["audits"]["species_kg"]:.3g} kg; energy-ledger error {r["audits"]["energy_MJ"]:.3g} MJ. One forward integration.','',f'Largest rack endpoint enthalpy discrepancy {max(abs(z) for z in r["closure"]["rack_enthalpy_J_kg"]):.3g} J/kg; battery discrepancy {r["closure"]["battery_MJ"]:.3g} MJ; warm store {r["closure"]["warm_MJ"]:.3g} MJ.','',f'Independent HEOS audit: maximum |Z−1| {audit["max_abs_Z_minus_one"]:.3g}; compressor-work difference {audit["max_compressor_work_relative_error"]:.3g} relative. Maximum checked compressor discharge temperature {audit["max_audited_compressor_outlet_K"]:.1f} K.','',f'Unresolved exospheric incident tail {hw["unresolved_exospheric_incident_kg"]:.4f} kg/pass (momentum still charged).','', 'Inputs: `results/transient/best_config.json`; complete trajectory: `results/transient/best.json`. Read the [implementation limits](../../modeling/primary/TRANSIENT_IMPLEMENTATION.md) before interpreting these engineering estimates.']
    (DOC/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(case=best['label'],payoff_days=r['operating_payoff_days'],dry_t=r['dry_kg']/1000,net_kg=r['net_liquid_kg']),indent=2))

if __name__=='__main__':main()
