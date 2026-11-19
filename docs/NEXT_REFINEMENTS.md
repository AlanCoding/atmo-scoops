# Refinement plan for the coupled design and geometry handoff

The active [staged reference](../investigations/staged_refinement/RESULTS.md)
now has a [reduced-loss continuation](../investigations/staged_refinement/REDUCED_LOSS.md)
at approximately **293 operating-orbit days** with gaseous propellant bypass,
fixed rack geometry and **1% resistance coefficient**. It includes the illustrative
Cf = 0.002 skin-friction impulse. This reduced-loss point passes numerical checks;
full resistance and some neighboring cases remain unresolved. Pitch and radius
optimization remain pending. The older 285-day
zero-skin-friction comparison remains historical evidence, not the active reference.

## Current scope

The owner selected sequential gas-feed, fixed-geometry head-loss, pitch and radius
studies. The gas-feed stage is validated; experimental lattice capabilities remain
available but are not promoted into the active optimization. Other
component penalties and hardware qualification remain deferred. **Future priority:
cryogenic processing integrated with the existing coast compressors, rack cooling,
propellant branch, recuperators and warm rejection loop.** Develop the actual
heat/flow network before refining stand-alone liquefier coefficients.

## Immediate investigations and sequence

| Work | Current status | Deliverable / acceptance gate |
|---|---|---|
| Mass allowance definitions | [Documented](../modeling/primary/MASS_ALLOWANCES.md) | Disjoint bus/PPU/motor boundaries, rack mechanisms/pressure hatches, and separate mass versus volume contingency. |
| External skin friction | Implemented impulse coupling; 0.001/0.002/0.005 coefficient scenarios | Replace illustrative Cf with an offline-calibrated edge-state/transition/temperature model. Include thermal loads separately. |
| Gaseous propellant routing | [Mixed-gas reserve implemented](../modeling/propellant_feed/GAS_RESERVE.md) | Add a cyclic gas reserve, actual feed/compression hardware and species routing. Compare unseparated gas and selective-condensation alternatives against a properly charged liquid-feed baseline. |
| Rack pressure, pitch, then radius | [Staged numerical gates](../investigations/staged_refinement/README.md) | Active continuation fixes 1 mm radius / 10 mm pitch and uses 1% resistance. Continue toward full resistance with numerical checks before releasing geometry. |
| Joint reoptimization | After the preceding physics is implemented | Run each discrete feed architecture under identical drag, propulsion and uncertainty assumptions. Optimize stages, schedules, capacities and initial states with periodic closure. |
| Geometry release | Parameter export can begin now; dimensions remain provisional | A versioned geometry/space/load specification tied to one accepted cycle, with assumptions and unresolved structures visibly labeled. |

Here rack pitch means rod spacing. Variable-pitch compressor blades are a
separate control/hardware candidate requiring stall/efficiency maps and actuator
cost; there is no assumption of an actively variable-spacing radiator rack.

## Penalties most likely to be missing or understated

These should enter their physical balances before any residual mass contingency.

| Priority | Upgrade | Why it can worsen payoff / required output |
|---|---|---|
| 1 | Molecular-air propulsion maps and lifetime | Couple efficiency, Isp, mixture, ionization/dissociation, cathode/neutralizer flow and power, plume losses and erosion. At unchanged Isp/impulse, reducing efficiency from 60% to 40% raises electrical demand by 50%; that is a sensitivity identity, not a claimed measured efficiency. |
| 1 | Rack pressure loss and nonuniform contact | Lower suction pressure, extra head, flow choking/bypass and hot spots can cost compressor mass, power and capture. Resolve the front rack's local thermal loading, not just its blended temperature. |
| 1 | Leading edge, external heating and other drag | Add reusable thermal protection/cooling, spillage/base/fin drag and attitude effects. An impulse-only skin term does not establish survivability or wall cooling mass. |
| 1 | Electrical conversion/distribution | Define bus voltage, conductor lengths/currents, insulation, switching, fault isolation and real PPU/motor-drive boundaries. Resistive/conversion heat and redundant power paths are not represented by the current bus mass coefficient. |
| 1 | Global structure and pressure hatches | Long-hull bending, local/global buckling, thermal expansion, empty-vessel loads, fatigue, seals, hinges and pressure-load paths. Thin membrane vessels and 4 kg/m² hull allowance are insufficient for a construction model. |
| 1 | Deployment mechanisms and cycle life | Replace 1 kg/m² rack mechanism allowance with supports/actuators, acceleration/tension loads, power, failed-deployment recovery and life. SiC attachments and high-temperature aluminum strength/creep need qualification. |
| 2 | Real heat rejection and storage hardware | Select an actual warm-store material/fluid, tanks, pumps, pipes, heat exchangers, phase/pressure limits and realistic radiator areal mass. Include solar/Earth loading, mutual shadowing and emissivity/coating degradation. The current constant-cp store is not qualified ammonia. |
| 2 | Cryogenic process and product quality | Real mixture separation/flash states, recuperators, pinch points, pressure drops, working-fluid inventory, purity and trace-species/freezing control. Finite Carnot efficiency is not a full liquefier design. |
| 2 | Actual compressor maps and manifolds | Low-Re efficiency, surge/stall, rotor stress at temperature, inlet distortion, seals, bearing losses and ducting. The provisional quadratic head/flow law is not a measured operating envelope. |
| 2 | Environment and operational reserve | Density/composition variability, navigation errors, attitude pointing, eclipse seasons, solar degradation, cooldown readiness and availability. A repeatable nominal orbit is not a robust campaign. |
| 2 | Packaging and maintenance | Margin currently adds mass but no volume. Add clearance for mechanisms, plumbing, harnesses, access, insulation, redundant equipment and contingencies; the receiver must surrender that volume. |
| Mission metric | Circular-apogee delivery and replenishment logistics | Docking/offload, export and return trajectories, transfer hardware, propellant and cycle time. Current payoff still measures product in the operating orbit. |

Not every refinement must worsen the result. Resolve overlap between electrical
allowances, replace generic mechanism masses with actual designs, and retain
gaseous-feed and heat-transfer improvements alongside penalties. Do not use a
blanket percentage to predetermine the direction of a trade.

## What to hand to Blender now

Use an explicitly versioned **engineering concept visualization**. Export the
selected config, physical chamber depths and heads, rack envelopes/unit cells,
compressor-bank envelopes, gas-reserve alternatives, folded equipment envelopes,
pressure-hatch positions and deployed areas. Distinguish bore, outside diameter,
pressure-vessel geometry and the aerodynamic outer mold line. Preserve the
fixed 317 m length and the receiver's residual allocation when changing packages.

Show the collection and coast states separately, with a sweep of deployment
paths and clearance. Mark radiation view directions, thruster plumes, electrical
routes, pressure boundaries and thermal zones. The geometric model should be
able to feed revised areas, volumes and routing lengths back to the numerical
package; it must not quietly resize equipment for appearance.

Do not render mass margin as hardware, equate an equivalent gas-storage depth
with a finished tank, or turn the generic bus/rack allowances into asserted
parts. Pin the feed architecture and pressure-hatch/support arrangement before
presenting a manufacturing-level layout. No publishing or external handoff is
performed merely by writing this plan.

## Next agreed scope: packaging snapshot and collector boundaries

Plan only: [plate scale sensitivity](../investigations/plate_scale/PLAN.md), then
[volume, mass-distribution and Blender requirements](PACKAGING_AND_BLENDER_PLAN.md).
Blender production and the three new optimizer runs have not started. Keep v1.0
as the deployable-plate snapshot; investigate fixed exchangers/active coolant in
higher-pressure volumes as the separate v1.1 direction.

The [collector-only metrics](../investigations/collector_metrics/README.md)
formalize captured gas per dry mass when propulsion and coast liquefaction are
outside the collector boundary. They supplement, not replace, useful-liquid
payoff. The first values are frozen-trajectory accounting, not new forward solves.

Publication order update: publish the existing verified reference as v1.0 before the plate-scale sensitivity or Blender. Use the [publication kit](publication/V1_0.md) and [provisional axial/CM study](../investigations/v1_layout/README.md); neither blocks publication on completing mechanical packaging. Dawn–dusk SSO is the mission target, with its seasonal illumination and 3D maintenance still pending in the numerical model.
