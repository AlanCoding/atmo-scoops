# Design investigations

- [Corrected staggered plates and explicit stage geometry](staggered_stage_a/README.md): constrained convergence, five-rack thermal/hydraulic review and numerical scale drawing.

- [Current staged refinement](staged_refinement/README.md): bypass-only optimization first; numerical gates before pressure losses, pitch and radius.

These documents record decision evidence separately from the single current
[design description](../docs/DESIGN.md). Each preserves numerical scope,
assumptions and reproduction inputs; a conclusion is not a chronological log.

- [Gaseous propellant feed](propellant_feed/PLAN.md): evidence, avoided-duty/storage screen, and closed-cycle implementation plan.
- [Rack pitch with pressure loss](rack_pitch/PLAN.md): stage-specific geometry and thermal/hydraulic optimization plan.
- [External skin friction](skin_friction/ANALYSIS.md): implemented impulse penalty and coupled payoff sensitivity.
- [Coupled-cycle reference and initial search](transient/README.md): complete gas, energy, thermal and propellant histories with periodic acceptance.
- [Mouth closure](mouth_closure/ANALYSIS.md): omit it. The freely sized cases gain
  no useful recovery benefit, so its mass worsens payoff. The conditional
  exception and limits remain documented with the complete frozen experiment.
- [Incremental nitrogen mixing](incremental_mixing/ANALYSIS.md): thermal and
  compressor trade, coolant restoration and conditional payoff comparison. Mixing
  remains supported pending improved compressor physics.

- [Rear storage depth](rear_storage_depth/INVESTIGATION.md): block power fractions,
  reduced storage pressure, vessel mass, coast work and conditional payoff;
  includes fixed-hull space reallocation and a 10:1 layout diagnostic.

General component calculations and annotated references live in
[modeling](../modeling/README.md).

- [Altitude and apogee](altitude_sensitivity/ANALYSIS.md): fixed-geometry sweep; [pressure, mass drivers and apogee sensitivity](altitude_sensitivity/MECHANISM.md).

- [Finite racks and constrained geometry](altitude_sensitivity/FINITE_RACK_LIMITS.md): actual convection, wire-thickness trade, folded packages, deployment time, L/D and pressure limits, and a 95 m rear-tank alternative.

- [Phase-change rack cores](pcm_racks/ANALYSIS.md): finite-rate shell/core model, radius/mass/suction sensitivity and matched latent-heat ablation.

- [Fixed-tube liquid cooling](liquid_cooling/ANALYSIS.md): coolant inventory, coast heat pump versus passive radiation, and cold-end temperature sensitivity at prescribed reference duties.

- [Integrated ammonia payoff](liquid_cooling/INTEGRATED.md): coupled inlet/compressor states, finite coolant inventories, regeneration and packing; fixed-orbit comparison with solid metal.

- [Reboost Isp and direct-solar arcs](reboost/README.md): atmospheric propellant, electrical mass, orbital restoration and processing duty trade.

- [Ammonia tube radius and pitch](liquid_cooling/TUBE_GEOMETRY.md): fixed-area geometry sweep, pressure-drop assumptions, wall-thickness control and boiling limits.

- [Transient gas volumes and wire racks](chamber_transient/README.md): independent chamber inventories, compressor connections, coast cooling and liquefaction feed withdrawal.

- [Transient allocation optimization](chamber_transient/OPTIMIZATION.md): atmospheric timing, independent rack/empty-depth search, explicit proxy mass and refined P/T histories.
- [Rack materials and allocation](chamber_transient/MATERIALS.md): FeCrAl/SiC fronts with aluminum downstream, finite heat transfer, volume and reset-time constraints.

- [Centered burn duration](reboost/BURN_DURATION.md): finite-arc impulse penalty versus thruster/bus power, energy and product mass; isolated screening optimum.

- [Gas reserve and rack-spacing integration](feed_pitch/RESULTS.md): separate gaseous propulsion reserve, finite booster/heat rejection and stage-specific hydraulic losses.

- [Rod radius/pitch constrained search](rack_radius/RESULTS.md): per-stage geometry, pressure loss, finite heat transfer and full-cycle constraints.

- [Parallel-plate coolers and constrained optimization](plates/README.md): replaces rod-bank resistance with channel wall friction in the power-only approximation; records the actual COBYLA termination and closure checks.

- [Plate scale sensitivity plan](plate_scale/PLAN.md): planned one-off 1×/2×/4× thickness and clearance comparison, with the other coordinates reoptimized.
- [Collector-only mass yield](collector_metrics/README.md): frozen-reference one-pass battery and solar-assisted subsystem metrics; not a new optimized spacecraft.

- [v1.0 axial placement and stability screen](v1_layout/README.md): complete mass-location register, CM calculation, and dawn–dusk sun-synchronous target.
