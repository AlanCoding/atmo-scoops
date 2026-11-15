# Oxygen propulsion and orbital restoration

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Air-derived propellant, electricity, thrust schedule and restored trajectory.

## Physics and independent variables to establish

Couple Isp, thrust, efficiency, mass flow, specific power, oxygen compatibility and lifetime. Integrate finite thrust and variable mass; no independent free efficiency/Isp.

## Evidence to collect

Multiple electric-thruster test programs with propellant species and measured operating points. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Performance/mass envelopes, reboost impulse and net product accounting. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `two_volume.py; system.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
