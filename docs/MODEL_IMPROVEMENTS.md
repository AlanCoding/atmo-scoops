# Model scope and evidence limits

The accepted [v1.0.1 reference](publication/V1_0_1.md) is a repeat-cycle numerical
study with a 306.4-day operating-orbit payoff. Its limitations are part of that
result, not extra capabilities credited to the design.

Development tasks have been consolidated into [issue drafts for review](../local-issue-drafts/README.md).
The [acceptance review](../local-issue-drafts/PROGRESS.md) distinguishes completed numerical milestones from remaining issue scope. An optional [flat-plate shear screen](../modeling/aerodynamics/FLAT_PLATE_SHEAR.md) now provides a physical alternative to the constant coefficient, with explicit applicability limits; it does not replace the published result.
The former improvement register is preserved there as supporting context; some
of its statements predate the implemented coupled model.

## What is implemented

The reference integrates five gas/rack inventories, four dive compressors,
receiver-dependent coast processing, gaseous propulsion feed through a valve-only
reserve, and electrical and thermal recovery. It uses SiC followed by aluminum
plates, finite heat transfer and storage, physical packing and deployment time.
Real-species compressor work, rotor energy and installed capacities participate in
the budget. Optional mixing remains supported; zero injection is a reference
choice, not a finding that mixing can never help.

## Limits of the published inference

| Area | What the result does and does not establish |
|---|---|
| Inlet and chemistry | Reduced admission/leakage and pressure support; no resolved shock position, reacting inlet, catalytic heat flux or reusable leading-edge qualification. |
| Racks | Finite sensible heat storage and a provisional effective-spacing heat-transfer model. Friction is charged as compressor electricity; a pressure-loss diagnostic does not prove achievable flow. |
| Compressors | Real-property work and conditional geometry/mass estimates; no qualified low-pressure off-design maps, surge/stall envelope or manufactured bank. |
| Propulsion | Finite-burn penalty with capability assumptions; efficiency, Isp, mass, plume clearance and low-pressure gas feed are not a tested integrated thruster. |
| Structure and packaging | Gas displacement and installed/folded envelopes are counted. Buckling, attachments, collision-free deployment and stability are not established by a mass/volume tally. |
| Power and thermal recovery | Scheduled solar/battery/radiator/buffer accounting closes within tolerances. Full hardware qualification, shading and illumination/attitude fidelity are not implied. |
| Cryogenics | Finite processing throughput and power produce receiver drawdown and liquid inventory. A fully engineered separation/recuperation train is not represented. |
| Atmosphere and orbit | Deterministic forcing and impulse accounting support a conditional reference, not robust flight guidance across density variability. Existing exterior Cf=0.002 is an allowance, not calibrated shape aerodynamics. |
| Payoff | Net useful liquid is counted in the operating orbit. Export, circular-apogee delivery and return are unimplemented. |
| Optimization | A scoped local constrained solution with tighter replay; no global-optimality claim. Closure is necessary but not physical validation. |

Completed comparisons and their applicable model versions are indexed in
[investigations](../investigations/README.md). Component equations and annotated
references belong in the [modeling library](../modeling/README.md). The
[version comparison](VERSION_ROADMAP.md) distinguishes the accepted craft from
v1.1 and v2.0 concepts without assigning them numerical benefits.
