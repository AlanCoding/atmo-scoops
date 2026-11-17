# Phase-change cores in deployable metal coolers

**Optional finite-rate PCM cells are now implemented.** See the
[model specification](../modeling/metal_coolers/PCM_MODEL.md) and
[paired numerical investigation](../investigations/pcm_racks/ANALYSIS.md).
The material survey below remains a design resource, not a selected flight material. Each rack can be made from sealed, thin metal cells containing a
phase-change material (PCM). The external metal remains solid and provides the
gas-contact surface, heat spreading, structural support and radiating coating.
The core melts while absorbing heat during collection and freezes while
releasing that heat to space during coast. It remains attached to the craft.

This can increase usable heat per kilogram and hold the cooler surface near a
chosen temperature. It does not reduce the heat that must ultimately be radiated.
Latent heat is not automatically much larger than sensible storage over a broad
temperature swing; it is particularly valuable when the allowable swing is narrow.
The choice must be assessed per complete cell, including metal skins, internal
fins, expansion space, seals, supports and deployment hardware.

## Match the phase transition to the job

For a pure or nearly eutectic core, a necessary charging condition is
`T_gas_local > T_melt + gas/skin/core temperature drops`. To finish cooling a
stream to a specified outlet temperature while the core is melting, its melting
point must be below that outlet by the required approach. Coast must bring it
below its actual freezing/nucleation temperature, allowing for supercooling,
with time left for the required solid fraction to recover. Solidification alone
need not return the cell all the way to 298 K; its next-cycle enthalpy is what matters.

The table below is a temperature-matching illustration using 710 K front gas,
660 K front material and 600 K interstage gas targets from the earlier capacity
screen. Those are **not prescribed endpoints in the active finite-rack model**:
each gas, casing and core state evolves. The current comparison starts at 298 K.
A 50 K approach is an illustration, not an enforced heat-transfer result.

| Location | Candidate transition range or strategy | Implication |
|---|---|---|
| Front hot portion of the precooler | High-temperature metal/alloy PCM, followed by cooler cells | Raw gas is much hotter than 710 K. A hot upstream PCM can take some heat even if it cannot deliver the final outlet temperature. Resolve the gas profile and surface survivability. |
| Front terminal portion, ending near 710 K gas | Core below roughly 660 K with the example approach | Nitrate salts or tin are plausible temperature matches. Zinc and AlSi12 are too hot for this terminal role. |
| Interstage hot portion, e.g. after a ~1,045 K compressor outlet | Cascaded hotter and colder cores | AlSi12 can absorb the hottest portion; a cooler material must finish the job. Outlet states vary through the pass. |
| Interstage terminal portion, gas target 600 K | Core below roughly 550 K | Tin, bismuth or lower-melting nitrate mixtures merit comparison. Pure sodium nitrate at ~579 K leaves only ~21 K approach, not the example 50 K. |
| Final cooling toward 380 K receiver gas | Lower-temperature core, or existing warm loop | None of the mid/high-temperature candidates below can finish this duty by melting. Low-temperature organic PCMs deserve a separate screen; their radiative rejection is slower. |

**Do not require the same PCM in every stage.** Repeating the same moderate-
temperature core across several terminal coolers could simplify fabrication.
Using a cascade within a rack can instead absorb heat at higher temperatures,
raise radiation flux and preserve the colder material for the final approach.
The useful question is how much heat each temperature band carries, not just
which material has the highest tabulated latent heat.

## Initial material evidence

Numbers describe core material, not an encapsulated flight panel. Temperatures
are kelvin; latent heats in kJ/kg have the same numerical value as J/g.

| Material | Transition | Latent heat | Role and qualification needs |
|---|---:|---:|---|
| Tin | 505.10 K | 60.22 kJ/kg | Conductive metallic core suited to moderate terminal temperatures; modest latent capacity per kilogram. NIST calorimetry reference, not cyclic spacecraft qualification. [1] |
| Bismuth | 544.556 K | 53.146 kJ/kg | Near the example 550 K interstage ceiling; little approach margin and low gravimetric latent capacity. [1] |
| Zinc | 692.59 K | 111.18 kJ/kg | Hotter section only for the current endpoints. The archived NBS certificate supplies these specific values; later determinations differ, so retain provenance rather than false precision. [2] |
| Sodium nitrate, NaNO3 | About 579 K (306°C) | About 178 kJ/kg | Good front-terminal temperature match; poor fit to a 600 K final gas target with a 50 K approach. Low conductivity and containment chemistry require internal heat spreading. [3,4] |
| Binary NaNO3–LiNO3 mixtures studied by Zhou/Eames | Just below 473 K (200°C) | Greater than 220 kJ/kg | Attractive lower-temperature salt candidates for terminal coolers. The study reports two compositions and cycling/chemical tests; exact formulation and phase diagram must be retained in a later material model. [5] |
| AlSi12 eutectic | About 850 K (577°C) | 515 kJ/kg in the cited experiment | Strong hot-zone candidate with high conductivity. It cannot be the only terminal cooler for 710 or 600 K gas. A separate, higher-melting enclosure must retain the liquid. [6] |

[1] [NIST SRM catalog, physical properties p.81](https://www.nist.gov/system/files/documents/srm/SRM-2011-Cat-v2_All.pdf): tin/bismuth transition temperatures and fusion enthalpies. Establishes calorimetric material properties, not panel mechanics or cycle life.

[2] [NBS SRM 2221 zinc certificate](https://tsapps.nist.gov/srmext/certificates/archives/2221.pdf): measured fusion temperature and enthalpy, with uncertainty and heating-rate conditions. This is an archived reference value, not a selected engineering alloy specification.

[3] [Bauer et al., DLR sodium-nitrate investigation](https://elib.dlr.de/59385/1/NaNO3-Paper_Effstock_Bauer_mit_Header.pdf): transition, heat capacity/conductivity measurements and thermal/chemical stability. It finds molten nitrate attacks graphite; conductive filler cannot simply be assumed compatible.

[4] [Thermal energy storage for direct steam generation: materials selection](https://idus.us.es/server/api/core/bitstreams/09bf8c96-7974-456f-ac2a-c4a47d0389c3/content): uses ~178 kJ/kg fusion heat and reports substantial volume expansion (~18%); distinguish room-solid-to-liquid expansion from the approximately 9.7% fusion-only jump in Bauer et al. for sodium nitrate. Expansion space is an explicit design requirement.

[5] [Zhou and Eames, binary sodium/lithium nitrates](https://doi.org/10.1016/j.solmat.2016.08.017): DSC cycling and TGA testing of two mixtures, sub-200°C transitions and >220 kJ/kg latent heat. Their terrestrial tests establish a candidate family, not vacuum containment or mission lifetime.

[6] [Kotzé, simulation and testing of metallic PCM storage, slide 25](https://sterg.sun.ac.za/wp-content/uploads/2013/09/4.1_J.-Kotz%C3%A9_Simulation-and-testing-of-a-latent-heat-thermal-energy-storage-unit-with-metallic-phase-change-materials1.pdf): reports AlSi12 at 577°C, 515 kJ/kg fusion heat, 0.939 kJ/(kg K) heat capacity and 181 W/(m K) conductivity in its property set. It describes a 408 kg test assembly; it does not demonstrate a thin deployable radiator.

[7] [Al–Si cycling and containment experiments](https://www.sciencedirect.com/science/article/pii/S0927024819304945): compares alloy changes under cycling and ceramic compatibility. AlSi12 retained heat-transfer performance better than the other tested alloys; alumina/AlN were promising containment candidates. A ceramic barrier may therefore be required inside a metal cell, with mass and thermal resistance counted.

## How much mass benefit could this mean?

The core enthalpy budget is

`q_core = integral(cp_s dT) + usable_melt_fraction * L + integral(cp_l dT)`.

For a cell, add skin/fins sensible enthalpy, then divide by **all cell mass**.
Usable melt fraction must come from heat transfer and cycle recovery, not be
set to one merely because melting is thermodynamically possible.

The current iron proxy stores about **190 kJ/kg** from 298 to 660 K. Thus tin's
60 kJ/kg fusion heat by itself is not a dramatic improvement over that broad
sensible swing. Conversely, in a narrow 50 K band, a metal with assumed
`cp=0.5 kJ/(kg K)` stores only 25 kJ/kg, making a 178–220 kJ/kg latent term
very valuable. The same endpoint and complete assembly mass must be compared.

One explicit **screening arithmetic example**, not a sourced panel performance:
use 70% salt core, 30% iron-like enclosure/fins; assume core mean cp=1.5 kJ/(kg K),
L=178 kJ/kg and complete melting over 298–660 K. Then

`q_cell ≈ 0.7 * (1.5*362 + 178) + 0.3*190 = 562 kJ/kg`.

That is about 3 times the existing iron sensible capacity, or about two-thirds
less storage-cell mass for equal heat, before separate deployment/support
changes. At only 50% latent utilization the estimate becomes ~500 kJ/kg. Much
of the improvement in this example is the assumed salt sensible heat capacity,
not the phase change alone. It must be checked against real cp(T), chemical
stability, fill fraction and achievable heat-transfer rates.

At the 90 km candidate, the current front metal is only ~640 t of ~26,992 t dry.
A hypothetical two-thirds reduction of this component saves ~427 t before
margin, not two-thirds of vehicle mass. This does not bound the value of
replacing interstage/warm-buffer hardware or enabling colder compressor inlets;
those coupled benefits are not represented by this one-component comparison.
No PCM payoff improvement has been inserted into the main model.

## Does freezing still radiate quickly?

With two unobstructed faces, emissivity 0.8, no absorbed sunlight/Earth heat and
skin at the phase temperature, physical panel area emits

`P/A = 2 epsilon sigma T_melt^4`.

At 470, 505, 579 and 850 K this is approximately **4.4, 5.9, 10.2 and 47.4 kW/m²**.
For a core loading of 10 kg per physical m², the latent-only ideal rejection
times are approximately:

- 220 kJ/kg at 470 K: **8.3 minutes**.
- Tin, 60.22 kJ/kg at 505 K: **1.7 minutes**.
- NaNO3, 178 kJ/kg at 579 K: **2.9 minutes**.
- AlSi12, 515 kJ/kg at 850 K: **1.8 minutes**.

These are optimistic radiative limits, not complete cooldown predictions. Include
sensible heat, a cooler skin than core, mutual views, environment, supports and
freezing kinetics. Ten times the loading takes ten times as long at the same
surface temperature. Higher storage capacity can use the existing radiative
time margin, but it does not make a thicker store discharge instantaneously.

For a planar freezing front, a conduction-only scale is
`t ~ rho L d²/(2 k DeltaT)`, where d is distance from a cooling surface.
As a declared salt example, rho=2,000 kg/m³, L=180 kJ/kg, k=0.5 W/(m K) and
DeltaT=20 K give about **18 s for 1 mm**, but **450 s for 5 mm**. Gas-film,
skin, contact and moving-interface resistance add to this. Thin sealed cells
and compatible internal fins matter; ordinary buoyancy-assisted terrestrial
heat transfer cannot be assumed during microgravity coast.

## Physical integration and next model

Use an array of small sealed cells with metal faces and compatible liners,
internal conduction paths and reserved expansion volume. A large common liquid
cavity would complicate slosh, acceleration loads, leakage and deployment.
Hinges or flexible connections belong between cells; freezing a core should not
be assumed compatible with bending its cell through a tight reel radius.
During the pass the cells experience chamber gas pressure; during coast their
outer surfaces face vacuum. The enclosure must withstand both conditions and
internal vapor/expansion pressure through repeated cycles.

Track each rack's core enthalpy/phase fraction and skin temperature over the
cycle. Solve gas-film transfer, wall/fin conduction, melt/freeze fronts and
pressure loss. Include nucleation/supercooling, phase segregation, corrosion,
volume change, rupture isolation, coating/emissivity durability and cyclic
mechanical stress. Only count the recovered solid fraction available before
the next pass. Optimize core identity, mass, cell thickness and area separately
for each stage alongside compressor inlet temperature and coast duration.

The design decision for now is to retain both sensible-metal and encapsulated
PCM racks as candidates. The first experiments should compare a moderate-
temperature nitrate core against metal-only cells at the same gas duty, and a
hot AlSi12 section followed by a lower-temperature terminal cooler. This study
specifies what to test; it does not select flight materials.
