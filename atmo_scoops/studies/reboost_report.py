"""Generate the two reboost investigation reports from saved numerical runs."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'results/reboost'; OUT=ROOT/'investigations/reboost'
LABEL={'solid':'Solid racks','ammonia':'Ammonia 200–300 K','warm_ammonia':'Ammonia 280–340 K'}
SOURCES={'solid':'solid','ammonia':'cold200','warm_ammonia':'warm280'}
def read(name):return json.loads((DATA/name).read_text())
def main():
 OUT.mkdir(exist_ok=True,parents=True)
 opts={r['architecture']:r for r in read('isp_optima.json') if r['n']==1601}
 baseline={k:json.loads((ROOT/f'results/ammonia_integrated/refined/{v}_1601.json').read_text()) for k,v in SOURCES.items()}
 text='''# Exhaust velocity versus dry-mass payoff

**The present model favors about 1,800–1,900 s Isp for battery-fed perigee reboost.**
Allowing nitrogen propellant removes the oxygen-only constraint; every kilogram
expelled still comes out of useful product. These are conditional minima for the
fixed 85 × 2,000 km orbit and existing thermal designs, not global spacecraft optima.
All payoffs below end in the operating orbit; circular-apogee delivery remains unmodeled.

## Full-primary-model results

| Cooling | 4,000 s payoff, days | Optimized Isp, s | Payoff, days | Dry mass, tonnes | Net liquid/pass, kg | Propellant/pass, kg | Of which N2, kg |
|---|---:|---:|---:|---:|---:|---:|---:|
'''
 for k,r in opts.items():
  b=baseline[k]['outputs']
  text+=f"| {LABEL[k]} | {b['operating_mass_payoff_days']:.1f} | {r['isp_s']:.0f} | {r['payoff_days']:.1f} | {r['dry_t']:,.0f} | {r['net_kg']:,.0f} | {r['propellant_kg']:,.0f} | {r['nitrogen_kg']:,.0f} |\n"
 text+='''
![Isp trade](isp_payoff.png)

For fixed impulse J and effective exhaust speed u, propellant is J/u while
propulsion electricity is Ju/(2η). Lower Isp sacrifices liquid output but reduces
battery, solar, engine and power-distribution mass. Too low an Isp consumes most
of the product; too high an Isp carries excessive electrical hardware. The minimum
is broad: the last few seconds of the reported optimum have no engineering significance.

Voltage is indeed a control for Hall thrusters, but actual efficiency, ionization,
propellant species and discharge operating limits must be coupled. These runs
hold the existing 60% thrust efficiency and hardware-specific masses fixed.
They establish a useful design target, not a qualified O2/N2 throttle setting.
[Equations and annotated primary references](../../modeling/propulsion/REBOOST_INVESTIGATIONS.md)
include NASA variable-Isp Hall tests, JPL propulsion theory and an oxygen experiment.

## Scope and reproduction

The primary model is rerun at every Isp; array, battery, thermal, packing and
deployment effects are included. Orbit, capture controls, cooler inventories,
compressor capabilities and the 300 s reboost burst are held fixed. The O2/N2
allocation is an inventory calculation, not a separate nitrogen-engine design.
A 1,200–5,000 s screen brackets a bounded 1,400–2,400 s local minimization at
201 samples. Final outputs are recalculated at 801 and 1,601 samples; the maximum
payoff change is below 0.34 days. This is numerical convergence, not hardware validation.

Run from the repository root:

```sh
.venv/bin/python -m atmo_scoops.studies.reboost_isp
.venv/bin/python -m atmo_scoops.studies.reboost_isp_refine
.venv/bin/python -m atmo_scoops.studies.reboost_report
```

Complete editable inputs: `configs/reboost_{solid,ammonia,warm_ammonia}_isp_optimum.json`.
Exact output states and mass ledgers: `results/reboost/*_isp_optimum_1601.json`.
The new `scenario.allow_nitrogen_propellant` switch defaults to false, preserving
older oxygen-only configurations. [Direct-solar comparison](SOLAR_ARCS.md).
'''
 (OUT/'ISP.md').write_text(text)
 fig,ax=plt.subplots(figsize=(8,4.5))
 rows=read('isp_screen.json')
 for k in LABEL:
  rr=sorted([r for r in rows if r.get('architecture')==k],key=lambda r:r['isp_s'])
  line,=ax.plot([r['isp_s'] for r in rr],[r['payoff_days'] for r in rr],'.-',label=LABEL[k])
  ax.scatter(opts[k]['isp_s'],opts[k]['payoff_days'],color=line.get_color(),marker='*',s=120)
 ax.set(xlabel='Specific impulse (s)',ylabel='Operating dry-mass payoff (days)',title='Less exhaust velocity can buy a lighter power system')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'isp_payoff.png',dpi=180);plt.close(fig)
 text='''# Direct-solar reboost before stow and after deployment

**Worth retaining as a design option, but deleting the propulsion battery is not
an automatic large payoff improvement.** At optimized Isp, the solid-rack case
improves from 371 to 346 days; warm ammonia is essentially tied near 393–394 days
if an additional, explicitly costed rejection-heat buffer is available.

These are separate fixed-capture budget/trajectory investigations. The main
simulation still uses battery-fed perigee thrust. Orbit is 85 × 2,000 km,
period 106.0 minutes; all payoff values end in that operating orbit.

## Optimized comparisons

Both arcs have the same duration: inbound thrust ends before stowing; outbound
thrust starts after recovery and deployment. The search varies Isp (1,000–7,000 s)
and duration (60–1,600 s per leg), with first-order orbit-restoring steering.

| Cooling / rejection | Isp, s | Each burn, min | Impulse / perigee impulse | Solar, MW | Battery, tonnes | Dry mass, tonnes | Net kg/pass | Payoff, days |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
'''
 cases=[]
 for k in LABEL:
  for suffix in ('closed_orbit','closed_orbit_buffered'):
   file=DATA/f'{k}_direct_{suffix}_best.json'
   if not file.exists():continue
   r=json.loads(file.read_text());cases.append((k,suffix,r))
   label=LABEL[k]+(' / buffered' if 'buffered' in suffix else ' / direct rejection')
   text+=f"| {label} | {r['isp_s']:.0f} | {r['window_each_s']/60:.1f} | {r['arc']['impulse_multiplier']:.3f} | {r['solar_W']/1e6:,.0f} | {r['battery_kg']/1000:,.0f} | {r['dry_kg']/1000:,.0f} | {r['net_kg']:,.0f} | {r['payoff_days']:.1f} |\n"
 text+='''
The appropriate battery-perigee comparisons are **371, 419 and 393 days** for
solid, cold ammonia and warm ammonia respectively, after optimizing their Isp.
Against the original 4,000 s cases, all these gains look larger; that comparison
would conflate Isp optimization with changing the thrust schedule.

## Why the orbit penalty is larger than an energy-only estimate

Thrust must restore both orbital energy and angular momentum. In polar components,
`dE = vr*dvr + vt*dvt` and `dh = r*dvt`. Tangential thrust away from perigee
has the wrong energy/angular-momentum ratio to undo perigee drag. Paying only the
speed/Oberth penalty changes the next perigee and therefore the next air capture.

The symmetric finite-arc solution steers partly radially and can eventually point
past 90 degrees from the prograde tangent. This costs 67–87% additional impulse
in the selected cases. Attitude, gimbal, plume clearance and array pointing still
need engineering; unrestricted in-plane steering is an assumption.

For example, the solid-rack optimum starts outbound thrust 10.6 minutes after
perigee, at about 321 km, and continues to about 1,486 km. Direction varies from
20 to 113 degrees from the local prograde tangent. The inbound arc is symmetric.
These are long burns, not short pulses immediately beside atmospheric contact.
At 3,000 s Isp, shortening each solid-rack burn to five minutes gives roughly
883 days, versus about 392 days with fifteen minutes: peak solar power matters.

The deliberately invalid energy-only runs give 158 days (solid), 291 (cold ammonia)
and 251 (warm ammonia). **These are not sustainable-cycle payoff predictions**;
they are retained only to expose the error from ignoring angular momentum.

## Where the battery saving goes

For solid racks, battery mass falls from 2,067 tonnes at the optimized perigee
Isp to 174 tonnes with direct-solar thrust. Warm ammonia falls from 2,115 to
151 tonnes in its buffered case. Those are roughly 92–93% battery reductions,
but only one part of the total dry-mass trade.

The model removes propulsion battery demand, retains compression and eclipse
batteries, and sizes arrays for peak thrust as well as later processing/recharge.
Cryogenic processing pauses during thrust; its plant must handle the same batch
in the remaining time. Area-dependent deployment feeds back into available
sunlight and burn altitude. The solid optimum retains only 82 seconds of sunlit
non-thrust processing and consequently uses eclipse processing/storage heavily.
This tight schedule is a sensitivity, not a robust operations margin.

Ammonia regeneration is sunlit-only. Compressing its operating window makes its
instantaneous heat rejection large. An optional warm-side buffer permits rejection
through the whole deployed coast; it is charged at the existing, unqualified
200 kJ/kg capability plus packing. It is distinct from the cold ammonia inventory
and from the existing pass/thruster heat buffer.

| Cooling | Extra rejection buffer, tonnes | Remaining sunlit processing, min | Physical solar area, m² |
|---|---:|---:|---:|
'''
 for k,s,r in cases:
  if 'buffered' in s:
   text+=f"| {LABEL[k]} | {r['masses_kg']['ammonia_rejection_buffer']/1000:,.0f} | {r['processing_sun_s']/60:.1f} | {r['solar_m2']:,.0f} |\n"
 text+='''
Thus direct rejection alone gives 526/471 days for cold/warm ammonia; adding the
costed buffer gives 431/394 days. Neither clearly beats its corresponding
Isp-optimized battery case under current assumptions. Hybrid solar/battery thrust,
flexible power schedules and longer battery-fed burns have not been searched.

## Verification and reproducibility

Mass sums, solar energy sufficiency, product/propellant accounting, thermal buffer
capacity, deployment and packing screens are checked. Arc quadrature changes
impulse by less than one part per million between 301 and 1,201 samples.
An independent Newtonian finite-burn integration with a perigee drag impulse
restores perigee/apogee to within 4 mm for these reference cases. This validates
the geometry calculation only: it uses constant mass and an impulsive drag event,
not the distributed atmospheric encounter, aerodynamic lift or flight controls.

Capture/thermal duty and compressor pass hardware are frozen from the existing
1,601-sample references. Coast plant mass uses a modular throughput scaling;
no new detailed plant layout or propellant-specific throttle map is claimed.
Efficiency stays 60%. Sun orientation is fixed. No circular-apogee delivery is charged.

```sh
.venv/bin/python -m atmo_scoops.studies.reboost_solar
.venv/bin/python -m atmo_scoops.studies.reboost_validation
.venv/bin/python -m atmo_scoops.studies.reboost_report
```

Inputs are the three ammonia-integrated reference results named in each best-case
JSON's `source_result`; exact settings, arc states, mass breakdowns and duty budgets
are in `results/reboost/*_direct_*_best.json`. Search summaries are `solar_optima.json`
and `solar_screen.json`; independent checks are `verification.json` in that folder.
[Equations and primary references](../../modeling/propulsion/REBOOST_INVESTIGATIONS.md).
'''
 (OUT/'SOLAR_ARCS.md').write_text(text)
 (OUT/'README.md').write_text('# Reboost investigations\n\n- [Variable Isp](ISP.md): full-model dry-mass payoff trade with O2/N2 propellant.\n- [Direct-solar arcs](SOLAR_ARCS.md): orbit restoration, battery savings and processing-time penalties.\n')
if __name__=='__main__':main()
