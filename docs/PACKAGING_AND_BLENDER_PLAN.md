# Packaging, mass distribution and Blender requirements

Status: planning only. The verified numerical reference is the starting point,
not a mechanically resolved spacecraft. No stability claim or construction-ready
layout follows from the existing aggregate equipment bay.

## v1.0 scope and sequence

1. Publish the verified plate reference as **v1.0 now**; the new sensitivity study
   and Blender are not prerequisites. See the [publication kit](publication/V1_0.md).
2. Use the [provisional axial register](../investigations/v1_layout/MASS_REGISTER.md)
   for an explicit mass/CM illustration, clearly distinguished from a resolved fit.
3. Later run the [one-off 1×/2×/4× plate study](../investigations/plate_scale/PLAN.md).
4. Resolve actual packaging, access and deployment paths before Blender, using
   the requirements below and revising the provisional register as necessary.
5. Build Blender later from the chosen snapshot. This document does not initiate
   Blender work now.

The intended arrangement puts heavy compressors, batteries, power electronics
and processing machinery forward, with the comparatively lightweight large gas
receiver extending aft. This is a layout objective, not a proven stability
criterion: static stability needs the aerodynamic center of pressure aft of the
center of mass by a quantified margin under the applicable flow. Track dry and
wet centers of mass as receiver inventory grows; deployment changes inertia and
loads. Aerodynamic/stability work remains outside the optimizer for now.

## Volume and mass register

For every component export: stable ID; function; material; mass (dry and variable
contents separately); envelope dimensions/shape; solid volume; fluid/free volume;
insulation and supports; service clearance; stowed envelope; deployed/swept
envelope; hatch/port; axial and transverse location; uncertainty/source.

Record all five chambers separately: barrel and heads, gross volume, rack solid
volume, rack envelope and void fraction, actually accessible gas, compressor
intrusions and dead volume. Never subtract the full rack envelope as solid, or
count rack voids twice. Pressure hatches, doors and supports occupy physical
space and need their own mass/pressure rating, even though the inlet stays open.

Equipment accounting includes all compressor banks and motors, coast compressor,
liquefier/separator/exchangers, battery modules and containment, power bus/cables,
thrusters, gaseous propellant reserve and booster, cryogenic tanks, warm coolant
inventory/pumps/pipes, folded solar and warm radiators, rack deployment mechanisms,
hull/thermal protection, service aisles and support trusses. Existing generic
packing density/fill fraction must be reconciled with actual component envelopes;
it is not evidence that these parts fit. Keep unallocated volume and mass margin
visible instead of creating a fictional physical “margin” component.

Calculate x_CM = sum(m_i x_i)/sum(m_i), radial offsets and inertia tensors for:
stowed entry, peak collection, end of collection, deployed coast, full liquid
inventory and post-transfer. Show the cumulative axial mass curve and component
mass by axial station. Report mass margin distribution as an explicit assumption
or uncertainty range, not guaranteed forward ballast.

## Preliminary dependency / access map

Locations below are proposed zoning requirements, not assigned dimensions.
Use x=0 at the mouth and x increasing aft. Keep intake and compressor flow paths
unobstructed. Resolve radial versus axial packing before assigning coordinates.

| System | Proposed zone | Connections / dependencies | Deployment or access requirement |
|---|---|---|---|
| SiC front cooler | Front flow volume | Intake, compressor 1, local thermal/support interfaces | Prefer forward extraction through mouth; demonstrate clearance and retention, not assumed ejection |
| Intermediate Al coolers | Individual compressor volumes | Adjacent compressor inlet, support guides | Dedicated pressure-rated side hatches and positively constrained extraction paths in v1.0 |
| Receiver Al cooler | Aft receiver | Receiver gas, withdrawal hardware | Pressure-rated side hatch in v1.0; open only after depressurization/processing interlock |
| Dive compressor banks | Forward stage cluster | Adjacent gas volumes, local battery/bus, cooling | Fixed machinery; bank annulus/module envelope and maintenance path must fit |
| Batteries and power electronics | Adjacent to forward compressor banks | Short high-current runs, warm rejection, array feeds | Fixed, segmented modules; containment/thermal isolation and service access |
| Solar arrays | **Opposed dorsal/ventral external bays on the forward equipment section**, behind inlet protection | Forward power bus, deployment drives, attitude control | Two separately reserved outward deployment corridors; no storage inside pressurized gas volumes; clear rack paths, radiator views and plume cones |
| Warm-loop radiators | Separate lateral equipment bays | Pumps, warm store, flexible lines if deployed | Dedicated outward corridors separated from solar and rack swept volumes |
| Coast compressor / cryogenic plant | Forward equipment section | Long low-pressure receiver pickup, cold product lines, power and warm rejection | Fixed machinery; size long pickup and transfer lines rather than assuming they are free |
| Propellant reserve / booster | Forward equipment section | Coast feed, regulator, thrusters, jacket cooling | Fixed tanks with isolation/service access |
| Product tanks | Aft available tank zone, subject to wet-CM check | Liquefier, insulation, transfer interface | Fixed; transfer port accessible without blocking deployed systems |
| Thrusters | Placement pending thrust-line and plume-clearance study | Power, gaseous feed, thermal rejection | Forces and moments must close; aft mounting cannot be assumed compatible with every array/rack position |
| Stability surfaces / aft skirt | Aft exterior | Hull load path | Preserve inlet area, deployment clearances and aerodynamic requirements |

The solar location is now a specific *proposal to test*. Do not present it in
Blender as a verified fit. Quantify array stowed thickness, cassette count, boom
length, wiring routes and swept volume; nominal area alone is insufficient.

For each moving assembly specify the attachment that stays on the craft, guide
or hinge path, slide distance, unfolding sequence, speed/acceleration limit,
final tension/support and retraction procedure. “Unfurls into space” is not a
mechanism. Distinguish translation through a hatch from lateral unfolding and
radiation area. Use the existing 10 m/s limit as a first timing constraint, not
a mechanical qualification.

## Deployment state machine and Blender deliverables

Show stowed dive, residual pumping, individual depressurization checks, hatch
opening, extraction, unfurling, coast processing, folding, reinsertion and hatch
closure. Different chambers can become safe at different times. Render the
pressure boundary and retained gas for each state; do not slide a plate through
a closed pressure vessel wall. Solar stow/deploy follows its separate atmosphere
and power schedule. Include collision and occlusion checks between all assemblies.

Blender input package: units in metres; axis/origin convention; machine-readable
component register and exact input hash; hierarchy of component IDs; dimensioned
orthographic sections; pressure boundaries and ports; stowed/deployed envelopes;
mechanism paths/keyframes; material/color legend; visible fixed-vs-moving parts;
per-state mass/CM markers; numerical versus illustrative dimensions labeled.
Provide total-vehicle views, front equipment cutaway, a single intermediate-stage
exploded view, receiver/cooler hatch detail and complete deployment animation.
Supports, cables, coolant hoses and safety clearances must not disappear simply
because they were absent from the scalar package-volume estimate.

## v1.1 branch: fixed exchangers and coolant inventory aft

Keep v1.0's plate deployment as the snapshot, then investigate replacing cooler
extraction from the higher-pressure volumes with fixed exchangers and a separate
active coolant inventory. This eliminates those deployment hatches/motions but
adds pipes, pumps, coolant storage and coast heat rejection or refrigeration.
Specify which stages change; do not silently replace the front SiC system.
Recompute heat transfer, pumping, fluid/solid volumes, mass, thermal reset and
access requirements before crediting a benefit. Record the user's preference
for this direction without assuming it already improves payoff.
