# Orbit, atmosphere, export and lifetime

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Atmospheric encounter, uncertain environment, operating orbit and circular-apogee delivery.

## Physics and independent variables to establish

Include finite-thrust trajectories, export/return hardware, mission inventory, component replacement and actual delivered mass payoff.

## Evidence to collect

Atmosphere observations/models, orbital mechanics benchmarks and transport-system engineering studies. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Uncertainty scenarios, conservation checks and delivered-payoff model interfaces. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `system.py; two_volume.py; optimization/`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
