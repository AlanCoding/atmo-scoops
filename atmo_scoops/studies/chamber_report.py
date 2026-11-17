"""Generate chamber histories and the receiver/coast comparison."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-chambers-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/chamber_transient';OUT=ROOT/'investigations/chamber_transient'
def read(name):return json.loads((DATA/f'{name}.json').read_text())
def at(r,key,t,i=-1):return float(np.interp(t,r['time_s'],np.array(r[key],dtype=float)[:,i]))
def main():
 OUT.mkdir(exist_ok=True,parents=True);r=read('reference');t=np.array(r['time_s'])/60
 names=[c['name'] for c in r['inputs']['chambers']];colors=plt.cm.tab10(np.arange(5))
 fields=[('pressure_Pa','Gas pressure (Pa)',True),('gas_temperature_K','Gas temperature (K)',False),('density_kg_m3','Gas density (kg/m³)',True),('metal_temperature_K','Metal temperature (K)',False),('gas_mass_kg','Gas mass (kg)',True)]
 for name,xlim in [('histories',(-440/60,40)),('encounter',(-3,10))]:
  fig,axes=plt.subplots(3,2,figsize=(13,10),sharex=True)
  for ax,(key,label,log) in zip(axes.flat,fields):
   a=np.array(r[key],dtype=float)
   for i in range(5):
    y=a[:,i].copy()
    if log:y[y<1e-8]=np.nan
    ax.plot(t,y,color=colors[i],label=names[i],lw=1.6)
   if log:ax.set_yscale('log')
   ax.set_ylabel(label)
  ax=axes.flat[-1];q=np.array([d['gas_to_metal_W'] for d in r['diagnostics']])/1e6
  for i in range(5):ax.plot(t,q[:,i],color=colors[i],lw=1.4)
  ax.set_yscale('symlog',linthresh=.01);ax.set_ylabel('Gas → metal heat (MW; signed)')
  for ax in axes.flat:
   ax.axvline(0,color='.4',lw=.8);ax.axvline(10,color='.4',ls='--',lw=.8);ax.set_xlim(*xlim);ax.grid(alpha=.2)
  for ax in axes[-1]:ax.set_xlabel('Minutes from perigee')
  handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=5,bbox_to_anchor=(.5,.96))
  fig.suptitle('Transient chamber experiment — racks remain inside; no external radiation',fontsize=14)
  fig.text(.5,.015,'Solid vertical line: perigee. Dashed: pumps stop and liquefaction withdrawal begins. Blank gas T: effectively empty volume.',ha='center',fontsize=9)
  fig.tight_layout(rect=(0,.035,1,.92));fig.savefig(OUT/f'{name}.png',dpi=170);plt.close(fig)
 comparisons={name:read(name) for name in ('reference','empty_receiver','no_withdrawal','contact_ends_180s')}
 labels={'reference':'Receiver rack + withdrawal','empty_receiver':'Empty receiver + withdrawal','no_withdrawal':'Receiver rack; no withdrawal','contact_ends_180s':'Thermal contact ends at +3 min'}
 fig,axes=plt.subplots(2,2,figsize=(11,7),sharex=True)
 for ax,key,label,scale in zip(axes.flat,['pressure_Pa','gas_temperature_K','gas_mass_kg','metal_temperature_K'],['Receiver pressure (kPa)','Receiver gas (K)','Receiver inventory (kg)','Receiver rack (K)'],[1e-3,1,1,1]):
  for name,rr in comparisons.items():
   if key=='metal_temperature_K' and name=='empty_receiver':continue
   ax.plot(np.array(rr['time_s'])/60,np.array(rr[key],dtype=float)[:,-1]*scale,label=labels[name])
  ax.axvline(10,color='.5',ls='--',lw=.8);ax.set_ylabel(label);ax.set_xlim(-3,40);ax.grid(alpha=.2)
 for ax in axes[-1]:ax.set_xlabel('Minutes from perigee')
 handles,ll=axes[0,0].get_legend_handles_labels();fig.legend(handles,ll,loc='upper center',ncol=2,bbox_to_anchor=(.5,.95),fontsize=9)
 fig.suptitle('Receiver rack, continued coast contact, and gas withdrawal')
 fig.tight_layout(rect=(0,0,1,.87));fig.savefig(OUT/'receiver_comparison.png',dpi=170);plt.close(fig)
 fine=read('refined');checks=dict(r['checks']);checks['relative_final_receiver_mass_change']=at(fine,'gas_mass_kg',2400)/at(r,'gas_mass_kg',2400)-1;checks['final_receiver_temperature_change_K']=at(fine,'gas_temperature_K',2400)-at(r,'gas_temperature_K',2400)
 (DATA/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
 text='''# Gas volumes and wire racks through the pass and coast

This is an isolated transient experiment, implemented in `atmo_scoops.chambers`.
It is not called by the primary payoff model or optimizer. Each chamber has its
own gas mass, internal energy and metal energy; compressor flows need not match.
Pressure, temperature and density are solved, not prescribed.

![All chamber histories](histories.png)

![Encounter detail](encounter.png)

## Experiment definition

85 × 2,000 km orbit, 30 m mouth/bore, reference atmosphere; time zero is perigee.
The run starts 440 seconds before perigee and ends 40 minutes afterward. All
racks initially start at 298 K. Flow capacities and maximum shaft head are drawn
from the solid-rack Isp reference, but the dynamic pump control is a new declared
screening law, not its old equal-flow compressor approximation.

The first four rack envelopes match that reference. A fifth rack, equal to the
last intermediate rack, is **added** to the 16 m receiver for this experiment.
This is not a mass-neutral redistribution or a new optimized spacecraft. The
empty-receiver control reaches about 188 kPa, above the primary design's 110 kPa
cap; structural limits are not enforced in this diagnostic experiment. There
is no forced 340 K aftercooler: gas in the receiver finds its own temperature.

| Volume | Physical depth, m | Rack envelope depth, m | Free gas volume, m³ | Metal, tonnes |
|---|---:|---:|---:|---:|
'''
 for c,g in zip(r['inputs']['chambers'],r['geometry']):text+=f"| {c['name']} | {c['depth_m']:.3f} | {c['rack_depth_m']:.3f} | {g['gas_m3']:,.1f} | {g['mass_kg']/1000:.2f} |\n"
 text+='''
Every rod has 1 mm radius and 10 mm pitch. Chamber depth and rack-filled depth
are independently editable, as are diameter, radius, pitch and initial gas/metal
states for every chamber. Rack-filled volume is mostly gas pore space.

Pumps stop at +600 s. Liquefaction withdrawal starts then, ramping its effective
flow toward 1.5 kg/s when receiver pressure is well above its 100 Pa floor.
The sink removes gas **and its enthalpy**. It does not calculate the cryoplant's
work, product yield or mass: this is its feed boundary, not free liquefaction.
The inlet remains open, with pressure-supported admission and reverse leakage.
Stopped compressor connections are assumed isolated by check valves.

## What happens in the receiver

![Receiver controls](receiver_comparison.png)

| Case | Gas at +10 min, K | Gas at +40 min, K | Pressure at +10 min, kPa | Pressure at +40 min, kPa | Gas remaining at +40 min, kg |
|---|---:|---:|---:|---:|---:|
'''
 for name,rr in comparisons.items():text+=f"| {labels[name]} | {at(rr,'gas_temperature_K',600):.1f} | {at(rr,'gas_temperature_K',2400):.1f} | {at(rr,'pressure_Pa',600)/1000:.2f} | {at(rr,'pressure_Pa',2400)/1000:.2f} | {at(rr,'gas_mass_kg',2400):,.0f} |\n"
 text+='''
The receiver rack absorbs compression heat during filling. Continued contact
can cool stored gas after pumping subsides, until gas and metal approach the
same temperature. It does not keep cooling indefinitely without an external
sink. During withdrawal, enthalpy leaves faster than internal energy per kilogram;
the residual gas cools and the rack can **return heat to the gas**. Negative values
in the signed gas-to-metal plot show this reversal.

In the reference, no rack is radiating externally. Its coast temperature changes
only by exchanging energy with gas. This deliberately separates retained-rack
cooling from deploying racks into space. The thermal-contact-off comparison
simply disconnects gas/metal exchange at +180 s, without pretending the rack is
physically removed or adding radiation; it is a controlled thermal ablation.

An effective emitting-area input exists for future thermal-link studies, but
its default is zero. A nonzero value requires a physical path to radiators outside
the closed pressure volume. The solver does not model opening a pressure hatch,
removing displaced solid volume or mechanically deploying racks while retaining gas.

## Equations and applicability

See [model equations and interfaces](../../modeling/chambers/README.md).
This experiment uses temperature-dependent frozen-air caloric properties with
an ideal-gas equation of state; it does not replace the main model's HEOS
compression. It also does not resolve shocks, reacting flow, spatial gas mixing,
manifold loss or measured compressor maps. Zero-throughflow gas-to-wire exchange
uses the current cylinder/free-molecular approximation, not a validated quiescent
microgravity chamber correlation. The well-mixed gas assumption needs spatial
validation before these histories can support optimization conclusions.

## Verification

'''+f"Maximum mass ledger residual: **{checks['max_mass_residual_kg']:.2g} kg**; energy residual: **{checks['max_energy_residual_MJ']:.2g} MJ**.\n\n"+f"Halving maximum step from 2 to 1 s and tightening relative tolerance fourfold changes final receiver mass by **{checks['relative_final_receiver_mass_change']:.2%}**, temperature by **{checks['final_receiver_temperature_change_K']:.4f} K**.\n\n"+'''Tests separately check sealed-volume equilibration, withdrawal enthalpy,
compressor work, radiation, geometry validation and conservation. Gas temperatures
are omitted below 10 micrograms inventory; a vacuum temperature inferred from
numerical roundoff is not a meaningful plotted state. Raw minimum gas mass and
caloric/material domain flags remain in each output's `checks`.

## Reproduce and modify

```sh
.venv/bin/python -m atmo_scoops.chambers --config configs/chamber_transient_reference.json --output results/chamber_transient/reference.json
.venv/bin/python -m atmo_scoops.studies.chamber_transient
.venv/bin/python -m atmo_scoops.studies.chamber_report
```

Edit the configuration to change individual chamber/rack dimensions, rod geometry,
starting temperatures, pump capacity/head/cutoff/stop time, coast mixing assumption,
withdrawal rate/start, or effective radiation. Full time series, boundary forcing,
energy/mass ledgers and exact inputs are saved under `results/chamber_transient/`.
'''
 (OUT/'README.md').write_text(text)
if __name__=='__main__':main()
