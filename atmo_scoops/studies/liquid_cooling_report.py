from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'investigations/liquid_cooling'
def read(n):return json.loads((ROOT/'results/liquid_cooling'/n).read_text())
def main():
 names=['Water_280_340_rad340_HP','Ammonia_200_300_rad340_HP','Propane_100_300_rad340_HP','Nitrogen_70_110_rad340_HP']
 rows=[]
 for name in names:
  r=read(name+'.json');s=r['inputs']
  rows.append(f"| {s['fluid']} | {s['cold_K']:.0f} → {s['hot_K']:.0f} | {r['total_coolant_kg']/1000:,.0f} | {r['coolant_tank_equivalent_depth_m']:.2f} | {r['solar_MW']:.1f} | {r['radiator_m2']:,.0f} | {r['dry_component_kg']/1000:,.0f} |")
 a=read(names[1]+'.json');w=read(names[0]+'.json');p=read('Water_280_340_rad260_passive.json')
 text='''# Once-through liquid cooling: a third thermal architecture

**Follow-up:** [integrated ammonia payoff analysis](INTEGRATED.md). The component screen below remains a separate investigation.

This study retains ordinary deployable metal and encapsulated PCM, and adds
**fixed tubes with a separate cold/hot coolant inventory**, regenerated during
coast. Direct nitrogen mixing remains a separate supported option. The options
can be combined by temperature band rather than selecting one for every stage.

## What this calculation answers

The standalone model sizes liquid capacity, tube area/mass/volume, flow and
pumping, pressure storage, coast refrigeration, solar and radiator requirements.
It uses real liquid properties. It is **not yet coupled to the primary inlet or
compressor simulation and does not give new capture or payoff numbers**.

Boundary conditions come from the 85 × 2,000 km, 30 m-bore tuned solid-metal
case: **225.92 GJ** total heat stored in four racks, of which 215.27 GJ is in the
front rack. For this requested one-minute experiment, that entire duty is put
through the exchangers in **60 s** (3.77 GW average). The saved encounter actually
has longer admission/recovery tails; 60 s is an explicit sizing assumption,
not a measured peak duration. Coast is 5,135 s with 2,785 s available sunlight.
Representative chamber temperatures and gas-side h are taken from the saved
reference. They are held fixed so these results cannot claim a colder outlet.

The tube screen uses 1 mm outer radius, 0.1 mm wall, 2 m/s liquid velocity,
radius/pitch 0.1 and 30% tube support allowance. Wall conductivity is 16 W/(m K).
The tank is a thin spherical pressure-shell lower bound with 50% support allowance,
not a selected diaphragm design. Pressures are 1 MPa water, 2 MPa ammonia/propane,
and 3 MPa nitrogen. Heat-pump effectiveness is assumed 35% of Carnot with 10 K
approaches. All coefficients are serialized; they are not qualified hardware.

## Equal 340 K radiator comparison

All entries use heat-pump regeneration during sunlight, 5 kg/m² radiator,
150 W/kg and 250 W/m² solar, and a refrigerator target of 500 electrical W/kg.
Dry mass below is **this cooling subsystem only**, including its extra solar,
radiator and pump battery. Inventory is additional; neither is the spacecraft mass.

| Liquid | Cold → warm K | Inventory incl. line fill, t | Shared tank equivalent depth, m | Extra solar MW | Radiator emitting area m² | Dry subsystem t |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+f'''

The quoted tank depth excludes tubes, equipment and folded panels. For the
ammonia example the front exchanger envelope is **{a['stages'][0]['rack_depth_m']:.2f} m**
deep; the tank is **{a['coolant_tank_equivalent_depth_m']:.2f} m** equivalent depth.
It consumes about **{a['coolant_batch_kg']/1000:.0f} t** of once-through batch plus
**{a['line_fill_kg']/1000:.0f} t** line fill. The tank needs only the maximum
hot-full/cold-full volume, not both simultaneously. There are many parallel tubes,
not a single passage carrying thousands of kilograms per second.

The ammonia reference regenerates approximately
**{a['regenerated_heat_J']/1e9:.1f} GJ**, including a conservative full-temperature
swing allowance for tube fill. Refrigeration uses **{a['refrigerator_J']/1e9:.1f} GJ**
of electricity. The radiator must reject their sum plus coast-pump heat; moving
work to coast does not remove it. Its standalone deployment travel estimate is
**{a['required_motion_s']:.0f} s** at 10 m/s. Combined spacecraft deployment and
packing must still be recomputed.

## Passive versus refrigerated rejection

Water at 280→340 K can reset using a 260 K passive radiator. That radiator works
through the whole deployed coast, including eclipse; heat-pump cases here run
only in sunlight. The passive case needs **{p['radiator_m2']:,.0f} m²** and
**{p['dry_component_kg']/1000:,.0f} t** dry subsystem mass. With a 340 K radiator
and heat pump, these become **{w['radiator_m2']:,.0f} m²** and
**{w['dry_component_kg']/1000:,.0f} t**, while extra solar rises to
**{w['solar_MW']:.1f} MW**. Thus refrigeration can trade electricity for radiator
mass even without cryogenic coolant. That comparison depends on the explicit
radiator/refrigerator/solar coefficients, not thermodynamics alone.

The sweep tries radiator temperatures 260/300/340/380 K and direct/heat-pump
modes for seven fluid-temperature pairs. Many cold cases prefer its 380 K upper
boundary. This is a sensitivity grid, not a radiator-temperature optimum or a
mission viability conclusion. All successful/failed local screens are saved.

## The more promising cold-end question

The model should distinguish **storing the incoming high-temperature heat** from
**finishing the gas at low temperature**. Sending the entire 226 GJ through a
70 K-class store is an expensive benchmark, not a requirement of the architecture.
A hot first bank could remove most of the incoming energy, followed by a much
smaller refrigerated bank. Each stage's cold duty would then come from its actual
gas enthalpy drop and compressor work; no arbitrary fraction should become a
claimed optimum. This is where independent per-stage flows, coolant endpoints
and temperature staging belong in the eventual optimizer.

Cold coolant can keep tube surfaces cold while the warm reservoir fills, unlike
a passive rack whose whole inventory heats in place. It also adds no molecules
to the captured gas. Whether that buys enough lower gas volume, compressor size
or battery power to repay the additional hardware is still unanswered by this
fixed-duty calculation. It would be incorrect to reject it by subtracting these
masses from the old reference while keeping its gas states unchanged.

## Reproduction and model scope

```
.venv/bin/python -m atmo_scoops.studies.liquid_cooling
.venv/bin/python -m atmo_scoops.studies.liquid_cooling_report
```

Editable inputs: `configs/liquid_cooling_reference.json`.
Results: `results/liquid_cooling/`, including source boundaries and property-library
version. [Equations, limitations and references](../../modeling/liquid_cooling/README.md)
include local wall-boiling and tube-stress checks, cold-phase limitations,
missing insulation/manifold/radiator-loop detail and the required coupling steps.
Local screen passage is not structural, deployment or mission validation.
'''
 DEST.mkdir(exist_ok=True);(DEST/'ANALYSIS.md').write_text(text)
if __name__=='__main__':main()
