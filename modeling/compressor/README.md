# Compressor train modeling

**Status: research stub with established calculations; hardware and maps remain
unselected.** The active cycle uses approximate isothermal work and provisional
volume-flow/power mass coefficients. It does not resolve the proposed three/four
cooled blocks, blade rows, interstage gas states or stall/surge limits.

Start with the [research requirements](RESEARCH_REQUIREMENTS.md) and
[comparable-hardware evidence table](COMPARABLE_SYSTEMS.md). The replacement
must use real-gas enthalpy/entropy states, an isentropic endpoint and realistic
efficiency, plus mass estimates supported by multiple comparable systems.
The constant-property calculations below are retained screening examples only.
No evidence-backed spacecraft compressor mass estimate has yet been established.

## Calculation inventory

- [Staged-compression investigation](SCREENING_CALCULATIONS.md):
  continuity, all-block flow areas, axial Mach, ideal work, metal intercooler
  inventory, pressure losses and off-design behavior.
- [State-resolved model plan](MODEL_PLAN.md):
  independent rack mass and lattice geometry in each volume, finite heat transfer,
  pressure losses, compressor maps, matched flow and periodic thermal restoration.
- [Rear-depth investigation](../../conclusions/rear_storage_depth/INVESTIGATION.md):
  block power fractions, storage-pressure sensitivity, hardware scaling and
  separation of dive work from downstream coast compression.

### Governing screening relations

For low axial Mach, `A v = m_dot R T / p`. Use static states for density and
total states for compressor maps; do not silently equate them at high Mach.
For a constant-property compressor block:

```
a = (gamma - 1)/gamma
w_shaft = cp T_in (pressure_ratio**a - 1) / eta_isentropic
T_out = T_in + w_shaft/cp
P_shaft = m_dot w_shaft
P_electric = P_shaft / eta_motor
```

This requires a pressure ratio and efficiency; an inlet-area table alone does
not establish power. A cooled block can contain multiple rotor/stator rows.
Equal block pressure ratios are a comparison allocation, not generally optimal
when inlet temperatures or efficiencies differ.

Reference screening point: 1.283 kg/s, 26.8 Pa, 1,000 K first inlet, 600 K
intermediate cooled inlets, 3,753 Pa final receiver, four equal ratios 3.44,
R=287 J/(kg K), gamma=1.35, block isentropic efficiency 0.8.

| Location | Net area at 60 m/s | State |
|---|---:|---|
| Block 1 inlet | 229 m² | 26.8 Pa, 1,000 K |
| Block 2 inlet | 39.9 m² | 92.2 Pa, 600 K |
| Block 3 inlet | 11.6 m² | 317 Pa, 600 K |
| Block 4 inlet | 3.38 m² | 1,091 Pa, 600 K |
| Final hot discharge | 1.44 m² | approximately 3,753 Pa, 883 K |

These are chosen states and net flow areas, not demonstrated hardware. Losses
and a finite pressure margin above the tank must be added. The last jet diffuses
into the storage volume. Peak flow and full-tank pressure need not coincide.

Corrected flow scales as `m_dot sqrt(T_in/T_ref)/(p_in/p_ref)` and corrected
speed as `N/sqrt(T_in/T_ref)`. Under constant capture/recovery, both flow and
inlet pressure scale with atmospheric density, so falling absolute pressure
need not move the first block far across its corrected-flow map. Reynolds
number, rarefaction and clearances still matter. A filling tank and declining
inlet pressure increase required head: all banks need matched operating maps.
Variable speed, guide vanes/stators, module scheduling, recycle and cutoff are
candidate controls; variable rotor pitch is a distinct mechanical option.

## Annotated primary references

1. [NASA Glenn, Compressor Thermodynamics](https://www.grc.nasa.gov/www/k-12/airplane/compth.html).
   Establishes pressure-ratio, inlet-temperature and efficiency dependence of
   specific compression work. Basis for the block equations above. It supplies
   no compressor mass, low-pressure efficiency, or stable operating map.
2. [Chapman, Lavelle and Litt, Practical Techniques for Modeling Gas Turbine
   Engine Performance, NASA/TM–2016-219147](https://ntrs.nasa.gov/api/citations/20160012485/downloads/20160012485.pdf).
   Describes component-map modeling and matching, including corrected flow/speed
   and variable geometry. Relevant to solving coupled banks rather than freely
   specifying flow, pressure ratio and efficiency independently. Its engine maps
   are not validated scoop-compressor maps.
3. [Chapman et al., T-MATS User’s Guide, NASA/TM–2014-216638](https://ntrs.nasa.gov/api/citations/20140012486/downloads/20140012486.pdf).
   Provides a concrete thermodynamic component-model framework and compressor
   map conventions. Useful implementation reference for consistent states and
   map interfaces; not evidence that sea-level maps retain efficiency at tens
   of pascals or with transient hot gas and metal racks.
4. [NASA contractor fan-stage test, variable inlet guide vanes and stator,
   NTRS 19720020168](https://ntrs.nasa.gov/citations/19720020168).
   Measured variable-geometry effects on off-design performance, stall margin
   and inlet-distortion tolerance. Establishes that these controls can change
   an operating envelope. It does not quantify our turndown, suggest a selected
   rotor speed or guarantee that inlet distortion can be controlled here.
5. [Interstage Pressures of a Multistage Compressor with Intercooling,
   Entropy 23(3), 351 (2021)](https://www.mdpi.com/1099-4300/23/3/351).
   Derives work-minimizing pressure allocations accounting for intercooling,
   unequal temperatures/efficiencies and pressure losses. Supports treating
   equal pressure ratios as a restricted case. It does not size transient solid
   racks or establish low-density blade performance.
6. [NASA Glenn, Compressible Mass Flow](https://www.grc.nasa.gov/www/BGH/mflchk.html).
   Establishes the ideal sonic throughput bound from upstream state and area.
   Useful as an access screen, not a compressor performance curve or proof of
   inlet starting and shock stability.

## Evidence still needed before model replacement

- Machine-family selection by block; applicable maps versus Reynolds number,
  temperature, pressure, mixture, speed and geometry, including reverse flow.
- Flow distortion from shock/racks, map stability margins and plenum coupling.
- Independently sized rotors, casing, motors, bearings, clearances and thermal
  expansion; reconcile suction-volume and power mass surrogates with hardware.
- Finite rack conductance/capacity, pressure drop and time-varying interstage states.
- Rotor inertia, startup, bank matching, cutoff, isolation and recovery losses.
- Receiver transient temperature and coast processing pressure. Lower storage
  pressure does not eliminate compression needed by the downstream process.

The reference list is a starting point for the requested component-by-component
review, not a completed literature survey or authorization to replace the model.
