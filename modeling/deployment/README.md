# Rack deployment, hatches and mechanisms

**Current implementation:** [Folded package allocation and area-dependent deployment timing are now implemented](IMPLEMENTED_VOLUME.md). See that specification for scope and unresolved physics.


**Status: first reference research and sizing formulation; not integrated or validated.**

## Scope and interfaces

Stowed racks, pressure closures, booms, seals and repeated coast deployment.

## Physics and independent variables to establish

Recover/isolate gas before hatch opening. Model timing, drive energy, structural mass, packing, interference, thermal distortion and cycle life.

## Evidence to collect

Repeated deployment mechanisms and pressure hatch qualification data; single-use solar deployment is insufficient evidence of cycling life. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. The linked packaging dossier records reviewed sources and their limits; no complete vehicle packaging coefficient is qualified.

## Deliverable and validation

Mass/time/power and reliability versus dimensions; interlocks and cooldown scheduling constraints. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `physical_cycle.py; modeling/compressor/DEPLOYMENT.md`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)

## Close-pass volume research

[Close-pass component allocation and independent chamber volumes](CLOSE_PASS_VOLUME.md).
