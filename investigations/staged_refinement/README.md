# Staged model refinement

[Current numerical results and gate status](RESULTS.md).

[Power-only loss estimate](POWER_ONLY.md) freezes saved gas states and flow and
charges resistance as additional compressor electricity at 1%, 10% and 100%.
It does not run the coupled hydraulic solve or change the active reference.

[Power-only pitch and radius searches](POWER_OPTIMIZATION.md) integrate that
energy charge into the finite motor, electrical and thermal budgets, then
release geometry at 10% and 100% resistance. The simplified model and its search
results remain distinct from the pressure-coupled reference.

[Reduced head-loss continuation](REDUCED_LOSS.md) tests smaller resistance
multipliers without releasing pitch or radius. This is a numerical homotopy,
not a calibrated reduction in physical rack drag.

The active reference is the gaseous-propellant bypass with fixed rack geometry
and a verified **1% resistance coefficient**, documented in the continuation
study above. The zero-loss reference is preserved for comparison. Full-loss
numerical reliability remains unresolved. The previous joint 55-variable lattice
search is experimental, not the active vehicle reference.

## Ordered release gates

1. **Bypass only:** retain the historical mixed-volume cooling law, 1 mm rod
   radius, 10 mm common pitch, existing rack inventories and chamber allocation.
   Optimize propulsion, installed electrical/thermal capacities and plant rating.
2. **Fixed-geometry pressure loss:** add the inline laminar resistance law while
   preserving the same thermal law, flow proxy, geometry and numerical settings.
   Re-optimize controls/hardware before changing geometry.
3. **Pitch:** release five common axial/transverse pitches, holding radius fixed.
   At a pitch change preserve solid inventory by changing rack depth; count rounded
   rows, solid displacement, minimum chamber envelope and deployed footprint.
4. **Radius:** release radii only after the pitch stage passes numerical checks.
   Retain the owner's 0.2 mm lower bound.

Each candidate is one forward integration, with hardware compiled first. No inner
closure solve or automatic resizing is introduced. A small feasible coordinate
poll replaces the poorly resolved all-at-once search. Jointly favorable directions
are checked in a separate complete trajectory before accepting their combination.

An accepted reference must pass all existing physical/closure and numerical audits.
Re-evaluate it at smaller time steps and tighter tolerances; require relative
product/payoff changes below 0.5%. Numerical failures are recorded separately from
physical infeasibility. If a stage cannot supply a reliable reference, retain the
last validated stage and explicitly leave subsequent variable releases pending.

## Isolation of pressure and heat-transfer changes

`rack_pressure_model="inline_laminar"` selects the published low-Re array pressure
coefficient independently of `rack_flow_layout`. Thus stage 2 does not also switch
to the Leveque thermal correlation or change the mixed-volume flow proxy. The
historical cylinder-based exchange law remains an approximation for an array;
this staged comparison isolates the effect of adding hydraulic resistance, not
validation of a final paired heat/drag correlation. The old coupled inline-bank
thermal option remains experimental and is not the active baseline.

The gas branch includes its tank, booster, aftercooler, jacket, feed limits,
compression work and cyclic inventory. Only the product branch is liquefied.
Materials remain SiC in front and aluminum downstream. Bore, hull L/D, perigee,
material capabilities and skin-drag assumption stay fixed across the stages.
Payoff still ends in the operating orbit; circular-apogee delivery is absent.

## Numerical treatment

The bypass baseline uses direct HEOS compression, not the optional property-table
accelerator. Refinement halves the supplied maximum time step and relative
integration tolerance and reduces absolute tolerance tenfold. It always tightens
the supplied settings, including when refining an already-tightened head-loss case.

Identical trial-flow evaluations are cached only inside each hydraulic root solve
and each current RHS evaluation. Nothing is reused across time/state changes.
A direct pump benchmark gave identical flow, suction pressure and specific work
before/after caching; its runtime fell from 1.63 to 1.27 s for 1,000 calls. This
removes duplicate HEOS calculations; it neither changes the equations nor cures
low-inventory integration stiffness. Timed-out/stagnating trajectories remain
unresolved, never accepted by relaxing conservation or closure tolerances.

An optional `integration_segment_s` diagnostic restarts the integration method's
history at fixed intervals while carrying the entire state and ledger forward.
The 60 s probe preserved the bypass result but did not cure the head-loss stall.
It is disabled (`0`) in the active configuration and is not a physical control.
