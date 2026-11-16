# Battery and electrical equipment volume

**Status: manufacturer module comparisons; no high-power installed-volume fit.**

| Reference | Energy and envelope | Derived package energy density | Limit |
|---|---|---:|---|
| MP Space Pack2 8S3P | 432 Wh at 23°C; 212.9 × 74.9 × 83.8 mm; 2.4 kg; rated current 38 A | 1.336 L; ~323 Wh/L | Manufacturer specifications, not our pulse/lifetime/thermal qualification |
| MP Space Pack2 8S6P | 864 Wh; 218.9 × 172.2 × 84.2 mm; 4.5 kg; max current 38 A | 3.174 L; ~272 Wh/L | Twice the energy does not imply twice the allowed current |
| EaglePicher SAR 10215 sheet | 446.4 Wh, 3.95 kg, published 343 Wh/L; 15 A continuous, 30 A pulse | Published density, not reconstructed enclosure | Sheet says “Concept Design / Product Under Development”; qualification language does not remove that status |

Sources: [MP Space manufacturer table and linked ICDs](https://mpspace.io/products/),
[EaglePicher specification sheet](https://www.eaglepicher.com/sites/default/files/SAR%2010215%201120.pdf).
The MP values above are calculations from published bounding dimensions. They
exclude vehicle mounting/clearance and external cooling/distribution. Do not
combine one module's best energy density with another's best power rating.

Use `N=max(ceil(E_nameplate_required/E_module), ceil(P_required/P_allowed_module))`
subject to series/parallel voltage, current and redundancy constraints.
`E_nameplate_required` includes usable depth, temperature, degradation and losses
exactly once. A stated pulse rating requires duration and duty-cycle evidence;
it cannot be assumed for the 300 s burn. A package's bounding volume times N
is a first envelope sum, followed by mounting, insulation, cooling, isolation,
buswork and routing. Energy-only V=E/e_V is a preliminary comparison, not a
complete module count when power is limiting.

Motors/inverters, thruster PPUs, contactors and cable runs must have their own
geometric records. For cabling, current follows P/V and conductor size follows
allowable loss/temperature; outside insulation and route bend radius govern
allocation. kg/kW does not yield m³/kW without actual dimensional evidence.
Compressor motors already included in compressor mass must not be charged again
as an unrelated electrical package. Their physical envelopes still belong in
the packing map. High-power converters/propulsion packaging is an unresolved
research item, not zero volume.
