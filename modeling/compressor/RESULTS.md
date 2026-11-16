# Compressor refinement: evidence and cycle consequences

The main model now computes real-fluid, finite-efficiency compression and an
explicit geometry-based hardware mass. **This is a conditional mass estimate,
not a calibrated low-density compressor design.** The fixed candidate geometry
returns about **520–556 days** of operating-orbit mass payoff under the two tested
module geometries, versus 515 days with the previous compressor approximation.
These runs do not establish a new vehicle optimum or circular-apogee delivery payoff.

## What supports the estimate

[Comparable systems](COMPARABLE_SYSTEMS.md) records three different hardware
families and their boundaries: AERZEN centrifugal blower packages, Leybold Roots
boosters, and the Pfeiffer HiPace molecular pump. Their mass-to-suction-volume
ratios cannot be pooled into one coefficient. Atmospheric blower packages and
Roots units are hundreds of kg per m³/s; the much lighter molecular-pump ratio
cannot supply its quoted pumping speed at our required throughput.

[NASA WATE-S](https://ntrs.nasa.gov/api/citations/19830008072/downloads/19830008072.pdf)
provides a useful stagewise blade/case geometry method, rather than a matched
scoop machine. The implemented buildup uses total blade-row volume, stators,
cases, simplified centrifugally loaded disks, accessories and electric drives.
The NASA model's validation accuracy does not transfer to this implementation.
Source values, package boundaries and applicability are tabulated in the dossier.

[The implementation specification](IMPLEMENTED_MODEL.md) gives the equations,
input assumptions and limitations. CoolProp HEOS supplies N2/O2/Ar enthalpy,
entropy, density, viscosity and sound speed. Each block solves an isentropic
outlet, applies isentropic efficiency to enthalpy rise, and solves the actual
outlet temperature. Four cooled dive blocks and three coast blocks replace the
isothermal work approximation. A block contains many rotor/stator rows.

Cooling targets remain prescribed; the required heat loads are charged to the
warm cooling system. Finite metal-rack heat transfer, independent intermediate
inventories and an empirically supported compressor map remain future work.

## Paired runs and sensitivity

The reference uses the 100 × 2,000 km orbit, 18.3 m mouth, 250 m front depth and
25 m rear depth (106.2-minute orbit). The existing candidate uses 90 × 937 km,
30 m mouth, 25 m front depth and 26.515 m rear depth (94.9-minute orbit).
Exact values and all capabilities are recorded in each result's `inputs`.

“Standard” uses 1 m maximum module diameter, 250 m/s tip speed and 80 m/s axial
velocity. “Compact” uses 0.5 m, 350 m/s and 100 m/s. Neither geometry is selected
or flight-qualified. All new cases charge a declared **100 m machinery bay**;
legacy comparisons retain the old 20 m allowance. The longer allowance fits the
resolved banks but has not been optimized or fully packed with intercoolers.

Light/heavy multiply compressor structural mass by 0.5/2, before adding motors.
They are sensitivity cases, not confidence bounds. Low-efficiency cases use
60% instead of 75% block isentropic efficiency. Other inputs remain fixed.

| Case | Dry mass (t) | Compressors (t) | Net product (kg/pass) | Compressor electricity (kWh/pass) | Operating payoff (days) |
|---|---:|---:|---:|---:|---:|
| reference_legacy | 2,469.1 | 424.5 | 177.26 | 148.8 | 1,027.1 |
| reference_real_standard | 3,501.4 | 1,136.9 | 177.25 | 812.8 | 1,456.7 |
| reference_real_compact | 2,553.7 | 424.9 | 177.25 | 487.6 | 1,062.4 |
| reference_real_compact_light | 2,255.5 | 212.8 | 177.25 | 301.4 | 938.4 |
| reference_real_compact_heavy | 3,150.4 | 849.4 | 177.25 | 860.0 | 1,310.6 |
| reference_real_compact_low_eff | 2,706.9 | 532.6 | 177.25 | 610.8 | 1,126.1 |
| candidate_legacy | 26,749.7 | 720.1 | 3,425.76 | 2,925.4 | 514.6 |
| candidate_real_standard | 28,845.0 | 2,269.9 | 3,420.42 | 3,825.3 | 555.8 |
| candidate_real_compact | 26,992.5 | 861.2 | 3,420.42 | 3,182.0 | 520.1 |
| candidate_real_compact_light | 26,422.0 | 439.7 | 3,420.42 | 2,808.9 | 509.1 |
| candidate_real_compact_heavy | 28,157.0 | 1,707.8 | 3,420.42 | 3,928.2 | 542.5 |
| candidate_real_compact_low_eff | 27,314.8 | 1,063.6 | 3,420.42 | 3,966.3 | 526.3 |
| candidate_rear_100m | 27,011.1 | 861.8 | 3,424.61 | 2,781.0 | 519.8 |
| candidate_rear_200m | 27,039.1 | 825.2 | 3,425.45 | 2,697.1 | 520.2 |
| candidate_cutoff_0.3Pa | 26,968.2 | 844.9 | 3,420.42 | 3,139.7 | 519.6 |
| candidate_cutoff_1Pa | 26,925.1 | 814.9 | 3,419.92 | 3,087.9 | 518.8 |
| candidate_cutoff_3Pa | 26,762.4 | 699.3 | 3,414.00 | 2,960.6 | 516.6 |
| candidate_cutoff_10Pa | 26,612.7 | 600.0 | 3,384.55 | 2,825.7 | 518.2 |

Machine-readable [summary](../../results/compressor_refinement/summary.json)
and complete per-case files include states, geometry, masses, energy and inputs.

## Where the mass comes from

For the compact candidate, dive banks 1–4 weigh approximately **586, 190, 61 and
23 tonnes**; coast machinery adds **1.2 tonnes**. The first bank contributes
about 68% of compressor mass. The four banks have 36/38/38/38 aerodynamic rows,
with 1,607/494/149/45 parallel modules. Their lengths sum to approximately 22 m,
before intercooler spaces and routing. This is a screening arrangement, not a
manufacturable layout or a four-rotor compressor.

The first bank's reported blade Reynolds number is only about **466** at the
peak-flow state (later banks approximately 2,000, 8,000 and 32,000). Thus 75%
efficiency is a scenario, not a demonstrated capability. Smaller rotors save
mass while worsening Reynolds number and multiplying bearings, drives and
integration requirements. These competing effects need actual low-Re maps;
optimizing the present buildup toward infinitesimal modules would be invalid.
Hot allowable stress, shaft dynamics, blade vibration, casing buckling and life
also remain unqualified. The present row layout retains each bank's inlet
annulus throughout its rows, rather than resolving a tapered flow path.

Full spin-up each orbit, without regeneration, costs the compact candidate about
**0.746 MWh/pass**. Spin-up energy and peak motor/battery power are counted. A
keep-spinning or regenerative scheme is a separate potential improvement.

Despite this large compressor, propulsion hardware (~7,063 t), solar (~5,182 t),
power distribution (~3,576 t) and batteries (~2,661 t), plus the overall margin,
dominate the candidate's total mass. That is why large compressor differences
produce a smaller percentage change in whole-vehicle payoff.

## Cutoff and rear volume

At fixed compact geometry, a 3 Pa cutoff gives **516.6 days**, compared with
520.1 days at the original deep cutoff: compressor mass falls from 861 to 699 t,
while net product falls from 3,420.4 to 3,414.0 kg/pass. Cutting off at 10 Pa
reduces hardware further but worsens payoff to 518.2 days. This is a local sweep,
not a jointly optimized operating policy.

Extending the rear vessel to 100 m reduces compression electricity from 3,182
to 2,781 kWh/pass but barely changes payoff (519.8 days); 200 m gives 520.2 days.
The adopted minimum train pressure ratio of 100 limits how much lower tank
pressure reduces installed head. Changing that startup/throttling policy and
intermediate storage scheduling requires a separate trade.

A supplementary 40%-efficiency case at 3 Pa cutoff gives **535.5 days** and
**1,304 t** of compressors. This does not bound failure, stall or efficiency at
very low Re: a scalar efficiency cannot establish that the machine operates.
Its full inputs are saved in `candidate_eta40_cutoff3.json`.

## Validation and reproduction

Run `.venv/bin/python -m atmo_scoops.studies.compressor_refinement` for the paired
study. Every JSON includes exact inputs; `manifest.json` records source hashes.
The main configuration now selects the real-fluid model by default; explicit
`compressor.mode="legacy"` preserves comparisons.

All **36 tests pass**, including independent CoolProp entropy-flash agreement,
finite-efficiency entropy increase, nonideality, geometry/motor accounting and
compression/idle/spin energy accounting. The audit passes eight cycle
resolution/conservation cases and Kepler energy/angular-momentum checks.
Increasing encounter and thermodynamic samples from 401 to 1,601 for the
standard reference, compact candidate and 3 Pa cutoff changes payoff by less
than 0.001%; see [convergence data](../../results/compressor_refinement/convergence.json).
Numerical convergence does not validate the omitted machinery or heat transfer.

**The resulting payoff is still a conditional operating-orbit estimate.** The
90 km candidate has no established reusable leading-edge envelope, and delivery
to circular apogee, calibrated low-Re maps and finite interstage cooling are
still required before claiming a mission-level payoff.
