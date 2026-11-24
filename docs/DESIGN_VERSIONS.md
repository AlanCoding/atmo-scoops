# Design snapshot register

Use **v1.0.z** for reviewed integrated-design snapshots. Acceptance, numerical
validation and a Git commit are separate statuses. Rejected candidates are kept
under unique names and never silently relabeled as the accepted design.

| Label | Status | Definition |
|---|---|---|
| v1.0.0-alpha | Historical concept, not a numerical design | [LN₂-mixing retention concept and the pivot to solid cooling](publication/V1_0_0_ALPHA.md). |
| v1.0.0 | Frozen historical publication snapshot, formerly v1.0 | Original approximately 278-day plate case 72; preserve its inputs. Historical implementation discrepancies do not imply architecture approval. |
| v1.0.1-rejected-boosted | **Rejected** | Corrected staggered-plate checkpoint e88f733, 275.7 days, with four boosted reserve spheres and a refill compressor. [Frozen archive and SVG](design_archive/v1.0.1_rejected_boosted/README.md). |
| v1.0.1 | **Accepted publication reference; numerical design** | Restored 125 m valve-connected aft reserve, narrowed main receiver, 46-variable constrained solve: 306.4 days operating-orbit payoff. [Results](../investigations/valve_reserve/README.md). No release tag. |

The owner selected the valve-connected design as v1.0.1. Its numerical source is
checkpoint `5a33ef6`; the [publication kit](publication/V1_0_1.md) identifies the
frozen inputs and validation. Acceptance does not imply hardware qualification. Later accepted integrated changes increment z. v1.1 downstream
coolant tubes and v2.0 tether mothership retain their broader architecture meaning.

The [version document index](publication/README.md) is the publication entry point. The completed restoration plan has been consolidated into the v1.0.1 design document.
