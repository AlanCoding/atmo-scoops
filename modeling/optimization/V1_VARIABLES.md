# v1.0 optimization: independent inputs, fixed choices and constraints

This documents the **actual 33-coordinate plate search**, not everything that the Python model can accept as an input. Bounds are copied from its saved [search manifest](../../results/transient/plates/cobyla_stable/search.json); reference values are the verified history point 72 in [the v1.0 configuration](../../configs/transient_plates_reference.json). This document changes no inputs and runs no optimization.

## Receiver: what is and is not independent

| Quantity | Status in this search | Meaning / reference |
|---|---|---|
| Hull diameter and length | Fixed | 30 m bore, 31.7 m outside diameter, 317 m length |
| Receiver depth / gas volume | Derived before integration | 247.37 m physical depth; 173,793 m³ free gas volume |
| Receiver vessel pressure rating | Fixed input | 6,500 Pa; limits realized pressure and sizes structure |
| Receiver gas mass | Integrated state | Inflow from upstream compressors minus coast outflow; about 7.11 t at 600 s |
| Receiver gas temperature | Integrated state | About 352 K at 600 s; evolves with gas energy and heat exchange |
| Receiver gas pressure | Calculated from state | About 4,137 Pa at 600 s; not an imposed target |
| Receiver cooler inventory, gap, thickness, initial temperature | Four independent optimizer coordinates | Change heat transfer, heat capacity, occupied volume and cooldown |
| Initial receiver gas state | Fixed initialization rule | Trace residual at nominal 0.001 Pa and 300 K; not optimized |

At fixed bore area A, the receiver gets the length left after other chambers and the equipment bay. Its free gas volume subtracts the cooler solid volume and accounts for vessel heads. Equipment masses, packed volumes and cooler envelopes change when the optimizer changes other inputs, so receiver volume can **move indirectly** even though it is not an independent coordinate.

The chamber model computes P = m R_mix T / V. Temperature comes from the integrated gas energy and composition. Real-fluid properties are used for compressor work; the dilute chamber pressure law is an ideal-mixture approximation screened against HEOS after the run. For the captured mass determined by the flow history, P, T and V cannot be prescribed independently. A different model could choose P, T and V as design targets and derive m, but would then need constraints ensuring the capture/energy balances actually achieve that inventory.

In particular, **gas temperature is not cooler temperature**, and **operating pressure is not pressure rating**. The rating does not force the receiver to fill to 6,500 Pa. The fixed approximately 1 bar coast-processing feed is also distinct from the low-pressure receiver.

## All 33 independent scalar coordinates

Stages 1–5 mean front, intermediate 2–4, and aft receiver. Full thickness and clear gap are separate inputs. The metal inventory coordinate s=V_solid/A has units of metres; it is neither rack depth nor chamber depth. With plate thickness t and gap g, rack depth = s(t+g)/t. Each stage can change its own inventory independently.

| # | Optimized scalar | Unit | Lower bound | Upper bound | v1.0 reference |
|---:|---|---|---:|---:|---:|
| 1 | Clear plate gap — stage 1 | mm | 0.5 | 30 | 6.18968 |
| 2 | Clear plate gap — stage 2 | mm | 0.5 | 30 | 2.97404 |
| 3 | Clear plate gap — stage 3 | mm | 0.5 | 30 | 3.60343 |
| 4 | Clear plate gap — stage 4 | mm | 0.5 | 30 | 3.517 |
| 5 | Clear plate gap — stage 5 | mm | 0.5 | 30 | 3.33055 |
| 6 | Full plate thickness — stage 1 | mm | 0.2 | 5 | 1.43509 |
| 7 | Full plate thickness — stage 2 | mm | 0.2 | 5 | 0.997075 |
| 8 | Full plate thickness — stage 3 | mm | 0.2 | 5 | 0.950323 |
| 9 | Full plate thickness — stage 4 | mm | 0.2 | 5 | 1.27168 |
| 10 | Full plate thickness — stage 5 | mm | 0.2 | 5 | 1.2239 |
| 11 | Solid inventory / bore area — stage 1 | m | 0.0851372 | 0.340549 | 0.16872 |
| 12 | Solid inventory / bore area — stage 2 | m | 0.00668368 | 0.0267347 | 0.0139527 |
| 13 | Solid inventory / bore area — stage 3 | m | 0.003275 | 0.0131 | 0.00676285 |
| 14 | Solid inventory / bore area — stage 4 | m | 0.00314159 | 0.0125664 | 0.00618291 |
| 15 | Solid inventory / bore area — stage 5 | m | 0.00538559 | 0.0215423 | 0.0107762 |
| 16 | Initial solid-cooler temperature — stage 1 | K | 300 | 400 | 300.006 |
| 17 | Initial solid-cooler temperature — stage 2 | K | 300 | 400 | 300.022 |
| 18 | Initial solid-cooler temperature — stage 3 | K | 300 | 400 | 300 |
| 19 | Initial solid-cooler temperature — stage 4 | K | 300 | 400 | 300 |
| 20 | Initial solid-cooler temperature — stage 5 | K | 300 | 400 | 300 |
| 21 | Solar physical area | m² | 1.38975e+06 | 2.7795e+06 | 1.84435e+06 |
| 22 | Battery installed energy | MWh | 250.405 | 500.811 | 334.195 |
| 23 | Warm thermal inventory | t | 381.132 | 762.264 | 521.143 |
| 24 | Warm radiator physical area | m² | 25,197.4 | 50,394.8 | 33,624.1 |
| 25 | Liquefier flow rating | kg/s | 1.48445 | 2.9689 | 1.99636 |
| 26 | Liquefier electrical rating | MW | 10.9637 | 21.9274 | 14.6355 |
| 27 | Dive compressor motor rating — stage 1 | MW | 17.85 | 47.6 | 30.9243 |
| 28 | Dive compressor motor rating — stage 2 | MW | 6.069 | 16.184 | 10.1144 |
| 29 | Dive compressor motor rating — stage 3 | MW | 4.7685 | 12.716 | 7.9498 |
| 30 | Dive compressor motor rating — stage 4 | MW | 7.803 | 20.808 | 12.9993 |
| 31 | Coast compressor motor rating | MW | 13.005 | 34.68 | 21.6723 |
| 32 | Thruster Isp | s | 1,200 | 3,000 | 1,794.94 |
| 33 | Symmetric total burn duration | s | 800 | 2,000 | 1,222.83 |

The six capacity bounds (solar, battery energy, warm inventory, radiator area, plant flow and plant electricity) are 0.75–1.5 times the original optimization seed. Motor bounds are 0.6–1.6 times that seed; solid inventories are 0.5–2 times their seed. These are declared search limits, not material laws or global optimum guarantees. The selected history point differs from the exact solver return because it passed the stronger resolution verification. Published values near 300 K are rounded; constraint/bound tolerances permit minute numerical deviations.

## Deliberately fixed design and control inputs

“Fixed” means the optimizer did not change these in this study; it does not mean they can never be changed.

| Fixed item | v1.0 value | Why it matters / limitation |
|---|---|---|
| Bore / radial allowance | 30 m / 0.85 m each side | Sets flow area and 31.7 m outer diameter |
| Hull L/D | 10 based on outside diameter | Gives 317 m length; no unlimited elongation |
| Perigee / apogee | 85 / 2,000 km | Neither was optimized in this plate search |
| Compressor blocks / gas volumes | Four dive blocks, five gas volumes | Stage count is not a variable |
| Cooler materials | SiC front; Al stages 2–5 | No material selection in this solve |
| Extra clear chamber depths | 0, 0, 0, 0 m | First four volume depths follow rack envelope and heads; no independent empty-volume allocation |
| Vessel head depth | 1.5 m per head | Included in geometry; front is open |
| Chamber pressure ratings (2–5) | 2,000; 10,000; 30,000; 6,500 Pa | Structural sizing and maximum pressure, not setpoints |
| Dive nominal suction capabilities | 27,464; 6,207; 1,723; 687 m³/s | Motors can vary, but these inlet-capacity assumptions cannot |
| Dive head capabilities | 941,484; 1,213,000; 933,924; 823,743 J/kg | Flow/head relation is fixed |
| Coast nominal suction / head | 500 m³/s; 5 MJ/kg | Three cooled blocks, suction fractions 1 / 0.25 / 0.0625 |
| Battery peak electrical rating | 940.196 MW | Energy capacity varies; peak MW does not |
| Bus peak electrical rating | 827.372 MW | Shared electrical-power ceiling and bus mass are fixed |
| Dive compressor enable interval | −500 to +600 s from perigee | Spin-up and residual pumping included |
| Coast-processing interval | +650 to +4,200 s | Not independently rescheduled by optimizer |
| Vent interval / suction cutoff | 120 s / 0.1 Pa | Affect residual losses and cooler release |
| Battery initial SOC / floor | 0.95 / 0.20 | Initial energy is capacity × SOC |
| Warm initial / maximum temperature | 340 / 450 K | Initial state and thermal envelope |
| Gas propellant reserve | 4,500 kg at 340 K; 500 m³; 15 bar rating | Buffer size, refill hardware and initial state are fixed |
| Product liquid tank | 20 m³ | Bounds accumulated liquid volume |
| Mixing | Supported, set to zero | Not a coordinate in this search |
| Deployment speed | 10 m/s | Deployment time scales with square root of physical panel area |
| Inlet treatment | Open mouth, ceiling/taper 250/50 km | No mouth-door design variable |
| Exterior skin-friction coefficient | 0.002 | Assumption used for impulse; not a calibrated hull solution |
| Sun-synchronous orbit target | Dawn–dusk, about 99.35° | Publication assumption; not a propagated/optimized inclination or seasonal sunlight variable |

### Fixed capability assumptions, separate from design choices

Compressor efficiency 0.75, motor efficiency 0.95, thruster efficiency 0.60; solar 250 W/m² and 150 W/kg; battery 150 Wh/kg and 1,500 W/kg; charge/discharge efficiency 0.95; machinery packing density 250 kg/m³ and aggregate fill fraction 0.70; 25% mass contingency. Plate friction multiplier is 1.0 in the power-only approximation. These quantities affect the answer but were not independently optimized. Other component coefficients remain in the exact configuration, rather than being implicit adjustable freedoms.

## Objective

Minimize **operating-orbit** mass payoff in days:

    f(x) = M_dry(x) / m_new,useful_liquid(x) × T_orbit / 86400.

Dry mass is compiled from installed hardware before one forward cycle. Useful new liquid is the inventory increment available for offload after reserving/refilling propellant; recycled material is not new product. Dry mass has no imposed ceiling. Since this search fixes the orbit, T_orbit≈6,361.69 s is constant. Circular-apogee export/return is not included.

## Conditions the candidate must satisfy

These are constraints or model-enforced limits, not additional free variables. Path checks operate on the recorded trajectory/integration states, not on a mathematically continuous certified envelope.

| Category | Requirement in the current implementation |
|---|---|
| Installed geometry | All declared hardware and cooler envelopes fit the fixed hull; aft receiver must fit its cooler and heads; gas volumes remain positive |
| Plate regime | Maximum recorded Re ≤1,000; lumped-solid Bi ≤0.1 |
| Solid temperatures | SiC ≤1,000 K; Al ≤550 K (study limits, not qualified flight allowables) |
| Chamber pressure | Each closed gas volume stays below its fixed pressure rating |
| Warm store | Temperature ≤450 K |
| Gas temperature | ≤2,000 K for chambers containing more than 0.01 kg |
| Battery and bus | SOC ≥0.20; finite installed MW ratings allocate available power |
| Unserved electricity | Integrated unmet demand ≤1 MJ |
| Mass / product | Nonnegative liquid and buffer species inventories; positive useful product; no deficit relative to initial liquid reserve |
| Liquid capacity | Total liquid volume ≤20 m³ |
| Propellant buffer | Pressure ≤1.5 MPa; temperature ≤500 K; refill and feed limits enforced |
| Cooler release | Chamber pressure <100 Pa at each scheduled hatch release; residual purge gas is charged as loss |
| Property-domain checks | Thermodynamic states must evaluate; audited absolute Z−1 <0.01 and compressor-work relative disagreement <1e−5 |

### End-to-start closure tolerances

| Residual | Allowed magnitude |
|---|---:|
| Each cooler specific enthalpy change | 500 J/kg per cooler |
| Battery stored energy change | 100 MJ |
| Warm-store energy change | 100 MJ |
| Total chamber gas mass change | 0.1 kg |
| Total chamber gas energy change | 0.01 MJ |
| Total remaining rotor energy | 0.01 MJ |
| Delivered reboost impulse / required impulse − 1 | 1e−4 |
| Each propellant-buffer species mass change | 0.1 kg |
| Propellant-buffer energy change | 1 MJ |

**Important scope:** chamber gas mass/energy closure is currently aggregated across the five volumes, not an independent mass/energy closure equation for each chamber. Cooler enthalpies and buffer species are individually checked. Material/emissivity assumptions and scheduled venting make the gas inventory nearly empty at cycle end, but aggregation is still a limitation worth tracking. These are finite tolerances, not exact zero residuals.

The released reference has at least 20 MJ nominal reserve inside the 100 MJ battery limit and passes three integration resolutions. That reserve was a **post-search selection rule**; it was not an extra constraint in the original 33-coordinate solve. The planned scale study will put a common reserve directly into all compared searches.

### Conservation, numerical checks and unresolved physics

Conservation acceptance: maximum species-balance error <1e−4 kg, energy-balance error <0.01 MJ, and gas species no more negative than −1e−4 kg numerical tolerance. The optimizer also has unit-coordinate bounds and scaled numerical tolerances. Each candidate has one forward integration, with no inner resizing or shooting-to-closure loop. A numerical failure stops the run rather than pretending the candidate is physically infeasible. Tighter-resolution checks validate the selected reference separately.

Not currently enforced: a resolved shock location; calibrated compressor surge/stall maps; full channel pressure-field feasibility (losses are charged as electricity); qualified leading-edge heating/erosion/lifetime; detailed 3D packaging/deployment collision checks; CM/CP or flexible-body stability; 3D sun-synchronous maintenance and seasonal lighting; delivered circular-apogee payoff. The provisional axial layout and its CM are post-processing, not optimizer constraints.

## L/D and lower perigee

Your expected direction is plausible: at fixed diameter, extra length can increase receiver volume, lower pressure for a given inventory and temperature, and ease pressure/thermal loading or accept more inventory. But **this solve has not established that increasing L/D necessarily lowers the best perigee**. Perigee is fixed, and longer structure also adds mass and wetted-area drag; capture, reboost and heating can become limiting. The head/pressure ratings, initial chamber allocations and material limits remain additional constraints.

To test that proposition later, fix a sequence of L/D values, release perigee under the same credible thermal/inlet limits, and reoptimize the other inputs. Distinguish any search-bound hit from a demonstrated survivability limit. This document does not start that study or change the agreed v1.0 snapshot.

## Code / data references

- [Search coordinates, objective and constraint vector](../../atmo_scoops/transient/plate_optimize.py).
- [Hardware compilation and remaining receiver volume](../../atmo_scoops/transient/hardware.py).
- [Forward balances, path margins and closure](../../atmo_scoops/transient/cycle.py).
- [Independent thermodynamic audit](../../atmo_scoops/transient/validate.py).
- [Full saved search manifest](../../results/transient/plates/cobyla_stable/search.json).

### Consequence of fixed clear depths

The [geometry provenance trace](../../investigations/v1_layout/FRONT_GEOMETRY_TRACE.md)
shows why the first SiC gas compartment is smaller than the next three despite
its much larger rack. Fixed 1.5 m vessel heads dominate downstream volume.
This search did **not** establish an optimal distribution of empty chamber space.
