# Complete coupled-cycle reference

This investigation replaces the isolated chamber laboratory's anchored mass/payoff
proxy with a forward simulation of installed hardware. The spacecraft's gas,
metal, electrical, thermal and liquid inventories now have to survive the same
cycle. [Numerical tables and figures](RESULTS.md) contain the results; the
[model specification](../../modeling/primary/TRANSIENT_IMPLEMENTATION.md) documents
its equations, independent inputs and limitations.

The best accepted candidate in this **limited initial search** gives about
**285 days of operating-orbit payoff**, **14,017 tonnes dry** and **3.62 tonnes of
net liquid per 106-minute orbit**. It collects about 7.11 tonnes of air and spends
about 3.49 tonnes of nitrogen/oxygen propellant on reboost. These are conditional
engineering estimates, not circular-apogee-delivery numbers or a global optimum.

The initial repeatable reference gives 317 days. Reducing installed power-system
reserve capacities and starting the racks at 300 K brings that to 285 days.
The first Isp/burn-duration screen does not establish a benefit from raising Isp
to 2,300–2,800 s: less propellant also requires more electrical energy and more
installed power hardware. That screen ties capacity proposals to reboost work;
it is not a complete optimization at each Isp. The 2,800 s / 23.3-minute case required a larger numerical Jacobian differencing step to complete; it gives about 339 days. The original failed attempt and successful numerical setting are preserved. Numerical failures otherwise carry no accepted payoff.

The difference from the earlier ~258-day burn-duration estimate is meaningful:
that was a frozen-budget propulsion aside. This model explicitly includes the
coast plant's power/rejection, battery recovery and eclipse timing, independently
moving thermal stores, finite machinery, and the fixed 317 m volume budget.

## Key implementation decisions

1. **One integration per candidate.** Compile installed hardware first. Return
   objective, periodic residuals and constraint margins for an external search.
   Physical feedback controls may curtail charging/radiation; nothing resets
   energy to the desired endpoint for free.
2. **Keep the hull fixed.** 30 m bore, 31.7 m outside, L/D exactly 10. Independent
   front/intermediate depths and rack allocations leave the residual length for
   the receiver. The best tested receiver is approximately 239 m deep.
3. **Use real-gas compressor work.** HEOS mixture isentropic enthalpy rise with
   efficiency, finite head/flow/motor ratings and spin energy. Chamber gas uses
   variable heat capacity and the audited low-density EOS approximation.
4. **Pay for a full reusable cycle.** Actual solar/battery power and warm-store
   heat rejection constrain compression and liquefaction. Gas left when a rack
   must deploy is discarded and debited. The inlet remains open; only pressure
   hatches for the sealed downstream rack chambers are involved.
5. **Let burn duration and Isp vary.** Use the finite-arc energy/angular-momentum
   correction. The best tested sizing case retains approximately 1,766 s Isp and
   a 20-minute burn. Nitrogen and oxygen can both supply propulsion.
6. **Keep the first search small and interpretable.** Perigee 85 km, apogee
   2,000 km, SiC front/aluminum downstream, and lattice geometry remain fixed.
   Stage capacities/volumes/temperatures are editable inputs, but their full
   joint allocation optimization has not been performed here.
7. **Preserve the older program.** `scalar/` is a compatibility gateway; legacy
   imports and studies are not broken by moving all their files at once.

The generic warm-store capability and uncalibrated compressor maps remain major
model assumptions. Hatch/vent hardware, pressure-vessel stability, external drag
and long-term deployed structures are not fully sized. **At this first coupled
reference review, the pitch reminder is due: include lattice pressure loss before
releasing pitch to the optimizer.** The reference still fixes 1 mm radius and
10 mm pitch and charges no rack head loss.

## Numerical verification

The validation run passed **84 tests**, plus the repository audit of eight legacy cycle/conservation cases and Kepler energy/angular-momentum checks. Both new-model mass-species and total-energy ledgers close. Reducing the integration step
from 10 to 5 seconds, tightening relative tolerance and halving the trace-gas
regularization changes the initial reference payoff by **0.018%**, and the best
candidate by **0.00076%**. This tests numerical resolution, not physical accuracy.
The best candidate's audited chamber compressibility deviation is only
approximately **0.0014%**; independent HEOS compressor calculations agree with
its work calculation. Neither check validates the assumed efficiency/map.

A 2% LN₂-injection exercise circulates about **142 kg/pass** and still passes
species, energy and periodic checks, including replenishment of the injected
inventory. It gives about **286 days** with unchanged installed hardware. This
is a feature/conservation check, not a renewed conclusion that mixing cannot help;
its value still depends on the compressor model and future film-cooling needs.

The selected warm store peaks near 445 K against a 450 K capability limit.
That narrow physical margin deserves a robustness study; numerical feasibility
must not be mistaken for a flight operating margin.

## Reproduction

From the repository root, using the local venv:

```bash
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -m atmo_scoops.transient --config configs/transient_reference.json
.venv/bin/python -m atmo_scoops.transient.search --workers 2
.venv/bin/python -m atmo_scoops.transient.search --study sizing --output results/transient/sizing --workers 2
.venv/bin/python -m atmo_scoops.transient.report
.venv/bin/python -m atmo_scoops.transient.verify
.venv/bin/python -m pytest -q
.venv/bin/python -m atmo_scoops.audit
```

The report chooses the best feasible saved candidate, audits its property regime,
and writes `results/transient/best_config.json` and `best.json`. Individual
candidate inputs and accepted/rejected status are preserved in the search
comparison files. `max_rhs_evaluations` bounds expensive numerical failures;
those failures must not be interpreted as physical infeasibility. A numerical
retry changes solver settings, not cycle closure through repeated missions.

The root `python -m atmo_scoops` command still reproduces the **legacy scalar**
model. The new coupled evaluator is explicitly `python -m atmo_scoops.transient`.

Search trajectories are stored losslessly as `cycle_N.json.gz`; summary tables and selected reference/best trajectories remain ordinary JSON.
