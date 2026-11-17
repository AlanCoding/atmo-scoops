"""Plot atmospheric timing, selected allocation, and transient histories."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-chamber-opt-mpl')
import numpy as np
from scipy.integrate import cumulative_trapezoid
from ..orbit import Orbit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/chamber_optimization';OUT=ROOT/'investigations/chamber_transient'
def read(n):return json.loads((DATA/f'{n}.json').read_text())
def main():
 OUT.mkdir(exist_ok=True,parents=True);r=read('best');base=read('baseline_refined');a=read('best_proxy');b=read('baseline_refined_proxy');rows=read('search')
 incident=np.trapezoid(r['boundary']['supply_kg_s'],r['boundary']['time_s'])
 t=np.array(r['time_s'])/60;names=[c['name'] for c in r['inputs']['chambers']];colors=plt.cm.tab10(np.arange(len(names)))
 forcing=r['boundary'];bt=np.array(forcing['time_s']);s=np.array(forcing['supply_kg_s']);column=cumulative_trapezoid(s,bt,initial=0);lo,hi=np.interp([.05,.95],column/column[-1],bt)
 fig,ax=plt.subplots(figsize=(9,3.8));ax.plot(bt/60,s,label='Incident mass rate',lw=2);ax.axvspan(lo/60,hi/60,alpha=.14,color='tab:blue',label='90% of incident column')
 ax.axvline(0,color='.4',lw=.8);ax.set(xlim=(-6,6),xlabel='Minutes from perigee',ylabel='Incident air (kg/s)',title='The useful atmospheric pass is concentrated near perigee');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'optimized_atmosphere.png',dpi=170);plt.close(fig)
 for fname,lim in [('optimized_pass',(-3,10)),('optimized_coast',(-3,40))]:
  fig,axes=plt.subplots(3,2,figsize=(12,10),sharex=True)
  for ax,(key,label,log) in zip(axes.flat,[('pressure_Pa','Pressure (Pa)',True),('gas_temperature_K','Gas temperature (K)',False),('density_kg_m3','Density (kg/m³)',True),('metal_temperature_K','Metal temperature (K)',False),('gas_mass_kg','Inventory (kg)',True)]):
   for i,n in enumerate(names):
    y=np.array(r[key],dtype=float)[:,i]
    if log:y=np.where(y>1e-8,y,np.nan)
    ax.plot(t,y,label=n,color=colors[i])
   if log:ax.set_yscale('log')
   ax.set_ylabel(label)
  ax=axes.flat[-1]
  for i,n in enumerate(names):ax.plot(t,np.array([d['gas_to_metal_W'] for d in r['diagnostics']])[:,i]/1e6,color=colors[i])
  ax.set_yscale('symlog',linthresh=.01);ax.set_ylabel('Gas → metal heat (MW)')
  for ax in axes.flat:ax.axvspan(lo/60,hi/60,alpha=.07,color='grey');ax.axvline(0,color='.5',lw=.7);ax.axvline(10,color='.5',ls='--',lw=.7);ax.set_xlim(*lim);ax.grid(alpha=.15)
  for ax in axes[-1]:ax.set_xlabel('Minutes from perigee')
  handles,ll=axes[0,0].get_legend_handles_labels();fig.legend(handles,ll,ncol=5,loc='upper center',bbox_to_anchor=(.5,.95));fig.suptitle('Best sampled allocation — constrained transient mass proxy',fontsize=14)
  fig.text(.5,.01,'Grey band: 90% of incident column. Dashed line: coast withdrawal begins. No external radiation during this trace.',ha='center',fontsize=9)
  fig.tight_layout(rect=(0,.025,1,.92));fig.savefig(OUT/f'{fname}.png',dpi=170);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(11,4.8))
 x=np.arange(5);width=.34
 for off,rr,label in [(-width/2,base,'Baseline'),(width/2,r,'Selected')]:
  full=np.array([c['depth_m'] for c in rr['inputs']['chambers']]);rack=np.array([c['rack_depth_m'] for c in rr['inputs']['chambers']])
  axes[0].bar(x+off,rack,width,label=label+' rack');axes[0].bar(x+off,full-rack,width,bottom=rack,alpha=.35,label=label+' empty')
  axes[1].bar(x+off,[g['mass_kg']/1000 for g in rr['geometry']],width,label=label)
 for ax in axes:ax.set_xticks(x,names,rotation=25,ha='right');ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
 axes[0].set_ylabel('Physical depth (m)');axes[1].set_ylabel('Metal mass (tonnes)');fig.suptitle('Independent chamber and rack allocation');fig.tight_layout();fig.savefig(OUT/'optimized_allocation.png',dpi=170);plt.close(fig)
 text=f'''# Constrained transient allocation investigation

**Best sampled layout: {a['proxy_days']:.1f} proxy days, versus {b['proxy_days']:.1f}
for the matched baseline ({100*(1-a['proxy_days']/b['proxy_days']):.2f}% improvement).**
This is an explicitly approximate mass/product proxy, not the primary model's
payoff or proof of a global optimum. It is useful for ranking allocations within
the declared hardware/control assumptions. No circular-apogee delivery is charged.

## Atmospheric timing

Integration starts ten minutes before perigee, with atmospheric forcing extended
to cover that start. **90% of the incident column lies between {lo:.0f} and
{hi:.0f} seconds from perigee.** The graphs emphasize this interval, not the long
nearly empty approach. There is no sudden entry switch at 200 km inside this window; the numerical
forcing is set to zero outside its ±600 s tabulation.

![Atmospheric pass](optimized_atmosphere.png)

## Allocations

All chambers have 30 m bore; wires have 1 mm radius, 10 mm pitch and 298 K initial
temperature. Rack-envelope depth and additional empty depth are independent for
each chamber. Metal occupies only 3.14% of the rack envelope; its pores remain
part of the gas volume. Fixed compressor capacities and head limits are unchanged.

| Chamber | Baseline depth, m | Selected depth, m | Selected rack depth, m | Selected empty depth, m | Baseline metal, t | Selected metal, t |
|---|---:|---:|---:|---:|---:|---:|
'''
 for cb,c,gb,g in zip(base['inputs']['chambers'],r['inputs']['chambers'],base['geometry'],r['geometry']):text+=f"| {c['name']} | {cb['depth_m']:.3f} | {c['depth_m']:.3f} | {c['rack_depth_m']:.3f} | {c['depth_m']-c['rack_depth_m']:.3f} | {gb['mass_kg']/1000:.2f} | {g['mass_kg']/1000:.2f} |\n"
 text+='\n![Allocation comparison](optimized_allocation.png)\n\n'
 text+=f'''Selected total metal is **{a['metal_kg']/1000:,.1f} tonnes**, versus
**{b['metal_kg']/1000:,.1f} tonnes** initially. Proxy dry mass is
**{a['proxy_dry_kg']/1000:,.0f} tonnes**, versus **{b['proxy_dry_kg']/1000:,.0f} tonnes**.
Useful batch after propulsion and counted purge is **{a['net_product_kg']:,.0f} kg**,
versus **{b['net_product_kg']:,.0f} kg**. These proxy batches include the remaining
receiver gas that the completion allowance assumes will be processed later.

Admitted air increases from **{base['ledger']['admitted_kg'][-1]:,.0f} to
{r['ledger']['admitted_kg'][-1]:,.0f} kg**, out of **{incident:,.0f} kg** crossing
the geometric mouth column. Peak front gas temperature falls from
**{np.nanmax(np.array(base['gas_temperature_K'],dtype=float)[:,0]):.0f} K to
{np.nanmax(np.array(r['gas_temperature_K'],dtype=float)[:,0]):.0f} K**. In this
fixed-hardware scenario, added upstream cooling recovers almost the entire column.
The retained product gain outweighs the extra metal and deployment mass.

Zero additional empty depth is a lumped-volume result, not a demonstrated
shock/diffuser clearance or literal placement of wires at the mouth. Intermediate
buffer space could have different value with adjustable compressor coast schedules.

## Pressure and temperature histories

![Selected pass histories](optimized_pass.png)

![Selected coast histories](optimized_coast.png)

Racks remain thermally coupled to gas throughout the plotted history. They do not
radiate externally during that history. The proxy subsequently charges a separate
finish-draining, purge, deployment, radiative-reset and retraction allowance. This
does not claim simultaneous gas contact and external deployment of the same rack.

| Chamber | Peak pressure, kPa | Peak metal temperature, K | Gas at +40 min, K |
|---|---:|---:|---:|
'''
 for i,c in enumerate(r['inputs']['chambers']):
  temp=r['gas_temperature_K'][-1][i]
  text+=f"| {c['name']} | {np.array(r['pressure_Pa'])[:,i].max()/1000:.3f} | {np.array(r['metal_temperature_K'])[:,i].max():.1f} | {temp if temp is None else round(temp,1)} |\n"
 text+=f"\nRequired motor uprating adds {a['motor_uprating_kg']/1000:.2f} tonnes to the selected layout ({b['motor_uprating_kg']/1000:.2f} tonnes to the matched baseline), plus packing and design margin. The final stage needs the uprating; reference motor power is not treated as unlimited.\n"
 text+='''
## Proxy and constraints

The [complete equations and assumptions](../../modeling/chambers/OPTIMIZATION.md)
identify every fixed and variable charge. Fixed hardware comes from the existing
solid-rack optimized-Isp case. Recomputed items include metal, deployment,
shell/pressure-vessel allowances, stage-specific motor uprating, changes in compressor electrical energy and a
speculative 10 kg/MJ hot-feed handling surcharge. Most installed hardware is held
fixed, so this is a deliberately limited layout comparison.

All cases use 2 kg/s nominal coast withdrawal, with a plant-throughputput allowance.
The earlier 1.5 kg/s visual demonstration did not leave enough reset time under
this conservative completion schedule. Count purge and propellant losses in useful
product. Impose rack fit, L/D ≤10 including accounted equipment volume, pressure
≤110 kPa, metal ≤1042 K, supported gas temperatures, positive useful batch,
cycle-completion time, and mass/energy audits.

| Constraint margin | Selected value |
|---|---:|
'''
 for k,v in a['margins'].items():text+=f'| {k} | {v:.5g} |\n'
 valid=[x for x in rows if x['feasible']];timeouts=[x for x in rows if 'timeout' in x.get('error','')]
 text+=f'''\n## Search limits and sensitivity

The bounded pattern search evaluated **{len(rows)} distinct layouts**, of which
**{len(valid)} passed screening constraints**. **{len(timeouts)} trials hit a numerical
timeout**; those are unresolved, not physically impossible. Two initial layouts
were compared before local refinement over all ten coordinates. This does not
establish an ideal global breakdown. Bounds and all failures are saved.

The following re-scores the sampled feasible layouts at different handling-cost
weights; it does not redo the dynamics or perform independent full searches.

| Hot-feed handling coefficient, kg/MJ | Best sampled trial | Proxy days |
|---|---:|---:|
'''
 for w in (0,5,10,20):
  def score(z):return (z['proxy_dry_kg']+(w-10)*z['excess_feed_heat_MJ']*1.25)/z['net_product_kg']*Orbit(**r['experiment_config']['orbit']).period/86400
  v=min(valid,key=score);text+=f"| {w} | {v['id']} | {score(v):.2f} |\n"
 text+='\n| Fixed hardware multiplier | Best sampled trial | Proxy days |\n|---|---:|---:|\n'
 for factor in (.5,1.,2.):
  def fixedscore(z):return (z['proxy_dry_kg']+(factor-1)*z['fixed_hardware_kg']*1.25)/z['net_product_kg']*Orbit(**r['experiment_config']['orbit']).period/86400
  z=min(valid,key=fixedscore);text+=f"| {factor:g} | {z['id']} | {fixedscore(z):.2f} |\n"
 verification=read('verification')
 text+=f"\nAt 1 s maximum step / 5e-7 tolerance, final receiver inventory changes by {verification['relative_final_receiver_mass_change']:.6%} and gas temperature by {verification['final_receiver_temperature_change_K']:.4f} K. The selected design still passes constraints.\n\nTwo timed-out front-depth cases were retried at tighter settings:\n\n| Trial | Refined proxy days | Feasible |\n|---|---:|---|\n"
 for rr in verification['retried']:
  text+=f"| {rr['id']} | {rr.get('proxy_days',float('nan')):.2f} | {rr.get('feasible',False)} |\n"
 text+='\nBoth resolved retries are worse than the selected design; the other screening timeouts remain unresolved.\n'
 text+='''
Screening used 8 s maximum step / 1e-4 relative tolerance; baseline and selected
histories above use 2 s / 2e-6. Numerical refinement must pass the same constraints.
The gas model is frozen-composition, temperature-dependent ideal gas; the low-flow
heat-transfer and compressor control laws remain provisional. Changing compressor
capacity, wire geometry, starting temperature, orbit or thermal-reset mechanism
can change the preferred allocation.

## Reproduce

```sh
.venv/bin/python -m atmo_scoops.studies.chamber_optimize
.venv/bin/python -m atmo_scoops.studies.chamber_optimization_validate
.venv/bin/python -m atmo_scoops.studies.chamber_optimization_report
.venv/bin/python -m atmo_scoops.chambers --config configs/chamber_transient_optimized.json --output results/chamber_optimization/replay.json
```

Full trial coordinates, proxy terms, constraint margins and selected histories are
in `results/chamber_optimization/`. The editable selected configuration is
`configs/chamber_transient_optimized.json`. This search is not wired into the main
payoff optimizer.
'''
 (OUT/'OPTIMIZATION.md').write_text(text)
if __name__=='__main__':main()
