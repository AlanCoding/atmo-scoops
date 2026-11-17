# Encapsulated phase-change rack model

The active model supports optional PCM cores independently in the front and each
interstage rack. The default remains ordinary metal. This is a finite-rate,
two-temperature engineering model, not a qualified cell design. Comparative
results and exact reproduction commands are in the [investigation](../../investigations/pcm_racks/ANALYSIS.md).

## Material inputs and evidence

| Core key | Melting K | Fusion kJ/kg | Solid/liquid cp J/(kg K) | Solid/liquid k W/(m K) | Solid/liquid density kg/m³ |
|---|---:|---:|---:|---:|---:|
| `nitrate_eutectic` (NaNO3/KNO3) | 495.15 | 108 | 1355 / 1492 | .3835 / .4574 | 2055 / 1965 |
| `sodium_nitrate` | 579.15 | 178 | 1384 / 1655 | .73 / .514 | 2260 / 1908 |
| `tin` | 505.10 | 60.22 | 230 / 250 | 60 / 30 | 7290 / 6970 |

These are constant-property screening values. Salt cp and conductivity samples
are taken at different temperatures, not fitted functions over the whole cycle.
The sodium-nitrate solid-solid transition is omitted. Tin cp values are rounded
engineering approximations. The casing retains the existing iron cp(T) proxy;
it is not a selected corrosion-resistant alloy.

Annotated primary references:

- [Tombrink and Bauer (2022), Tables 3–4](https://elib.dlr.de/186971/1/Tombrink_Bauer_2022_Rev1_Clean_Version.pdf): measured/reviewed salt transition, heat capacity, density and conductivity inputs. Eutectic fusion heat uses the table's 108 kJ/kg. These establish material properties, not flight-cell cycle life.
- [Bauer et al., sodium nitrate](https://elib.dlr.de/59385/1/NaNO3-Paper_Effstock_Bauer_mit_Header.pdf): room-temperature solid density and molten density, chemical stability and graphite incompatibility. We use 623.15 K as a conservative salt-core screening ceiling, not a qualified lifetime limit. Room-solid-to-liquid volume change is larger than the fusion-only density jump.
- [NIST SRM catalog, p.81](https://www.nist.gov/system/files/documents/srm/SRM-2011-Cat-v2_All.pdf): tin fusion enthalpy and temperature.
- [NISTIR 6586, Table I](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir6586.pdf): solid/liquid tin conductivity used for the screening conduction resistance.
- [Indium Corporation tin properties](https://www.indium.com/products/metals/tin/): solid and liquid densities. Manufacturer material data do not establish containment compatibility.

## Geometry and independent controls

`racks.pcm_material` accepts `none` or a table key. `pcm_materials` overrides it
with one identity per rack; `wire_radii_m` similarly overrides the common outer
radius. Independent `masses_kg` or the existing `mass_factors` remain available.
Cells default to 0.5 m length, 0.5 mm metal wall/end caps, 80% core-cavity filling,
no internal fins and contact resistance 1e-4 m² K/W. These are explicit design
assumptions, not optimized or pressure-qualified values.

For radius r, thickness t and cell length l, the cavity fraction is
`c=(1-t/r)^2*(1-2*t/l)`. Fins occupy fraction f of that cavity. Outer-volume
fractions are metal `1-c+cf`, core `c(1-f)*fill`, and sealed ullage
`c(1-f)*(1-fill)`. Density-weighted fractions determine total assembly mass.
The liquid expansion check requires `fill*rho_s/rho_l <= 1`.

The entire sealed outer volume displaces chamber gas. Rack envelope, gas-accessible
pores, wetted area and deployment footprint follow the ordinary wire-plane
geometry. Output `solid_m3` retains its legacy name but means displaced sealed
body volume for PCM; `material_m3` and `sealed_void_m3` separate its constituents.
The budget's legacy `hot_metal` mass is the complete assembly, including core,
casing, end caps and optional fins. It is not just the metal fraction.

## Thermal states and energy conservation

Each rack has total assembly specific enthalpy H and core-specific enthalpy hc.
Core temperature is piecewise sensible heating, a constant melting-temperature
plateau of width L, then liquid sensible heating. Melt fraction is tracked;
latent heat is never added to a gas heat-transfer coefficient.

```
M dH/dt = Qgas - Qspace
Mc dhc/dt = G (Tskin - Tcore)
H = (1-fmass) hmetal(Tskin) + fmass hc
```

Gas-to-skin convection is the existing finite conductance/rarefaction bridge.
The front gas/skin/core equations are integrated together. Interstage racks use
the existing quasi-steady gas train with finite thermal storage and implicit
core exchange. The investigation checks time resolution; this is still subject
to the existing small-interstage-holdup domain screen.

For total wire length Lwire, contact length is approximated as `fill*Lwire`.
The core conductance has resistances in series:

```
1/G = 1/(4*pi*keffective*Lcontact)
    + ln(r/(r-t))/(2*pi*kmetal*Lcontact)
    + Rcontact/(2*pi*(r-t)*Lcontact)
```

The first term reproduces the ideal constant-wall cylindrical Stefan freezing
time `rho*latent*rcore²/(4*k*deltaT)` in the latent-dominated limit. It is a
reduced conduction approximation, not a spatial moving-interface solution.
The smaller solid/liquid conductivity is used. Optional fins use an explicit
parallel-path conductivity approximation and are charged metal mass; that
approximation needs geometric validation. No liquid natural-convection credit
is assumed in microgravity.

In coast, the skin radiates through the same deployed view-factor model, while
the core freezes through the same finite conductance. BOTH nodes must return to
cold-start temperature plus 0.1 K; the core must fully refreeze. This cooldown
must fit the available deployed coast interval after unfurling. No capacity is
reset for free. `pcm_latent_fraction=0` disables fusion heat for a diagnostic;
hold explicit assembly masses fixed to isolate latent heat rather than resizing.

## Limits and next refinement

Gas-side pressure loss remains omitted by scope. Wetting, void location,
corrosion, fatigue, hermeticity, creep, freezing stress, supercooling and cell
pressure qualification are unresolved. A radius increase lowers surface per
volume and increases the core diffusion time approximately with radius squared.
Thus capacity-per-kilogram alone cannot establish an improvement. An axial,
spatial Stefan model and compatible conductive inserts are logical next tests.
Core/shell redistribution during stowed deployment transitions is not separately
resolved; the coast calculation starts from the encounter's final two-node state.

## Capacity-only sanity check

For 10 mm cells with the default casing/ullage, equilibrated heating from 298 to
600 K stores about 401 kJ/kg of complete eutectic assembly, 457 kJ/kg for sodium
nitrate, and 135 kJ/kg for tin, compared with 154 kJ/kg for the solid iron proxy.
The fusion contributions alone are respectively 71, 120 and 52 kJ/kg of
assembly. These are thermodynamic capacities, **not achievable pass duties**.
The finite-rate simulation determines how much of them is actually accessible.
