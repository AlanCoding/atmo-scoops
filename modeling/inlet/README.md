# Inlet, shock, diffuser and leakage

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Freestream state and geometry to compressor-face total/static states, admission and reverse leakage.

## Physics and independent variables to establish

Resolve starting/unstart, rarefaction, non-equilibrium chemistry, rack obstruction and suction-dependent recovery. Keep CFD offline; generate reduced maps.

## Evidence to collect

Hypersonic inlet tests and rarefied-flow benchmarks with geometry and flow conditions. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Conservative transient mass/energy maps, shock clearance and leakage limits. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `inlet.py; analysis/fluid/`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
