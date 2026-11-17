"""Report saved ammonia geometry sensitivity, including rejected candidates."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/ammonia_tubes'
def main():
 rows=json.loads((DATA/'summary.json').read_text());checks=json.loads((DATA/'checks.json').read_text())
 text='''# Ammonia tube radius and pitch

## Reference geometry and what is actually modeled

Both integrated ammonia references use **1 mm outer radius, 0.1 mm wall and
10 mm center-to-center pitch**: 1.8 mm internal diameter, 8 mm clear external gap.
Warm ammonia runs 280–340 K at 5 MPa; cold ammonia 200–300 K at 2 MPa.
Exterior exchange area is 170,000 m² in front and 6,000 m² in each of three
interstage coolers. This is tube surface area, not spacecraft frontal area.
The 30 m bore has 707 m² frontal area.

The front bank occupies 3.83 m depth, and each intermediate bank 0.135 m under
the idealized lattice-volume rule. All banks together contain 140.6 tonnes of
metal; warm-reference tube liquid hold-up adds 48.2 tonnes. The front alone has
about **3.01 million parallel paths**, each about **8.98 m** long. Interstage
banks each have about 134,000 paths, 7.13 m long. These are inferred hydraulic
passages, not a manufactured manifold design.

Pump head is already represented, but only approximately: Darcy friction along
an equivalent path plus a fixed 100 kPa header allowance, with 65% pump efficiency.
The warm reference has about 150 kPa peak pressure drop and 291 MJ pass pump work.
Its approximately 116 GJ ammonia regeneration electricity is much larger.
Five MPa is containment pressure, not an assumed five-MPa pressure drop every pass.
Real manifold branching, connectors, maldistribution, supports and startup still
need modeling. Gas-side lattice pressure loss remains deliberately omitted.

At the reference's reported peak-flow states, gas-side resistance accounts for
about **96% of the combined gas/wall/liquid thermal resistance**. Improving liquid
convection alone cannot remove that bottleneck. Smaller diameter can improve
external gas heat transfer, as well as reducing metal and tube liquid inventory.

## Controlled radius sweep

Orbit remains 85 × 2,000 km, with battery-fed 300 s perigee thrust. Isp is fixed
at each architecture's previous optimum: 1,815.65 s warm, 1,869.41 s cold. The
thermal geometry sweep does not re-optimize Isp or orbit. All heat-transfer states,
compressors, regeneration, deployment, packing and power masses are recomputed.

Hold exterior area, maximum coolant flow and installed tank inventories fixed.
Hold radius/pitch=0.1 and wall/radius=0.1. Thus pitch and wall thickness change
with radius; pressure-stress capability is approximately comparable. Thin walls
are a sensitivity assumption, not qualified manufacturing/cycling capability.
The model adjusts parallel-path count to retain 2 m/s at the specified maximum
flow; it does **not** keep the plumbing network fixed when changing radius.

Payoffs end in the operating orbit, not circular-apogee delivery. Rejected rows
show diagnostic model output only, not viable designs.

| Coolant | Radius, mm | Pitch, mm | Tube metal, t | Peak front inlet, K | Dry mass, t | Payoff, days | Screens |
|---|---:|---:|---:|---:|---:|---:|---|
'''
 for r in rows:
  if r['ratio']!=.1:continue
  status='Pass' if r['screens'] else 'Rejected: '+', '.join(r['failed'])
  text+=f"| {'Warm' if r['architecture']=='warm_ammonia' else 'Cold'} | {r['radius_mm']:g} | {r['pitch_mm']:g} | {r['tube_t']:.1f} | {r['peak_inlet_K']:.0f} | {r['dry_t']:,.0f} | {r['payoff_days']:.1f} | {status} |\n"
 text+='''
Reducing the warm-case radius fourfold saves roughly six days (about 1.5%), while
the same-solid-rack benchmark is about 371 days. Thus these tube changes alone
do not reverse the earlier ranking. Very small tubes also multiply passage
count: at 0.25 mm radius the front needs about 48 million equivalent paths,
2.25 m long. No detailed mass model for those manifolds is present.

Larger tubes have more liquid hold-up and larger bank volumes at fixed surface
area. The conservative liquid-side heat-transfer model also loses conductance.
A wall-boiling failure means the assumed single-phase exchanger is no longer a
valid representation; its numerical payoff must not be used as a feasible result.

## Separate wall-thickness and resolution checks

| Radius, mm | Wall, mm | Samples | Payoff, days | Tube metal, t | Peak pressure drop, kPa | Screens |
|---|---:|---:|---:|---:|---:|---|
'''
 for r in checks:
  text+=f"| {r['radius_mm']:g} | {r['wall_mm']:g} | {r['n']} | {r['payoff_days']:.2f} | {r['tube_t']:.1f} | {r['peak_dp_kPa']:.1f} | {'Pass' if r['screens'] else 'Rejected'} |\n"
 text+='''
The fixed-wall cases retain the original 100-micron wall while shrinking the
outer diameter. These distinguish thermal/geometry improvements from credit for
thinner metal. High-resolution baseline results are 392.99 days warm and 418.99
cold; the table's baseline screening runs use 201 samples, so compare radius
changes at matched resolution. No sub-day optimum is claimed.

## Pitch sensitivity

Here radius stays 1 mm and exterior area stays fixed. Pitch changes bank envelope,
gas hold-up and the modeled gap velocity, rather than adding exchange surface.

| Pitch, mm | Front bank depth, m | Payoff, days | Screens |
|---|---:|---:|---|
'''
 for r in rows:
  if r['architecture']=='warm_ammonia' and r['radius_mm']==1:
   text+=f"| {r['pitch_mm']:g} | {r['front_depth_m']:.2f} | {r['payoff_days']:.2f} | {'Pass' if r['screens'] else 'Rejected: '+', '.join(r['failed'])} |\n"
 text+='''
These are conditional packing/convection results. Without gas pressure loss and
manifold layout, tighter pitch is not a qualified optimization direction.

## Scaling and modeling priorities

For exterior area A, outer radius r, wall thickness t and radius/pitch ratio q:

- Tube length: A/(2πr).
- Sealed tube volume: Ar/2; gas-bank envelope: Ar/(2πq²).
- Metal volume: A[r²−(r−t)²]/(2r), approximately At for thin fixed walls.
- Liquid hold-up volume: A(r−t)²/(2r).

At fixed wall/radius and liquid design velocity, equivalent parallel count scales
as 1/r² and path length as r. Therefore a radius reduction does not incur the
same pressure-drop scaling as shrinking a fixed-length, fixed-count pipe network.
Resolving manufacturable branching and hydraulic path length is the most important
next geometry refinement. Then qualify internal heat transfer (including variable
Reynolds number), wall temperatures, boiling margins and cycling allowables.

Thrust-loss heat coupling to this coolant is a separate integration question. The
current model retains a fraction of thruster waste heat in the warm rejection
system; this sweep does not move it into the cold once-through ammonia inventory.
Such a change must add coolant enthalpy, flow and regeneration duties explicitly.

## Reproduction

```sh
.venv/bin/python -m atmo_scoops.studies.ammonia_tubes
.venv/bin/python -m atmo_scoops.studies.ammonia_tubes --checks
.venv/bin/python -m atmo_scoops.studies.ammonia_tube_report
```

Inputs start from `configs/reboost_{warm_ammonia,ammonia}_isp_optimum.json`.
All resolved inputs, per-stage geometry and mass/energy ledgers are saved in
`results/ammonia_tubes/`; summaries preserve every rejected screen.
[Integrated model and property treatment](../../modeling/liquid_cooling/INTEGRATED_MODEL.md).
'''
 (ROOT/'investigations/liquid_cooling/TUBE_GEOMETRY.md').write_text(text)
if __name__=='__main__':main()
