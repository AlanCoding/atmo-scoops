# Stability, attitude and flexible-body dynamics

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Distributed hardware/gas mass, skirt/fins, aerodynamic forces and deployment disturbances.

## Physics and independent variables to establish

Distinguish vehicle stability from inlet shock stability. Include changing centre of mass, damping, control authority, bending modes and slosh.

## Evidence to collect

Hypersonic aerodynamic derivatives, structural dynamics and flight/control validation studies. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Force/moment maps, loads and control hardware requirements linked to geometry. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `analysis/stability/; analysis/fluid/`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
