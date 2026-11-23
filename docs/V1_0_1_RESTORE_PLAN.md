# v1.0.1 restoration plan — valve-connected aft reserve

**Implemented and numerically checked.** The original planning calculations below are retained as the design rationale; current optimized numbers are in the [results](../investigations/valve_reserve/README.md). The boosted-reserve candidate is rejected and
[archived with its scale drawing](design_archive/v1.0.1_rejected_boosted/README.md).
The new [working SVG](images/v1_perigee_scale.svg) / [PNG](images/v1_perigee_scale.png)
now depicts the selected simulated replacement reference.

## Agreed architecture

Keep the 317 m hull, 30 m bore, L/D=10 and last **125 m** as a valve-connected
propellant compartment. Keep SiC first and staggered Al plates downstream.
Delete the four spherical storage tanks, reserve refill compressor/motor/rotor,
refill-cooler allowance, high-pressure storage requirement and their sizing knobs.
Retain coast compression and liquefaction only for the main receiver's product
stream. Retain physical valve/manifold and thermal-boundary accounting; removal
of a compressor does not make those components massless.

The reserve supplies pre-entry thrust. Open its connection when receiver pressure
catches reserve pressure; finite valve flow supplies equalization and shared
feeding. Isolate before coast product processing draws down the main receiver.
The large reserve is not emptied, vented or refilled through the liquefaction
train. Its carried mass and thermal state must close over a cycle.

## Algebraic geometry and altitude screen

The working drawing keeps inherited front geometry only as a starting point:

| Region | Axial range m | Barrel diameter m | Free gas volume m³ |
|---|---|---:|---:|
| Front four cooling/compressor blocks | 0–48.110 | 30 bore | Recomputed per stage later |
| Main receiver | 48.110–192 | 24.283 | 65,937.5 |
| Isolated propellant compartment | 192–317 | 30 | 87,300.5 |

The main receiver is 143.890 m long. All remaining package displacement is
assigned ahead of the protected reserve: **34,708 m³**, retaining the old hardware
sizes for this first screen after removing the old reserve system. Two rounded
heads per tank use the existing 1.5 m head depth. This charges the additional
heads; it does not simply split the old gas volume in half. Valve/bulkhead/support
allowances and resizing are still pending. Do not subtract package volume again
after reducing the main radius to fit it.

The receiver rack's inherited material inventory cannot remain a 30 m rack inside
a 24.283 m barrel. Preserving its mass, thickness, gaps and surface area makes its
core **0.250 m** long, rather than 0.164 m. Its changed flow area, gas volume and
pressure loss must propagate through the future model.

### Cyclic inventory, not two initially empty tanks

Let C be fresh captured gas per pass, B be propellant consumed, M the main
receiver mass at isolation, and R the reserve mass at the same cyclic boundary.
For full capture, neglecting small incidental losses in this screen:

```
R_start + C - B = M + R_end
R_end = R_start  =>  M = C - B
B = beta C       =>  C = P_fill V_main / [R_specific T_fill (1-beta)]
R_end = P_fill V_reserve / (R_specific T_fill)
```

This equal-temperature/equal-pressure approximation is for initial sizing. The
transient valve calculation must replace it when temperatures and pressures differ.
The old full-aperture forcing gives C0=7,113.67 kg at 85 km and B0=3,567.53 kg,
so beta=0.501504 at the inherited Isp/burn/drag settings. Actual old admitted gas
was 7,112.04 kg: a small difference, but admission losses must become an explicit
feasibility check, not a way to improve payoff by undersizing capture hardware.

For the primary working screen, preserve the old **actual working pressure
4,766.83 Pa and temperature 357.29 K**. This introduces no new fill pressure:

- Main receiver inventory: **3,064.47 kg**.
- Cyclic reserve inventory: **4,057.33 kg**.
- Fresh capture needed: **6,147.44 kg**.
- Propellant: **3,082.96 kg**.
- After an illustrative half-burn from the reserve: **2,515.85 kg** remains.

Near 85 km the same reference atmosphere has local density scale height
H=5.68484 km. Holding encounter speed/duration, composition, temperature and beta
fixed for this algebraic estimate gives:

```
C_new / C0 ≈ rho_new / rho0 = 0.864172
h_new ≈ 85 km - H ln(C_new/C0) = 85.83 km
```

Thus the provisional orbit in the working SVG is **85.83 × 2,000 km**. It is a
starting estimate, not a demonstrated capture/thermal/propulsion-feasible orbit.
The height increases slightly because the reserve is recycled working inventory,
and the reduced main receiver stores the net capture after propulsion.

“Full” needs a pressure/temperature specification, not volume alone. The inherited
6,500 Pa rating is a ceiling, not evidence of the intended operating pressure:

| Illustrative fill-pressure choice | Algebraic fresh capture kg | Perigee km |
|---|---:|---:|
| Preserve actual prior 4,766.83 Pa | 6,147 | 85.83 |
| 6,500 Pa rating / 1.1 | 7,621 | 84.61 |
| 6,500 Pa rating with no margin | 8,383 | 84.07 |

The latter two are sensitivity examples, not newly selected requirements. Review
the working fill pressure/margin before implementation. No new payoff is claimed.
Reproduce with `PYTHONPATH=. .venv/bin/python investigations/v1_layout/valve_restore_screen.py`.
It uses the old atmospheric forcing and local density slope; no new cycle is run.

## Fixed-input audit and decisions for review

The [complete input register](../investigations/v1_layout/FIXED_INPUT_AUDIT.md)
lists every current design/capability input, including the optimized ones so that
fixed choices cannot disappear behind a variable list. The highest-risk findings:

| Existing choice | Why it matters | Proposed disposition |
|---|---|---|
| Perigee 85 km; apogee 2,000 km | Orbit was not reconciled with the reserve split | Start from algebra above; solve perigee against full capture and receiver fill in outer constrained solve. Hold apogee for this correction unless coast duration fails. |
| Receiver 6,500 Pa ceiling; stage ceilings 2/10/30 kPa | Structural limits are not operating targets | Review working fill pressure/margin; retain separate structural and operating quantities. |
| Dive suction 27,464/6,207/1,723/687 m³/s and fixed head ratings | Motor-only search cannot resize the main flow path | Reconcile flow/head with full incident flow and stage states; expose capacities or derived sizing constraints in outer solve. Do not use the old arrays unchanged. |
| Coast suction 500 m³/s, fractions 1/0.25/0.0625, head 5 MJ/kg | Sized for product AND reserve refill | Remove reserve branch, retain liquefaction thermodynamics, resize product-only coast train. |
| 500 m³ / 4,500 kg / 15 bar / 5 MW reserve | Wrong architecture and unnecessary controls | Remove; derive tank volume from 125 m geometry and solve cyclic reserve initial inventory/energy. |
| Thruster minimum feed 1 bar, maximum 5 kg/s | The low-pressure reserve would fail this inherited cutoff immediately | Replace with an explicit reviewed low-pressure feed model. Do not quietly set an arbitrary near-zero limit, and do not insert another storage/refill compressor. Feed interface capability is unresolved. |
| Bus 827.37 MW; battery discharge 940.20 MW | Fixed power ratings can block an otherwise resized vehicle | Expose installed power capacity or derive from declared demanded loads, charging mass and heat; enforce actual limits. |
| Pump enable −500 s / stop +600 s; plant +650 to +4,200 s | Schedule can conflict with changed burn, valve sequence and orbital coast | Derive event order from capture, burn, isolation, stow/deploy and reset requirements. Optimize only genuinely discretionary times. |
| 0.1 Pa pump cutoff; 10 s vent time constant; 120 s vent interval | Can hide low-pressure loss and force an empty state | Audit hydraulic feasibility and product residual; reserve must NEVER receive main-tank purge. Preserve counted losses. |
| Four rows, full-bore racks, 1.5 m heads, 1 m hatch buffers | Forces shape; smaller main barrel changes rack 5 | Keep declared front assumptions initially; recompute receiver geometry. Row-count/area redesign deferred except mandatory fit correction. |
| Compressor surrogate: 0.5 m modules, 350 m/s tip, 100 m/s axial; dummy rho=0.001 | Hardware mass/volume not fully tied to actual inlet states | Record as a capability model; check applicability at revised states. Do not treat it as a validated rotor design. |
| Package density 250 kg/m³, fill 0.7, fixed folded-volume factors | Annular fit and volume budget are approximate | Preserve explicit assumptions, charge once, resolve sectors/ports. Distinguish tank displacement from external thruster location. |
| Gas reserve thermal UA 50 kW/K and 340 K initial state | Implies unexamined thermal conditioning of reserve | Replace with the large compartment's heat-transfer boundary and cyclic thermal state; no free reset. |
| 20 m³ liquid tank and single-cycle offload | Does not prove five-pass storage | Address five-cycle campaign as next checkpoint, keeping original operating cycle distinct. |
| Fixed Cf=0.002, fixed composition, static reference atmosphere and simplified shadow | Environment/drag affects required propellant and matching altitude | Retain as declared baseline sensitivities; recompute forcing and orbital factors at the revised altitude. No new weather/CFD scope now. |

Intentionally fixed scope: diameter and L/D; front SiC/downstream Al; deployment
speed 10 m/s; no inlet door; no coolant injection for the reference (mixing remains
supported); current reduced liquefaction process. Capability coefficients remain
explicit assumptions. Detailed cryogenic refinement is deferred as requested.

## Incremental implementation after review

1. **Geometry and accounting only.** Implement main/reserve volumes and separate
   pressure boundaries, remove old sphere/booster package and mass, retain valve/
   manifold/bulkhead costs. Resolve radial displacement ahead of x=192 m and rack
   5 area. Produce a deterministic volume/mass ledger before running a cycle.
2. **Valve-connected dynamics.** Reuse reserve species/energy states. Add finite
   inter-tank mass and enthalpy transfer, pressure-triggered opening and coast
   isolation with hysteresis/event control. Preserve pre-entry drawdown and
   shared feeding. Product train draws only from main tank while isolated.
   Remove the booster rotor state/energy or migrate it explicitly; never silently
   reinterpret ledger indices. Preserve the rejected model for reproduction.
3. **Capacity and orbit consistency.** Recompute atmospheric supply, momentum,
   reboost and thermal loads for each declared perigee. Reconcile dive/coast
   flow/head/power capacities and power-system ratings. Use the algebraic screen
   as an initial guess; actual gas temperatures and finite valve behavior must
   determine the matching condition in the outer solve.
4. **Constraint contract.** Require full capture of the declared collection
   window, with a documented numerical tolerance only; report missed incoming
   mass separately from later venting and propellant. Do not reward a design
   financially for rejecting air it was sized to process. A pump or heat-transfer
   bottleneck is infeasible, not an alternate low-collection optimum. Enforce
   receiver fill target and pressure ceilings, reserve species/energy closure,
   thrust completion, material limits, volume fit and electric/thermal closure.
5. **Fixed-case gate before optimization.** Verify valve shut/open limits,
   equalization mass/energy conservation, no reserve coast drain/purge, pre-entry
   feed and capture capacity. Check two numerical resolutions with robust event
   initialization. No inner repeated-cycle closure iteration: initial inventory/
   temperature and perigee may be outer coordinates constrained by residuals.
6. **Constrained optimization and handoff.** Only after those gates, optimize the
   agreed coordinates, record actual termination, validate its returned point,
   regenerate pressure histories, budget/CM and scale SVG, then commit a reviewable
   checkpoint. The existing 275.7-day number remains attached to the rejected
   boosted architecture. Follow with the separate five-cycle storage checkpoint.

### Review items that need explicit disposition

- Keep 4.767 kPa as the provisional working fill target, or use a different
  justified working pressure/margin? This sets the algebraic altitude estimate.
- What low-pressure gas-feed capability may be credited at the thruster interface?
  The valve-only reserve architecture is fixed; this question does not reopen
  high-pressure storage or authorize adding a refill compressor.
- Define the useful collection window and numerical full-capture tolerance.
  Literal capture of every vanishing atmospheric tail is not a finite-machine
  requirement; deliberate missed collection within the defined pass is not an
  optimizer trade variable.

Implementation dispositions are recorded in [the valve-reserve model](../modeling/propellant_feed/VALVE_RESERVE.md). The constrained solution and tighter-resolution validation are recorded in the results report.
