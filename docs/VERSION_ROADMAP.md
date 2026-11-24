# Design version comparison

**v1.0.1 is the accepted published numerical reference.** The boosted-reserve
candidate is rejected; the valve-only replacement is accepted. Version labels
identify architecture snapshots, not flight readiness.

| Version | Status | Cooling architecture | Orbital recovery |
|---|---|---|---|
| v1.0.0-alpha | Historical concept | Direct LN₂ mixing; closure to retain gas | Elliptical scoop concept without a closed numerical cycle |
| v1.0.0 | Historical 278-day snapshot | Front SiC and downstream Al plates, directly deployed in coast | Integrated finite-duration electric reboost |
| v1.0.1 | Published 306.4-day reference | Staggered SiC/Al plates with corrected packing | Valve-only reserve and finite-duration onboard reboost |
| v1.1 | Concept, no numerical release | Fixed solid heat stores with embedded coast-recovery channels; front SiC deployment remains an option | Onboard propulsion retained |
| v2.0 | Concept, no numerical release | Diver retains cooling, processing, solar panels and batteries | Mothership/tether release, capture and retrieval; external reboost on mothership |

The [version register](DESIGN_VERSIONS.md), [publication document](publication/V1_0_1.md)
and [reference configuration](../configs/transient_v1_0_1_valve.json) identify the
frozen inputs and results. The published article is
[Actively Cooled Atmospheric Scoop Diver Concept](https://medium.com/@alanse/actively-cooled-atmospheric-scoop-diver-concept-8ae047bc5bb7).

## v1.1 concept boundary

[Fixed solid thermal stores](V1_1_FIXED_THERMAL_STORES.md) retain heat in the solid
during the brief atmospheric pass. Embedded coolant channels primarily restore
that solid during coast through external radiators. This differs from requiring
a large liquid inventory to carry the entire pulse immediately. Downstream racks
can remain inside pressurized tanks, eliminating their extraction hatches while
adding coolant plumbing, supports and regeneration hardware. Hot-pass thermal
access and coast conduction are distinct limits. No mass or payoff improvement
is yet credited.

## v2.0 concept boundary

The diver has no propulsion in the baseline. It retains its own collection,
processing, solar, battery and thermal systems. Mechanical release begins a
multi-pass sortie at a higher apogee; accumulated atmospheric drag lowers the
apogee toward tether capture. The mothership retrieves the diver and restores
the complete system's orbital energy and angular momentum. A velocity match alone
does not establish rendezvous: position and epoch also matter.

System payoff includes both craft, tether, capture/retrieval equipment, ballast,
power and propulsion. A diver-only or gas-only number is not comparable to the
integrated useful-liquid payoff. The [source handoff](V2_TETHER_HANDOFF.md) is an
attributed concept brief, not a solved flight sequence or implementation mandate.

## Development tracking

The proposed sequence, dependencies and acceptance criteria now live in the
[temporary issue-review folder](../local-issue-drafts/README.md). No issues have been
filed. The full earlier roadmap, including tether equations and resonance scope,
is preserved in that folder's supporting specifications. These tasks do not
change the accepted v1.0.1 inputs or publication numbers.
