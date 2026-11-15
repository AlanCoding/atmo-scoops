# Staged compression with deployable metal intercoolers

**Status: theoretical design investigation, not a design selection or cycle-model run.**
The proposal is a sequence of cooling volumes and independently sized compressor
banks. This note uses saved reference quantities and pencil-and-paper ideal-gas
calculations. It changes no simulation inputs, component coefficients or payoff
results. Mixing remains supported and is not excluded by this proposal.

The planned state-resolved replacement is specified in [MODEL_PLAN.md](MODEL_PLAN.md),
including independent rack masses and lattice heat-transfer inputs.

General equations and annotated sources are indexed in the
[compressor calculation dossier](README.md).
The [rear-storage investigation](../../conclusions/rear_storage_depth/INVESTIGATION.md) extends
this example to block power fractions and tank-depth sensitivity.

## 1. The first compressor does not see orbital-speed axial flow

The saved reference in `results/system.json` has an 18.3 m clear mouth and front
bore, a 20 m outer envelope, about 1.283 kg/s peak admitted flow, approximately
26.7 Pa front pressure at perigee, and 1,000 K cooled front gas. Its hot-bank
rated suction is about 13,727 m³/s and sound speed about 619 m/s. Peak admission
and perigee pressure are not precisely simultaneous; this is a representative
near-peak sizing calculation, not an instantaneous replay.

For transparent arithmetic use R = 287 J/(kg K), γ = 1.35, p = 26.8 Pa and
mass flow 1.283 kg/s. These are fixed-property air proxies, not high-temperature
shock chemistry. Then:

```
Mouth area A_m = π (18.3 m)² / 4 = 263.0 m²
Outer projected envelope = π (20 m)² / 4 = 314.2 m²
Cooled density = p/(RT) = 9.34 × 10⁻⁵ kg/m³
Volume flow Q = mass flow / density ≈ 13,740 m³/s
Axial velocity C_a = Q/A_flow
```

If **net open compressor area is 80% of the mouth**, A_flow = 210.4 m²,
C_a ≈ **65.3 m/s**, and axial Mach ≈ **0.105**. If 80% instead means the outer
20 m envelope, its 251.3 m² gives approximately 54.7 m/s. The mouth-based
interpretation is used below. Net area excludes hubs, struts, blades, rack
blockage and manifolds; an 80%-diameter machine is not an 80%-area machine.

| Net area / mouth | Net flow area | Continuity velocity at prescribed density | Axial Mach |
|---:|---:|---:|---:|
| 80% | 210.4 m² | 65 m/s | 0.11 |
| 50% | 131.5 m² | 104 m/s | 0.17 |
| 30% | 78.9 m² | 174 m/s | 0.28 |
| 20% | 52.6 m² | 261 m/s | 0.42 |

These velocities are bulk compressor-face velocities after diffusion and cooling,
not freestream velocities or rotor tip speeds. With p_front = C ρ∞u∞²,
full capture, no added coolant and A_flow = f A_m:

```
C_a = RT / (f C u∞)
```

Using C = 0.7 and u∞ ≈ 7.86 km/s gives the same approximately 65 m/s at f = 0.8.
Density cancels under those assumptions. Partial capture, mixing, actual pressure
recovery and nonuniform flow alter the result. At higher face Mach, the simple
constant-density calculation must give way to compressible total/static states.
It cannot be extrapolated to arbitrarily small area: the ideal choked-flow bound
with γ = 1.35 and discharge coefficient 0.8 requires approximately **47 m²**, or
18% of the mouth, for this throughput and upstream state. That is a limiting
bound, not a recommended operating area.

At 65 m/s, local velocity head is only about **0.20 Pa**, or 0.75% of plenum
pressure. At 174 m/s it is about **1.42 Pa**, or 5.3%. This explains the appeal
of a large first-stage face: less inlet acceleration and more pressure-loss
margin. It does not prove maximum face area minimizes installed mass. Rotor
span, low-speed stage loading, supports, manifolds and clearance losses compete.

## 2. The asymmetric machine follows directly from continuity

At fixed mass flow and axial velocity, required flow area is proportional to
T/p. The table uses C_a = 60 m/s and no mixing, leakage or bleed. Each row is a
possible cooled inlet station, not a selected stage pressure ratio.

| Station pressure | Area at 1,000 K | Area at 600 K |
|---:|---:|---:|
| 26.8 Pa | 229.0 m² | 137.4 m² |
| 100 Pa | 61.37 m² | 36.82 m² |
| 300 Pa | 20.46 m² | 12.27 m² |
| 1,000 Pa | 6.14 m² | 3.68 m² |
| 3,753 Pa | 1.64 m² | 0.98 m² |

The last pressure is the saved reference's end-of-pass rear pressure. It is not
present throughout collection. A fixed-throughput comparison to that pressure
is a design-point bound; an actual train must follow rising tank pressure and
falling inlet pressure. One bar belongs to a later processing requirement,
not the reference atmospheric-phase discharge condition.

From 26.8 Pa/1,000 K to 3,753 Pa/600 K, area falls by a factor of about **233**.
Equivalent full-circle diameter at 60 m/s falls from about 17.1 m to 1.12 m.
Actual turbomachines have annuli, hubs and potentially many parallel modules.
The diameter comparison illustrates scale, not a proposal for one enormous rotor.

This supports a broad low-pressure collector/compressor bank feeding progressively
smaller banks. Separate electric drives/spools allow different speeds. They are
not compelled by density alone: an axial train can also reduce annulus height
on a common shaft. Choose speed from velocity triangles, loading, stress and
operating maps:

```
Euler work per mass: Δh₀ = U₂ Cθ₂ − U₁ Cθ₁
Flow coefficient: φ = C_a/U
Loading coefficient: ψ = Δh₀/U²
Rotational speed: rpm = 60 U/(2π radius)
```

As a kinematic illustration only, U = 200 m/s corresponds to 225 rpm at 8.5 m
radius and 3,470 rpm at 0.55 m radius. This is not a selected blade speed.
Axial Mach 0.1 does not establish blade-relative Mach: the relative tangential
velocity includes blade motion and swirl. Neither efficiency nor allowable
single-rotor pressure ratio follows from the low axial velocity.

## 3. What intercooling can save in compression work

For a constant-property ideal gas, equal block pressure ratios, identical
isentropic efficiencies and complete return to the same inlet temperature:

```
Π = p_out/p_in;  a = (γ−1)/γ
w_N = N c_p T_in [Π^(a/N) − 1] / η_s
w_isothermal,reversible = R T_in ln Π
```

Here a “block” means a compressor group between coolers. It may contain several
rotor/stator stages. Four cooled blocks do not imply four rotor rows.

Take Π = 3,753/26.8 ≈ 140 and T_in = 1,000 K. The following is **reversible
compression in each block**, with ideal intercooling and no pressure losses:

| Cooled compressor blocks | Shaft work | Shaft power at 1.283 kg/s | Saving versus uncooled block |
|---:|---:|---:|---:|
| 1, no intercooling | 2.879 MJ/kg | 3.694 MW | — |
| 2 | 1.987 MJ/kg | 2.550 MW | 31% |
| 4 | 1.672 MJ/kg | 2.145 MW | 42% |
| 8 | 1.538 MJ/kg | 1.974 MW | 47% |
| Isothermal limit | 1.418 MJ/kg | 1.820 MW | 51% |

At a uniform illustrative block η_s = 0.8, divide finite-block work/power by 0.8.
Do not identify that efficiency with the existing model's isothermal efficiency.
The single uncooled perfect-gas calculation would reach about 3,600 K: its frozen
properties become inaccurate there. It illustrates why the uncooled path is
unattractive, not a credible prediction of air chemistry or hardware operation.

**The existing numerical model already assumes cooled, approximately isothermal
compression work.** Its hot section uses RT ln(p_out/p_in) divided by an efficiency
allowance. We cannot apply the 42–51% savings above to that model again. This
scheme may provide a physical realization of cooling already credited, improve
actual efficiency, or change the temperature at which later pressure increments
are obtained. Those are distinct benefits.

A second theoretical comparison makes the temperature effect explicit. Use four
equal-pressure-ratio blocks, first inlet at 1,000 K and the other three cooled
to 600 K. With constant properties and η_s = 0.8:

```
w = c_p [Π^(a/4) − 1] (1000 + 600 + 600 + 600) / 0.8
  ≈ 1.463 MJ/kg; shaft power ≈ 1.877 MW
```

Returning every block to 1,000 K at the same efficiency would require 2.090 MJ/kg
and 2.681 MW. The colder intermediate volumes save **30%** in that controlled
comparison. This does not beat a same-temperature reversible limit: most
compression is now performed at a lower temperature. Equal pressure ratios
are a convenient example, not the optimum when inlet temperatures differ.
For fixed temperatures, lossless blocks and constant efficiencies, minimizing
work gives `(T_i/η_i) r_i^a` equal between unconstrained blocks: hotter/less
efficient blocks should generally take less pressure ratio.

## 4. Can the cooling volumes be metal racks that radiate during coast?

Yes, in principle: each cooler is a cyclic thermal store during collection and
a radiator during coast. Gas-side conductance, heat capacity and later emission
must all be satisfied. A volume by itself supplies neither cooling nor storage.
The cold metal must remain colder than the desired gas outlet by a finite
approach, throughout the required heat load.

For the four-block example, each ratio is about 3.44. With η_s = 0.8 the first
block exits near 1,471 K; subsequent 600 K inlets exit near 883 K. Cooling the
first discharge to 600 K removes approximately **0.96 MJ/kg**. Each subsequent
883→600 K intercooler removes approximately **0.31 MJ/kg**. The three interblock
coolers together absorb approximately **1.59 MJ/kg**, or about **2.04 MW** at the
chosen mass flow. A further final aftercooler is additional. A flat 60 s pulse
would deposit about **122 MJ** in those three stores. This is illustrative pulse
arithmetic, not an integration of the orbital intake curve.

This heat has to fit a useful solid temperature swing. With an explicit rough
c_p,solid = 600 J/(kg K), 122 MJ requires about 4.1 t for a 50 K swing, or 1.0 t
for a 200 K swing. The larger swing is only available if metal starts sufficiently
cold to keep its hottest outlet-contact region below 600 K. The saved front rack
starts at 500 K and reaches 900 K; it cannot simply be reused at 900 K to deliver
600 K gas. A separate cooler that warms 500→550 K leaves only a 50 K end-of-pulse
approach to 600 K gas. A spatially graded regenerator may use its thermal inventory
better than a lumped rack, but needs its own transient analysis.

At emissivity 0.8, a 550 K surface emits about 4.15 kW/m² per face before
background and view-factor deductions. For 122 MJ spread across roughly 4,950 s
of deployed coast, constant-temperature ideal radiation would need only about
3 m² of two-sided panels. **That is not a cooler design:** the stored solid mass,
falling temperature, sheet thickness, gas-side area and deployment mechanics
usually demand much more area. Radiation capacity alone can be easy while
making an effective low-loss regenerator is hard.

There is also a deployment interface: intermediate stores sit inside pressurized
compartments. They must release their gas to downstream storage, isolate safely,
and expose their surfaces to space without venting useful product. The largest
front opening does not automatically give aft racks a clear deployment path
through compressor banks. Retractable side panels, external store deployment,
or thermal transport to separate emitting sheets are candidate arrangements,
each with a mass/volume/heat-transfer penalty.

## 5. Denser gas helps packaging, but does not guarantee better heat transfer

For a passage with hydraulic diameter D_h and area A:

```
Re = ρ C_a D_h/μ = mass_flow D_h/(A μ)
```

At fixed flow, area and gas viscosity, merely increasing pressure does not
increase Reynolds number: velocity falls in inverse proportion to density.
Higher density permits smaller passages and larger mass flux while retaining
moderate velocity. That redesign can increase gas-side heat-transfer coefficients
and make coolers compact. At similar temperature/velocity/geometric diameter,
higher pressure does raise Re; the comparison constraints must be explicit.

The first-stage heat exchanger faces the largest volume flow and the tightest
absolute pressure-loss budget. At 26.8 Pa, 1 Pa is a 3.7% loss; at 300 Pa it is
0.33%. Moving some cooling downstream may therefore reduce exchanger size and
pressure loss enough to justify hotter, more expensive early compression.
It does not remove the leading-edge/diffuser thermal-protection requirement.

The pressure loss of every cooler adds compression work. If cooler j retains
pressure fraction (1−δ_j), the compressor pressure ratios must satisfy:

```
product(r_i) = overall pressure ratio / product(1−δ_j)
```

Intercooling can also increase stored gas inventory and control complexity.
A front volume with one-second residence at the chosen peak flow needs about
13,740 m³—roughly 65 m depth at 80% mouth area. A 10 ms transit needs about
0.65 m depth. Neither is a required residence time: heat-transfer area and
conductance determine what is necessary. At 300 Pa and 600 K, the same mass
flow occupies only about 736 m³/s. Intermediate volumes need not resemble the
250 m front plenum.

## 6. Useful figures of merit and a first design target

| Question | Figure of merit / constraint |
|---|---|
| How hard is the compression? | Shaft/electric MJ per kg of **new atmospheric gas**, over the full pressure history; include coolant throughput and idle/backflow work |
| How much is intercooling worth? | Work saved against the **same** inlet/outlet states, efficiency and allowed heat sinks, minus extra losses and auxiliary power |
| Does the first bank fit? | Net face area, axial and blade-relative Mach, φ, ψ, inlet volume flow, admissible pressure loss and clearance/leakage margins |
| Are smaller downstream banks truly lighter? | Per-bank installed mass, kg/(m³/s), kg/kW, pressure structure, motors/manifolds/supports; avoid assigning one coefficient to every bank |
| Is the cooler effective? | Heat-transfer conductance UA, effectiveness/NTU, pressure loss, stored J/kg over usable temperature swing, end-of-pulse pinch |
| Does cyclic radiation help? | Complete deployed/stowed system kg per MJ stored and rejected per orbit, including mechanisms and insulation |
| Does staging improve the craft? | Net system mass change, net electrical energy change and lost product, before converting them into payoff |

For similar temperatures, per-block ratio r and a volume-flow-proportional
hardware model, the aggregate inlet-volume scale is
`Q_first (1 + 1/r + 1/r² + …)`. At r ≈ 3.44, the infinite sum is only 1.41 Q_first:
the first bank accounts for about 71% of that asymptotic volume-rate burden.
Colder later inlets shrink it further. This supports concentrating design effort
on the first bank, but it is **not a mass prediction**: high-pressure casings,
additional motors, small clearances and thermal stores do not scale with Q alone.

A useful next conceptual target is **three to five cooled compressor blocks**,
with separate speed capability where it earns its mass, and aggressively smaller
intermediate volumes. This is a hypothesis to compare, not a selected stage
count. The ideal-work table shows diminishing returns beyond about four blocks;
pressure loss, machinery and deployment overhead can move the best count either
way. A much larger number of blade rows within those blocks may still be needed.

The credible broad promise is tens-of-percent compression-work reduction relative
to a poorly intercooled train, plus much smaller downstream flow paths and a
possible reduction in warm-loop thermal-buffer load. No compressor-mass percentage
or overall-payoff gain is established yet. Relative to the existing already-cooled
work model, the opportunity must be demonstrated through actual block efficiency,
intermediate temperature, pressure loss and **complete** thermal-system mass.

## Sources and scope

The continuity, ideal-gas, similarity and thermal-store arithmetic above is this
investigation's calculation. Saved reference quantities are from
[the current reference output](../../results/system.json); they are representative
scales, not a new model run.

- [NASA compressor thermodynamics](https://www.grc.nasa.gov/www/k-12/airplane/compth.html)
  supplies the pressure-ratio/temperature/efficiency work relation. It does not
  qualify a stage loading or hardware design at this pressure and temperature.
- [Interstage Pressures of a Multistage Compressor with Intercooling](https://www.mdpi.com/1099-4300/23/3/351)
  treats work-minimizing interstage pressures with different temperatures,
  efficiencies and cooler pressure losses. Equal ratios are a restricted case.
- [NASA compressible mass flow](https://www.grc.nasa.gov/www/BGH/mflchk.html)
  gives the sonic throughput bound. The static-density velocity table is intended
  for subsonic screening, not as a replacement for that bound.

No compressor type, blade speed, stage map, cooler conductance, pressure loss,
deployment mechanism or overall mass benefit is inferred from these equations.

## 7. Area–velocity trade at every block and at final discharge

Use the same illustrative design point: 1.283 kg/s, 26.8→3,753 Pa,
R=287 J/(kg K), γ=1.35, four equal-ratio blocks (ratio 3.44 each),
1,000 K first inlet and 600 K after each intermediate cooler. At low axial
Mach, static/total differences are neglected for this screening table. Cooler
and duct pressure losses are omitted. These are chosen states, not simulated
states or an optimized pressure allocation.

| Location | Pressure | Temperature | Net area at 30 m/s | At 60 m/s | At 120 m/s |
|---|---:|---:|---:|---:|---:|
| Block 1 inlet | 26.8 Pa | 1,000 K | 458.0 m² | 229.0 m² | 114.5 m² |
| Block 2 inlet, after cooler 1 | 92.2 Pa | 600 K | 79.88 m² | 39.94 m² | 19.97 m² |
| Block 3 inlet, after cooler 2 | 317.1 Pa | 600 K | 23.22 m² | 11.61 m² | 5.81 m² |
| Block 4 inlet, after cooler 3 | 1,091 Pa | 600 K | 6.75 m² | 3.38 m² | 1.69 m² |
| Block 4 discharge, before final cooling | 3,753 Pa | 883 K | 2.89 m² | 1.44 m² | 0.72 m² |
| After an optional 600 K final cooler | 3,753 Pa | 600 K | 1.96 m² | 0.98 m² | 0.49 m² |
| After final cooling to reference receiver temperature | 3,753 Pa | 340 K | 1.11 m² | 0.56 m² | 0.28 m² |

The final discharge temperature uses an illustrative block isentropic efficiency
of 0.8. It is not the existing model's efficiency definition. At 60 m/s the hot
final discharge needs about 1.44 m²: equivalent full-circle diameter 1.36 m.
At the same 883 K state, 1 m² implies about 87 m/s and 2 m² about 43 m/s.
These are net flow areas, not external casing diameters, and include no hub or
structure allowance. At the first inlet, 30 m/s needs more area than the
reference mouth: that row would require a wider internal flow path. The previous
80%-mouth case corresponds to 65 m/s rather than the table's 60 m/s.

A three-block version has larger ratios (about 5.19), intermediate cooled-inlet
pressures about 139 and 723 Pa, and net inlet areas about 26.5 and 5.1 m² at
60 m/s. Its hot final discharge is approximately 1,000 K under the same
constant-property/efficiency assumptions, needing about 1.64 m² at 60 m/s.
Thus the broad last-discharge scale is **one to a few square metres**, not
hundreds, for this particular mass flow and tank pressure.

The gas does not keep a single velocity once it enters a large receiver: the
jet spreads and diffuses, and bulk storage velocity can be much smaller. A
manifold/diffuser can enlarge the terminal area to reduce jet losses. Compressor
discharge total pressure must exceed receiver pressure enough to cover velocity
head and losses. Using tank pressure as the table's station pressure is a
low-Mach sizing approximation, not an assertion of finite flow with zero
pressure driving force. Early in the pass the tank pressure is lower, while
later mass flow is lower; the peak-flow/full-tank table is an envelope comparison,
not a claim that both conditions occur simultaneously.

## 8. Off-design operation: the pressure pulse is not the whole problem

A turbocompressor's operating point depends on pressure ratio, corrected flow,
corrected speed and geometry. Schematically, for the same gas:

```
corrected mass flow = mass flow × sqrt(T_in/T_ref) / (p_in/p_ref)
corrected speed = shaft speed / sqrt(T_in/T_ref)
```

Use total inlet states for actual compressor maps. If capture fraction and
pressure recovery are approximately constant, admitted mass flow scales with
atmospheric density, and inlet pressure scales with density times encounter
speed squared. Consequently corrected flow scales approximately as sqrt(T)/u,
not directly with atmospheric density. A tenfold fall in inlet pressure together
with a tenfold fall in mass flow need not by itself move the first block far
across its corrected-flow map. It can primarily reduce torque and power at
similar velocity triangles. This similarity does not preserve Reynolds number,
clearance/backflow behavior or rarefaction as absolute pressure falls.

The rear tank breaks that convenient similarity: it fills while inlet pressure
subsequently falls. At a fixed 3,753 Pa receiver, inlet pressures of 26.8 and
2.68 Pa require overall ratios of about 140 and 1,400. Equal sharing across four
blocks changes each ratio from 3.44 to 6.12. That is a major new head requirement,
not just lower-density operation. At 0.03 Pa the required overall ratio would
be about 125,000. The existing numerical pressure floor does not demonstrate
that the proposed turbocompressor train can operate there.

Rotating stall is a blade-row flow instability; surge is an instability of the
compressor coupled to ducts, plena and downstream storage, potentially involving
large oscillations and flow reversal. Lower flow against excessive backpressure
is a classic dangerous direction. High flow can encounter choking or other map
limits. Slow variation over a minute can aid scheduling, but does not prevent
fast aerodynamic instability once a boundary is crossed. The proposed cooling
volumes add storage and can participate in surge dynamics; they are not
unconditionally stabilizing buffers.

Control candidates to evaluate, without selecting hardware yet:

- Independently controlled bank speeds, with finite torque, rotor inertia and
  spin-up/down power. Match all banks, not only the first.
- Variable inlet guide vanes and selected variable stators to adjust incidence
  and stage matching. Variable rotor pitch is another possibility, but is a
  distinct, more involved mechanical arrangement—not implied by “variable vanes.”
- Bank/module scheduling and startup bypass to handle a nearly empty receiver
  and a developing inlet pulse. Any bypass must have an explicit flow destination.
- Recycle/bleed for minimum stable compressor flow where justified. Recycle
  charges extra work, heat and volume flow; vented bleed loses product.
- A cutoff based on actual flow-map stability, head and recovery value, followed
  by rear isolation. It is not necessary to compress product all the way to
  vanishing atmospheric pressure.

There is no defensible universal percentage turndown or efficiency penalty to
assign before choosing a machine/map. The plan should allow variable geometry
and speed throughout the train where justified. “Only the first stage needs
control” is not established: a last bank feeding a filling tank can be the
limiting bank. Each cooler changes corrected speed and flow for the next bank,
so time-varying rack temperature makes matching a thermal as well as aerodynamic
problem. Positive-displacement machinery has different operating limits and
should not be assessed using an axial-compressor surge map.

References for this extension:
[NASA compressor map and variable-geometry modeling](https://ntrs.nasa.gov/api/citations/20160012485/downloads/20160012485.pdf),
[NASA corrected-speed/flow modeling](https://ntrs.nasa.gov/api/citations/20140012486/downloads/20140012486.pdf), and
[NASA variable-guide-vane/stator fan testing](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19720020168.pdf).
These support the map variables and control mechanisms, not an operating envelope
for this low-pressure, hot-gas spacecraft compressor.
