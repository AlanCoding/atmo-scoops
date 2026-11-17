"""Generate integrated ammonia investigation from the refined model results."""
from pathlib import Path
import json,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-scoops-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'investigations/liquid_cooling';RESULT=ROOT/'results/ammonia_integrated'
def load(label):return json.loads((RESULT/'refined'/f'{label}_1601.json').read_text())
def main():
 labels=[('solid','Solid metal, retuned'),('cold200','Ammonia 200→300 K'),('cold200_small','Ammonia 200→300 K, smaller exchanger'),('warm280','Ammonia 280→340 K')]
 data={k:load(k) for k,_ in labels};b=data['solid']['outputs'];a=data['warm280']['outputs'];c=data['cold200']['outputs']
 rows=[]
 for k,label in labels:
  o=data[k]['outputs'];stock=o.get('payoff_including_ammonia_inventory_days');stock='—' if stock is None else f'{stock:.1f}'
  rows.append(f"| {label} | {o['total_dry_kg']/1000:,.0f} | {o['compressor_mass_kg']/1000:,.0f} | {o['compressor_peak_MW']:.1f} | {o['net_liquid_equivalent_kg']:,.0f} | {o['operating_mass_payoff_days']:.1f} | {stock} |")
 massrows=[]
 for key in ['hot_metal','hot_sheet_deployment','compressor_hot','compressor_warm','ammonia_tank','ammonia_radiator','ammonia_refrigerator','solar','battery','design_margin']:
  x=b['masses_kg'].get(key,0)/1000;y=a['masses_kg'].get(key,0)/1000
  massrows.append(f'| {key} | {x:,.1f} | {y:,.1f} | {y-x:+,.1f} |')
 detail=[]
 for i,x in enumerate(c['ammonia']['stages']):
  rack=c['racks'][i]
  detail.append(f"| {i+1} | {rack['depth_m']:.3f} | {rack['wetted_m2']:,.0f} | {x['used_kg']/1000:.2f} | {x['available_kg']/1000:.2f} | {x['mean_return_K']:.1f} | {x['peak_wall_K']:.1f} |")
 vals=json.loads((RESULT/'refined/summary.json').read_text())
 error=max(abs(next(x['payoff_days'] for x in vals if x['name']==k and x['n']==801)-next(x['payoff_days'] for x in vals if x['name']==k and x['n']==1601)) for k,_ in labels)
 text=f'''# Integrated ammonia cooling: initial payoff comparison

## Result

The fixed-tube ammonia option is now in `system.simulate`: heat exchange changes
front gas temperature/pressure, admission/leakage and compressor inlet states.
Actual coolant consumption and pump work determine regeneration, solar, radiator,
battery and tank budgets. Added folded volume and solar/radiator motion feed back
into the coast window. This is no longer a prescribed-duty component subtraction.

At the fixed **85 × 2,000 km orbit**, the best warm-ammonia case here gives
**{a['operating_mass_payoff_days']:.1f} days**, compared with
**{b['operating_mass_payoff_days']:.1f} days** for the retuned solid-metal reference.
The representative 200 K ammonia case gives **{c['operating_mass_payoff_days']:.1f} days**.
These are conditional **operating-orbit dry-mass payoffs**. Circular-apogee delivery
is still unimplemented. The large absolute vehicle masses reflect the current
power/propulsion hardware assumptions, not a qualified vehicle design.

| Case | Dry t | All compressors t | Peak compressor MW | Net new kg/pass | Dry payoff days | Payoff also charging ammonia inventory, days |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

All table cases pass implemented screens at 1,601 samples. This does not validate
inlet shock stability, material life, heat-transfer correlations or machinery.
Ammonia inventory in the last column includes batch and fixed-tube hold-up; it
is additional to dry mass. Warm radiator-loop fluid is reported separately in
working mass, consistent with the existing model's distinction.

## What cooling buys, and what it costs

In the 200 K case, peak front compressor-inlet temperature drops from
**{b['compressor_inlet_K']:.0f} to {c['compressor_inlet_K']:.0f} K** and total compressor
mass falls by **{(b['compressor_mass_kg']-c['compressor_mass_kg'])/1000:.0f} t**.
The gas is not forced to equal the 200 K coolant supply. Finite gas-side heat
transfer, liquid capacity rate and incoming heat set its temperature.

The warmer case trades away some deep-cooling benefit to reduce regeneration
cost. Its mass changes against solid metal are:

| Budget entry | Solid t | Warm ammonia t | Change t |
|---|---:|---:|---:|
'''+ '\n'.join(massrows)+f'''

The reference assigns about **{100*b['compressor_mass_kg']/b['total_dry_kg']:.1f}%**
of total dry mass to compressors. Reboost peak electrical power remains around
**{b['reboost_peak_MW']/1000:.2f} GW**, versus only
**{b['compressor_peak_MW']:.1f} MW** for peak compression in the solid case.
Cooling does not remove capture momentum. Consequently, substantial compressor
savings do not remove the dominant propulsion and power-system burden in this
particular numerical model. The heat-pump/radiator/tank cost exceeds the savings.

![Selected dry-mass changes](ammonia_mass_change.png)

## Physical dimensions and cycle: 200 K example

Mouth/internal bore remains 30 m. Actual front chamber depth is
**{c['front_depth_m']:.2f} m**; rear receiver depth is **{c['rear_depth_m']:.2f} m**.
The tube-bank envelopes include gas-accessible pores:

| Bank | Tube-bank depth m | Gas-contact area m² | Spent ammonia t | Available batch t | Mean return K | Peak inner-wall K |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(detail)+f'''

The complete coolant tank has **{c['ammonia']['tank_m3']/(3.141592653589793*15**2):.2f} m**
equivalent bore depth, including unused reserve, excluding tube hold-up. This is
volume accounting, not a selected hull-spanning diaphragm geometry. Shared
hot/cold storage counts the larger full inventory volume, not two full tanks.
Total assembled length is **{c['overall_length_allowance_m']:.1f} m**, including
interstage envelopes, packed plant, panels, radiator and tank. Exterior diameter
is 31.7 m; the L/D limit remains 10 and receiver pressure cap 110 kPa.

- Orbit: **{c['cycle']['orbit_s']/60:.1f} min**.
- Deployed coast: **{c['cycle']['deployed_s']/60:.1f} min**; deployed sunlight: **{c['cycle']['sunlit_s']/60:.1f} min**.
- Common deployment/retraction allowance: **{c['cycle']['deploy_s']:.1f} s** each, recalculated from combined areas.
- Added ammonia-loop radiator: **{c['ammonia']['radiator_m2']:,.0f} m²** emitting area.
- Total solar area: **{c['solar_area_m2']:,.0f} m²**; ammonia adds **{c['ammonia']['additional_solar_W']/1e6:.1f} MW**.
- Separate existing warm-system radiator: **{c['warm_radiator_panel_m2']:,.0f} m²** physical panel area, two emitting faces.
- Deployable metal-cooler area: **zero**; tubes remain inside.

The dynamic encounter retains the reference's longer low-density admission and
recovery tails. No new fixed 60 s collection assumption is imposed. Heat-pump
operation is confined to actual deployed sunlight; its electrical work is charged
in full. Available coolant is sized from screening consumption plus 10% reserve,
then checked again after the changed packing/deployment window.

## Search, rejected cases and limitations

The 14-case screen includes a fresh solid reference; 200 K banks at 0.5/1/1.5
area multipliers and suction scales 0.6/0.85/1.1; and 240/280 K supply with 340 K
return target at two suction scales. Initial 200 K pressure is 2 MPa; warmer
340 K-return cases use 5 MPa to remain liquid with wall-temperature margin.

Two smaller 200 K variants exceed the local wall-boiling screen at 2 MPa. The
refined smaller-bank row explicitly raises pressure to **2.5 MPa**, charges the
resulting tank mass and rechecks properties/stress. No single-phase performance
is claimed for the rejected 2 MPa variants. The weakest small-bank suction case
also loses oxygen closure. Full rejected outputs remain alongside passing ones.

The refined cases run at 801 and 1,601 samples; the largest payoff change is
**{error:.3f} day**. This is numerical convergence, not physical validation. It is
not a global optimization of orbit, gas storage, stage-specific coolant
conditions, control law or mixed cooling architectures. Cooler inventory depletion
rejects a trial rather than simulating post-exhaustion operation.

Tube walls and liquid flow are quasi-steady; liquid exchange uses a real-property
enthalpy secant and a conservative internal-film estimate. Compressor gas states
remain real-gas isentropic calculations with efficiency. The refrigerator still
uses 35% Carnot performance and 500 electrical W/kg as explicit capability
assumptions. Insulation, manifold geometry, cyclic containment, separator heat
leak and heat-pump hardware maps remain unresolved. See the
[integrated equations](../../modeling/liquid_cooling/INTEGRATED_MODEL.md).

## Reproduction

```
.venv/bin/python -m atmo_scoops.studies.ammonia_integrated
.venv/bin/python -m atmo_scoops.studies.ammonia_validation
.venv/bin/python -m atmo_scoops.studies.ammonia_report
.venv/bin/python -m atmo_scoops --config configs/ammonia_cold200_reference.json --samples 801 --output /tmp/ammonia.json
```

Full inputs and component ledgers are in `results/ammonia_integrated/`; complete
editable primary configurations are `configs/ammonia_cold200_reference.json`,
`configs/ammonia_cold200_small_reference.json` and
`configs/ammonia_warm280_reference.json`. The ordinary-metal default is retained.
'''
 DEST.mkdir(exist_ok=True);(DEST/'INTEGRATED.md').write_text(text)
 keys=['hot_metal','hot_sheet_deployment','compressor_hot','compressor_warm','ammonia_tank','ammonia_radiator','ammonia_refrigerator','solar','design_margin']
 values=[(a['masses_kg'].get(k,0)-b['masses_kg'].get(k,0))/1000 for k in keys]
 fig,ax=plt.subplots(figsize=(8,4.8));ax.barh([k.replace('_',' ') for k in keys],values,color=['#2b8f83' if v<0 else '#bf6b39' for v in values]);ax.axvline(0,color='black',lw=.8);ax.set(xlabel='Change in dry mass (tonnes)',title='280 K ammonia minus solid-metal reference');ax.invert_yaxis();fig.tight_layout();fig.savefig(DEST/'ammonia_mass_change.png',dpi=170);plt.close(fig)
 (RESULT/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'atmo_scoops').rglob('*.py')},indent=2)+'\n')
if __name__=='__main__':main()
