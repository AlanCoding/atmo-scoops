# Atmospheric scoop divers v1.0.0-alpha — LN₂ mixing and gas retention

**Historical concept, not a validated numerical design.** The original vision
cooled incoming atmospheric gas by **injecting and mixing liquid nitrogen (LN₂)**
inside the mouth. It combined an elliptical scoop pass, ram/shock confinement,
and a mouth closure to retain the batch. It was not an uncooled capture concept.
This retrospective alpha label is distinct from the later numerical v1.0.0;
there is no accepted alpha mass or payoff number.

## Original intent and source history

The public starting point is the author's
[Atmospheric Scoop Divers page](https://alancoding.github.io/concepts/atmospheric-scoop-divers/).
The local page and its earliest recovered revision (`a9e4b26`) already discuss
active cooling restored during coast. The author's clarification here specifies
what that meant: **direct LN₂ mixing, including possible film cooling just inside
the mouth**, rather than an unspecified heat exchanger. The earlier account in
this repository calling the concept uncooled was an error, not a separate
historical version. The website does not fully specify every component or control
sequence; this document records the clarified engineering intent.

The proposed sequence was to admit air during the useful atmospheric encounter,
mix in cold nitrogen to absorb incoming energy, rely on the incoming flow to
confine the mixture, close the mouth before losing the batch, and process and
restore the coolant during coast. The adjacent
[nitrogen-factory post](https://alancoding.github.io/2025/10/08/l1-diamond-nitrogen-factory.html)
also discusses collection and downstream processing, but does not establish a
closed onboard thermal cycle.

## The storage drawback and the key pivot

**LN₂ cooling adds N₂ to the captured gas.** Once vaporized and warmed, the
circulating coolant occupies storage volume and must pass through the gas-handling
system. At a specified pressure and temperature, the ideal-gas comparison is

\[
V = (n_{\rm captured}+n_{\rm coolant})RT/P.
\]

Cooling lowers temperature and therefore helps density; injection also increases
the number of gas molecules. Both effects must be counted. Relative to cooling
the same captured batch to the same temperature without injection, mixing requires
more gas volume. That added inventory was insufficiently appreciated in the
original vision, particularly because tank volume repeatedly limited production.
Recovered coolant is not new product: its compression, recovery, reliquefaction
and any replacement losses belong in the cycle budget.

**Cooling with solid racks, without adding gas inventory, was the key pivot to
[v1.0.1](V1_0_1.md).** The front SiC rack and downstream aluminum racks absorb the
hot-pass heat and reject it during coast. They still cost mass and displace some
gas volume, but their thermal capacity does not require adding coolant molecules
to the stored gas. This is a clear storage advantage; the size of the overall
payoff advantage still depends on real heat transfer, materials and hardware.

A closing mouth does not resolve that storage problem. It can retain gas already
captured, but cannot independently increase the pressure supported during open
collection. The [column analysis](../../modeling/primary/ATMOSPHERIC_COLUMN.md)
explains why increased atmospheric density raises both the arriving inventory
and the ram-supported pressure, leaving the basic volume/aperture requirement
unchanged at fixed speed and thermal state. The later
[mouth-closure investigation](../../investigations/mouth_closure/ANALYSIS.md)
concerns the cooled/compressed architecture, not a definitive rejection of every
mixing-cooled design. Accepted v1.0.1 uses an open mouth and dive compressors.

## Why mixing might return

### Film cooling and leading-edge life

The original injection proposal included a protective gas layer along the inside
of the mouth. The author's current hypothesis is that this may be less important
than initially expected, and that conventional reusable thermal-protection
approaches might suffice for the mouth. That is a research question, not an
established consequence of operating above the denser part of reentry. Leading-edge
radius, local heat flux, catalytic behavior and repeated exposure must be checked
for this inlet; Shuttle or Starship heritage alone does not establish its life.

### Suppressing dissociation and controlling recombination

The more consequential reason to revisit injection may be **chemistry in the
inlet**. Ambient atomic-oxygen abundance is not the whole exposure: hypersonic
deceleration can dissociate incoming molecular oxygen. Recombination can then
release energy at a catalytic surface. NASA's
[surface-catalycity workshop](https://ntrs.nasa.gov/api/citations/20240004999/downloads/ArcjetWorkshop_Catalycity_Final.pdf)
explains why this chemical energy affects wall heating; NASA's
[Shuttle catalytic-heating analysis](https://ntrs.nasa.gov/api/citations/20080026348/downloads/20080026348.pdf)
shows that it is a separate contribution to the surface heat load. These establish
the mechanism, not the dissociated fraction or material lifetime in our scoop.

One candidate is to inject cold N₂ or O₂, as gas or liquid, **upstream of the first
SiC rack**, distributing incoming energy over additional material and potentially
reducing dissociation and reactive-oxygen exposure. This might justify some
storage and processing penalty even when injection is not the cheapest bulk
cooler. N₂ and O₂ injection are distinct chemical/material cases, not automatically
interchangeable coolants.

The suggested **two injected N₂ molecules per incoming O₂ molecule** is an
exploratory ratio, not a calculated requirement. The balance must include the
entire incoming air stream, injection enthalpy, mixing, dissociation energy and
reaction times. Location matters: injection after a shock cannot prevent
molecules from having already dissociated there. Cooling may encourage later
recombination, but does not establish that free O never appears. Neither zero
atomic oxygen nor indefinite reuse is presently demonstrated. Finite reaction
rates relative to flow residence time are essential, as explained by the
[University of Colorado hypersonics research group](https://www.colorado.edu/lab/ngpdl/research/hypersonics).

### A competing route: cooling before full stagnation

Another proposed inlet would admit gas into the plate lattice before full
stagnation, with low incidence angles to cold sheets. The question is whether
distributed deceleration and heat removal could limit dissociation without
injected inventory. Small normal impact velocity does not remove the stream's
tangential kinetic energy; gas–surface accommodation, shear, shocks within the
channels and surface chemistry still determine where that energy goes.

This is an unresolved research direction. Compare plain solid cooling, upstream
mixing, and low-incidence plate entry using a reacting-flow treatment with
appropriate continuum/rarefied validity checks. Track species, residence times,
wall heat flux, catalytic recombination, material loss, pressure recovery and
capture—not just a blended gas temperature. Then determine whether injection
buys sufficient material life to justify its inventory and processing costs.

Optional mixing remains supported in the numerical package. The accepted
v1.0.1 reference takes no credit for these proposed chemistry-control benefits;
its lumped gas/rack model does not resolve them. The alpha concept is therefore
an incompletely resolved mixing-cooled pathway, not proof that mixing cannot work.
