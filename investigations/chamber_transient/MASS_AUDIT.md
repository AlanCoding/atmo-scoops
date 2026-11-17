# Mass audit of the SiC/aluminum transient proxy

This traces the reported 373-day isolated result to its component ledger. It
**does not recouple or rerun the full spacecraft model**. The supported design
direction is a high-temperature front rack with aluminum downstream; the SiC
versus FeCrAl engineering choice remains open.

## Where the mass is

| Component | Mass, tonnes | Share of dry mass |
|---|---:|---:|
| Thruster hardware | 5,386.0 | 27.70% |
| Electrical distribution | 2,747.9 | 14.13% |
| Solar arrays | 2,244.0 | 11.54% |
| Battery | 2,066.8 | 10.63% |
| Dive compressors incl. motor uprating | 935.9 | 4.81% |
| Warm heat buffer | 576.4 | 2.96% |
| Rack deployment hardware | 449.9 | 2.31% |
| Rack material | 443.0 | 2.28% |
| Warm radiators | 387.2 | 1.99% |
| Refrigeration machinery | 151.5 | 0.78% |
| Pressure vessels | 87.0 | 0.45% |
| Hull/TPS allowance | 47.2 | 0.24% |
| Other equipment and proxy adjustments | 30.8 | 0.16% |
| Design margin | 3,888.4 | 20.00% |
| **Total** | **19,442.1** | **100%** |

The margin is 25% of the equipment subtotal (therefore 20% of final dry mass),
added once. There is no arithmetic double counting of that margin. Solar arrays,
battery, electrical distribution and thrusters are separate ledger items; their
real hardware scope must nevertheless be defined to avoid counting a thruster
power-processing unit both in installed thruster mass and distribution.

## The dominant physical requirement and the dominant assumptions

The assumed intercepted-column impulse is **55.98 MN s**.
At **17.32 km/s** effective exhaust velocity, 60% efficiency
and a 300 s burst:

- Propellant: J/u = **3.233 t/pass**.
- Electric energy: Ju/(2 eta) = **807.9 GJ/pass**.
- Thruster input: E/300 s = **2.693 GW**.
- Thrust: J/300 s = **186.6 kN**.
- Net useful inventory: **3.838 t** per **106.03 min** orbit,
  or **52.13 t/day**. Dividing dry mass by that rate reproduces payoff.

These equations are dimensionally consistent: Ns × m/s = joules, then divide by
seconds for watts. They do not multiply drag by spacecraft dry mass. The assumed
momentum bill includes the intercepted column, including rejected air, but lacks
a resolved external hull/fin drag calculation.

The 5,386 t thruster entry is the explicit **2 kg/kW** installed capability target
multiplied by 2.693 million kW. Distribution is **1 kg/kW** times the approximately
2.748 GW combined bus requirement. Neither coefficient is a demonstrated
multi-gigawatt O2/N2 installation. Efficiency, lifetime, power-processor scope,
plume accommodation and thermal interfaces still need component research.

Even propulsion alone implies about **1969 t** of batteries
under 150 Wh/kg, 80% usable capacity and 95% discharge efficiency, and about
**2057 t** of arrays at 150 W/kg with the inherited sunlight
window and charge/discharge losses. The large power-system mass is therefore
not mainly an uncooled compressor penalty.

As a diagnostic, propulsion-only thrusters, bus, batteries and arrays plus the
same margin already imply about **15,131 t**, or **290 days**
at the selected net production rate, even if all other equipment were free.
This is conditional on the current 300 s burst, Isp/efficiency, sunlight and
specific-mass assumptions, not a fundamental bound on atmospheric scoops.

## What is frozen, and what should respond

| Item | Current isolated treatment | Required coupled treatment |
|---|---|---|
| Rack material, area and displacement | Recomputed per material and geometry | Retain; add alloy/ceramic supports, coating and lifetime |
| Compressor bodies/rows/annuli | Anchor geometry and suction/head envelopes frozen | Co-optimize capacities and schedules using stage inlet T, density, flow, required head and real compressor maps |
| Compressor motors | Uprated if sampled pumping peak exceeds installed motor; never downsized | Size for both pumping and spin-up, with speed/inertia/control schedules |
| Compressor electricity | Transient flow work changes charged relative to a separate transient baseline | Replace absolute pumping, idle and spin energy consistently; do not splice unlike baselines |
| Thrusters and propellant | Fixed geometric-column impulse, Isp, efficiency and burst | Recompute when capture/escape/hull drag, Isp or burn schedule changes; cooler gas alone does not remove momentum |
| Battery and solar | Anchor plus signed compressor-energy mass correction | Rebuild time-resolved loads, energy/power limits, eclipse, efficiency, recharge and array deployment |
| Warm buffer and radiators | Old duties retained | Rebuild heat ledger: gas heat retained in deployable racks, motor/drive losses, propulsion heat, charge/discharge heat and coast processing |
| Coast compressor and cryoplant | Mass multiplied by a nominal throughput factor | Recompute receiver P/T/mass over time, actual feed compression, exchanger approach/UA, cold duty and plant electrical loads |
| Warm aftercooler | Legacy unit retained, plus extra hot-feed surcharge | Define whether receiver rack replaces it, supplements it, or leaves a distinct exchanger duty |
| Equipment packing and deployment | Anchor bay retained plus added motor volume | Update every resized machine, plant, buffer and mechanism; iterate geometry, deployment and available operating time |
| Pressure vessels and outer shell | Recomputed with simple screen | Resolve heads, access hatches, common bulkheads and stability loads |

## Concrete accounting limitations found

1. **Plant mass grows without matching electrical and thermal resizing.** The
   nominal 2 kg/s withdrawal gives a **1.479×** mass multiplier
   for selected processing components. The anchor cryoplant is 10.69 MW;
   straightforward throughput scaling would imply 15.81 MW installed
   process capacity, but the proxy does not propagate that duty into arrays,
   eclipse batteries, rejection hardware or package volume. A larger machine
   need not consume proportionally more total energy per batch; the actual
   operating schedule must be calculated, rather than scaling energy blindly.
2. **The thermal architecture is not fully reconciled.** Legacy warm-buffer,
   radiator and aftercooler masses remain, while the transient racks store heat
   that is later radiated directly. An additional 10 kg/MJ hot-feed surcharge is
   also charged. That is a conservative proxy charge, not a proof of disjoint
   physical components. It can overcharge overlapping duties; other omitted
   duties can undercharge mass, so the total is not a rigorous upper bound.
3. **Compressor electrical accounting has a baseline mismatch.** The anchor
   includes 13.51 GJ for compression, including
   2.87 GJ spin-up and idle consumption. The selected transient
   integrates 8.74 GJ of pumping electricity, with
   neither explicit spin nor idle. Only its difference from another transient
   is added to the anchored electrical system. One must not call the entire
   difference an available saving: spin and idle have to be retained or redesigned.
4. **Equipment volume is stale.** Increased plant capacity and changed rack
   deployment hardware are not fully reflected in the inherited equipment bay.
   The motion formula used sqrt(deployment mass), rather than sqrt(area).
   This audit corrects it to use area. It gave the same value for these saved
   cases because the coefficient is 1 kg/m² and the solar-array motion allowance
   is larger; the correction does not change their payoff. A regression test
   now checks that changing mechanism kg/m² does not change travel time.
5. **Dry/wet boundaries need a consistent definition.** Useful liquid and
   propulsion consumables are excluded from dry mass; thermal storage medium is
   included in its package. The primary model exposes warm-loop working fluid
   separately, whereas this dry-mass proxy does not add that inventory. The
   installed-component and working-inventory definitions should be reported
   together before claiming launch mass.
6. **Numerical conservation does not validate the subsystem budgets.** The
   transient conserves gas/solid energy, but it is not a closed, repeated-cycle
   spacecraft heat/electricity/propellant simulation. Frozen ideal-mixture caloric
   gas properties are used here; the primary compressor uses HEOS. Actual
   high-temperature inlet chemistry and rarefied compressor performance remain
   open. The 300 s thrust burst also remains an impulse-equivalent requirement,
   not a distributed-thrust orbital closure calculation.

## Stage-specific compressor evidence

These are observed pumping requirements, not newly sized banks. Installed mass
includes spin-up capability that peak flow work alone cannot justify deleting.

| Stage | Fixed structure, t | Fixed motor, t | Transient peak electric MW | Pumping MWh/pass | Flow-weighted inlet K | Observed max head, kJ/kg | Fixed head capability, kJ/kg |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 626.22 | 34.82 | 13.27 | 0.62 | 751.23 | 921.86 | 941.48 |
| 2 | 181.97 | 13.87 | 11.97 | 0.58 | 446.90 | 1205.01 | 1213.00 |
| 3 | 38.15 | 10.53 | 9.45 | 0.49 | 451.22 | 933.89 | 933.92 |
| 4 | 13.42 | 9.77 | 16.96 | 0.75 | 417.31 | 823.74 | 823.74 |

The first compressor remains most of the compressor mass, but all dive
compressors together are under 5% of total dry mass. Its 35 aerodynamic rows,
roughly 1,865 half-metre modules and 626 t structural estimate are retained from
the anchor; they are not a new optimum for the SiC path. A colder inlet changes
specific volume (RT/p), specific compression work and feasible flow. Because the
simulation keeps suction capacity and maximum head fixed, it credits increased
throughput/lower work but does not automatically remove that installed structure.

## Sensitivity to the largest coefficients

Holding all dynamics and other hardware fixed, reducing just one coefficient
by 10%, including the resulting margin reduction, gives:

| Assumption reduced 10% | Algebraic proxy days |
|---|---:|
| propulsion_hardware | 360.0 |
| power_distribution | 366.4 |
| solar | 367.6 |
| battery | 368.0 |

These are local bookkeeping sensitivities, not alternative validated spacecraft.
They show why propulsion/electrical hardware research is now at least as important
as further rack refinement.

## Recommended interpretation and next coupling step

The mixed-material rack architecture is worth retaining as the working design.
The 373-day figure is a **conditional operating-orbit proxy**, with stated
power-system coefficients and frozen hardware. It is not yet a fully recoupled
SiC/aluminum spacecraft estimate, and excludes circular-apogee export.
Publishing the architecture and conditional calculation is reasonable if that
scope accompanies the number; neither the conservation tests nor this audit
turn it into a demonstrated mission payoff.

Next: build an absolute cycle ledger from these transient stage histories;
resize compressor banks/motors, define coast plant duty and thermal paths, then
resize battery/arrays/buffers/radiators/distribution and their packing. Iterate
until deployment and duty windows agree. Only then reoptimize allocation and
Isp. Preserve the current frozen results as comparison data.

Source equations: `chambers/proxy.py`, `physical_cycle.py`, `two_volume.py`,
`compressor.py`. [Propulsion assumptions and primary references](../../modeling/propulsion/REBOOST_INVESTIGATIONS.md).
Exact ledger and reproduction:

```sh
.venv/bin/python -m atmo_scoops.studies.chamber_mass_audit
```

Machine-readable output: `results/chamber_materials/mass_audit.json`.
