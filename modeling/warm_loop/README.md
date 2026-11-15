# Warm heat exchangers, fluid loops and radiators

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Residual compressor, refrigeration and electrical heat to deployed radiators.

## Physics and independent variables to establish

Confirm ammonia or alternative fluid pressure/phase limits. Resolve exchanger conductance, coolant flow, pump head, freeze protection, radiator temperature gradients and view factors.

## Evidence to collect

Space radiator and fluid-loop test data, distinguishing panels, plumbing, coolant and deployment mass. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Transient heat balance, pump power, radiator areas and full installed mass with uncertainty. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `process.py; two_volume.py; physical_cycle.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
