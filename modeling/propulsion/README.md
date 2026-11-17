# Atmospheric-propellant propulsion and orbital restoration

**Status: reduced impulse/power budgets implemented; hardware performance remains unqualified.**

[Variable Isp and direct-solar equations, accounting and annotated references](REBOOST_INVESTIGATIONS.md) document the current investigations. The coupled transient model supports nitrogen/oxygen propulsion and the finite-arc penalty. See the [gas-feed/bypass research and implementation plan](../../investigations/propellant_feed/PLAN.md) and [skin-friction impulse study](../../investigations/skin_friction/ANALYSIS.md).

## Scope and interfaces

Air-derived propellant, electricity, thrust schedule and restored trajectory.

## Physics and independent variables to establish

Couple Isp, thrust, efficiency, mass flow, specific power, oxygen compatibility and lifetime. Integrate finite thrust and variable mass; no independent free efficiency/Isp.

## Evidence to collect

Multiple electric-thruster test programs with propellant species and measured operating points. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. The linked dossier provides initial references; no O2/N2 efficiency or mass map is yet qualified.

## Deliverable and validation

Performance/mass envelopes, reboost impulse and net product accounting. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current coupled integration: `transient/`; legacy scalar: `two_volume.py; system.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
