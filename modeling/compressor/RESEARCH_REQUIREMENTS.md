# Compressor model: required evidence and formulation

Research before implementation. The existing coefficients are unvalidated;
constant-property screening calculations are not the replacement model.

## Real-gas thermodynamics and irreversible compression

Use composition-dependent thermodynamic and transport properties over the actual
state range: h, s, u, density, cp, viscosity, conductivity and sound speed.
Do not replace the existing isothermal approximation with another constant-cp,
constant-gamma power law. Distinguish temperature-dependent ideal-mixture
properties from a real-gas equation of state. A property package's name does not
guarantee either. Document EOS validity, chemical state, phase validity and any
transition between hot-gas and cryogenic property backends.

For each approximately adiabatic compressor block, using total states and a
declared frozen-composition assumption where appropriate:

```
h1 = h(T01, p01, composition)
s1 = s(T01, p01, composition)
h2s = h(p02, s=s1, composition)       # reversible isentropic endpoint
h2 = h1 + (h2s - h1)/eta_isentropic  # actual irreversible endpoint
T02 = T(p02, h=h2, composition)
P_shaft = mass_flow * (h2-h1)
P_electric = P_shaft / eta_motor
```

Solve the intervening heat exchange separately. If significant heat transfer
occurs inside a compressor, subdivide it and close its energy balance; do not
quietly apply the adiabatic efficiency relation to a strongly cooled block.
Specify total-to-total versus total-to-static efficiency. Test frozen chemistry
against reaction times before assuming equilibrium or frozen composition.

Efficiency must ultimately depend on map position, Reynolds number, Mach number,
clearances and geometry. Until supported by data, use explicit bounded scenarios,
not an optimized efficiency that invents better hardware. Solve interstage states
and match bank flow through chamber inventory balances, including coast operation.

Property references to assess:

- [Cantera thermodynamic state interface](https://www.cantera.org/3.2/matlab/thermo.html):
  entropy/pressure and enthalpy/pressure states support endpoint calculations.
  EOS and phase definitions still determine whether the chosen model is real gas.
- [CoolProp mixture models](https://coolprop.org/fluid_properties/Mixtures.html):
  mixture EOS and interaction parameters offer a real-fluid property route;
  investigate temperature range, phase/flash support and transport availability
  for the actual species. Do not extrapolate a cryogenic EOS into dissociating gas.

## Comparable hardware, not a single guessed specific mass

Build multiple primary-source comparisons for both individual blocks and full
trains: axial fan/compressor rigs, centrifugal stages, Roots vacuum boosters and
coast/process compressors. Molecular pumps provide a regime comparison, not an
automatic candidate for the high-throughput first bank. Obtain independent
manufacturer/test-program families; multiple sizes in one catalog are not
independent corroboration. [Initial hardware evidence](COMPARABLE_SYSTEMS.md)
is a seed, not a completed survey or mass estimate.

For every datum retain model/variant, source page/table/date, measured versus
rated status, gas, inlet/outlet pressure and temperature, mass flow, inlet volume
flow at stated conditions, pressure ratio, speed, efficiency, power, dimensions,
stage count and mass boundary. Separate bare compressor, motor, drive, cooling,
backing pumps, casing and supports. Mark missing fields unknown; never combine
maximum speed, pressure ratio and flow from incompatible operating points.

Derive mass estimates conditional on inlet/outlet states, flow and selected
architecture. Convert Q to mass flow using the source's actual inlet density,
not standard litres or mass flow at our conditions. Fit/derive dimensional
scaling for rotor area/diameter, tip speed, stress, stage loading and casing,
alongside motor/power scaling. Check Reynolds/Mach/Knudsen similarity and pressure
loads before extrapolating. Normalize full-train and single-stage comparisons
separately and avoid charging both for the same hardware.

The desired output is an uncertainty-bounded function of boundary states and
throughput, with discrete bank architecture and duty schedule, not a universal
kg/(m³/s) coefficient. Quantify sensitivity to lightweight purpose-built hardware
without assuming terrestrial packaging mass disappears for free. Include
isolation, idle/spinup power, bearings, thermal growth, service life and controls.

## Deliverables before updating the main program

1. Auditable multi-source evidence table, applicability assessment and missing-data list.
2. Real-gas state/work benchmarks with energy closure, eta→1 and property-domain checks.
3. Stage and whole-train mass estimates with uncertainty and comparable-system cross-checks.
4. Stable maps/control envelope, including startup, reverse flow and outbound cutoff.
5. Proposed reduced model/API, validation fixtures, replacement of specific old
   equations, and sensitivity of payoff to mass/efficiency uncertainty.

Do not claim a validated mass envelope until relevant axial/centrifugal evidence
and a geometry-based extrapolation join the initial vacuum-pump comparisons.
