# Finite metal racks in the primary cycle

Implemented in `atmo_scoops/racks.py`, `inlet.py`, `compressor.py` and
`two_volume.py`. Enabled by default through the `racks` input section. This
replaces prescribed front temperature and ideal intercooler endpoints in the
active calculation. It is a reduced engineering model, not a validated mesh or
hypersonic heat-exchanger design. Lattice pressure drop is **deliberately zero**
for this investigation, at the owner's request.

## Geometry and independent inputs

The declared geometry is alternating transverse wire planes, separated axially
by one pitch. Wires within each plane have the same pitch. Adjacent planes do
not intersect, so there is no intersection-volume double count. With radius
`r`, pitch `p`, metal density `rho_m`, and individual rack mass `M_i`:

```
solid fraction = pi (r/p)^2
solid volume = M_i/rho_m
rack envelope = solid volume / solid fraction
gas pore volume = rack envelope - solid volume
wetted wire area = 2 solid volume/r
minimum chamber depth = rack envelope / chamber frontal area
unfurled footprint = wire length * pitch = solid volume/(pi r (r/p))
```

The front input depth is now a **minimum**. The actual chamber is enlarged if
its rack will not fit. Only solid metal is subtracted from that chamber's gas
volume; rack pores are not subtracted a second time. Each intermediate rack has
its own mass, envelope, pore volume, thermal state and minimum depth. Intermediate
rack depths are added to hull allocation. Their current reference frontal area
is the inner bore area; choosing smaller local flow paths remains future work.

`racks.masses_kg` can specify all four masses independently. An empty list invokes
an explicit sizing rule: the front mass uses the geometric atmospheric column's
heat load divided by the chosen Fe enthalpy interval; intermediate racks use an
estimated per-block compression duty. `mass_factors` independently multiplies
these four reference masses. These are sizing coordinates, **not temperatures
that the solver must achieve**. Actual heat transfer, gas temperatures and rack
utilization are calculated afterward. `design.compressor_inlet_K` and its approach
remain sizing targets in this automatic rule, not imposed gas states. The old
foil thickness does not size an active wire rack.

## Heat transfer and gas states

The front chamber integrates mass, oxygen inventory, gas internal energy and
solid enthalpy. Admission brings atmospheric sensible/chemical enthalpy plus
orbital kinetic energy. Pumping and leakage remove the instantaneous gas
enthalpy. The finite surface transfers `h A_w (T_g-T_m)` to the metal. Gas
pressure follows its changing mass, temperature and metal-displaced volume.
Fe heat capacity is the existing NIST Shomate proxy, with an enforced 1042 K
upper material/property limit. Peak-flow Biot numbers are reported to assess the lumped-wire assumption;
this does not predict axial hot spots, oxidation or wire life.

The continuum estimate uses Churchill–Bernstein for crossflow over a cylinder:
`Re=rho v (2r)/mu`, with gas velocity through the gaps of a wire plane. Gas
viscosity uses Sutherland's approximation and conductivity is `mu cp/Pr` with
Pr=0.71. A kinetic free-molecular conductance with an explicit accommodation
coefficient is combined in series with the continuum conductance. This limits
continuum extrapolation at low pressure. Reynolds, Knudsen and Biot numbers are
reported. This interpolation is a **sensitivity model**, not a calibrated
rarefied wire-bank correlation. Very low Re·Pr, bank shielding, large temperature
ratios and chemical surface reactions require further validation.

The inlet port is linearized within a 0.1% relative pressure difference to
avoid the square-root singularity at equal pressures in the stiff thermal ODE.
A tenfold reduction of that numerical interval changes the reference payoff by
less than one part per million; the separate convergence report records this.

The front thermodynamic table uses Cantera molecular-air enthalpy/internal
energy, with incoming chemical energy retained. It does not resolve shock-layer
reaction kinetics. Very tenuous startup gas can leave that molecular regime;
reported compressor-domain checks apply to significant pumping flow. This is
not a prediction of startup shock temperatures. Compressor states themselves use
CoolProp HEOS N2/O2/Ar, isentropic endpoints and the specified efficiency.

After each of the first three compression blocks, finite `UA/(mdot cp)` gives
the cooler outlet temperature. Real-fluid enthalpy differences determine heat
transferred to that rack; its accumulated enthalpy changes subsequent cooling.
The fourth block feeds the warm aftercooler and rear receiver. No interstage
rack is magically reset to 600 K during the pass. The reference 600 K is only
used in the pressure-ratio allocation rule. The warm loop still absorbs final
aftercooling and remaining electrical losses. Coast compression retains its
separate active intercooled heat-exchanger assumption.

## Intermediate inventories: explicit approximation boundary

Intermediate pores contain gas at their computed pressure and temperature.
Their inventory is subtracted from gas reaching the aft receiver, and residual
interstage gas is vented and charged as lost product before rack deployment.
Its energy is also charged; HEOS/Cantera energy-reference offsets are reconciled.

The series train currently uses quasi-steady equal gross flow through blocks,
not independently actuated intermediate storage. Pressure feedback from the
small intermediate hold-up is neglected in the front encounter integration.
A named screen rejects cases whose maximum intermediate hold-up exceeds **1%
of the batch**. This is a numerical approximation criterion, not a physical
chamber-size limit. Designs intended to store significant gas between banks
require the planned fully coupled inventory/controller model. The optimizer
cannot currently claim benefits from deferring that inventory's compression.

## Coast restoration and deployment

Wires unfurl at their existing pitch. Deployment footprint includes wire gaps;
wetted surface is not mislabeled as deployed footprint. Cooling integrates Fe
enthalpy against net radiation, applying an explicit view factor to wire surface
area. All racks must return to their specified initial temperature before the
next pass. A maximum travel length proportional to `sqrt(total footprint)` and
10 m/s motion capability delays full radiation. No radiation credit is taken
while unfolding or retracting. Solar and warm radiator timing use the same
conservative scheduling rule. See [volume and timing implementation](../deployment/IMPLEMENTED_VOLUME.md).

## Sources and scope

- [Churchill and Bernstein (1977), original paper](https://doi.org/10.1115/1.3450685):
  cylinder crossflow correlation, including its Re·Pr applicability. It is not
  a mesh-array or hypersonic inlet correlation.
- [NASA rarefied-gas heat-transfer report](https://ntrs.nasa.gov/api/citations/19930089513/downloads/19930089513.pdf):
  temperature jump and accommodation motivate restricting continuum heat transfer
  at small length scales. The implemented series bridge is our approximation.
- [Energy accommodation measurements](https://pmc.ncbi.nlm.nih.gov/articles/PMC5621611/):
  accommodation depends on gas/surface conditions; a fixed value is an explicit
  scenario, not a universal material property.
- [Compressor reference dossier](../compressor/COMPARABLE_SYSTEMS.md):
  the mass method and its limitations remain separate from the thermal refinement.
