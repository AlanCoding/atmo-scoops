"""Generate the PCM comparison document and figure from saved model outputs."""
from pathlib import Path
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-scoops-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];RESULT=ROOT/'results/pcm_racks'
def read(p):return json.loads(p.read_text())
def main():
 dest=ROOT/'investigations/pcm_racks';dest.mkdir(exist_ok=True)
 names=[('solid_reference','Original solid metal, 1 mm'),('solid_tuned','Retuned solid metal, 1 mm'),('pcm_best','NaNO3 core, 5 mm'),('pcm_melting','Melting eutectic core, 5 mm'),('pcm_10mm','Eutectic: 10 mm front / 5 mm later')]
 rows=[]
 for key,label in names:
  r=read(RESULT/'refined'/f'{key}_1601.json');o=r['outputs'];rs=o['racks']
  rows.append(f"| {label} | {sum(x['mass_kg'] for x in rs)/1000:,.0f} | {o['total_dry_kg']/1000:,.0f} | {o['net_liquid_equivalent_kg']:,.0f} | {o['operating_mass_payoff_days']:.1f} | {max(x.get('melt_fraction_max',0) for x in rs):.0%} | {o['ideal_metal_cooldown_s']/60:.1f} |")
 pcm=read(RESULT/'refined/pcm_melting_1601.json');z=read(RESULT/'refined/pcm_melting_no_latent.json')
 on=pcm['outputs']['operating_mass_payoff_days'];off=z['outputs']['operating_mass_payoff_days']
 convergence=read(RESULT/'refined/summary.json')
 delta=max(abs(next(x['payoff_days'] for x in convergence if x['name']==k and x['n']==1601)-next(x['payoff_days'] for x in convergence if x['name']==k and x['n']==801)) for k,_ in names)
 text='''# Phase-change cores: capacity is useful only if the heat reaches it

## Finding

Optional PCM cells are now supported in every rack, including independent material,
outer radius and assembly mass. This comparison does **not** select them for the
reference: the tested PCM cases do not beat a fairly retuned solid-metal rack.
The model does demonstrate melting and complete coast refreezing. That is a
real capacity benefit, but it does not remove the gas-side heat-transfer limit.

All results below are **operating-orbit mass payoff**, not circular-apogee
delivered payoff. The very large absolute masses remain conditional on the
existing component model; this investigation compares rack changes within it.

## Controlled comparison

Fixed orbit 85 × 2,000 km, 30 m bore, rear depth 16 m, cold start 298 K,
no injected nitrogen, open inlet, four cooled compressor blocks. L/D ≤ 10,
storage ≤ 110 kPa and existing oxygen, packing, access-area, temperature and
coast-restoration screens remain active. This deliberately fixes altitude and
apogee so the material comparison is not disguised by an orbit change.

PCM cells have 0.5 mm walls/end caps, 0.5 m sealed length, 80% cavity fill,
contact resistance 1e-4 m² K/W, and no fins in the comparison table. Radius/pitch
is 0.1. Casing and sealed ullage are included in chamber displacement. All
rack/core/casing mass, compressor changes, deployment and radiation enter the
full system calculation. These containment dimensions are assumptions requiring
structural and chemical qualification.

| Case (outer radius) | Rack assembly t | Craft dry t | New net kg/pass | Payoff days | Maximum encounter melt fraction¹ | Longest reset min |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

¹ Maximum across racks, not a mass-weighted fleet melt fraction. The fastest salt
case stays below its melting point: its performance is a sensible-heat/geometry
result, not evidence that latent heat shortened payoff. All five displayed cases
pass the implemented screens at the reported resolution; this is not hardware
validation.

![Rack mass and payoff sensitivity](trade.png)

## What the centimetre radius changes

For a cylindrical cell, gas-contact area per outer volume is `2/r`. A larger
radius reduces external area and core conduction speed. At fixed rack-envelope
volume and pitch ratio it also reduces the number of wire planes. Changing from
a dense solid wire to a lighter salt-core cell changes outer volume per kilogram;
the model derives both effects rather than assuming equal area at equal mass.
Core diffusion/solidification time scales approximately as radius squared.

The 10 mm-front case in the table uses 5 mm cells between compressors. Making
**every** rack 10 mm did not yield a screen-passing candidate in the coarse
mass-factor sweep. Some cases exceeded the compressor property domain, some
lost oxygen closure, and others exceeded the model's small-interstage-holdup
limit or hull length. A property-domain error and the 1% holdup screen are model
limitations, not proofs that that hardware is impossible. The 10 mm-front case
shows that centimetre cells are representable without pretending that every
intermediate chamber can be arbitrarily large.

Adding capacity can also defeat its own latent-heat purpose: a sufficiently
massive core never reaches melting temperature. The final states and peak melt
fractions are saved separately for each rack. Hot skin is not treated as proof
of a molten core.

## Isolating latent heat

For the melting 5 mm eutectic case, turn off fusion enthalpy while holding every
assembly mass, radius, casing, void, orbit and suction setting identical.
Payoff changes from **{on:.2f} days with latent heat to {off:.2f} days without**,
a signed **{100*(on-off)/off:+.3f}% change** with fusion heat. That is effectively
no payoff benefit at the precision warranted here.
The zero-latent control passes implemented screens: {z['constraints']['all_implemented_screens_pass']}.
Fusion heat lowers the peak skin temperature from about 549 to 537 K and
stores roughly 46 GJ as latent heat in the front rack, yet leaves peak compressor
inlet temperature essentially unchanged (1,132 K). It therefore provides thermal
margin without materially improving this case's throughput/power bottleneck.
This isolates phase change; it is not a comparison with an independently
optimized sensible-only material or with the tuned solid-metal design.

## Search scope and reproducibility

The first 21-case sweep compares solid radii 1/3/10 mm; tin, sodium nitrate and
eutectic 10 mm cores at mass factors 1.5/3/6/12; 5 mm eutectic cells; and a solid
front with PCM interstages. A further 31-case discrete sensitivity varies front
mass and compressor suction for both solid and PCM designs. Interstage mass
factors are recorded separately. One fin-enhanced trial fails compressor access
area; it is not a feasible recommendation. This is a local sensitivity, **not a
global optimization** of material, radius, rack allocation, orbit or controller.

Screening uses 201 samples. The five table cases are repeated at 801 and 1,601
samples in both inlet and compressor quadrature. The largest payoff change
between those resolutions is **{delta:.3f} day**. Exact inputs, per-stage states,
constraints and mass/energy outputs are retained in `results/pcm_racks/`.

```bash
.venv/bin/python -m atmo_scoops.studies.pcm_racks
.venv/bin/python -m atmo_scoops.studies.pcm_tuning
.venv/bin/python -m atmo_scoops.studies.pcm_validation
.venv/bin/python -m atmo_scoops.studies.pcm_report
```

Editable examples are `configs/pcm_melting_reference.json` and
`configs/pcm_10mm_reference.json`; neither replaces the ordinary-metal reference.
The [model dossier](../../modeling/metal_coolers/PCM_MODEL.md) contains equations,
source annotations, property approximations and implementation limits. The
[broader material survey](../../docs/PHASE_CHANGE_COOLERS.md) includes hotter
materials not covered by this terminal-cooler comparison. Stage-specific and
axially cascaded materials, conductive inserts and explicit transient
intermediate chambers remain worthwhile investigations.
'''
 (dest/'ANALYSIS.md').write_text(text)
 for key in ('pcm_melting','pcm_10mm'):
  r=read(RESULT/'refined'/f'{key}_1601.json')
  (ROOT/'configs'/f'{key}_reference.json').write_text(json.dumps(r['inputs'],indent=2)+'\n')
 fig,ax=plt.subplots(figsize=(8,4.6))
 data=read(RESULT/'tuned/summary.json')
 for prefix,label,color,marker in [('solid','Solid metal, 1 mm','#4155a6','o'),('sodium_nitrate','NaNO3, 5 mm','#d77d22','s'),('nitrate_eutectic','Eutectic, 5 mm','#1e947c','^'),('eutectic_10mm','Eutectic, 10 mm front','#a64a83','D')]:
  values=[x for x in data if x['name'].startswith(prefix) and x['screens']]
  ax.scatter([x['rack_t'] for x in values],[x['payoff_days'] for x in values],label=label,c=color,marker=marker,s=45)
 ax.set(xlabel='Complete rack assembly mass (tonnes)',ylabel='Operating-orbit payoff (days)',title='Fixed orbit and rear tank; mass/suction sensitivity')
 ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(dest/'trade.png',dpi=170);plt.close(fig)
if __name__=='__main__':main()
