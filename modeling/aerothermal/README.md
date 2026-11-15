# Leading edge, hull heating and reusable materials

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Hypersonic heat flux, radiation, surface chemistry and active cooling.

## Physics and independent variables to establish

Determine allowable perigee from thermal stress, erosion, oxidation and repeat life. Include local film cooling if needed, not just bulk rack temperature.

## Evidence to collect

Reusable hypersonic material and actively cooled leading-edge tests at documented heat flux and atmosphere. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Material/cooling operating envelopes, mass and service-life costs. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `inlet.py; analysis/fluid/`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
