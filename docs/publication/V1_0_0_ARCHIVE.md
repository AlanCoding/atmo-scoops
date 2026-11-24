> Historical publication-kit snapshot. Figures at shared paths may since have changed; use its recorded historical inputs, not those mutable images, to reproduce v1.0.0. The current kit is [v1.0.1](V1_0_1.md).

# Atmospheric scoop divers v1.0 — publication kit

This is an editorial working document, not a published article. **Publish the
verified reference now; Blender and further optimization are not prerequisites.**
Freeze the existing plate case 72 as the numerical v1.0 snapshot (checkpoint
`46bf877`; configuration `configs/transient_plates_reference.json`). The axial
layout and dawn–dusk SSO are explicitly labeled design assumptions attached to
that snapshot, not a rerun that improved its payoff.

Suggested working title: **Atmospheric scoop divers: a spacecraft that unfolds
its heat sink**. More numerical alternative: **Atmospheric scoop divers v1.0:
317 metres, seven tonnes of air per pass**.

Aim for **1,200–1,600 words**, six figures, two compact tables and at most two
equations. The full component register belongs behind a link, not as thirty rows
in the post. The tone can be enthusiastic about the machine and exact about
what the numbers mean. No need to narrate every intermediate design or solver
problem.

## Pictures to use, in reading order

- **Opening: [dive/coast overview SVG](../images/v1_overview.svg).** Caption:
  “One vehicle, two operating states: capture and store heat during the dive;
  deploy power and heat-rejection surfaces during coast.” This is a functional
  illustration, not the dimensioned axial layout. The current gas path has five
  coolers and four dive compressor blocks, shown more explicitly below.
- **Orbit: [v1.0 orbit and timeline SVG](../images/v1_orbit_cycle.svg)**
  ([PNG](../images/v1_orbit_cycle.png)). Caption: “85 × 2,000 km, 106-minute
  period. Dawn–dusk sun synchronization is the intended orbit; seasonal lighting
  has not yet been incorporated into the numerical reference.” The equal-scale
  orbit drawing and timeline are current; replace the old 100 km orbit figure.
- **Mechanism: [five cooling volumes and gas/product paths SVG](../images/feed_racks.svg)** ([PNG](../images/feed_racks.png)).
  Caption: “SiC up front, aluminum downstream. The coast-processing flow splits
  between useful liquid and gaseous propellant for the next pass.” This makes
  the absence of a mouth door and the liquefier bypass understandable.
- **Updated v1.0.1 comparison (not this archived design): [cycle histories SVG](../images/v1_cycle_history.svg)**
  ([PNG](../images/v1_cycle_history.png)). Caption: “Gas pressures, solid-cooler
  temperatures and inventories evolve through a complete simulated cycle.” The
  top panel zooms into the dive; the other panels show coast cooling/processing.
  The propellant-reserve curve includes preloaded gas; it is not all new product.
- **Physical tour: [axial mass placement / CM SVG](../images/v1_axial_mass.svg)**
  ([PNG](../images/v1_axial_mass.png)). Caption: “Assigned stowed locations put
  the dry center of mass about 33 m behind the mouth. Equipment spans can overlap
  in different radial sectors; this is not a collision-free mechanical design.”
- **What weighs so much: [v1.0 mass-budget SVG](../images/v1_mass_budget.svg)**
  ([PNG](../images/v1_mass_budget.png)). Caption: “The coolers enable the cycle,
  but power generation, stored electrical energy and propulsion dominate much
  of the mass. The 25% contingency is shown separately.”

Optional substitutions, not additional mandatory figures:

- [Current working scale PNG](../images/v1_perigee_scale.png)
  ([SVG](../images/v1_perigee_scale.svg)): valve-connected 125 m aft reserve,
  planning dimensions and an algebraic perigee estimate. This has no new simulated
  payoff. The rejected boosted-reserve drawing is preserved in its
  [archive](../design_archive/v1.0.1_rejected_boosted/README.md).

- [Three thermal/electrical systems SVG](../images/v1_thermal_cycle.svg): use if
  the distinction between solid heat storage, warm-loop radiation and solar
  supply needs more explanation. Swap this for the detailed gas-path figure if
  the post becomes crowded.
- [Column-physics SVG](../images/column_physics.svg): useful for a short historical
  aside explaining why ram confinement alone was insufficient. It explicitly
  uses an earlier **100 × 2,000 km, no-compressor comparison**, not v1.0. Do not
  present its numbers as the current design.

Do **not** reuse `feed_pitch_histories.png`, the older altitude/payoff charts,
`orbital_cycle.svg`, or `staged_cooling_deployment.svg` as current numerical
results. They refer to older inputs; the last also omits the receiver cooler
and depicts the aft tank remaining sealed while the four front racks deploy.
They can remain linked historical investigations without delaying publication.

## Suggested rhetorical structure

### 1. Start with what the craft does — 100–150 words

Open with the machine rather than the optimization: a long spacecraft skims the
atmosphere, compresses collected air into an aft reservoir, then spreads large
surfaces in space to recover. Connect to the
[project's initial atmospheric-scoop concept](https://alancoding.github.io/concepts/atmospheric-scoop-divers/)
and say this is this project's first numerical reference design, not a flight-ready vehicle.
Use the overview and orbit figures. The memorable scale is **317 m long, 30 m
bore, about seven tonnes of gas captured per pass**.

### 1a. What is inherited, and what is different — about 250 words

**Editorial update:** use the [four-figure break-out article](ELLIPTICAL_COLLECTION_ORBITS.md)
for the expanded comparison. Slough's newly supplied **2022 RON paper** explicitly
includes repeated elliptical collection, batteries and perigee reboost. The
2026 *Space Gas Station* discussed below is a separate design; the original
two-source scope is not a basis for a broader novelty claim.

Suggested prose, with the detailed comparison kept behind a link:

Atmospheric collection is not a new idea, and neither is compressing the gas in
stages. Michael Minovitch's [self-refueling spacecraft patent](https://patents.justia.com/patent/4754601),
filed in 1984 and granted in 1988, describes a diffuser, temporary hot-gas
storage, serial turbocompressors with cooling between them, and cryogenic
products. It explicitly allows liquefaction to continue after the atmospheric
pass. Retractable radiators and using collected nitrogen for propulsion are
also present. Those are precedents, not discoveries of this project.

John Slough's [*The Space Gas Station*](https://msnw.com/?page_id=26), an
author-hosted preprint, explores a different operating regime: a lightweight
collector around 300 km, freezing oxygen onto cryogenic surfaces and using
ambient ions for drag compensation. It also discusses elliptical collection
orbits, dawn–dusk sun synchronization, and the time to collect the spacecraft's
own mass. The mass-payoff metric is therefore shared, too.

Slough's earlier **2022 Refueling Orbital Navigator** is an even closer mission
precedent: it explicitly combines repeated elliptical collection, multi-stage
pumping, compressed-gas storage and battery-backed perigee thrust. Those ideas
also belong in the inherited foundation, as the [break-out article](ELLIPTICAL_COLLECTION_ORBITS.md)
illustrates. It must not be confused with the later cryogenic/ambient-ion design.

The distinction worth investigating here is the thermal cycle. In this v1.0
design, solid plates inside successive compression volumes absorb heat during
a brief, much deeper dive. Those same attached plates then deploy into space
to radiate their stored heat during coast. They are finite heat stores as well
as heat-transfer surfaces. Neither supplied source describes that particular
arrangement. Slough's cold surfaces instead accumulate frozen product; the
patent's staged cooling uses space radiators along the gas path.

Our contribution is a specific implementation and a reproducible,
time-dependent sizing study, including thermal and electrical cycle closure.
That is a narrower claim than inventing atmospheric refueling—and a more useful
one to test. A [source-by-source comparison](LITERATURE_COMPARISON.md) records
the overlaps, distinctions and unresolved assumptions; two documents cannot
establish historical priority.

### 2. Explain how this version handles the heat — 200–250 words

Walk through gas cooling, staged compression, storage and coast processing.
Explain why entry heat is carried temporarily in solid material rather than
requiring all heat rejection at the hottest instant. SiC handles the front;
aluminum serves the cooler stages. Attached plates expose their surfaces to
space after their chambers are emptied sufficiently to open deployment hatches.
The inlet itself stays open. Propellant stays gaseous and bypasses liquefaction.
Use the flow schematic and current cycle histories. Show the plate dimensions
only if they help readers visualize the channels; put all five values in a link.

Optional equation: at fixed local flow, parallel-plate wall friction scales as
Δp = 12 μ L u / g². Immediately explain that wider gaps reduce shear cost but
also reduce heat-transfer effectiveness/compactness. This is why the dimensions
are optimized, not simply made as small as possible. The present model charges
that resistance to compressor electricity without resolving its pressure field.

### 3. Give a short physical tour — 200–250 words

The heavy equipment occupies the first approximately **70 m**. The remaining
**247 m** is mostly receiver. Describe forward batteries/compressors, folded
solar cassettes in dorsal/ventral sectors, later processing equipment, and the
large aft tank. Use the axial graphic, with a link to the
[complete register](../../investigations/v1_layout/MASS_REGISTER.md).

CM is about **33 m** behind the mouth under that assigned layout. Gas loading
moves it less than 0.1 m. This favors an aft stabilizing surface's lever arm;
it does not establish the aerodynamic center of pressure. Keep this assessment
brief and link the [stability screen](../../investigations/v1_layout/README.md).

### 4. Show the payoff and the price — 300–350 words

Lead with **about 278 days of operating-orbit useful-liquid production to equal
the vehicle's dry mass**. Use Table A and the mass chart. This is the principal
result; avoid calling it delivered-to-circular-apogee payoff. Put the expensive
power system next to the result so the reader sees why efficient coolers have
not made the vehicle small.

The useful equation, if including only one, is:

    mass payoff time = dry mass / useful new liquid per orbit × orbit period.

Explain that the optimizer co-solves design choices and cyclic closure constraints
using one forward trajectory per candidate. A brief methodology note is enough:
99 completed evaluations, successful local constrained termination, and a nearby
closure-reserved reference checked at three integration resolutions. No claim
of a global optimum. Detailed numerical history belongs in the linked study.

### 5. End at a real version boundary — 150–200 words

v1.0 is a reproducible numerical design worth showing now. Identify the largest
remaining uncertainties: compressor capabilities, physical inlet/leading-edge
survival, actual cooler transport/deployment and full orbital/illumination
accounting. Keep this to a paragraph, rather than making the post a research
backlog. The intended dawn–dusk SSO has a first-order inclination of **99.35°**;
its seasonal energy and 3D maintenance consequences remain to be modeled.

Finish with two concrete next questions: thicker/more widely spaced plates;
and v1.1 fixed coolant exchangers in higher-pressure volumes to remove awkward
cooler deployment hatches. Blender follows the publication, not the other way
around. Link the repository and the next-work plans rather than promising a
finished spacecraft.

## Table A — headline numbers, ready to adapt

| Quantity | v1.0 reference |
|---|---:|
| Bore / outside diameter / length | 30 / 31.7 / 317 m |
| Nominal perigee / apogee | 85 / 2,000 km |
| Orbit period | 106.03 min |
| Intended SSO inclination (first-order J2) | 99.35° |
| Dry mass | 13,250 t |
| New gas in aft receiver at collection cutoff | 7.11 t |
| Useful new liquid per orbit | 3.509 t |
| Propellant spent per orbit | 3.594 t |
| Operating-orbit mass payoff | 278.02 days |
| Thruster Isp / total burn duration | 1,795 s / 20.38 min |
| Assigned dry CM from mouth | about 33 m |

The gas-at-cutoff and whole-orbit product figures use different endpoints; small
residuals and losses mean their sum is not an exact identity. The published
payoff does not include circular-apogee delivery/return. An 85 km numerical
reference is not a qualified reusable leading-edge operating limit.

## Table B — the three deployed systems

| System | Physical deployed area | Installed mass | Job |
|---|---:|---:|---|
| Solar panels | 1,844,347 m² (1.84 km²) | 3,074 t | Electrical supply and battery recharge |
| Warm-loop radiators | 33,624 m² | 336 t | Process/electrical heat rejection |
| Solid-cooler plates | 107,686 m² | 455 t solid + 108 t mechanisms | Store dive heat, then radiate directly |

Radiator and plate areas here are **physical panel area**, not the sum of two
emitting faces. The warm buffer and other equipment are separate mass entries.
The front solid is silicon carbide, a ceramic; “solid coolers” is more precise
than calling all five inventories metal.

## Optional table — what the optimizer actually chose

Use this instead of a longer methodological paragraph if readers ask what was
free. The [full variable/constraint register](../../modeling/optimization/V1_VARIABLES.md)
lists all 33 scalar values, original bounds, fixed assumptions and closure limits.

| Optimized quantity | Independent scalars |
|---|---:|
| Plate clear gaps, one per volume | 5 |
| Full plate thicknesses, one per volume | 5 |
| Solid-cooler inventories, one per volume | 5 |
| Initial solid-cooler temperatures, one per volume | 5 |
| Solar area; battery energy; warm inventory; warm radiator area | 4 |
| Liquefier flow and electrical ratings | 2 |
| Four dive motor ratings and one coast motor rating | 5 |
| Thruster Isp and burn duration | 2 |
| **Total** | **33** |

Deliberately fixed: **30 m bore, 31.7 m outside diameter, L/D=10, 85 × 2,000 km
orbit**, materials, stage count, suction/head capabilities, peak battery/bus
ratings, schedules, vessel pressure ratings and deployment speed. Receiver volume
is the derived remainder of the hull; its gas pressure and temperature evolve
from the mass/energy balances. They are **not three independently optimized
receiver settings**. The initial cooler temperature is an input, not a fixed gas
temperature. Path constraints enforce pressure/temperature/power/volume limits;
closure constrains end-to-start inventories and stored energy. L/D and perigee
were not released together, so this study does not prove that a longer craft's
optimum lies deeper in the atmosphere.

## Linked numerical assets / source of truth

- [Exact v1.0 configuration](../../configs/transient_plates_reference.json).
- [Verified reference selection and three-resolution results](../../results/transient/plates/reference_selection.json).
- [Constrained plate optimization](../../investigations/plates/README.md).
- [All axial positions, masses and centroids](../../investigations/v1_layout/MASS_REGISTER.md)
  and [machine-readable register](../../investigations/v1_layout/results.json).
- [Sun-synchronous assumption and calculation](../../investigations/v1_layout/SUN_SYNCHRONOUS.md).
- [Plate equations and annotated sources](../../modeling/metal_coolers/PLATES.md).
- [Optional collector-only sidebar](../../investigations/collector_metrics/README.md):
  0.283% captured gas / collector dry mass per pass, excluding propulsion and
  coast liquefaction. Omit from the main post unless discussing mothercraft;
  it is a different boundary and can distract from the principal result.

No new optimization, Blender scene, website edit or publication was performed
for this kit. Figures and the placement register are generated by
`investigations/v1_layout/build.py`; they do not change the forward model.

## Packaging qualification for the scale illustration

The [numerical volume and propulsion review](../../investigations/v1_layout/PACKAGING_REVIEW.md)
provides folded equipment allowances, gas-feed routing and aft-thruster CM
sensitivity. The hull scale is accurate; pod placement and symbolic solar strips
are not a validated mechanical/deployment layout. The literature break-out is
now [published on Medium](https://medium.com/@alanse/atmosphere-orbital-scoop-diver-literature-db3aba700a28).

The scale illustration now shows the valve-connected restoration plan, not the
rejected boosted-reserve simulation. See the [finalized replacement design](V1_0_1.md)
and [version register](../DESIGN_VERSIONS.md). Preserve this distinction when using
it alongside frozen v1.0 publication numbers.
