# Literature comparison for the v1.0.1 publication

**Scope update:** the subsequently supplied **Slough 2022 RON paper** explicitly
describes repeated elliptical refueling with battery-backed perigee thrust.
It is a different source from the 2026 *Space Gas Station* reviewed below.
See [the illustrated break-out article](ELLIPTICAL_COLLECTION_ORBITS.md). Do not extend
this original two-document comparison into a claim that Slough never described
such a cycle, or that this project originated perigee-reboost collection.

This supports [the publication kit](V1_0_1.md).
It compares the two documents supplied by the author with the accepted v1.0.1
reference. It is not an exhaustive literature search or a determination of
patent novelty. Absence below means **not found in these two disclosures**, not
that nobody has proposed it. No numerical model assumptions were changed by
this comparison.

## Sources and how to read them

**M — Michael A. Minovitch, US 4,754,601, *Self-refueling space propulsion system
and operating method*.** Filed December 18, 1984; granted July 5, 1988.
[Public patent text](https://patents.justia.com/patent/4754601).
The supplied pasted text reproduces the description and claims. Its heading's
1984 date is the filing date, not the grant date. Locators below use numbered
components, figure references in the description, and claims because the pasted
copy has no stable page numbers. The numerical examples are proposed designs,
not evidence of demonstrated hardware.

**S — John Slough, *The Space Gas Station*, supplied 34-page version.**
[Author's page](https://msnw.com/?page_id=26) and
[public PDF](https://msnw.com/wp-content/uploads/2026/08/The-Space-Gas-Station-AA-paper.pdf).
The author's page labels it a preprint submitted to *Acta Astronautica*; do not
describe it as an accepted, peer-reviewed journal article on that evidence.
Page numbers below refer to the printed pages, which match PDF page order.
The collector drawings and mass tables were checked against the rendered PDF.

## Feature-by-feature comparison

| Feature | What the supplied literature already describes | What v1.0.1 does / defensible distinction |
|---|---|---|
| Atmospheric collection and self-refueling | M: atmospheric ingestion during decelerating maneuvers, then use of collected gas for propulsion. S: an orbital propellant-production station. | Shared premise. Producing useful liquid rather than only consuming intake gas is not new here. |
| Deep atmospheric passes | M: worked Earth maneuver reaching roughly 50 km; it deliberately uses capture drag for deceleration. S: primarily much higher collection altitudes. | Our 85.8 km pass is a different reference, not a new deep-dip principle. Repeated restoration of a production orbit differs from M's illustrated transfer maneuvers. |
| Staged compression with intercooling | M: holding tank 52, turbocompressors 53 and 58, radiators 54 and 60; description of Fig. 4. Compression raises temperature from about 500 to 1,000 K, followed by cooling back toward 500 K. | Explicit precedent. Four dive compressor blocks and five finite gas/cooler inventories are this project's implementation, not invention of intercooling. |
| Buffering capture and processing later | M: approximately 500 m³ temporary hot-gas tank; liquefaction explicitly continues after the atmospheric maneuver. S: frozen inventory is accumulated and later regenerated (§2.5). | A large aft receiver and coast processing are refinements of an established separation in time. |
| Handling entry heat before cryogenic cooling | M: hot-gas radiation chamber and subsequent radiators. S: warm collector wall takes arrival/recombination energy; cold louvers capture re-emitted molecules (§§2.2–2.4). | Shared thermal objective. Our finite sensible-heat plates and their deployment cycle are the specific difference. |
| Deployable cooling surfaces | M: retractable radiators stowed in atmosphere and extended outside it (claims 53–54). S: deployable collector and cold-head supports; closure for regeneration (Fig. 4, §2.5). | Deployment alone is not new. Neither source describes extracting the same interstage solid heat stores to radiate the heat accumulated during each dive. |
| Cryogenic products and propulsion species | M: separation, nitrogen propulsion and saved oxygen; liquid storage followed by vaporization for the illustrated accelerator. S: oxygen reference, plus nitrogen collection/propulsion in elliptical variants (§4.3). | Our gaseous propellant reserve bypasses the liquefier. This is a specific accounting/architecture choice, not a claim to invent gas-fed electric propulsion or nitrogen use. |
| Solar power and stored electricity | M explicitly permits solar-electric power and battery/flywheel alternatives to its main nuclear/superconducting embodiments. S uses solar power. | Shared technologies; “solar instead of nuclear” is not a sound novelty claim against the whole patent. |
| Elliptical collection and sun synchronization | S explicitly discusses dawn–dusk SSO and elliptical collection orbits (§§4.2–4.3). | The 85 × 2,000 km reference and its timing differ. Our intended SSO lighting remains an assumption, not a demonstrated benefit in the simulation. |
| Mass payoff and sizing | S defines time to collect the craft's mass (Eq. 13, pp. 21–22) and develops scale/orbit tradeoffs (§6). | Shared metric. Our contribution is the coupled transient implementation and constrained design/closure search, not the first quantitative scoop study. |

## The narrower contribution worth describing

The clearest architectural distinction in this comparison is **a repeated cycle
in which the same solid surfaces receive heat from gas inside successive
compression volumes, then deploy to space and radiate their stored energy**.
They provide finite thermal capacity during the pass rather than requiring
instantaneous rejection of all that heat. The current reference uses SiC at
the front and aluminum downstream; it does not depend on phase-change storage.

There are superficially similar pieces in both sources. Minovitch has staged
cooling and retractable radiators. Slough has louvers, deployable supports, and
alternating collection/regeneration. But Slough's cold head is a cryogenic
product collector that must be warmed for regeneration, whereas our solids
warm while cooling the gas and must cool again to reset. These are different
roles despite both involving surfaces and thermal cycling.

Describe that arrangement as **a potentially distinctive combination**, not a
verified first invention. Likewise, our 33-coordinate optimization, finite
gas/solid energy balances, and end-to-start inventory/energy constraints are
concrete research outputs. They do not establish that earlier literature never
used optimization or that numerical closure validates the compressors, inlet,
leading edge, or deployment mechanism.

## Why the payoff numbers are not a direct contest

Slough's main reference is a 5 m-radius collector near 300 km, approximately
170 kg launch mass and 490 kg/year oxygen collection: about four months to
collect its own mass (§5, Table 3, Eq. 13). The very low-density flow is treated
as collisionless (§2.3), and the ambient ion accelerator obtains its reaction
mass from the ionosphere rather than consuming an onboard product allocation.
That physics is not our dense-pass shock/diffuser and compressor model.

Our v1.0.1 reference is 12,840 tonnes dry, about 3.086 tonnes of useful new liquid per
106-minute orbit, and 306.4 days of **operating-orbit** payoff. It spends about
3.101 tonnes of onboard gas propellant each orbit. Circular-apogee export and
return are not included. The sources use different products, propulsion,
thermal loads, mass models and delivery boundaries. Their numerical payoff
estimates should be reported as conditional results, not ranked as though only
the cooler design changed. For example, S's Table 3 assumes 500 W/kg solar
arrays; this reference uses 150 W/kg.

## Ambiguities and qualifications to preserve

- **Slough's “liquid oxygen” production includes an intervening solid store.**
  The collection surfaces operate around 25–30 K at extremely low pressure,
  accumulating oxygen frost. Regeneration closes the collector, warms the cold
  head and pumps gas toward storage (§§2.2, 2.5, pp. 5–6 and 11–13). Calling the
  entire station compressor-free would overlook the pump and the compressor
  included in Table 3.
- **Capture efficiency is partly an extrapolation.** The trajectory analysis
  gives about 93% for the modeled specular geometry; the roughly 96% figure
  includes an estimated diffuse-reflection improvement (§2.3, pp. 9–10).
  Neither number is a measured collection result.
- **Cold-head load is uncertain within the paper.** Table 1 (p. 11) spans
  15–25 W optimistic, 25–50 W most likely, and 250–300 W conservative. Table 3
  sizes the cryocooler around 40 W below 28 K. Cite that adopted case rather
  than treating the mass budget as independent of accommodation/recombination.
- **Slough presents several orbit/design cases.** The main 300 km circular
  reference, the 275 × 375 km discussion (§6), and Table 4's 250 × 300 km
  variants should not be merged into one design. On p. 27, Table 4 gives
  3.5 t/year for the upscaled case but the following prose says 20.5 t/year.
  The discrepancy is visible in the PDF; use the main reference when quoting
  payoff, and do not silently select the more favorable number.
- **Minovitch's specific hardware assumptions are not validated inputs for us.**
  Its transparent hot-gas radiation chamber, high-power electrical systems,
  and approximately 500-atmosphere feed to the illustrated liquefier are part
  of its proposed implementation. They establish disclosure of a scheme, not
  experimentally supported mass, survival or efficiency. Its capture drag is
  useful braking during the illustrated maneuvers; restoring our repeated
  production orbit still requires an explicit momentum/energy budget.

For publication, the short subsection is sufficient. Keep this comparison
available for readers who want to see exactly why a feature is being credited
to the earlier work or identified as a difference.
