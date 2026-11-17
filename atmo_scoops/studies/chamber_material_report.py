"""Report saved material-allocation searches and reset sensitivity."""
from pathlib import Path
import json,os,copy
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-material-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..chambers.proxy import evaluate
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/chamber_materials';OUT=ROOT/'investigations/chamber_transient'
def main():
 summary=json.loads((DATA/'summary.json').read_text());settings=json.loads((DATA/'settings.json').read_text())
 anchor=json.loads((ROOT/settings['anchor']).read_text())
 results={k:json.loads((DATA/k/'best.json').read_text()) for k in summary}
 labels={'iron':'Iron throughout','fecral':'FeCrAl + aluminum','sic':'SiC + aluminum'}
 fig,axes=plt.subplots(1,3,figsize=(13,4.5))
 for i,(k,v) in enumerate(summary.items()):
  p=v['proxy'];axes[0].bar(i,p['proxy_days']);axes[0].text(i,p['proxy_days']+2,f"{p['proxy_days']:.1f}",ha='center')
  r=results[k];x=np.arange(5)+(i-1)*.25
  axes[1].bar(x,[g['mass_kg']/1000 for g in r['geometry']],.25,label=labels[k])
  depths=np.array([c['rack_depth_m'] for c in r['inputs']['chambers']]);total=np.array([c['depth_m'] for c in r['inputs']['chambers']])
  axes[2].bar(x,depths,.25,color=f'C{i}');axes[2].bar(x,total-depths,.25,bottom=depths,alpha=.25,color=f'C{i}')
 axes[0].set_xticks(range(3),[labels[k] for k in summary],rotation=20,ha='right');axes[0].set_ylabel('Operating-orbit proxy payoff (days)')
 for ax in axes[1:]:ax.set_xticks(range(5),['Front','Inter 1','Inter 2','Inter 3','Receiver'],rotation=20,ha='right')
 axes[1].set_ylabel('Rack mass (tonnes)');axes[1].legend(fontsize=8);axes[2].set_ylabel('Physical depth (m); pale = empty')
 for ax in axes:ax.grid(axis='y',alpha=.2)
 fig.suptitle('Material choice with independently reallocated racks and volumes');fig.tight_layout();fig.savefig(OUT/'materials_comparison.png',dpi=170);plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(13,7),sharex=True)
 colors=plt.cm.tab10(range(5))
 for col,(k,r) in enumerate(results.items()):
  t=np.array(r['time_s'])/60
  for i,c in enumerate(r['inputs']['chambers']):
   axes[0,col].plot(t,np.array(r['metal_temperature_K'])[:,i],color=colors[i],label=c['name'])
   axes[1,col].plot(t,np.array(r['pressure_Pa'])[:,i],color=colors[i])
  axes[0,col].set_title(labels[k]);axes[1,col].set_yscale('log');axes[1,col].set_xlabel('Minutes from perigee')
  for ax in axes[:,col]:ax.set_xlim(-3,40);ax.grid(alpha=.2)
 axes[0,0].set_ylabel('Rack temperature (K)');axes[1,0].set_ylabel('Pressure (Pa)');axes[0,0].legend(fontsize=8)
 fig.tight_layout();fig.savefig(OUT/'materials_histories.png',dpi=170);plt.close(fig)
 text='''# Per-rack materials and allocation

This investigation reruns the **isolated transient mass/product proxy**, not the
primary payoff optimizer. It compares iron throughout with FeCrAl or SiC in front
and aluminum in all four downstream racks. Payoff ends in the operating orbit;
circular-apogee delivery remains uncharged. These are best sampled local layouts,
not global optima or qualified hardware.

## Comparison

| Materials | Proxy days | Proxy dry mass, t | Rack mass, t | Net useful batch, kg | Reset allowance used, min |
|---|---:|---:|---:|---:|---:|
'''
 for k,v in summary.items():
  p=v['proxy'];text+=f"| {labels[k]} | {p['proxy_days']:.2f} | {p['proxy_dry_kg']/1000:.1f} | {p['metal_kg']/1000:.1f} | {p['net_product_kg']:.1f} | {p['estimated_reset_s']/60:.1f} |\n"
 text+='\n![Payoff, rack mass and physical allocation](materials_comparison.png)\n\n'
 from ..orbit import Orbit
 period=Orbit(**results['iron']['experiment_config']['orbit']).period
 text+='| Case | Improvement versus refreshed iron | Extra material-specific hardware that erases advantage, t (before margin) |\n|---|---:|---:|\n'
 for k in ('fecral','sic'):
  p=summary[k]['proxy'];control=summary['iron']['proxy']['proxy_days']
  allowance=(control*p['net_product_kg']*86400/period-p['proxy_dry_kg'])/1.25/1000
  text+=f"| {labels[k]} | {100*(1-p['proxy_days']/control):.2f}% | {allowance:.1f} |\n"
 text+='\nThis allowance holds dynamics fixed and applies the existing 25% design margin. It is a sensitivity, not a support-mass prediction.\n\n'
 text+='''The main finding is a large rack-mass change with a modest whole-craft effect.
SiC/aluminum reduces rack mass by about 47%, but most hardware remains unchanged.
Its larger front rack adds deployment area, partly offsetting the material saving.
The SiC front is 5.42 m deep versus 3.97 m for iron, despite weighing much less.
Its front radiative cooldown is about 9.4 minutes versus 13.7 for iron under the
assumed surfaces. The FeCrAl/aluminum payoff difference is too small to establish
an engineering preference. Its downstream aluminum also approaches the provisional
550 K cap; a selected alloy and support design could change that allocation.

The previous isolated optimum was about 381 days. The refreshed iron search
itself improves that to 379; only the remaining difference is attributed here
to material choice. No comparison to the separate primary-model 371-day result
is implied.

'''


 text+='''Radius stays 1 mm, pitch 10 mm, bore 30 m and starting temperature 298 K.
Orbit, incident column, suction/head envelopes, withdrawal schedule, propulsion
and fixed hardware anchor are common. All five rack-envelope depths and five
additional empty depths are independently varied. Bounds: front rack 2–12 m,
three intermediate racks 0.015–0.8 m, receiver rack 0.015–1 m; empty depths 0–12 m
in the first four chambers and 2–100 m in the receiver. The former front bound
was 7 m; this search permits extra volume for lower volumetric heat capacity.
Each material case starts from the earlier selected geometry and a second seed
scaled to equal sensible heat capacity, then uses the same pattern search.

## Selected physical allocations

| Case | Chamber | Full depth, m | Rack depth, m | Rack mass, t | Displaced solid, m³ | Wetted area, m² | Peak rack K | Radiative cooldown, s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
'''
 for k,r in results.items():
  p=summary[k]['proxy'];tm=np.array(r['metal_temperature_K'])
  for i,(c,g) in enumerate(zip(r['inputs']['chambers'],r['geometry'])):
   text+=f"| {labels[k]} | {c['name']} | {c['depth_m']:.3f} | {c['rack_depth_m']:.3f} | {g['mass_kg']/1000:.2f} | {g['solid_m3']:.2f} | {g['wetted_m2']:.0f} | {tm[:,i].max():.1f} | {p['rack_cooldown_s'][i]:.1f} |\n"
 text+='''
Radiative cooldown is after gas processing, not concurrent external exposure of
racks inside pressurized chambers. The total reset allowance above includes
remaining drainage and deployment/retraction. Material energy, displaced volume,
gas-side transfer and material-specific cooldown are described in the
[property dossier](../../modeling/chambers/MATERIALS.md).

![Temperature and pressure histories](materials_histories.png)

## Surface sensitivity at fixed selected geometry

Aluminum and SiC nominal emissivity 0.8 is a surface capability assumption;
FeCrAl uses 0.7 from its oxidized-wire datasheet. The following changes the
post-pass radiative reset only. The histories have no external radiation, so a
new transient integration is unnecessary. No extra radiator or coating mass is
silently added to rescue a failing reset. These rows are not reoptimized.

| Case | Aluminum emissivity | SiC emissivity | Reset used, min | Reset margin, min | Feasible |
|---|---:|---:|---:|---:|---|
'''
 sensitivity=[]
 for k in ('fecral','sic'):
  for epsilon in (.8,.6,.4,.2):
   r=copy.deepcopy(results[k])
   for c in r['experiment_config']['chambers']:
    if c['material'] in ('sic','aluminum'):c['rack_emissivity']=epsilon
   p=evaluate(r,anchor,settings['reference_shaft_MJ'])
   sensitivity.append(dict(case=k,emissivity=epsilon,proxy=p))
   text+=f"| {labels[k]} | {epsilon} | {epsilon if k=='sic' else '—'} | {p['estimated_reset_s']/60:.1f} | {p['margins']['reset_time_s']/60:.1f} | {p['feasible']} |\n"
 (DATA/'surface_sensitivity.json').write_text(json.dumps(sensitivity,indent=2)+'\n')
 text+='''
## Numerical checks and interpretation limits

| Case | Screened layouts | Feasible | Numerical failures | Refined payoff change | Max Biot number |
|---|---:|---:|---:|---:|---:|
'''
 for k,v in summary.items():
  delta=v['verified_proxy']['proxy_days']-v['proxy']['proxy_days'];bi=.1-v['proxy']['margins']['lumped_Biot']
  text+=f"| {labels[k]} | {v['search_count']} | {v['feasible_count']} | {v['numerical_failures']} | {delta:+.4f} days | {bi:.5f} |\n"
 text+='''
Screening uses 8 s / 1e-4; selected cases use 2 s / 2e-6 and are verified at
1 s / 5e-7. Numerical timeouts remain unresolved, not physical rejections.
Property changes do not validate the common provisional low-pressure compressor
maps, well-mixed gas assumption or gas-to-wire correlation. Conductivity is
screened through Bi < 0.1; internal rod gradients are not resolved.

The mass proxy holds most installed hardware fixed, so savings are primarily
rack mass, deployment, thermal handling and changed retained product. It does
not completely redesign the booster, compressor bodies or plant. SiC needs a
credible segmented deployment/support design; aluminum needs a selected alloy
and durable emissive finish. Material-specific coating/support mass is not yet
modeled. No mesh pressure-drop or leading-edge survivability credit is inferred.

## Reproduce

```sh
.venv/bin/python -m atmo_scoops.studies.chamber_materials
.venv/bin/python -m atmo_scoops.studies.chamber_material_report
.venv/bin/python -m pytest -q
.venv/bin/python -m atmo_scoops.audit
```

Inputs, every search coordinate and failure, selected full histories, proxy ledgers
and tighter-resolution histories are in `results/chamber_materials/`. Each case's
`config.json` can be edited and run through `python -m atmo_scoops.chambers`.
'''
 (OUT/'MATERIALS.md').write_text(text)
if __name__=='__main__':main()
