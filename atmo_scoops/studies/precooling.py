"""Report a matched-input gas-temperature / metal-capacity sensitivity."""
import json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    data=json.loads(Path('results/precooling_trade.json').read_text())
    runs=data['runs'];base=min(runs,key=lambda r:abs(r['inputs']['design']['compressor_inlet_K']-1000))
    d=base['inputs']['design'];b=base['outputs']
    baseline_T=d['compressor_inlet_K']
    lines=[f'''# Precooling: metal rack versus compressor mass

This is a one-variable sweep of compressor inlet gas temperature, with the
current two-compartment architecture and all other input choices held fixed.
Physical front/rear depths are {d['front_depth_m']:.0f}/{d['rear_depth_m']:.0f} m,
with {d['front_diameter_m']:.1f} m front diameter. **The {d['front_depth_m']:.0f} m comparison depth is not
an optimized choice.** No temperature row is a validated spacecraft optimum.

Metal starts at **{d['metal_cold_K']:.0f} K**. The chosen minimum gas-to-metal
approach is **{d['gas_metal_approach_K']:.0f} K**, so:

    metal hot endpoint = compressor inlet temperature - approach
    metal heat capacity per kg = integral Cp(T) over the metal temperature swing
    metal mass = net absorber heat / capacity per kg

Cooling to a lower gas endpoint requires a lower metal hot endpoint. A warmer
passive rack cannot supply a colder outlet at the end of the encounter. This is
a uniform-rack endpoint screen; a distributed or thermally stratified rack could
have a different temperature profile and must be modeled explicitly.

Compressor suction capacity scales approximately with gas temperature at the
same pressure target. Its mass follows the same explicit installed-capacity
coefficient in every row: {base['inputs']['hardware']['compressor_kg_per_m3_s']:g} kg/(m³/s). Efficiency is held fixed across the sweep,
which is a requirement for future pump development, not a verified pump map.

| Compressor inlet | Metal hot endpoint | Metal capacity | Metal mass | Compressor mass | Metal deployment mass | Total dry mass | Net product/cycle |
|---:|---:|---:|---:|---:|---:|---:|---:|''']
    for run in runs:
        o=run['outputs'];T=run['inputs']['design']['compressor_inlet_K']
        lines.append(f"| {T:.0f} K | {o['metal_hot_K']:.0f} K | {o['metal_capacity_kJ_kg']:.1f} kJ/kg | {o['masses_kg']['hot_metal']/1000:.2f} t | {o['compressor_mass_kg']/1000:.2f} t | {o['masses_kg']['hot_sheet_deployment']/1000:.2f} t | {o['total_dry_kg']/1000:,.2f} t | {o['net_liquid_equivalent_kg']:.2f} kg |")
    best=min(runs,key=lambda x:x['outputs']['total_dry_kg'])
    o=best['outputs'];T=best['inputs']['design']['compressor_inlet_K']
    lines.append(f'''
The lowest sampled total is **{T:.0f} K**, at **{o['total_dry_kg']/1000:,.1f} t**.
Compared with {baseline_T:,.0f} K, compressor mass decreases by
**{(b['compressor_mass_kg']-o['compressor_mass_kg'])/1000:.1f} t**, while metal increases by
**{(o['masses_kg']['hot_metal']-b['masses_kg']['hot_metal'])/1000:.1f} t** and its deployment
allowance increases by **{(o['masses_kg']['hot_sheet_deployment']-b['masses_kg']['hot_sheet_deployment'])/1000:.1f} t**.
The full mass ledger, including all other duty changes and margin, decreases by
**{(b['total_dry_kg']-o['total_dry_kg'])/1000:.1f} t**.

As gas temperature approaches the cold-metal-plus-approach limit, the metal's
usable temperature swing shrinks and its required mass rises steeply. The model
rejects {d['metal_cold_K']+d['gas_metal_approach_K']:.0f} K and below with these fixed cold/approach inputs:
there would be no positive metal temperature swing.

The rack absorbs approximately the same few gigajoules throughout. Lower inlet
gas temperature removes more initial gas heat but also reduces hot-compressor
work and associated heat. The dominant metal penalty here is **less thermal
capacity per kilogram**, not a large increase in atmospheric energy.

## Deployed areas and duties

| Gas inlet | Solar panels | Warm radiator panels (two faces) | Metal sheets (two faces) | Compressor electricity | Net absorber heat |
|---:|---:|---:|---:|---:|---:|''')
    for run in runs:
        o=run['outputs'];T=run['inputs']['design']['compressor_inlet_K']
        lines.append(f"| {T:.0f} K | {o['solar_area_m2']:,.0f} m² | {o['warm_radiator_panel_m2']:,.0f} m² | {o['metal_panel_m2']:,.0f} m² | {o['compressor_kWh']:.1f} kWh/pass | {o['hot_absorbed_GJ']:.3f} GJ |")
    lines.append('''
All cases retain the same orbit, opening/closure rule and presumed intake.
Small net-output differences come from gas left in the front chamber under the
same 90% recovery rule. Capture is not revalidated at each temperature.

The temperature/port-area/oxygen/radiation screens pass for these rows. Missing
constraints include actual gas-to-metal conductance, flow/rack pressure loss,
shock position, available pump maps and structural/deployment design. These can
move or remove the apparent minimum. Changing cold metal temperature, approach,
material properties or compressor mass target also changes the result; the
input file permits those capability/design sensitivities explicitly.

Metal heat capacities use [NIST solid iron properties](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896&Mask=2&Units=SI).
The 100 K approach and mass coefficients are chosen engineering targets.

Reproduce:

```sh
.venv/bin/python -m atmo_scoops --config configs/reference.json --sweep-precooling 650 700 750 800 900 1000 1100 --output results/precooling_trade.json
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.precooling
```

![Matched-input precooling trade](../../figures/precooling_trade.png)
''')
    Path('analysis/primary/PRECOOLING_TRADE.md').write_text('\n'.join(lines)+'\n')
    temp=[x['inputs']['design']['compressor_inlet_K'] for x in runs]
    fig,ax=plt.subplots(1,2,figsize=(12,5))
    for key,label in [('compressor_mass_kg','Compressors'),('metal','Metal + deployment')]:
        y=[(x['outputs']['compressor_mass_kg'] if key=='compressor_mass_kg' else
            x['outputs']['masses_kg']['hot_metal']+x['outputs']['masses_kg']['hot_sheet_deployment'])/1000 for x in runs]
        ax[0].plot(temp,y,'-o',label=label)
    ax[0].legend();ax[0].set(ylabel='Installed mass (tonnes)',title='Colder gas: smaller pumps, more metal')
    ax[1].plot(temp,[x['outputs']['total_dry_kg']/1000 for x in runs],'-o',color='#185e74')
    ax[1].set(ylabel='Total dry mass including margin (tonnes)',title=f"Lowest sampled total near {best['inputs']['design']['compressor_inlet_K']:.0f} K")
    for a in ax:
        a.set_xlabel('Compressor inlet gas temperature (K)');a.grid(alpha=.2)
    fig.suptitle(f"Precooling trade • metal starts at {d['metal_cold_K']:.0f} K • {d['gas_metal_approach_K']:.0f} K gas/metal approach")
    fig.text(.5,.015,f"{d['front_depth_m']:.0f} m front / {d['rear_depth_m']:.0f} m rear comparison; fixed capability targets; exchanger and shock constraints remain unresolved.",ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.94))
    for ext in ('png','svg'):fig.savefig(f'figures/precooling_trade.{ext}',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
