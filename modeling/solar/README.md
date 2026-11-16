# Solar generation and repeatable deployment

**Status: first reference research and sizing formulation; not integrated or validated.**

## Scope and interfaces

Sunlight/orientation to bus electricity and recurring stow/deploy operations.

## Physics and independent variables to establish

Include temperature, radiation degradation, shadowing, harness losses, packing and demonstrated repeated deployment times/life.

## Evidence to collect

Multiple flight or qualification array systems with deployed/stowed dimensions and complete specific power. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. The linked packaging dossier records reviewed sources and their limits; no complete vehicle packaging coefficient is qualified.

## Deliverable and validation

Power/area/mass curves and deployment constraints over orbit and service life. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `two_volume.py; system.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)

## Close-pass volume research

[Folded solar-array volume, reference architectures and retraction evidence](PACKAGING.md).
