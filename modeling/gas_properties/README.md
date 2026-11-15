# Gas composition and real-fluid properties

**Status: research stub; not implemented or validated.**

## Scope and interfaces

Composition, temperature, pressure and phase; carry enthalpy, entropy and energy consistently across every subsystem.

## Physics and independent variables to establish

Validate EOS, caloric and transport properties for hot air, added nitrogen and cryogenic mixtures. Define chemistry and phase treatment; never call temperature-dependent ideal gas a validated real-gas model.

## Evidence to collect

NIST REFPROP and primary species/mixture property measurements; hot-gas chemistry data. Compare independent property predictions in overlap regions. Record multiple primary sources, exact page/table, operating range,
measurement uncertainty and what each source establishes. No references or
coefficients have yet been qualified for this subsystem in this dossier.

## Deliverable and validation

Initial primary reference: [NIST REFPROP](https://www.nist.gov/srd/refprop)
documents real-fluid thermodynamic and transport modeling, including mixture
equations of state. It is a candidate reference/property backend, not a claim
of validity for every hot, reacting or rarefied state in this spacecraft. Record
species coverage, temperature/pressure limits and phase/transport uncertainties.

Property-domain maps, reference states, mixture flash and isentropic endpoint benchmarks. Include conservation and limiting cases, independent benchmarks,
applicability bounds and uncertainty propagation before proposing code changes.

## Numerical handoff

Current integration areas: `nitrogen.py, two_volume.py, process.py`. Define inputs, outputs, units and replacement
equations; identify double-counting at interfaces. Keep detailed simulation offline
and supply validated reduced relations to the primary model.

[Research index](../README.md) · [Review workflow](../WORKFLOW.md)
