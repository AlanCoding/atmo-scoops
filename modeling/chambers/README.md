# Transient gas volumes and solid racks

`atmo_scoops.chambers` is a standalone laboratory in the main package, not a
replacement for `system.simulate`. Its API accepts chamber geometry, compressor
connections, an external inlet history and a schedule. The CLI builds that
history from the existing orbit/atmosphere functions. The
[experiment](../../investigations/chamber_transient/README.md) supplies plots,
controlled comparisons and reproduction commands.

## Modules and independent coordinates

- `model.py`: immutable Chamber, Pump and Schedule inputs; Boundary time series;
  geometry and conservative coupled differential equations.
- `thermo.py`: temperature-dependent frozen-air and iron caloric tables.
- `__main__.py`: editable JSON experiment and orbit-forcing adapter.
- `studies/chamber_transient.py` and `studies/chamber_report.py`: comparisons,
  resolution check and plot/document generation.

For each volume specify diameter, physical depth and rack-envelope depth
independently. Also specify rod radius/pitch, initial metal/gas temperature and
initial pressure. A single metal temperature is a lumped energy-representative
value, not an assertion of spatial uniformity in a real bank. If blending a
nonuniform initial rack, average **specific enthalpy**, then invert to temperature.
For equal material density, `solid = frontal_area * rack_depth * pi*(r/p)^2`;
`free_gas = frontal_area*depth - solid`, `metal_mass = 7870*solid` and
`wire_surface = 2*solid/r`. Empty volume and gas-filled lattice pores are both
counted. A zero rack depth explicitly represents an empty chamber.

## Conserved states and exchanges

Every chamber integrates gas mass m, gas internal energy U and metal energy E:

```
dm/dt = sum(inflow) - sum(outflow)
dU/dt = sum(mdot_in*h_in) - sum(mdot_out*h_local) - Q_gas_to_metal
dE/dt = Q_gas_to_metal - Q_external_radiation
rho = m / V_free
T = inverse_u(U/m)
p = rho * R * T
```

Compressor discharge carries `h_in + shaft_work_per_kg`. Isentropic temperature
is obtained from the variable-cp entropy relation, then enthalpy rise is divided
by isentropic efficiency. Shaft energy is separately accumulated. The controlled
flow is suction capacity times inlet density, with ultimate-pressure and smooth
cutoff reductions, multiplied by `max(1 - (required_head/max_head)^2, 0)`.
This is an explicit off-design **scenario**, not a calibrated compressor map.
Connections have no reverse flow and isolate when stopped. There is no pump,
engine or cryoplant mass estimate in this experiment.

The external boundary supplies incident mass flux, support pressure and total
incoming enthalpy including encounter kinetic energy. The existing compressible
port relation caps entry and permits reverse leakage; it is not a shock solution.
The CLI currently uses fixed molecular-air composition, not changing atmospheric
chemistry. Outside the tabulated encounter interval it sets external supply and
support to zero while retaining an open inlet.

Gas-to-wire heat exchange reuses the cylinder/free-molecular conductance bridge
in `racks.py`, evaluated at film temperature. Signed `UA*(Tgas-Tmetal)` permits
both cooling and reheating. Flow velocity comes from adjacent flows or an explicit
mixing-velocity floor (default zero). At zero flow the model's residual conduction
is only a sensitivity approximation; the gas remains a lumped, well-mixed node.
No gas pressure drop across the lattice is charged.

Withdrawal represents feed to a coast liquefaction system: specified rate times
`max(1 - pressure_floor/p_receiver, 0)` after its scheduled start. Removed enthalpy
is accumulated along with removed mass. This does not assume that disappearing
gas has become liquid without electricity; cryoplant dynamics and work lie outside
this subsystem boundary.

Optional external radiation is `emissivity * sigma * effective_area *
(Tmetal^4 - Tsink^4)` after a linear exposure ramp. The default effective area is
zero. Nonzero area represents an explicitly assumed thermal connection to space,
not radiation through a closed vessel. Gas/metal contact can be disabled separately
for diagnostic comparisons. No moving-solid volume or deployment mechanism is
silently included; both volumes and metal masses stay fixed.

## Properties, limits and verification

Air uses frozen N2/O2/Ar mass fractions 0.755/0.232/0.013 and an ideal EOS, with
Cantera caloric functions tabulated over 200–15,000 K. Heat capacity is not a
constant gamma. [Cantera's species-thermodynamic documentation](https://www.cantera.org/stable/reference/thermo/species-thermo.html)
establishes the NASA polynomial representation of cp, enthalpy and entropy;
it does not validate this frozen-composition flow approximation. This is distinct
from the main model's HEOS mixture calculation. Reacting high-temperature gas,
nonideal high-pressure behavior and condensation are not supported here.

Iron uses the existing Fe correlation over 298–1042 K; constant endpoint cp
extensions permit a diagnostic run to finish, but out-of-reference-range metal
states are flagged. Air-table boundary hits and appreciable gas above 2000 K are
also flagged. Temperatures for less than 1e-8 kg gas are reported null; internal
near-vacuum arithmetic must not be interpreted as a physical vacuum temperature.

BDF integration is segmented at schedule discontinuities. State variables use
kg and MJ; audit ledgers use the same enthalpy reference as chamber states.
Internal flows and gas/metal exchange cancel exactly in the global balance.
The remaining terms are inlet/leakage enthalpy, shaft work, withdrawal enthalpy
and external radiation. Raw mass and energy residuals, minimum integrated mass,
material flags and a refined-step comparison are preserved in results.

Next refinements: validated low-flow mixing and local temperature gradients;
compressor maps and shaft schedules; pressure-vessel structure and supports;
explicit rack deployment versus retained-gas heat paths; composition/real-fluid
properties; gas-to-wall transfer and heat leaks; coupled coast liquefaction.
The primary model's 1% intermediate-holdup restriction is not applied here,
because these chamber inventories are now independently integrated. That does
not turn the remaining lumped-flow assumptions into physical validation.

The [allocation search](OPTIMIZATION.md) varies rack and empty depths using an explicitly approximate mass/product proxy, separately from the primary optimizer.

Per-rack material identities, property sources and reset constraints are documented
in [MATERIALS.md](MATERIALS.md). The isolated model supports iron, FeCrAl, SiC and
aluminum independently in each chamber; the primary system model is unchanged.
