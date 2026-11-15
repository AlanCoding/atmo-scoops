# Rear storage depth, compression duty and spacecraft length

**Status: open investigation, not a selected layout.** Extending rear storage
substantially reduces dive compression head. Whether that improves payoff depends
on compressor hardware, minimum-gauge structure, the coast process and whether
the volume occupies an already-required stability structure. The current model
does not demonstrate a payoff benefit, and cannot resolve the proposed staged
compressor hardware. It does not predict an optimum hundreds of kilometres long.

Reproduce from repository root:

```
.venv/bin/python conclusions/rear_storage_depth/calculate.py
```

[Results](results.json) preserve exact resolved cycle inputs, outputs, constraints,
analytic inputs, resolution check and source hashes. Two distinct calculations
are kept separate: constant-property four-block point sizing, and a one-variable
depth sweep of the unchanged active cycle. Neither is a new optimization. The
four-block proposal is not inserted into the isothermal cycle mass/payoff model.

## Geometry and the question being tested

Keep the 18.3 m clear bore/mouth and 20 m outer diameter. Physical rear depth
includes two 2:1 ellipsoidal heads. With diameter D and physical depth L:

```
V_rear = (pi D²/4) (L - D/6)
p_rear = m_stored R T_rear / V_rear
```

Reference rear depth is 25 m. At fixed inventory and 340 K, its 3,753 Pa pressure
scales inversely with `(L - 3.05 m)`. The rounded-number ideal-air example implies
about 222 kg stored. This is retained gas, not net exported liquid after propulsion.

There are two different L/D ratios: tank slenderness and whole-vehicle
slenderness. The existing comparison vehicle is **250 m front + 20 m machinery
+ 25 m rear = 295 m**, already **14.75:1** on its 20 m envelope. It is mainly front
volume. A rear tank with L/D≈10 is about **183 m** long. A whole craft with L/D=10
is only **200 m** long; one diagnostic arrangement is 30 m front + 20 m machinery
+ 150 m rear. These are space allocations, not proof that all four banks, racks,
deployment paths and shock-start margins fit.

## How power is distributed between blocks

Use the previous illustrative state allocation: first inlet 26.8 Pa/1,000 K,
three later inlets at 600 K, final pressure 3,753 Pa, mass flow 1.283 kg/s,
R=287 J/(kg K), gamma=1.35 and block isentropic efficiency 0.8. Four equal
pressure ratios are 3.44 each. No duct/cooler losses are included.

For each block, `w = cp T_in (r^((gamma-1)/gamma)-1)/eta`.

| Block | Shaft work | Shaft power at reference flow | Fraction |
|---|---:|---:|---:|
| First | 522 kJ/kg | 0.670 MW | 35.7% |
| Second | 313 kJ/kg | 0.402 MW | 21.4% |
| Third | 313 kJ/kg | 0.402 MW | 21.4% |
| Fourth | 313 kJ/kg | 0.402 MW | 21.4% |
| Total | 1,463 kJ/kg | 1.877 MW | 100% |

Power follows inlet temperature at equal ratio/efficiency, **not inlet area**.
These fractions change if pressure ratios, efficiency or cooling allocation
change. Equal ratios are not work-optimal for unequal temperatures. Electrical
power adds motor losses. The first block accounts for about 81% of the sum of
bank suction volume flows, but only 36% of work. This distinction matters when
translating power savings into installed mass.

## Rear-depth thermodynamic sensitivity

For each larger tank, retain the same inventory, temperature and first inlet,
then redistribute the reduced overall pressure ratio equally across four blocks.

| Rear physical depth | Final pressure | Four-block shaft power | Reduction from 25 m |
|---|---:|---:|---:|
| 25 m | 3,753 Pa | 1.877 MW | — |
| 50 m | 1,755 Pa | 1.548 MW | 17.5% |
| 100 m | 850 Pa | 1.248 MW | 33.5% |
| 150 m | 561 Pa | 1.083 MW | 42.3% |
| 180 m | 466 Pa | 1.010 MW | 46.2% |
| 200 m | 418 Pa | 0.969 MW | 48.4% |
| 500 m | 166 Pa | 0.623 MW | 66.8% |
| 1,000 m | 82.6 Pa | 0.376 MW | 80.0% |

These are comparable end-pressure/peak-flow sizing points, not integrated
one-minute power traces. For scale only, a flat 60-second pulse at these duties
would save about 54.5 MJ, or **15.1 kWh shaft energy**, from 25 to 200 m. A full
cycle must solve inventory, tank temperature, map constraints and pressure loss.
At equal gas states the first bank still has to swallow about 13,740 m³/s.

Lower pressure ratios do not necessarily shrink the train. In the four-block
equal-ratio comparison, downstream inlet pressures are also lower, increasing
their volume flows. Applying the same provisional 30 kg/(m³/s) to every block
gives 511 t at 25 m versus 631 t at 200 m. **This is a sensitivity of a crude
mass proxy, not a prediction of a heavier real compressor.** Lower head may
permit fewer blade rows, lower tip speeds, lighter rotors or omission/bypass of
a block. Conversely, casing and inlet size do not vanish with shaft work. We
need geometry/map-based hardware sizing to decide the sign of the mass change.

At roughly 3.08 km rear depth, this same batch at 340 K has pressure equal to
the 26.8 Pa first-inlet pressure. This is only an endpoint equilibrium bound:
it supplies no finite flow margin and ignores the declining inlet pressure.
There is no positive compression work left to eliminate by extending the tank
indefinitely. It is not evidence that an unpumped collector fills this way.

## Constant PV: correct pressure-shell scaling, but not constant total structure

For a thin cylindrical barrel in vacuum, hoop stress gives
`t = safety_factor p r / allowable_stress`. Its barrel mass is then approximately
`2 rho_material safety_factor p V / allowable_stress`.
Thus at fixed gas inventory and temperature, **the pressure-required barrel mass
is independent of length**. Heads and finite aspect ratio modify the coefficient;
they do not invalidate the useful leading-order argument.

The current reference already has a different controlling allowance. Its
150 MPa allowable stress, factor 1.5 and 18.3 m bore require only **0.343 mm**
pressure thickness at 3,753 Pa. At 418 Pa that falls to **0.038 mm**. Both are
below the model's **1 mm minimum gauge**, so lengthening provides no gauge
reduction in this calculation. The gauge is an assumption to refine, not a
demonstrated physical minimum.

The model also charges supports (50% of metal mass), insulation (1 kg/m²), and
an independent outer shell/TPS allowance (4 kg/m²). At fixed diameter these add:

| Incremental term | Mass per additional rear metre |
|---|---:|
| 1 mm tank, supports and insulation | 290 kg/m |
| 20 m outer shell/TPS | 251 kg/m |
| Combined, before design margin | 542 kg/m |

From 25 to 200 m that is 50.8 t additional tank/support/insulation and 44.0 t
outer shell. An integrated pressure-bearing outer structure could share load
paths and reduce this sum. A tank installed inside an already-required skirt
need not pay the entire outer-shell increment. Neither credit is established
by the present separate allowances. They should be tested explicitly rather
than either double-counted or assumed free.

Finite structure must also carry thrust, bending, aerodynamic moments, thermal
distortion and fin loads, including when storage is empty. Pressure membrane
stress alone cannot set its mass. [NASA SP-8007 Rev. 2](https://ntrs.nasa.gov/citations/20205011530)
provides cylinder buckling guidance and emphasizes imperfection-sensitive shell
design; it does not establish a gauge or safe length for this craft.

## Lower storage pressure shifts some work to the coast

The active process feeds a 1 bar nitrogen-equivalent liquefaction train. It
therefore includes a coast compressor evacuating the rear tank to a residual
fraction of 0.001. Reducing storage pressure by a factor F adds approximately
`R T_coast ln(F)` reversible compression work per kilogram to reach the same
process pressure (plus evacuation effects and efficiency losses).

For 25→200 m, F≈8.97. At 340 K the added reversible requirement is about
**214 kJ/kg**. This must be included alongside the reduced dive duty, rather
than calling all dive savings an energy saving for the mission. Moving pressure
rise from hot gas to colder gas can still save work, and moving it from a brief
battery-powered pulse to a long solar-powered coast can help equipment sizing.
If the shifted pressure rise occurs at the same temperature and efficiency,
ideal logarithmic work largely cancels. A different liquefaction process may
change the required pressure; that must be modeled explicitly.

The current model already performs its rear-stage dive compression at 340 K.
It keeps a 300 Pa intermediate pressure, regardless of rear depth. Consequently
the model gives little net energy benefit to moving that work to the coast,
and ceases reducing the rear-stage dive work once the entire fill is below
300 Pa (rear depth about 278 m). This does **not** test the new finite-temperature
four-block scheme or optimized intermediate pressures.

## What the unchanged cycle currently predicts

Hold all reference inputs fixed except rear depth: front 250 m, orbit
100×2,000 km, zero injected nitrogen, the same pumping and cutoff controls.
Here net production stays **177.264 kg/pass** and the orbit is **106.2 minutes**.
The current front solver is not coupled to rear pressure through real compressor
maps; unchanged collection is a property of this model, not evidence that rear
volume can never increase recovery in a head-limited machine.

| Rear depth | Total dry mass | Installed compressors | Operating payoff |
|---|---:|---:|---:|
| 25 m | 2,469.1 t | 424.5 t | 1,027.1 days |
| 100 m | 2,519.8 t | approximately 425.4 t | 1,048.2 days |
| 180 m | 2,574.8 t | 426.2 t | 1,071.1 days |
| 200 m | 2,588.6 t | 426.5 t | 1,076.9 days |
| 500 m | 2,796.2 t | 429.8 t | 1,163.2 days |

These are unoptimized reference sensitivities, not the prior optimized results
and not payoff for a state-resolved staged design. Circular-apogee export remains
unimplemented. At 200 m the 119.6 t increase consists mainly of the 94.8 t
structural allowances and 23.9 t added design margin. Coast compressor mass
increases 1.93 t; battery, warm buffer and electrical distribution save about
1.20 t combined. Hot/warm dive compressor masses are unchanged because their
volume-flow sizing controls. Dive compression electricity falls from 148.8 to
129.0 kWh/pass, while total required solar power changes from 25.309 to 25.319 MW.

### Reallocate existing front length instead of extending the hull

Because the proposed first chamber might be much shorter, also evaluate layout
diagnostics with the same active-model capabilities and physical machinery
allowance. No shock-position or rack-clearance feasibility is claimed.

| Front / rear / machinery depth | Whole length and L/D | Dry mass | Operating payoff |
|---|---|---:|---:|
| 250 / 25 / 20 m | 295 m; 14.75 | 2,469.1 t | 1,027.1 days |
| 175 / 100 / 20 m | 295 m; 14.75 | 2,496.2 t | 1,038.4 days |
| 125 / 150 / 20 m | 295 m; 14.75 | 2,514.8 t | 1,046.1 days |
| 75 / 200 / 20 m | 295 m; 14.75 | 2,533.7 t | 1,054.0 days |
| 30 / 150 / 20 m | 200 m; 10 | 2,485.0 t | 1,033.7 days |

Net liquid changes by less than 0.01 kg/pass in these runs. Reallocation avoids
the extension's outer-shell cost but still adds tank surface. The compact 10:1
layout is within about 0.6% of reference payoff under current allowances. It is
a useful candidate geometry for the refined analysis, not an endorsed optimum.

## Design implications and next discriminating calculations

1. Larger rear volume is a strong **head and burst-power lever**. Lower storage
   pressure may also postpone an outbound head-limited cutoff. That collection
   benefit requires the planned compressor maps; it is absent from this sweep.
2. Fixed inventory does not mean larger volume collects more gas. Larger volume
   increases capacity at a prescribed pressure limit; actual recovery must be
   solved with admission, leakage, bank capacity and cutoff.
3. Treat minimum front depth as a result of inlet starting/unstart margin,
   shock/rack interaction, cooling residence/conductance, access and transients.
   Suction influences backpressure but does not arbitrarily prescribe shock
   location. Cooler placement downstream of compression/diffusion is a candidate,
   not a proven shock-clearance rule.
4. A distant skirt/fin can provide restoring leverage if its force acts suitably
   behind the moving centre of mass. Filling its intervening space is worth
   studying. Tank/rack mass, stored gas and deployments move the centre of mass;
   damping, bending modes, drag and thermal loading must accompany static margin.
   No stabilizing fin benefit or extra skin drag is credited in these numbers.
5. Next compare shared load-bearing shell versus separate tank, independently
   sized/map-limited compressor blocks, finite rack cooling and a consistent
   coast pressure path. Search rear depth and front depth separately. Do not
   assume pressure-shell scaling makes arbitrary length mass-free.

Validation: the 200 m case changes operating payoff by less than 0.001 day when
history samples increase from 1,601 to 3,201. This checks numerical integration,
not physics. Full resolved constraint margins are retained in the result file;
the comparison is not a flight-feasibility certificate.

Related references and their applicability are collected in the
[compressor dossier](../../modeling/compressor/README.md). The barrel
PV scaling above is a direct thin-shell derivation, distinct from the current
minimum-gauge screening allowance in `physical_cycle.evaluate`.
