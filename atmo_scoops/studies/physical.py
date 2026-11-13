"""Generate physical-depth tables and scientific figures from saved results."""
import json
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    data=json.loads(Path('results/physical_cycle.json').read_text())
    r=data['reference'];cy=r['cycle'];hw=data['hardware_inputs']
    lines=[f'''# Physical depths, complete-cycle duties, and conditional spacecraft mass

The comparison layout has **18.3 m clear diameter in both compartments**,
matching the 18.3 m mouth. Front depth means mouth
plane to compressor bulkhead. Rear depth is the entire axial tank length,
including two 2:1 ellipsoidal heads, each 4.575 m deep. No equivalent depth is
used in the tables. The rear tank needs at least 9.15 m for those heads alone.

Comparison point: 250 m front + 25 m rear + 20 m machinery/layout allowance = 295 m,
inside a 20 m outer-diameter shell. The sweep allows the overall length to
change; shell/TPS mass changes with it. It does not leave an empty 500 m shell
around every case. The 20 m machinery allowance is not a verified equipment
packing plan. Fore/aft cowling and support details still need layout work.
**250 m has no optimization justification.** It is a reproducible comparison
coordinate. Shorter fronts score better in this model because shock accommodation,
heat-transfer conductance and pressure-loss requirements do not yet impose a
minimum usable length. No row is a selected spacecraft design.

Use the configurable [Python API and CLI](../../README.md) and the independent
input ledger in [PARAMETERS.md](PARAMETERS.md). The [precooling trade](PRECOOLING_TRADE.md)
varies compressor inlet temperature and derives the metal's hot endpoint.

The orbit remains **100 × 2,000 km**. Full geometric capture while open is a
requirement assumption. Total drag in these tables is **captured-air momentum
only**. Exterior/closed-door drag has not been calculated. The output is a
conditional installed-mass estimate with explicit allowances for all main
subsystems, not a validated structural design or delivered-mass payoff.

## One full cycle

Times below are measured from mouth closure at perigee. Reboost overlaps the
encounter; the 180 s thrust burst is an impulse-equivalent sizing assumption,
not an integrated thrust trajectory.

| Phase | Timing | Gas / equipment state |
|---|---|---|
| Open collection | −{cy['collection_s']:.1f} to 0 s | {r['captured_kg']:.2f} kg enters; {r['collected_before_closure_kg']:.2f} kg already transferred aft |
| Sealed residual recovery | 0–{cy['recovery_s']:.0f} s | Transfer another {r['recovered_after_closure_kg']:.2f} kg; front pump capacity {r['recovery_suction_m3_s']:.0f} m³/s |
| Reopen front, isolate rear, deploy | 450–750 s | Vent {r['vent_kg']:.3f} kg front residual; deploy attached metal sheets, arrays and warm radiators |
| Fully deployed coast | {cy['deploy_complete_s']/60:.2f}–{cy['retract_start_s']/60:.2f} min | {cy['deployed_s']/60:.2f} min processing/radiation, including {cy['sunlit_s']/60:.2f} min sunlight |
| Retract | {cy['retract_start_s']/60:.2f}–{(cy['retract_start_s']+cy['retract_s'])/60:.2f} min | Five-minute mechanism allowance; then prepare next entry |
| Next mouth opening | {(cy['orbit_s']-cy['collection_s'])/60:.2f} min | Next inbound collection window begins |
| Next perigee | {cy['orbit_s']/60:.2f} min | Cycle repeats |

After recovery the front is at about {r['front_pressure_Pa']/10:.2f} Pa, and
rear storage at {r['rear_pressure_Pa']/1000:.3f} kPa and 340 K. The batch retained
aft is **{r['retained_kg']:.2f} kg**. The 4,000 s Isp capture-only reboost uses
**{r['propellant_kg']:.2f} kg oxygen**. Including the 0.1% first-cycle rear gas
heel, useful liquid-equivalent remaining is **{r['net_liquid_equivalent_kg']:.2f}
kg/cycle**, or **{r['net_liquid_equivalent_kg_day']:.0f} kg/day** continuously at
this orbit. These are operating-orbit production numbers, before circular
apogee delivery. The rear heel is retained, not repeatedly destroyed; subsequent
cycles differ by less than 0.1 kg with this small carryover assumption.
Reboost burns oxygen prepared on the preceding coast; it does not require the
current hot intake to become thruster propellant immediately. Startup therefore
needs a charged battery and an initial oxygen inventory.

Gas compressors draw {r['compressor_peak_MW']:.2f} MW at peak and
{r['compressor_kWh']:.1f} kWh per encounter. Coast refrigeration draws
{r['cryoplant_electric_kW']:.1f} kW for {r['cold_duty_kW']:.2f} kW of cold duty.
Reboost needs {r['reboost_MWh']:.2f} MWh and an impulse-equivalent
{r['reboost_peak_MW']:.1f} MW burst. This large peak is why propulsion hardware,
batteries and electrical distribution matter in the mass ledger.

## The three deployed systems

| System | Physical deployed panel/sheet area | Emitting area | Main duty |
|---|---:|---:|---|
| Solar arrays | {r['solar_area_m2']:,.0f} m² | — | {r['solar_MW']:.2f} MW in usable sunlight at 250 W/m² |
| Warm ammonia-loop radiators | {r['warm_radiator_panel_m2']:,.0f} m² | {r['warm_radiator_emitting_m2']:,.0f} m² | Two exposed emitting faces, 320 K |
| Hot metal absorbers/radiators | {r['metal_panel_m2']:,.0f} m² | {r['metal_emitting_m2']:,.0f} m² | Two exposed faces; 500–900 K thermal cycle |

The warm radiator area assumes both faces have the modeled view factor. A
single-sided implementation needs twice this physical panel area. Installed
warm-radiator mass remains 5 kg per square metre of emitting area (10 kg per
square metre of double-sided panel), so halving physical area does not halve
mass. Hot sheets are 0.25 mm thick. Deployment booms and spacing make the actual
spatial footprint larger than panel area; no football-field spacing geometry
has been solved. The iron heat-capacity proxy is not a selected flight alloy.
The metal holds about {r['hot_absorbed_GJ']:.2f} GJ. If its full two-face area is
exposed with the assumed emissivity and background, cooling from 900 to 500 K
takes only {r['ideal_metal_cooldown_s']:.0f} seconds in the ideal sheet calculation.
Deployment, mutual shadowing and hot-spot equilibration can take longer. Metal
sheets can be recovered independently after cooling; keeping them exposed for
the entire coast would cool them below the assumed 500 K cycle starting point.
Solar and warm radiators retain the long deployed-coast schedule in this model.

## Compressor mass: an explicit development target

A compressor mass cannot be obtained uniquely from mass flow and pressure.
The installed compressor model uses an explicit capability target:

    M_bank = max(alpha × required suction capacity, peak electrical power / beta)

Reference alpha = **30 kg/(m³/s)** and beta = **1,000 W/kg**. Each coefficient
applies to a complete bank, including its stages, motors, housings and immediate
manifolds. Hot, warm, and coast feed banks are sized separately. The hot bank
serves both collection and recovery: its mass uses the larger of their capacities,
not their sum. No rotor speed, blade chord, pump mechanism or module count has
been silently selected. Losses/conductance must ultimately fit this installed
performance target. Equivalent-isothermal efficiency remains a 50% target.

For an evidence anchor, Leybold lists **650 kg and 9,800 m³/hour** nominal speed
for the WH 7000 at its highest listed frequency: about **239 kg/(m³/s)** for that
booster alone. Nominal displacement is not delivered speed with backing pumps;
adding stages can worsen the installed ratio. That machine is neither a 1,000 K
space pump nor the required spacecraft design. Our 30 target asks for about an
eightfold improvement over its nominal bare-booster ratio, despite including
stages. R&D may change topology and remove terrestrial vacuum-housing burdens,
but this source does not prove that improvement. The 10–300 sweep below is an
engineering sensitivity, not a confidence interval or physical lower bound.
[Manufacturer data](https://www.leybold.com/content/dam/brands/leybold/downloads/brochures/product-brochures-fore-vacuum/mechanical-booster-pumps/3611019802_RUVAC%20WH_web.pdf).

| Compressor target alpha | All three compressor banks | Total dry mass, incl. margin |
|---:|---:|---:|''']
    for x in data['compressor_mass_sensitivity']:
        lines.append(f"| {x['compressor_kg_per_m3_s']:.0f} kg/(m³/s) | {x['compressor_mass_kg']/1000:,.0f} t | {x['total_dry_kg']/1000:,.0f} t |")
    lines.append(f'''
At the reference target the compressor mass is **{r['compressor_mass_kg']/1000:.0f} t**,
and the whole installed dry-mass estimate is **{r['total_dry_kg']/1000:,.0f} t**.
There is no mass ceiling or feasibility rejection attached to these values.
A separate {r['circulating_warm_fluid_kg']:.0f} kg circulating-fluid allowance is
wet inventory. Hot metal, installed PCM and deployment hardware count as dry.
The 500 kg liquid-system allowance covers one-cycle storage/plumbing, not an
arbitrarily large export inventory or a delivery vehicle.

## Whole-system mass ledger

| Component | Reference mass |
|---|---:|''')
    for key,value in r['masses_kg'].items():
        lines.append(f"| {key.replace('_',' ')} | {value/1000:,.3f} t |")
    lines.append(f"| **Total dry** | **{r['total_dry_kg']/1000:,.1f} t** |")
    lines.append('''
All new coefficients are saved in `results/physical_cycle.json` under
`hardware_inputs`. Principal additional targets: propulsion 2 kg/kW of peak
input power; distribution 1 kg/kW of peak bus power; hot-sheet deployment
1 kg/m² of sheet; 1 mm minimum aluminum tank gauge with 150 MPa allowable,
1.5× design pressure, 50% support allowance and 1 kg/m² insulation; shell/TPS
4 kg/m²; 25% additive mass margin. These are engineering allowances, not measured
hardware capabilities. The propulsion target alone is 242 t at the reference
121 MW burst. Its sensitivity is saved separately. Array and warm-radiator
specific masses include their deployment/support allowances; they are not
added a second time. Power conversion losses use the existing lumped electrical
path efficiencies; no independent detailed PMAD circuit has been modeled.

Thermal exchange, actuator energy, rotor spin-up, structural modes, oxygen
compatibility, hot pump clearances and actual deployment mechanisms still need
design. Ten kilowatts auxiliary power is an allowance, not a mechanism solution.
The margin does not validate these capabilities or bound their mass errors.

## Physical depth sweep

Fixed mouth, orbit, temperatures, open suction capacity and 450 s/90% residual
recovery. All rows ingest 84.8 kg. More front depth leaves more gas at closure;
the fixed 90% recovery rule leaves slightly more vent loss. It does not mean a
long chamber intrinsically captures less; a different recovery policy changes
that outcome. Total lengths span 55–520 m including the 20 m layout allowance;
500 m is an approximate design target, not a sharp feasibility cutoff. Both
gas-space diameters are 18.3 m.

| Front depth | Rear depth, incl. ends | Total length allowance | Rear pressure | Compressors | Total dry mass | Net liquid-equivalent per cycle | Net per day |
|---:|---:|---:|---:|---:|---:|---:|---:|''')
    for x in data['depth_sweep']:
        lines.append(f"| {x['front_depth_m']:.0f} m | {x['rear_depth_m']:.0f} m | {x['overall_length_allowance_m']:.0f} m | {x['rear_pressure_Pa']/1000:.3f} kPa | {x['compressor_mass_kg']/1000:.1f} t | {x['total_dry_kg']/1000:,.0f} t | {x['net_liquid_equivalent_kg']:.2f} kg | {x['net_liquid_equivalent_kg_day']:.0f} kg/day |")
    lines.append('''
This is a depth sweep, not a physical optimum. Shortening the front removes
shell mass in this model, but the model has not established the length needed
for the shock/diffuser, heat exchange or survivable surfaces. Making the rear
longer reduces required discharge pressure, while adding minimum-gauge tank
skin, insulation, supports and hull. It also increases the coast feed pump's
volumetric duty. Minimum-gauge construction dominates these low-pressure tanks.
A wider/deeper gas store is therefore not free even when membrane stress is low.

## What front depth does to pumping and shock control

For constant temperature, the cooled front compartment obeys

    V/(R T) × dp_front/dt = mdot_in − mdot_pump
    mdot_pump = p_front S/(R T).

Depth sets V, which changes how much imbalance can be buffered. For slowly
changing p, mdot_pump must approach mdot_in regardless of depth. For a chosen
pressure trajectory, required pumping is mdot_in − V/(RT) dp/dt. This permits a
real control trade; it does not permit arbitrary removal through finite openings.

I solved for the minimum *constant* suction capacity that keeps the modeled
plenum below 0.7 rho u² throughout the collection window, assuming full intake.
That 0.7 remains a control-screen target, not a validated shock stability limit.
The minimum has no reserve; it is a sensitivity calculation, not a controller
recommendation.

| Physical front depth | Minimum constant suction capacity | Front acoustic transit | Front turnover at that capacity |
|---:|---:|---:|---:|''')
    for x in data['minimum_constant_suction_sweep']:
        lines.append(f"| {x['front_depth_m']:.0f} m | {x['hot_suction_m3_s']:,.0f} m³/s | {x['acoustic_transit_s']:.3f} s | {x['front_turnover_s']:.2f} s |")
    lines.append(f'''
Going from 25 m to 400 m reduces that required constant capacity only about
1.2%. In this length range, storage buffers seconds of flow while collection
lasts 81 seconds. The instantaneous peak rate is {r['hot_suction_m3_s']:,.0f} m³/s
at the front gas conditions; it is not the amount of atmosphere collected.

For the 250 m front, sound speed at the cooled 1,000 K state is approximately
{r['hot_sound_speed_m_s']:.0f} m/s; one-way acoustic travel is
{r['acoustic_transit_s']:.2f} s and gas turnover is {r['front_turnover_s']:.2f} s.
If pumping stops at peak inflow, pressure initially rises about
{r['pressure_rise_pump_off_Pa_s']:.1f} Pa/s. Thus control and reserve matter on
subsecond-to-second timescales. This sound speed is calculated from gas
properties; it is not a blade-speed assumption.

There is also a finite-flow test. A cooled stagnant plenum feeding compressor
ports has a sonic mass-flow ceiling. Using the local gas gamma, a discharge
coefficient of 0.8, and the current required suction capacity, the total clear
port area must be at least **{r['required_compressor_open_area_m2']:.1f} m²**.
The illustrative 30%-open bulkhead supplies **{r['available_compressor_open_area_m2']:.1f}
m²**, with a suction-equivalent sonic limit of
{r['suction_choking_bound_m3_s']:,.0f} m³/s. This necessary geometric check passes.
Mean port-flow dynamic pressure is about
{100*r['estimated_access_dynamic_pressure_fraction']:.1f}% of plenum pressure
under a low-Mach estimate; actual contraction/exchanger loss still needs a map.
[NASA mass-flow relation](https://www.grc.nasa.gov/www/k-12/airplane/mflchk.html).

That check does **not** prove the hypersonic shock stays between mouth and
compressor. Backpressure can move a shock system upstream and cause inlet
unstart. Stable shock position depends on inlet area profile, boundary layers,
heat extraction, losses and pump response. Existing NASA inlet/isolator work
shows unstart predictions are sensitive to the boundary treatment and modeling;
its Mach-4 geometry is not a validation of this scoop.
[NASA inlet/isolator study](https://ntrs.nasa.gov/citations/20240016426).

The next resolving calculation is a coupled inlet/exchanger calculation with
finite pump suction curves and valve response, measuring shock location and
captured mass. Until then, the depth sweep gives duties conditional on full
capture, rather than silently assuming an unconstrained controller proves it.

## Pressure-control reserve sensitivity

Lowering the chosen front-pressure target increases required suction capacity.
This is a mass/control trade, not a new CFD limit. The same 30%-open bulkhead is
used in the access check; a failed check calls for more port area or a changed
operating point, not an automatic rejection of the whole concept.

| Target front pressure / ram | Suction capacity | Required clear port area | Total dry mass | 30%-open access check |
|---:|---:|---:|---:|---|''')
    for x in data['pressure_control_sensitivity']:
        lines.append(f"| {x['pressure_target_over_ram']:.1f} | {x['hot_suction_m3_s']:,.0f} m³/s | {x['required_compressor_open_area_m2']:.1f} m² | {x['total_dry_kg']/1000:,.0f} t | {'passes' if x['access_bound_pass'] else 'needs more clear area'} |")
    lines.append('''
Reproduce in the local venv:

```sh
.venv/bin/python -m atmo_scoops.physical_cycle
MPLCONFIGDIR=/tmp/atmo-scoops-mpl .venv/bin/python -m atmo_scoops.studies.physical
```

![Physical-depth trade study](../../figures/physical_depth_trade.png)
''')
    Path('analysis/primary/PHYSICAL_CYCLE.md').write_text('\n'.join(lines)+'\n')
    plot(data)


def plot(data):
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for rear in (10,25,50,100):
        rows=[x for x in data['depth_sweep'] if x['rear_depth_m']==rear]
        axes[0,0].plot([x['front_depth_m'] for x in rows],[x['total_dry_kg']/1000 for x in rows],'-o',label=f'{rear} m rear')
        axes[1,0].plot([x['front_depth_m'] for x in rows],[x['net_liquid_equivalent_kg'] for x in rows],'-o',label=f'{rear} m rear')
    axes[0,0].set(ylabel='Conditional total dry mass (tonnes)',xlabel='Physical front depth (m)',title='Depth adds structure; suction duty changes little')
    axes[0,0].legend(fontsize=9)
    axes[1,0].set(ylabel='Net liquid-equivalent (kg/cycle)',xlabel='Physical front depth (m)',title='Collection fixed; small residual-recovery differences')
    rows=[x for x in data['depth_sweep'] if x['front_depth_m']==250]
    axes[0,1].plot([x['rear_depth_m'] for x in rows],[x['rear_pressure_Pa']/1000 for x in rows],'-o',color='#b45309')
    axes[0,1].set(xlabel='Physical rear depth including ends (m)',ylabel='Rear pressure (kPa)',title='Longer rear tank lowers discharge pressure')
    ss=data['compressor_mass_sensitivity']
    axes[1,1].bar([str(int(x['compressor_kg_per_m3_s'])) for x in ss],[x['total_dry_kg']/1000 for x in ss],color='#457b9d')
    axes[1,1].set(xlabel='Compressor mass target: kg per (m³/s)',ylabel='Conditional total dry mass (tonnes)',title='Pump mass target is a much larger uncertainty')
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.suptitle('18.3 m diameter compartments • 100 × 2,000 km orbit • capture-only reboost',fontsize=13)
    fig.text(.5,.014,'Assumed full intake and hardware targets; these curves do not validate shock stability, pump performance or delivered payoff.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.95))
    for ext in ('png','svg'):fig.savefig(f'figures/physical_depth_trade.{ext}',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
