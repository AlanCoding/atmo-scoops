"""Physical chamber lengths, conditional installed mass, and finite pump access.

Every mass coefficient is serialized. This is a requirements/sensitivity model,
not a qualified compressor, inlet, structure, or delivered-payoff solution.
"""
from dataclasses import dataclass, asdict, replace
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .two_volume import Reference, calculate


@dataclass(frozen=True)
class Hardware:
    shell_TPS_kg_m2: float = 4.
    # Purpose-built complete-bank targets, not catalogue pump performance.
    compressor_kg_per_m3_s: float = 30.
    compressor_electric_W_kg: float = 1000.
    thruster_kg_kW: float = 2.
    distribution_kg_kW: float = 1.
    rear_min_gauge_m: float = .001
    rear_allowable_Pa: float = 150e6
    rear_material_density: float = 2700.
    rear_pressure_factor: float = 1.5
    rear_support_fraction: float = .5
    rear_insulation_kg_m2: float = 1.
    sheet_deployment_kg_m2: float = 1.
    # Array and warm radiator specific masses already include their mechanisms.
    mouth_closure_kg_m2: float = 10.  # Door, seals, actuation and supports; unqualified target.
    compressor_bulkhead_kg_m2: float = 10.
    warm_aftercooler_W_kg: float = 20000.
    separator_kg_kW: float = 5.
    liquid_system_fixed_kg: float = 500.
    avionics_attitude_fixed_kg: float = 1000.
    warm_loop_fluid_kg_m2: float = .25
    design_margin: float = .25
    compressor_open_fraction: float = .30
    access_discharge_coefficient: float = .8


def rear_geometry(depth_m, diameter_m=18.3):
    """Full physical length incl. two 2:1 ellipsoidal heads (each D/4 deep)."""
    if depth_m < diameter_m/2:
        raise ValueError('Rear depth must accommodate both ellipsoidal heads')
    r=diameter_m/2;head_depth=diameter_m/4
    barrel=depth_m-2*head_depth
    area=math.pi*r*r
    volume=area*barrel+4*math.pi*r*r*head_depth/3
    # Two oblate hemispheroids make one oblate spheroid.
    e=math.sqrt(1-(head_depth/r)**2)
    heads=2*math.pi*r*r*(1+(1-e*e)*math.atanh(e)/e)
    return dict(volume_m3=volume,surface_m2=math.pi*diameter_m*barrel+heads,
                barrel_m=barrel,head_depth_m=head_depth)


def minimum_suction(r, front_depth_m, diameter_m=18.3, limit=.7):
    """Smallest constant open-phase S meeting a PRESCRIBED plenum-pressure target.

    This does not calculate a shock position, start margin, or real leakage.
    """
    t=np.array(r['collection_time_s']);q=np.array(r['intake_mass_flow_kg_s'])
    ram=np.array(r['ram_pressure_Pa']);V=math.pi*diameter_m**2/4*front_depth_m
    RT=r['gas_R_J_kg_K']*r['inputs']['gas_K']
    def residual(S):
        sol=solve_ivp(lambda ti,y:[np.interp(ti,t,q)-S*y[0]/V],
            (t[0],t[-1]),[0.],t_eval=t,rtol=1e-8,atol=1e-10,max_step=(t[-1]-t[0])/150)
        return float(np.max(sol.y[0]*RT/V/ram)-limit)
    if residual(0)<=0:return 0.
    return brentq(residual,0,2*r['open_suction_m3_s'],xtol=1e-5)


def reference(front=250.,rear=25.,capacity_factor=1.):
    """Comparison point only; 250 m is not a selected or optimized length."""
    geom=rear_geometry(rear)
    # Depths are gas-space dimensions; 20 m is an explicit machinery/layout allowance.
    return replace(Reference(),front_bore_m=18.3,front_length_m=front,
                   receiver_m3=geom['volume_m3'],outside_diameter_m=20.,
                   total_length_m=front+rear+20.,suction_capacity_factor=capacity_factor)


def evaluate(r, front, rear, hw=Hardware(), rear_diameter_m=18.3):
    c=r['inputs'];b=next(x for x in r['budgets'] if x['total_impulse_over_capture']==c['total_impulse_over_capture'])
    geom=rear_geometry(rear,rear_diameter_m);A=math.pi*c['front_bore_m']**2/4
    flow=np.array(r['history']['pump_mass_flow_kg_s'])
    hotpower=np.array(r['history']['hot_pump_electric_W'])
    totalpower=np.array(r['history']['pump_electric_W'])
    # Same front machinery serves open collection and sealed pumpdown.
    hotS=max(r['open_suction_m3_s'],r['closed_suction_m3_s'])
    warmS=float(max(flow))*r['gas_R_J_kg_K']*c['receiver_K']/c['intermediate_Pa']
    feed=r['coast_feed_compressor']
    pump_hot=max(hw.compressor_kg_per_m3_s*hotS,float(max(hotpower))/hw.compressor_electric_W_kg)
    pump_warm=max(hw.compressor_kg_per_m3_s*warmS,float(max(totalpower-hotpower))/hw.compressor_electric_W_kg)
    pump_coast=max(hw.compressor_kg_per_m3_s*feed['pumping_speed_m3_s'],feed['peak_power_W']/hw.compressor_electric_W_kg)
    pieces=dict(b['assigned_masses_kg'])
    pieces['shell_TPS_allowance']=math.pi*c['outside_diameter_m']*c['total_length_m']*hw.shell_TPS_kg_m2
    pieces.update(compressor_hot=pump_hot,compressor_warm=pump_warm,compressor_coast=pump_coast)
    # Thin cylindrical hoop-stress rule applied to all wetted skin; ends are
    # ellipsoidal. This is a screening allowance, not a shell stress solution.
    gauge=max(hw.rear_min_gauge_m,hw.rear_pressure_factor*r['final_receiver_Pa']*rear_diameter_m/(2*hw.rear_allowable_Pa))
    pieces['rear_tank_and_supports']=geom['surface_m2']*(gauge*hw.rear_material_density*(1+hw.rear_support_fraction)+hw.rear_insulation_kg_m2)
    pieces['propulsion_hardware']=hw.thruster_kg_kW*b['impulse_equivalent_burst_W']/1000
    peakbus=b['impulse_equivalent_burst_W']+max(r['compression_peak_open_W'],r['compression_peak_closed_W'])+c['auxiliary_W']
    pieces['power_distribution']=hw.distribution_kg_kW*max(peakbus,b['solar_bus_W'])/1000
    pieces['hot_sheet_deployment']=hw.sheet_deployment_kg_m2*r['metal_physical_area_m2']
    pieces['compressor_bulkhead']=A*hw.compressor_bulkhead_kg_m2
    pieces['mouth_closure']=(r['mouth_area_m2']*hw.mouth_closure_kg_m2 if c['mouth_closure'] else 0.)
    pieces['warm_aftercooler']=r['warm_store_capture_J']/r['collection_s']/hw.warm_aftercooler_W_kg
    pieces['product_heat_exchangers']=sum(r['liquefaction']['mass_breakdown_kg'][k] for k in ('product_condenser','process_precooler'))
    pieces['separator']=r['separation_energy_J']/r['deployed_coast_s']/1000*hw.separator_kg_kW
    pieces['liquid_storage_valves_plumbing']=hw.liquid_system_fixed_kg
    pieces['avionics_attitude']=hw.avionics_attitude_fixed_kg
    before=sum(pieces.values());pieces['design_margin']=before*hw.design_margin
    total=sum(pieces.values())
    gamma=r['gamma_hot'];RT=r['gas_R_J_kg_K']*c['gas_K']
    sound=math.sqrt(gamma*RT)
    choked_speed=sound*(2/(gamma+1))**((gamma+1)/(2*(gamma-1)))
    required_access=hotS/(hw.access_discharge_coefficient*choked_speed)
    # Local hydraulic access check uses the cooled, approximately stagnant plenum.
    # It is not applied to hypersonic freestream or to the rotating machinery.
    open_area=A*hw.compressor_open_fraction
    hydraulic_capacity=open_area*hw.access_discharge_coefficient*choked_speed
    # Backpressure sensitivity to one second of lost suction at peak flow.
    pressure_rate=r['peak_intake_kg_s']*RT/r['front_volume_m3']
    retained_product=r['first_cycle_liquid_before_propellant_kg']-b['required_propellant_kg']
    orbits_day=86400/r['orbit_period_s']
    return dict(front_depth_m=front,rear_depth_m=rear,diameter_m=c['front_bore_m'],rear_diameter_m=rear_diameter_m,
        overall_length_allowance_m=c['total_length_m'],rear_geometry=geom,
        rear_pressure_Pa=r['final_receiver_Pa'],front_pressure_Pa=r['closure_front_Pa'],
        captured_kg=r['captured_kg'],retained_kg=r['retained_kg'],
        net_liquid_equivalent_kg=retained_product,net_liquid_equivalent_kg_day=retained_product*orbits_day,
        propellant_kg=b['required_propellant_kg'],vent_kg=r['vented_front_kg'],
        mouth_closure=c['mouth_closure'],mouth_leakage_kg=r['mouth_leakage_kg'],
        final_front_vent_kg=r['final_front_vent_kg'],outbound_admitted_kg=r['outbound_admitted_kg'],
        inbound_admitted_kg=r['inbound_admitted_kg'],pump_stop_reason=r['pump_stop_reason'],
        front_pressure_at_pump_stop_Pa=r['final_front_Pa'],
        collected_before_closure_kg=r['transferred_before_closure_kg'],
        recovered_after_closure_kg=r['recovered_after_closure_kg'],
        solar_area_m2=b['solar_area_m2'],warm_radiator_panel_m2=b['warm_radiator_emitting_m2']/2,
        warm_radiator_emitting_m2=b['warm_radiator_emitting_m2'],metal_panel_m2=r['metal_physical_area_m2'],
        metal_emitting_m2=r['metal_two_face_emitting_m2'],solar_MW=b['solar_bus_W']/1e6,
        ideal_metal_cooldown_s=float(r['ideal_metal_radiation_cooling_s']),
        peak_intake_kg_s=r['peak_intake_kg_s'],hot_absorbed_GJ=float(r['hot_store_J']/1e9),
        hot_suction_m3_s=r['open_suction_m3_s'],recovery_suction_m3_s=r['closed_suction_m3_s'],
        warm_suction_m3_s=warmS,coast_feed_suction_m3_s=feed['pumping_speed_m3_s'],
        compressor_peak_MW=r['compression_peak_open_W']/1e6,compressor_kWh=r['compression_electric_J']/3.6e6,
        compressor_mass_kg=pump_hot+pump_warm+pump_coast,masses_kg=pieces,total_dry_kg=total,
        circulating_warm_fluid_kg=hw.warm_loop_fluid_kg_m2*b['warm_radiator_emitting_m2'],
        oxygen_available_kg=b['oxygen_available_kg'],oxygen_mass_margin_kg=b['oxygen_balance_kg'],
        oxygen_propellant_fraction=b['required_propellant_kg']/b['oxygen_available_kg'],
        total_with_loop_fluid_kg=total+hw.warm_loop_fluid_kg_m2*b['warm_radiator_emitting_m2'],
        hot_sound_speed_m_s=sound,acoustic_transit_s=front/sound,
        front_turnover_s=r['front_volume_m3']/r['open_suction_m3_s'],
        pressure_rise_pump_off_Pa_s=pressure_rate,
        required_compressor_open_area_m2=required_access,available_compressor_open_area_m2=open_area,
        suction_choking_bound_m3_s=hydraulic_capacity,access_bound_pass=bool(hotS<=hydraulic_capacity),
        estimated_access_dynamic_pressure_fraction=gamma/2*(hotS/(open_area*sound))**2,
        rear_wall_gauge_mm=gauge*1000,
        cold_duty_kW=r['liquefaction']['actual_cold_duty_W']/1000,
        cryoplant_electric_kW=r['liquefaction']['electricity_W']/1000,
        reboost_peak_MW=b['impulse_equivalent_burst_W']/1e6,
        reboost_MWh=b['propulsion_electric_J']/3.6e9,
        cycle=dict(orbit_s=r['orbit_period_s'],collection_s=r['collection_s'],recovery_s=r['actual_recovery_s'],
            deploy_s=c['deploy_s'],retract_s=c['retract_s'],deploy_complete_s=r['coast_start_s'],
            retract_start_s=r['coast_end_s'],deployed_s=r['deployed_coast_s'],sunlit_s=r['sunlight_deployed_s']))


def main():
    raw=calculate(reference(),n=801)
    base=evaluate(raw,250,25)
    rows=[]
    for front in (25,50,100,250,400):
        for rear in (10,25,50,100):
            r=raw if (front,rear)==(250,25) else calculate(reference(front,rear),n=401)
            rows.append(evaluate(r,front,rear))
    capacities=[]
    for front in (25,50,100,250,400):
        S=minimum_suction(raw,front)
        rr=calculate(reference(front,25,S/raw['open_suction_m3_s']),n=801)
        v=evaluate(rr,front,25)
        v['max_front_over_ram']=rr['max_front_over_ram']
        capacities.append(v)
    masses=[]
    for alpha in (10.,30.,100.,300.):
        v=evaluate(raw,250,25,replace(Hardware(),compressor_kg_per_m3_s=alpha))
        masses.append(dict(compressor_kg_per_m3_s=alpha,compressor_mass_kg=v['compressor_mass_kg'],total_dry_kg=v['total_dry_kg']))
    thrusters=[]
    for kgkW in (1.,2.,4.,8.):
        v=evaluate(raw,250,25,replace(Hardware(),thruster_kg_kW=kgkW))
        thrusters.append(dict(thruster_kg_kW=kgkW,total_dry_kg=v['total_dry_kg']))
    controls=[]
    for target in (.4,.5,.7):
        rr=calculate(replace(reference(),inlet_pressure_fraction=target),n=801)
        v=evaluate(rr,250,25)
        v['pressure_target_over_ram']=target
        controls.append(v)
    out=dict(status='Conditional physical-depth and installed-mass study, not a validated spacecraft or delivered payoff',
        hardware_inputs=asdict(Hardware()),cycle_inputs=raw['inputs'],reference=base,
        depth_sweep=rows,minimum_constant_suction_sweep=capacities,
        compressor_mass_sensitivity=masses,thruster_mass_sensitivity=thrusters,
        pressure_control_sensitivity=controls)
    Path('results/physical_cycle.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(reference=base,compressor_mass_sensitivity=masses,
        minimum_suction=[(x['front_depth_m'],x['hot_suction_m3_s']) for x in capacities]),indent=2))


if __name__=='__main__':main()
