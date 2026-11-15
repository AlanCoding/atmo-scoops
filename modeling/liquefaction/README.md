# Coast refrigeration and liquefaction

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Cooled receiver gas through coast compression, process buffer and cryogenic product.

## Physics and independent variables to establish

Select a conventional process and justified operating pressure. Resolve real-fluid states, heat exchangers, pinch points, refrigerator work and rejection; distinguish gas feed compressor from refrigerant machinery.

## Evidence to collect

Multiple air/nitrogen liquefaction plants and space cryocoolers with throughput, efficiency, temperatures and mass boundaries. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Process state diagram, mass/energy closure, scale/duty-dependent installed masses and uncertainty. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `process.py; two_volume.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
