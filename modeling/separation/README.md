# Separation, cleanup and product accounting

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Captured mixture, recombination, impurities and recoverable nitrogen/oxygen/argon products.

## Physics and independent variables to establish

Include separation work, equipment, purity, recovery losses and oxygen service requirements; avoid counting recycled coolant as new product.

## Evidence to collect

Air separation and gas cleanup experiments/plants with feed composition, throughput and measured recovery. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Species balances and separation mass/power/loss correlations for the selected process. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `process.py; mixing.py; two_volume.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
