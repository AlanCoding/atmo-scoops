# Plan: resolve the compressor path and allocate cooling hardware

The [research requirements](RESEARCH_REQUIREMENTS.md) govern the replacement:
real-gas property states, isentropic compression corrected by realistic
efficiency, multiple comparable hardware references for mass, and finite
[gas-to-metal heat transfer](../metal_coolers/README.md). Existing constant-gamma
screening arithmetic is not the planned property model.

**Planning only. No implementation, optimization or new cycle runs are authorized
by this document.** Start with three and four cooled compressor blocks as
separate configurations. A block may contain multiple aerodynamic rotor/stator
stages; this does not select a three- or four-rotor machine.

The current model assigns representative temperatures and cooled compression
work. It tracks inventories and aggregate energy, but does not predict the
spatial gas states or demonstrate that real hardware can maintain those
conditions. The replacement must solve those states from finite machinery and
heat transfer. Prescribed isothermal compression becomes a limiting benchmark,
not an assumed operating path.

## Physical sequence and state accounting

Represent front cooling volume → compressor block → cooling volume → compressor
block → … → rear storage. Give the front rack its own allocation as well as
every intermediate rack. Specify whether final aftercooling uses another rack
or the warm loop; it must not disappear between blocks.

Track each gas volume's mass, species and internal energy over time. Resolve
inlet and outlet pressure, temperature, density, enthalpy, mass flow and velocity
at each compressor and cooler. Keep static and stagnation states distinct where
kinetic energy matters. Track solid temperature along each rack, initially with
a modest number of axial cells rather than detailed CFD.

Each compressor raises gas enthalpy through shaft work and its operating map.
Each cooler removes heat according to its actual geometry and instantaneous
gas/solid temperatures. Pressure losses, finite gas inventories and rising tank
backpressure couple adjacent blocks. Stage flows cannot be independently
prescribed at incompatible steady values: differences accumulate in the
intermediate volumes and change their states.

## Independent variables without redundant geometry

| Group | Independent choices | Derived or solved quantities |
|---|---|---|
| Architecture | Three or four cooled compressor blocks; selected lattice/material family | Number of state volumes, banks and rack allocations |
| Rack i | **Metal mass M_i independently for every rack**, frontal envelope area, and a minimal lattice parameter set | Rack depth, solid fraction, wetted area, free area, hydraulic scale and thermal capacity |
| Intermediate volume i | Physical free-plenum depth or volume, independent of rack solid volume | Gas residence/inventory, acoustic and pressure response |
| Compressor block i | Installed size/module arrangement and admissible drive/control schedule | Mass flow, pressure rise, discharge temperature, power, losses and mass |
| Thermal deployment i | Exposed arrangement and deployment constraints | Effective emitting area/view factors, cooldown and mechanism mass |
| Mixing | Optional injection amount/location and operating policy | Mixed gas states, added throughput, losses and restored coolant inventory |

For example, a declared lattice family might be parameterized by wire/strut
thickness and pitch, or sheet thickness and channel spacing. These are
alternative geometry families, not simultaneous independent descriptions.
For a given family, material density, frontal area and lattice dimensions,
metal mass determines rack depth through the calculated solid volume fraction.
Do not also optimize depth, porosity, wetted area and mass independently.
Count manifold, support and deployment mass separately from heat-storage metal.

Likewise, do not independently command every pressure ratio, every flow rate
and every shaft speed. The compressor map and adjacent volume balances must
close the problem. Target intermediate pressures may guide a controller, but
achievable pressures and flows must remain solved outputs. Separate speed
capability can be explored without assuming it is always lighter or necessary.

## Lattice heat transfer and loss model

For each local state, calculate fluid properties, passage velocity, Reynolds
number and the applicability of continuum/slip/rarefied approximations at the
actual passage scale. Choose heat-transfer and pressure-loss correlations for
the selected lattice family and document their validity ranges and uncertainty.
Do not transplant a packed-bed relation to arbitrary wire mesh without evidence.

Compute local heat transfer from a finite conductance, schematically
`Qdot = h A_wetted (T_gas − T_solid)`, including conduction/contact or fin
limitations when needed. Solve gas enthalpy and solid energy balances together;
use a distributed or effectiveness-based treatment rather than applying the
full inlet temperature difference across a large cooler. Correlate friction,
contraction/expansion and bypass losses consistently with the same geometry.
Assess choking where the flow requires it.

Greater metal mass must buy finite heat capacity and/or geometry changes, not
arbitrarily perfect cooling. More wetted area may also increase pressure loss,
packing volume and deployment cost. The hottest gas and solid locations, and
the end-of-pass temperature approach, are constraints—not freely selected
outlet temperatures or efficiencies.

During coast, solve each rack's radiative cooldown with its deployed geometry,
mutual shading and background. Do not equate internal mesh wetted area with
independently exposed radiating area. The starting temperature distribution
must be restored over repeated cycles; optimizing an arbitrarily cold initial
rack without paying to restore it is invalid.

## Optimization sequence and comparison outputs

1. Establish the state and energy accounting on a fixed three-block design.
   Check finite compressor discharge heating and finite intercooler effectiveness.
2. Expose M_front, M_1, M_2, … independently. Let the optimizer distribute metal
   and its associated geometry/cost; do not impose equal rack masses or equal
   pressure ratios. First compare allocations at a common total rack mass,
   then allow total mass to vary with full spacecraft costs.
3. Release lattice geometry, bank sizing and admissible controls in controlled
   steps. Compare the three- and four-block families under the same capability
   assumptions and cyclic restoration constraints. Keep mixing available.
4. Compare per-block states, pressure losses, rack utilization, compressor
   power/mass and deployment costs before calculating the whole-cycle payoff.
   Report thermal bottlenecks and active constraints, not just the winning mass.

Primary figures of merit are electric work per kg of new air, total compressor
and thermal-system dry mass, net recovered product, and ultimately mission mass
payoff. Preserve the distinction between operating-orbit and delivered payoff.
Pressure recovery, temperature limits, flow-map stability, hydraulic access,
material life and periodic thermal restoration constrain the search.

## Acceptance checks before interpreting an optimum

- Conserve mass, species and energy locally and globally, including shaft work,
  gas kinetic energy where retained, injection, leakage and radiated heat.
- Recover adiabatic compression when heat transfer vanishes, and approach the
  appropriate isothermal bound only with adequate conductance and heat sinks.
- Recover zero cooling as rack capacity/conductance vanishes; demonstrate
  finite storage saturation and repeat-orbit thermal drift when undersized.
- Benchmark cooler heat transfer and pressure loss against applicable data and
  limiting solutions. Check axial-cell and time-step convergence.
- Demonstrate map consistency and stage matching over the complete dive,
  pump cutoff and coast, rather than only a favorable peak design point.
- Keep detailed CFD offline; use it to validate reduced correlations and maps.

Related: [theoretical investigation](SCREENING_CALCULATIONS.md),
[current input definitions](../../analysis/primary/PARAMETERS.md), and
[model improvement list](../../docs/MODEL_IMPROVEMENTS.md).

## Off-design control addition

The [current design](../../docs/DESIGN.md#staged-compression-and-cooling-with-deployable-metal-racks)
now specifies local pressure-retaining rack-deployment hatches as a candidate
layout. Include hatch panels, frames, seals, latches and actuators in hardware
mass; recover interstage inventory and isolate aft storage before depressurizing
each deployment chamber. Charge residual losses and operation time, verify
pressure load cases and repeated sealing/deployment life, and distinguish these
coast-only hatches from the omitted inlet-mouth closure. This is not yet modeled.

The theoretical investigation now includes per-block area/velocity estimates
and the changing tank-to-inlet pressure ratio. Plan for map-based surge/stall
and choke margins across every bank, variable-speed and guide-vane/stator
options, finite rotor inertia, startup/bypass or recycle accounting, and a
stability/head-limited cutoff. Do not assume that only the first bank needs
control, or that a slow atmospheric pressure pulse guarantees stability.
Intermediate cooling volumes must enter the dynamic stability model alongside
the compressor maps and rear tank. This remains a plan, not implemented control.

## Optimize intermediate storage and when compression occurs

Allow every enclosed low/intermediate-pressure chamber's usable gas volume to
vary independently, including the large aft receiver. Report physical depth at
the chosen bore, and derive usable volume after rack/machinery displacement;
do not optimize depth and the same volume as redundant coordinates. Do not
prescribe all intermediate chambers as small flow-through plena. Their inventory
can buffer flow and shift compression into the coast phase.

Jointly optimize installed bank capacity, chamber geometry, independent rack
mass/lattice geometry and each bank's time-dependent operation. Enforce
`dm_i/dt = inlet_flow_i - outlet_flow_i` with the corresponding energy/species
balances. Adjacent banks need not have equal instantaneous flow when a chamber
is filling or emptying. Pressure and temperature histories are solved states;
pressure ratings and operating controls are design inputs within hardware limits.

Compare a predominantly dive-compression schedule with schedules that retain
gas in intermediate chambers and finish transfer during coast. Charge the
additional pressure structure, isolation valves, hatches, leakage, residuals,
thermal inventory and recovery time against any savings in downstream compressor
capacity, peak bus power, batteries and heat buffers. Moving work later does not
automatically reduce total work or installed mass. Independent gas storage must
be sealed from the open inlet; compressor rows are not assumed gas-tight.

Couple this schedule to rack deployment: an intermediate chamber holding gas
cannot open its deployment hatch. Delaying its evacuation delays direct metal
radiation and may limit cooldown before the next dive. Alternative external heat
paths require their own hardware and energy accounting. Enforce the complete
repeatable orbit, not just an economical collection pulse.

Treat the final liquefaction plant's pressure as an explicit process requirement
in the first study, with sensitivity cases rather than a freely invented optimum.
The preferred starting topology is coast compression feeding a small process
buffer and a continuous liquefaction train, with product accumulating in liquid
tanks. Do not require a large high-pressure gas tank for the entire batch. Buffer
size must still support process stability and throughput; conventional process
selection and its operating pressure remain pending.

Report mass and duty by bank, separating volume-flow-driven hardware from
head/power-driven hardware. The first bank may dominate installed mass even
when later banks consume substantial power. Its required peak capacity can
change only if front inventory and the inlet/shock/leakage constraints actually
allow buffering; enclosed downstream inventory does not itself eliminate the
first bank's collection duty. Compare optimized payoff and mass breakdowns to
determine whether deferred compression is a useful lever, rather than assuming
the answer from work fractions alone. This is an owner-requested TODO, not an
implemented optimizer feature.
