# Two atmospheric-refueling architectures: Minovitch 1988 and Slough 2022

Break-out article draft and illustration kit. These are original explanatory
drawings based on the references, not reproductions of their figures or newly
validated spacecraft designs. The distinction is **collection during a
descending transfer versus repeated collection with perigee drag compensation**.

All four light-scheme SVGs and PNGs are together in
[`docs/images/refueling_precedents/`](../images/refueling_precedents/).

## The four illustrations

- **Minovitch orbit:** [SVG](../images/refueling_precedents/minovitch_1988_orbit.svg) · [PNG](../images/refueling_precedents/minovitch_1988_orbit.png).
  Capture drag lowers apogee on the return from GEO; a final powered maneuver
  raises perigee to circularize in LEO. Intermediate ellipses are illustrative.
- **Minovitch spacecraft:** [SVG](../images/refueling_precedents/minovitch_1988_craft.svg) · [PNG](../images/refueling_precedents/minovitch_1988_craft.png).
  Nuclear power, capture and processing, cryogenic storage, folding radiators
  and the **same vehicle's** microwave/ECR propulsion. Engine inactive in the
  illustrated capture state; dashed radiator envelopes indicate deployment.
- **Slough orbit:** [SVG](../images/refueling_precedents/slough_2022_orbit.svg) · [PNG](../images/refueling_precedents/slough_2022_orbit.png).
  The 150 × 950 km collection ellipse, perigee thrust and coast recharge.
  This is the proposed operating sequence, not our independent orbit simulation.
- **Slough spacecraft:** [SVG](../images/refueling_precedents/slough_2022_craft.svg) · [PNG](../images/refueling_precedents/slough_2022_craft.png).
  Passive intake, active multi-stage pumping, compressed-gas tank, solar arrays,
  battery and Hall thruster. Component positions are schematic.

## Minovitch: refueling on the way down

Michael Minovitch's US 4,754,601, filed in 1984 and granted in 1988, proposes a
large nuclear-electric transport that collects atmospheric gas during its return
from geostationary orbit. The incoming gas supplies braking and new inventory
at the same time. Nitrogen becomes propulsion working fluid, while oxygen can
be retained for other uses.

The orbit diagram isolates that return sequence. A powered maneuver first
lowers perigee into the atmosphere. Collection then lowers apogee. The patent
allows multiple passes, but its numerical example simplifies the encounter to
one dive with approximately 50 km perigee. Afterward, a burn near the new low
apogee raises perigee out of the atmosphere and circularizes the orbit. This
is **aerobraking**, not lithobraking: the craft does not strike the ground.

It would be incorrect to describe this vehicle as lacking propulsion. Its
3,500 MW nuclear-electric system drives an onboard microwave-powered electron
cyclotron resonance accelerator. The preferred embodiment's collector and
powered transport are the same vehicle. The description does not establish the
separate microwave-powered transfer fleet suggested in the initial illustration
brief. Microwave references elsewhere should not be turned into an unverified
fleet or rendezvous architecture.

| Feature | Patent reference configuration |
|---|---|
| Electrical generation | 3,500 MW nuclear-electric |
| Inlet / diffuser length | 22 m / 48 m |
| Overall length / main body diameter | 250 m / 14 m |
| Main propulsion working fluid | Nitrogen |
| Gas processing | Radiation chamber, compression, liquefaction and separation |
| Temporary hot-gas buffer | Approximately 500 m³ |
| Product storage | Cryogenic tanks |
| Deployables | Folding power-plant radiators and accelerator radiators |
| Collection trajectory | Descending transfer; multiple passes or a simplified single dive |

| Storage component | Published capacity | Published dimensions |
|---|---|---|
| Hot-gas buffer, Tank 52 | 500 m³ | Not specified |
| Liquid nitrogen, Tank 149 | 1,000,000 kg | 10 m long × 13 m diameter; toroidal, with a central access tunnel |
| Liquid oxygen tanks | 170,000 kg maximum | Not specified |
| Liquid hydrogen tanks | 20,000 kg maximum | Not specified |

The hypervelocity intake and radiative cooling chamber precede Tank 52; gas
enters that buffer at approximately 1,600 K. The drawing includes a red
**“Isolation valve ?”** upstream of the buffer as an editorial engineering
question, not as a component specified by the patent. The passage about
processing continuing after the **atmospheric pass** motivates asking how hot
gas is retained; it does not by itself prove a particular valve is required or
that the patent specifies one. This is distinct from an apogee passage.

The spacecraft drawing scales its external dimensions together. Interior
component lengths and radiator envelopes are editorial placements. It does
not imply that the illustrated packaging was independently reconstructed from
patent drawings. The radiation chamber's annular fold-back detail is simplified.

**Source:** [US 4,754,601](https://patents.justia.com/patent/4754601), preferred
embodiment, Table 1 and description of Fig. 9. The key trajectory sentence is:

> “the refueling retro propulsion maneuvers 168 on the way back to LEO comprise a series of several atmospheric re-entry trajectories designed to lower the vehicle's apogee 170 until it reaches LEO 150.”

## Slough: recharge between repeated collection passes

John Slough's **2022 Refueling Orbital Navigator (RON)** is a different source
from his later *Space Gas Station* preprint. This distinction changes the
literature comparison materially: the 2022 paper explicitly includes perigee
drag compensation, battery storage and repeated refueling in an ellipse.

A conical intake directs rarefied atmospheric gas toward an active multi-stage
pumping system. Gas accumulates in a pressure vessel, not a cryogenic product
tank. A portion supplies the electric thruster, while the net inventory supports
later servicing and debris-removal maneuvers. Solar generation over the orbit
supports a much more powerful but intermittent thruster through batteries.

The scoop also serves as a passive cooler, transferring deposited heat to space
by radiation (the paper's thermal discussion and Figs. 21–22). The spacecraft
drawing now shows internal dividers suggesting its multiple-cone collection
geometry, and outward thermal-radiation arrows. These are schematic sectional
dividers, not a specified cone count or a reconstruction of one tested array.

The orbit drawing shows the refueling phase of this larger mission. It should
not be read as a claim that the vehicle remains in that ellipse forever: once
refueled, RON leaves to perform the next task. Nor does the drawing independently
verify exact per-orbit element closure. It faithfully shows the paper's intended
perigee-thrust mechanism, which is absent from the later paper's predominantly
apogee-arc compensation argument.

| Feature | 2022 RON reference |
|---|---|
| Collection orbit | 150 × 950 km; worked example uses 151 km perigee |
| Scoop | 3.5 m conical silica reference in Table III |
| Storage | 50 kg gas at 1,000 psi (approximately 69 bar), Table III |
| Pumping | Multi-stage compressor system; turbomolecular collection discussed |
| Thruster | 30 kW Hall-effect reference, atmospheric propellant |
| Electrical supply | 5 kW solar array with batteries for perigee operation |
| Array position | Within the scoop's projected frontal area |
| Product state | Compressed gas; no cryogenic liquefaction train shown |

The source discusses nitrogen and nitrogen/oxygen thruster operation. The
drawing therefore says “nitrogen-bearing atmospheric propellant” rather than
inventing a demonstrated nitrogen-separation plant. Likewise, arrays **behind
the scoop silhouette** need not be folded or stored internally: no folding
mechanism has been added to the diagram. The passive intake does not make the
collection system passive; the pumps require power.

**Source:** [Slough, *Refueling Orbital Navigator for Active Debris Removal, and
Asset Relocation, Recovery and Repair*, IEEE Aerospace 2022](https://msnw.com/wp-content/uploads/2026/09/2022-IEEE-Aerospce-Conference-paper-on-RON.pdf),
pp. 5–6, Table III (p. 11), Fig. 20 (p. 13). The supplied 20-page PDF was checked
against those locations. Page 6, mission stage 3, states:

> “RON will refuel for several orbits using ambient propellant to counteract drag and store fuel for future use in an orbit with an apogee of 950 km and a perigee of 150 km.”

The preceding stage explicitly says it starts firing at perigee for drag makeup.
This is direct evidence of a proposed repeated elliptical refueling sequence.
Our earlier conclusion about the two originally supplied documents must not be
generalized to this third source or to Slough's work as a whole.

## What the comparison actually shows

Both designs collect gas for later use. Minovitch exploits a descent that the
transport mission already needs; Slough 2022 spends stored electricity and
collected propellant to remain in its collection orbit while inventory grows.
Consequently, **repeated elliptical collection, solar/battery power and perigee
drag compensation are established conceptual precedents for this project**.
Any discussion of our contribution must focus on the detailed thermal-storage
architecture, implementation and numerical analysis rather than claiming those
mission-level ideas as new.

The figures deliberately keep the 2026 cold-head/ambient-ion-grid architecture
out of the 2022 spacecraft. The [earlier two-source comparison](LITERATURE_COMPARISON.md)
remains useful only with its original source boundary made explicit.

## Reproduction

Run `.venv/bin/python investigations/literature_figures/build.py` from the repo.
It writes four SVGs and four PNGs (2160 pixels wide, with height fitted to the figure) into
`docs/images/refueling_precedents/` using ImageMagick. Equal-scale
orbit drawings use Earth radius 6,371 km and the stated apsidal altitudes;
they are geometric illustrations, not propagated flight paths. No primary
model inputs, mass estimates or payoff results are changed.
