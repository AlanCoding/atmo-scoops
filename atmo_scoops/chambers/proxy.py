"""Explicit, anchored mass/product proxy for isolated chamber allocation searches.

Not a new system.simulate payoff. No engine or compressor performance improvement
is granted; fixed hardware comes from the saved perigee-Isp reference.
"""
import math
import numpy as np
from .thermo import Air
from ..orbit import Orbit
from .materials import material


def evaluate(result,anchor,reference_shaft_MJ,processing_kg_MJ=10.):
    o=anchor['outputs'];p=anchor['inputs']['performance'];hw=anchor['inputs']['hardware']
    cfg=result['experiment_config'];orbit=Orbit(**cfg['orbit']);g=result['geometry'];ch=cfg['chambers'];air=Air()
    t=np.array(result['time_s']);mass=np.array(result['gas_mass_kg']);P=np.array(result['pressure_Pa']);T=np.array(result['gas_temperature_K'],dtype=float);Tm=np.array(result['metal_temperature_K'])
    L=result['ledger'];initial=mass[0].sum()
    vent_reserve=2*cfg['schedule']['withdrawal_floor_Pa']*g[-1]['gas_m3']/(air.R*298.)
    batch=L['withdrawn_kg'][-1]+mass[-1,-1]-initial-vent_reserve
    # Same intercepted-column impulse allowance for every candidate, including
    # uncollected air. N2/O2 propellant is charged against useful product.
    J=o['geometric_intercept_impulse_Ns'];prop=J/(anchor['inputs']['design']['isp_s']*9.80665)
    product=batch-prop
    removed={'hot_metal','shell_TPS_allowance','rear_tank_and_supports','hot_sheet_deployment','design_margin'}
    fixed=sum(v for k,v in o['masses_kg'].items() if k not in removed)
    feed_ratio=max(1.,cfg['schedule']['withdrawal_kg_s']/(o['retained_kg']/o['cycle']['deployed_s']))
    fixed+=sum(o['masses_kg'][k] for k in ('refrigerator','product_heat_exchangers','separator','compressor_coast'))*(feed_ratio-1)
    metal=sum(x['mass_kg'] for x in g)
    deployed_area=sum(x['solid_m3']/(math.pi*c['rod_radius_m']*(c['rod_radius_m']/c['rod_pitch_m'])) for c,x in zip(ch,g))
    deploy=deployed_area*hw['sheet_deployment_kg_m2']
    banks=o['compressor_analysis']['dive']['banks']
    electric_peaks=np.zeros(len(cfg['pumps']))
    for j,d in enumerate(result['diagnostics']):
        for i,f in enumerate(d['pump_kg_s']):
            if f>0:
                work=air.compression(T[j,i],P[j,i],P[j,i+1],cfg['pumps'][i]['efficiency'])
                electric_peaks[i]=max(electric_peaks[i],f*work/p['motor_efficiency'])
    motor_W_kg=anchor['inputs']['compressor']['motor_W_kg']
    motor_uprating=sum(max(0.,power/motor_W_kg-bank['motor_kg']) for power,bank in zip(electric_peaks,banks))
    fixed+=motor_uprating
    package=anchor['inputs']['packaging']
    bay=o['packaging']['equipment_equivalent_depth_m']+motor_uprating/package['machinery_bulk_kg_m3']/package['equipment_bay_fill_fraction']/(math.pi*ch[0]['diameter_m']**2/4)
    length=sum(c['depth_m'] for c in ch)+bay
    diameter=o['packaging']['outside_diameter_m'];shell=math.pi*diameter*length*hw['shell_TPS_kg_m2']
    # Thin membrane lower bound plus minimum gauge. Includes each sealed volume;
    # shared bulkheads and actual head geometry are not resolved.
    vessel=0.
    for i,(c,x) in enumerate(zip(ch,g)):
        if i==0:continue
        area=math.pi*c['diameter_m']*c['depth_m']+math.pi*c['diameter_m']**2/2
        minimum=area*hw['rear_min_gauge_m']*hw['rear_material_density']
        membrane=1.5*float(P[:,i].max())*(x['gas_m3']+x['solid_m3'])*hw['rear_material_density']/hw['rear_allowable_Pa']*hw['rear_pressure_factor']
        vessel+=max(minimum,membrane)*(1+hw['rear_support_fraction'])+area*hw['rear_insulation_kg_m2']
    # Retain reference electrical plant and add changes in pass-compression energy.
    # Battery plus average-sunlight array mass, not a redesigned peak-power bus.
    energy_coeff=1/(3600*p['battery_Wh_kg']*p['battery_usable']*p['battery_discharge_efficiency'])+1/(o['cycle']['sunlit_s']*p['solar_W_kg']*p['battery_charge_efficiency']*p['battery_discharge_efficiency'])
    delta_energy=(L['shaft_work_MJ'][-1]-reference_shaft_MJ)*1e6/p['motor_efficiency']
    compression_adjustment=delta_energy*energy_coeff
    # Warm feed excess is a declared composite tank/heat-exchanger/rejection
    # surcharge, not refrigeration at the high inlet temperature.
    h340=air.at(340.)[0]
    withdrawn_enthalpy=L['withdrawn_enthalpy_MJ'][-1]*1e6
    remaining_h=mass[-1,-1]*air.at(T[-1,-1])[0]
    excess_MJ=max(0.,(withdrawn_enthalpy+remaining_h-(L['withdrawn_kg'][-1]+mass[-1,-1])*h340)/1e6)
    processing=processing_kg_MJ*excess_MJ
    subtotal=fixed+metal+deploy+shell+vessel+compression_adjustment+processing
    dry=subtotal*(1+hw['design_margin'])
    # Finish draining to twice the 298 K cutoff inventory, then vent that
    # explicitly lost remainder before rack deployment. Integrate the commanded
    # pressure-taper law at 298 K, a conservative cold receiver approximation.
    flow=cfg['schedule']['withdrawal_kg_s'];floor=vent_reserve/2
    remaining=max(mass[-1,-1],vent_reserve)
    remaining_time=(remaining-vent_reserve+floor*math.log(max((remaining-floor)/max(floor,1e-20),1.)))/max(flow,1e-10)
    materials=[material(c.get('material','iron')) for c in ch]
    resets=[mat.cooldown(float(Tm[-1,i]),c['initial_metal_K'],x,
        c.get('rack_emissivity') if c.get('rack_emissivity') is not None else (cfg['schedule']['emissivity'] if mat.name=='iron' else mat.emissivity))
        if x['mass_kg'] else 0. for i,(c,x,mat) in enumerate(zip(ch,g,materials))]
    motion=max(o['cycle']['deploy_s'],math.sqrt(max(deployed_area,0.))/10.)
    reset_budget=orbit.period-600-cfg['schedule']['end_s']
    reset= max(resets)
    margins=dict(length_m=10*diameter-length,pressure_Pa=110000-float(P.max()),metal_K=min(mat.limit_K-float(Tm[:,i].max()) for i,mat in enumerate(materials)),
        lumped_Biot=.1-max((max(d.get('rack_Biot',[0.])) for d in result['diagnostics']),default=0.),
        gas_K=2000-float(np.nanmax(np.where(mass>.01,T,np.nan))),net_product_kg=product,
        reset_time_s=reset_budget-remaining_time-reset-2*motion,
        mass_audit_kg=1e-5-result['checks']['max_mass_residual_kg'],energy_audit_MJ=1e-4-result['checks']['max_energy_residual_MJ'])
    feasible=all(x>=-1e-8 for x in margins.values()) and not result['checks']['caloric_table_boundary_reached'] and not result['checks']['metal_outside_reference_range']
    return dict(proxy_days=dry/product*orbit.period/86400 if product>0 else 1e9,proxy_dry_kg=dry,batch_kg=batch,receiver_vent_reserve_kg=vent_reserve,net_product_kg=product,propellant_kg=prop,
        motor_uprating_kg=motor_uprating,compressor_electric_peaks_W=electric_peaks.tolist(),metal_kg=metal,vessel_kg=vessel,structural_shell_kg=shell,deployment_kg=deploy,fixed_hardware_kg=fixed,compression_adjustment_kg=compression_adjustment,
        processing_surcharge_kg=processing,processing_kg_MJ=processing_kg_MJ,excess_feed_heat_MJ=excess_MJ,
        rack_cooldown_s=resets,length_m=length,estimated_reset_s=remaining_time+reset+2*motion,margins=margins,feasible=feasible)
