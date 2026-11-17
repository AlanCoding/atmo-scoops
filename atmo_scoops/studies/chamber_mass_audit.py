"""Trace the isolated proxy back to its hardware anchor; no new payoff model."""
from pathlib import Path
import json,math
import numpy as np
from ..chambers.thermo import Air
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'results/chamber_materials';OUT=ROOT/'investigations/chamber_transient'

def calculate():
 a=json.loads((ROOT/'results/reboost/solid_isp_optimum_1601.json').read_text());o=a['outputs'];inp=a['inputs'];perf=inp['performance'];hw=inp['hardware']
 r=json.loads((DATA/'sic/best.json').read_text());p=json.loads((DATA/'sic/proxy.json').read_text());cfg=r['experiment_config']
 removed={'hot_metal','shell_TPS_allowance','rear_tank_and_supports','hot_sheet_deployment','design_margin'}
 parts={k:v for k,v in o['masses_kg'].items() if k not in removed}
 factor=max(1.,cfg['schedule']['withdrawal_kg_s']/(o['retained_kg']/o['cycle']['deployed_s']))
 additions={k:parts[k]*(factor-1) for k in ('refrigerator','product_heat_exchangers','separator','compressor_coast')}
 for k,v in additions.items():parts[k]+=v
 parts.update(compressor_motor_uprating=p['motor_uprating_kg'],rack_material=p['metal_kg'],rack_deployment=p['deployment_kg'],shell=p['structural_shell_kg'],pressure_vessels=p['vessel_kg'],compression_energy_adjustment=p['compression_adjustment_kg'],warm_feed_surcharge=p['processing_surcharge_kg'])
 parts['design_margin']=sum(parts.values())*hw['design_margin']
 assert math.isclose(sum(parts.values()),p['proxy_dry_kg'],abs_tol=1e-6)
 groups={
 'Thruster hardware':parts['propulsion_hardware'],
 'Electrical distribution':parts['power_distribution'],
 'Solar arrays':parts['solar'],
 'Battery':parts['battery'],
 'Dive compressors incl. motor uprating':parts['compressor_hot']+parts['compressor_warm']+parts['compressor_motor_uprating'],
 'Warm heat buffer':parts['warm_buffer'],
 'Rack deployment hardware':parts['rack_deployment'],
 'Rack material':parts['rack_material'],
 'Warm radiators':parts['warm_radiator'],
 'Refrigeration machinery':parts['refrigerator'],
 'Pressure vessels':parts['pressure_vessels'],
 'Hull/TPS allowance':parts['shell'],
 'Other equipment and proxy adjustments':sum(parts[k] for k in ['compressor_coast','compressor_bulkhead','warm_aftercooler','product_heat_exchangers','separator','liquid_storage_valves_plumbing','avionics_attitude','compression_energy_adjustment','warm_feed_surcharge']),
 'Design margin':parts['design_margin']}
 assert math.isclose(sum(groups.values()),p['proxy_dry_kg'],abs_tol=1e-6)
 J=o['geometric_intercept_impulse_Ns'];u=inp['design']['isp_s']*9.80665;E=J*u/(2*perf['thruster_efficiency']);W=E/inp['design']['thrust_burst_s']
 assert math.isclose(W/1e6,o['reboost_peak_MW'],rel_tol=1e-8)
 t=np.array(r['time_s']);T=np.array(r['gas_temperature_K'],dtype=float);P=np.array(r['pressure_Pa']);flow=np.array([d['pump_kg_s'] for d in r['diagnostics']]);air=Air();banks=[]
 for i,b in enumerate(o['compressor_analysis']['dive']['banks']):
  work=np.array([air.compression(T[j,i],P[j,i],P[j,i+1],cfg['pumps'][i]['efficiency']) if flow[j,i]>0 else 0 for j in range(len(t))]);power=flow[:,i]*work/perf['motor_efficiency'];active=flow[:,i]>flow[:,i].max()*1e-6
  banks.append(dict(stage=i+1,anchor_structure_t=b['structural_kg']/1000,anchor_motor_t=b['motor_kg']/1000,actual_peak_electric_MW=float(power.max()/1e6),actual_flow_work_MWh=float(np.trapezoid(power,t)/3.6e9),flow_weighted_inlet_K=float(np.trapezoid(flow[:,i]*np.nan_to_num(T[:,i]),t)/np.trapezoid(flow[:,i],t)),active_max_inlet_K=float(T[active,i].max()),actual_head_kJ_kg=float(work[active].max()/1000),fixed_head_cap_kJ_kg=cfg['pumps'][i]['max_shaft_J_kg']/1000))
 gain_sens={}
 for key in ['propulsion_hardware','power_distribution','solar','battery']:
  gain_sens[key+'_minus_10_percent_days']=p['proxy_days']*(1-.1*parts[key]*(1+hw['design_margin'])/p['proxy_dry_kg'])
 spin=o['compressor_analysis']['dive']['spinup_electric_J'];idle=o['compressor_analysis']['dive']['idle_electric_W']*(o['cycle']['collection_s']+o['cycle']['recovery_s'])
 return dict(parts_kg=parts,groups_kg=groups,total_kg=sum(parts.values()),proxy_days=p['proxy_days'],plant_throughput_factor=factor,plant_additions_kg=additions,
  propulsion=dict(impulse_Ns=J,exhaust_m_s=u,propellant_kg=J/u,electric_GJ=E/1e9,power_GW=W/1e9,thrust_kN=J/inp['design']['thrust_burst_s']/1000,orbit_minutes=o['cycle']['orbit_s']/60,net_kg=p['net_product_kg'],net_t_day=p['net_product_kg']*86400/o['cycle']['orbit_s']/1000,propulsion_only_battery_t=E/perf['battery_discharge_efficiency']/(3600*perf['battery_Wh_kg']*perf['battery_usable'])/1000,propulsion_only_solar_t=E/(perf['battery_discharge_efficiency']*perf['battery_charge_efficiency']*o['cycle']['sunlit_s']*perf['solar_W_kg'])/1000),
  banks=banks,sensitivity=gain_sens,energy=dict(anchor_total_compressor_GJ=o['compressor_kWh']*.0036,anchor_spin_GJ=spin/1e9,anchor_idle_estimate_GJ=idle/1e9,transient_flow_compressor_GJ=r['ledger']['shaft_work_MJ'][-1]/1000/perf['motor_efficiency']),
  anchor_cryoplant_MW=o['cryoplant_electric_kW']/1000,scaled_capacity_cryoplant_MW=o['cryoplant_electric_kW']/1000*factor)

def main():
 d=calculate();(DATA/'mass_audit.json').write_text(json.dumps(d,indent=2)+'\n')
 text='''# Mass audit of the SiC/aluminum transient proxy

This traces the reported 373-day isolated result to its component ledger. It
**does not recouple or rerun the full spacecraft model**. The supported design
direction is a high-temperature front rack with aluminum downstream; the SiC
versus FeCrAl engineering choice remains open.

## Where the mass is

| Component | Mass, tonnes | Share of dry mass |
|---|---:|---:|
'''
 for k,v in d['groups_kg'].items():text+=f"| {k} | {v/1000:,.1f} | {100*v/d['total_kg']:.2f}% |\n"
 text+=f"| **Total** | **{d['total_kg']/1000:,.1f}** | **100%** |\n\n"
 text+='''The margin is 25% of the equipment subtotal (therefore 20% of final dry mass),
added once. There is no arithmetic double counting of that margin. Solar arrays,
battery, electrical distribution and thrusters are separate ledger items; their
real hardware scope must nevertheless be defined to avoid counting a thruster
power-processing unit both in installed thruster mass and distribution.

## The dominant physical requirement and the dominant assumptions

'''
 q=d['propulsion']
 text+=f'''The assumed intercepted-column impulse is **{q['impulse_Ns']/1e6:.2f} MN s**.
At **{q['exhaust_m_s']/1000:.2f} km/s** effective exhaust velocity, 60% efficiency
and a 300 s burst:

- Propellant: J/u = **{q['propellant_kg']/1000:.3f} t/pass**.
- Electric energy: Ju/(2 eta) = **{q['electric_GJ']:.1f} GJ/pass**.
- Thruster input: E/300 s = **{q['power_GW']:.3f} GW**.
- Thrust: J/300 s = **{q['thrust_kN']:.1f} kN**.
- Net useful inventory: **{q['net_kg']/1000:.3f} t** per **{q['orbit_minutes']:.2f} min** orbit,
  or **{q['net_t_day']:.2f} t/day**. Dividing dry mass by that rate reproduces payoff.

These equations are dimensionally consistent: Ns × m/s = joules, then divide by
seconds for watts. They do not multiply drag by spacecraft dry mass. The assumed
momentum bill includes the intercepted column, including rejected air, but lacks
a resolved external hull/fin drag calculation.

The 5,386 t thruster entry is the explicit **2 kg/kW** installed capability target
multiplied by 2.693 million kW. Distribution is **1 kg/kW** times the approximately
2.748 GW combined bus requirement. Neither coefficient is a demonstrated
multi-gigawatt O2/N2 installation. Efficiency, lifetime, power-processor scope,
plume accommodation and thermal interfaces still need component research.

Even propulsion alone implies about **{q['propulsion_only_battery_t']:.0f} t** of batteries
under 150 Wh/kg, 80% usable capacity and 95% discharge efficiency, and about
**{q['propulsion_only_solar_t']:.0f} t** of arrays at 150 W/kg with the inherited sunlight
window and charge/discharge losses. The large power-system mass is therefore
not mainly an uncooled compressor penalty.

'''
 only=(d['parts_kg']['propulsion_hardware']+q['power_GW']*1e6+1000*(q['propulsion_only_battery_t']+q['propulsion_only_solar_t']))*1.25
 text+=f'''As a diagnostic, propulsion-only thrusters, bus, batteries and arrays plus the
same margin already imply about **{only/1000:,.0f} t**, or **{only/1000/q['net_t_day']:.0f} days**
at the selected net production rate, even if all other equipment were free.
This is conditional on the current 300 s burst, Isp/efficiency, sunlight and
specific-mass assumptions, not a fundamental bound on atmospheric scoops.

'''
 text+='''## What is frozen, and what should respond

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
'''
 text+=f'''   nominal 2 kg/s withdrawal gives a **{d['plant_throughput_factor']:.3f}×** mass multiplier
   for selected processing components. The anchor cryoplant is {d['anchor_cryoplant_MW']:.2f} MW;
   straightforward throughput scaling would imply {d['scaled_capacity_cryoplant_MW']:.2f} MW installed
   process capacity, but the proxy does not propagate that duty into arrays,
   eclipse batteries, rejection hardware or package volume. A larger machine
   need not consume proportionally more total energy per batch; the actual
   operating schedule must be calculated, rather than scaling energy blindly.
'''
 text+='''2. **The thermal architecture is not fully reconciled.** Legacy warm-buffer,
   radiator and aftercooler masses remain, while the transient racks store heat
   that is later radiated directly. An additional 10 kg/MJ hot-feed surcharge is
   also charged. That is a conservative proxy charge, not a proof of disjoint
   physical components. It can overcharge overlapping duties; other omitted
   duties can undercharge mass, so the total is not a rigorous upper bound.
3. **Compressor electrical accounting has a baseline mismatch.** The anchor
'''
 text+=f'''   includes {d['energy']['anchor_total_compressor_GJ']:.2f} GJ for compression, including
   {d['energy']['anchor_spin_GJ']:.2f} GJ spin-up and idle consumption. The selected transient
   integrates {d['energy']['transient_flow_compressor_GJ']:.2f} GJ of pumping electricity, with
   neither explicit spin nor idle. Only its difference from another transient
   is added to the anchored electrical system. One must not call the entire
   difference an available saving: spin and idle have to be retained or redesigned.
'''
 text+='''4. **Equipment volume is stale.** Increased plant capacity and changed rack
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
'''
 for b in d['banks']:text+='| '+ ' | '.join([str(b['stage'])]+[f"{b[k]:.2f}" for k in ['anchor_structure_t','anchor_motor_t','actual_peak_electric_MW','actual_flow_work_MWh','flow_weighted_inlet_K','actual_head_kJ_kg','fixed_head_cap_kJ_kg']])+' |\n'
 text+='''
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
'''
 for k,v in d['sensitivity'].items():text+=f'| {k.replace("_minus_10_percent_days","")} | {v:.1f} |\n'
 text+='''
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
'''
 (OUT/'MASS_AUDIT.md').write_text(text)
 print(json.dumps(d,indent=2))
if __name__=='__main__':main()
