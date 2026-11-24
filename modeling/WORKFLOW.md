# Research-to-model workflow

1. Define the subsystem boundary, physical states, hardware mass boundary and
   independent inputs. Separate geometry/control choices from technology limits.
2. Collect multiple primary references: measurements, manufacturer operating
   curves, flight hardware or test rigs. Record exact variant, page/table,
   conditions, units, uncertainty, exclusions and source URL. Label theoretical
   derivations separately from empirical capability. A source must establish
   something applicable, not merely mention the same component.
3. Formulate conservation equations and constitutive laws using actual gas and
   material properties. Identify dimensional similarity, phase/regime limits,
   scale extrapolation and uncertainty. State what remains unidentifiable.
4. Build reproducible subsystem calculations and independent benchmarks before
   replacing primary-model coefficients. Check limiting cases, resolution,
   conservation and predictions against comparable hardware not used in a fit.
5. Propose the numerical handoff: state variables, independent design inputs,
   controls, capability envelopes, units, outputs and failure conditions. Name
   the old approximation being replaced and avoid double-counting across systems.
6. Incorporate reviewed relations into the fast numerical package, then rerun
   optimization and quantify how uncertainties affect conclusions. Expensive CFD
   or detailed structural solvers provide maps, not inner optimization loops.

Every dossier states its status: stub, sourced, formulated, benchmarked or
integrated. Do not label old conditional results validated by newer research.
Preserve historic arithmetic as screening evidence with its original assumptions.
Research priorities and dependencies are recorded in the [issue-review index](../local-issue-drafts/README.md). This document defines the evidence workflow, not a separate task queue.
