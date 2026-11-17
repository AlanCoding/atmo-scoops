# Per-rack sensible materials

The isolated chamber simulation accepts `material` independently in every chamber:
`iron` (legacy default), `fecral`, `sic`, or `aluminum`. Optional
`rack_emissivity` overrides the material surface assumption. This does not change
the primary payoff model or select a flight construction.

| Property | Iron proxy | FeCrAl | SiC | Aluminum |
|---|---:|---:|---:|---:|
| Density, kg/m³ | 7870 | 7100 | 3210 | 2700 |
| Study temperature cap, K | 1042 | 1042 | 1000 | 550 |
| Surface emissivity | 0.8 | 0.7 | 0.8 assumed | 0.8 assumed coating |
| Conductivity screening value, W/(m K) | 40 | 11 | 40 | 150 |

The caps are comparison constraints, **not qualified reusable hardware limits**.
FeCrAl retains the legacy cap; SiC stays within the first NIST fit interval.
Aluminum's 550 K cap is a provisional mechanical screen well below melting;
alloy, temper, loading, oxidation and fatigue require design work. High emissivity
is not a property of bare aluminum. SiC joints, supports and deployment cannot be
assumed to behave as flexible metal wire. Extra material-specific support and
coating masses remain unmodeled; the comparison uses the same deployment allowance.

## Energy, volume and heat transfer

Each material has integrated temperature-dependent specific enthalpy. Each volume
integrates its own solid energy and inverts that material's caloric table for
solid temperature. Out-of-range extensions let rejected trials finish; they do
not grant additional usable capacity.

For radius r, pitch p and rack envelope V, displaced solid volume is
`V π(r/p)²`, mass is density times that volume, and gas volume is chamber volume
minus displaced solid. Wetted area is `2 Vsolid/r`. Thus lower density saves mass
at unchanged geometry, but does not create extra surface or heat capacity per
volume. Each search varies all five rack depths and all five additional empty
depths. Radius and pitch remain 1 and 10 mm for this comparison.

The existing continuum-cylinder/free-molecular conductance bridge uses the actual
gas state, flow and wetted area. Accommodation remains the common uncalibrated
0.8 assumption. Conductivity enters the lumped-temperature validity check
`Bi = h r/(2 k)`; candidates with Bi > 0.1 are rejected. It is not an extra gas-side
heat-transfer multiplier. Internal gradients are not spatially solved. The SiC
40 W/(m K) screen is representative, not a temperature fit; its suitability is
checked against the reported Bi margin.

After draining/venting, reset time integrates each material's cp(T) against
`epsilon sigma T⁴ − 80 W/m²`, using wetted area times the inherited deployed view
factor 0.7. All racks must cool back to their initial 298 K before the next pass,
with drainage and deployment/retraction allowances. This is a post-pass reset
screen, not an assumption that externally deployed racks still cool sealed gas.
A surface with insufficient net radiation at 298 K fails reset. Explicit optional
radiation during the transient also uses the per-rack emissivity.

## Annotated property references

- [Kanthal A-1 manufacturer datasheet](https://www.kanthal.com/en/products/datasheets/material-datasheets/wire/resistance-heating-wire-and-resistance-wire/kanthal_a_1/): FeCrAl density, tabulated temperature-dependent heat capacity, conductivity and oxidized-surface emissivity. Furnace operating temperatures do not establish flight cycle life. Linear interpolation of cp is used.
- [NIST alpha-SiC solid caloric data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C409212&Table=on&Type=JANAFS): Shomate cp over 298–1000 K, integrated for energy. Does not establish rack manufacture or emissivity.
- [Washington Mills SiC properties](https://www.washingtonmills.com/silicon-carbide/sic-properties): solid density 3210 kg/m³ and approximate conductivity range; distinguishes solid density from loose-powder bulk density.
- [NIST aluminum caloric data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7429905&Table=on&Type=JANAFS): solid cp fit; used with nominal solid density 2700 kg/m³. Pure-element caloric behavior is a proxy for an eventual selected alloy, not a strength specification.
- [NIST iron caloric data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896&Table=on&Type=JANAFS): retained legacy comparison, including the change in heat capacity near the upper study interval.

Implementation: `atmo_scoops/chambers/materials.py`, `model.py`, `proxy.py`.
Results and reproduction: [material allocation investigation](../../investigations/chamber_transient/MATERIALS.md).
