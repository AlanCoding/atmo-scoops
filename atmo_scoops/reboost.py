"""First-order orbit-restoring coast burns and duty-aware subsystem rebudget.

Separate investigation model: fixed capture/thermal duty from a primary run,
with new propellant, thrust scheduling, process capacity and deployed envelopes.
"""
from dataclasses import replace
import math
import numpy as np
from scipy.optimize import brentq
from .orbit import Orbit,MU,R_EARTH


def state_at(o,t):
    M=np.asarray(t)*2*np.pi/o.period;E=M.copy()
    for _ in range(9):E-=(E-o.e*np.sin(E)-M)/(1-o.e*np.cos(E))
    r=o.a*(1-o.e*np.cos(E));f=2*np.arctan2(np.sqrt(1+o.e)*np.sin(E/2),np.sqrt(1-o.e)*np.cos(E/2))
    return r,MU/o.h*o.e*np.sin(f),o.h/r


def eclipse_start(o):
    f=brentq(lambda f:o.h**2/MU/(1+o.e*math.cos(f))*math.sin(f)-R_EARTH,math.pi/2,math.pi)
    E=2*math.atan2(math.sqrt(1-o.e)*math.sin(f/2),math.sqrt(1+o.e)*math.cos(f/2))
    return (E-o.e*math.sin(E))*o.period/(2*math.pi)


def arc_restore(o,start,duration,samples=301,energy_only=False):
    """Two symmetric arcs; constant thrust, optimal in-plane steering.

    Maximize perigee-equivalent impulse efficiency subject to matching both
    orbital energy and angular momentum. Odd radial components cancel the net
    apsidal rotation across the two arcs to first order.
    """
    t=start+(np.arange(samples)+.5)*duration/samples
    r,vr,vt=state_at(o,t);vp=o.h/o.rp
    ar=vr/vp;at=vt/vp;b=r/o.rp
    lam=None
    if energy_only:
        speed=np.hypot(vr,vt);ur=vr/speed;ut=vt/speed
    else:
        def direction(lam):
            x=lam*ar;y=b+lam*(at-b);norm=np.hypot(x,y)
            return x/norm,y/norm
        def residual(lam):
            ur,ut=direction(lam);return float(np.mean(ar*ur+(at-b)*ut))
        high=1.
        while residual(high)<0:high*=2
        lam=brentq(residual,0.,high,xtol=1e-12);ur,ut=direction(lam)
    energy=float(np.mean(ar*ur+at*ut));angular=float(np.mean(b*ut))
    efficiency=energy if energy_only else angular
    return dict(impulse_multiplier=1/efficiency,energy_efficiency=energy,
        angular_momentum_efficiency=angular,closure_residual=energy-angular,
        altitude_start_km=float((r[0]-R_EARTH)/1000),altitude_end_km=float((r[-1]-R_EARTH)/1000),
        steering_min_deg=float(np.degrees(np.arctan2(ur,ut)).min()),steering_max_deg=float(np.degrees(np.arctan2(ur,ut)).max()),
        energy_only=energy_only,steering_lagrange_multiplier=lam)


def rebudget(source,raw,isp_s,window_s,*,energy_only=False,efficiency=None,buffer_ammonia_rejection=False,iterations=60):
    """Redirect solar to two burns, pausing processing in those intervals.

    Existing surface, capture, compressor and material coefficients are retained.
    Processing modules scale with required throughput, not with unchanged duty.
    This is not a finite-thrust trajectory or engine performance-map solution.
    """
    cfg=source['inputs'];o0=source['outputs'];p=cfg['performance'];h=cfg['hardware'];pack=cfg['packaging'];pr=cfg['process']
    orbit=Orbit(cfg['design']['perigee_km'],cfg['design']['apogee_km'])
    gate=max(orbit.time_at_altitude(200),raw['actual_recovery_s']);shadow=eclipse_start(orbit)
    v=isp_s*9.80665;eta=efficiency or p['thruster_efficiency'];J=o0['propellant_kg']*cfg['design']['isp_s']*9.80665
    product=o0['net_liquid_equivalent_kg']+o0['propellant_kg'];nitrogen=raw['mixing']['nitrogen_available_kg'];oxygen=o0['oxygen_available_kg']
    oldcoast=o0['cycle']['deployed_s'];oldsun=o0['cycle']['sunlit_s']
    Ecomp=raw['compression_electric_J'];Einject=raw['mixing'].get('injection_pump_J',0.)
    Ecryo=raw['liquefaction']['electricity_W']*raw['deployed_coast_s']
    Efeed=raw['coast_feed_compressor']['electricity_J'];Esep=raw['separation_energy_J']
    Eprocess=Ecryo+Efeed+Esep
    Qprocess=raw['liquefaction']['radiator_heat_W']*raw['deployed_coast_s']+Efeed+Esep
    Qpass=raw['warm_store_capture_J'];aux=p['auxiliary_W'];auxE=aux*orbit.period
    etaD=p['battery_discharge_efficiency'];etaC=p['battery_charge_efficiency']
    ammonia=o0.get('ammonia');ammoniaW=ammonia['refrigeration_J'] if ammonia else 0.
    ammoniaPump=(ammonia['pass_pump_J']+ammonia['coast_pump_J']) if ammonia else 0.
    motion=o0['cycle']['deploy_s'];details=None
    for iteration in range(iterations):
        start=gate+motion;coast=orbit.period-2*start;sun=2*(shadow-start);night=coast-sun
        available=sun-2*window_s;processing=coast-2*window_s
        if min(available,processing,coast)<=1:raise ValueError('Burn windows leave no sunlit processing interval')
        arc=arc_restore(orbit,start,window_s,energy_only=energy_only)
        prop=J*arc['impulse_multiplier']/v;net=product-prop
        if net<=0 or prop>oxygen+nitrogen:raise ValueError('Atmospheric propellant exceeds available batch')
        Eprop=J*arc['impulse_multiplier']*v/(2*eta);Pthrust=Eprop/(2*window_s)
        Eother=Ecomp+Einject+Eprocess+auxE
        # Process power is constant during non-thrust deployed time; eclipse is
        # supplied by the remaining battery. Ammonia regeneration stays sun-only.
        processP=Eprocess/processing
        stored=Ecomp+Einject+aux*(orbit.period-sun)+processP*night
        solar_other=Eother+stored*(1/(etaD*etaC)-1)
        solar_nonburn=(solar_other-aux*2*window_s+ammoniaW+ammoniaPump/.9)/available
        solar=max(Pthrust+aux,solar_nonburn)
        packE=(stored+(ammonia['pass_pump_J']/.9 if ammonia else 0.))/etaD
        peakother=max(o0['compressor_peak_MW']*1e6+aux,processP+aux)
        if ammonia:peakother+=max(x['liquid_peak_pump_W'] for x in source['outputs']['racks'])
        battery=max(packE/(3600*p['battery_Wh_kg']*p['battery_usable']),peakother/p['battery_W_kg'])
        retained=Eprop*(1-eta)*p['thruster_loss_retained']
        electricloss=stored*(1/(etaD*etaC)-1)
        warmE=Qpass+Qprocess+auxE+retained+electricloss
        flux=pr['emissivity']*pr['view_factor']*5.670374419e-8*cfg['design']['warm_radiator_K']**4-pr['environment_W_m2']
        rad=warmE/coast/flux
        # Conservative transient thermal buffer: keep full pass heat and retained
        # thrust heat, plus all electrical losses. No free buffer deletion.
        buffer=Qpass+retained+electricloss+aux*(orbit.period-coast)
        initial=Qpass+electricloss+aux*(orbit.period-coast)
        at_first=initial+retained/2+aux*window_s-warmE/coast*window_s
        at_last=at_first+Qprocess+aux*processing-warmE/coast*processing
        trace=[0.,initial,at_first,at_last]
        scheduled_buffer=max(trace)-min(trace)
        buffer=max(buffer,scheduled_buffer)
        masses=dict(o0['masses_kg']);masses.pop('design_margin',None)
        masses.update(solar=solar/p['solar_W_kg'],battery=battery,
            propulsion_hardware=Pthrust/1000*h['thruster_kg_kW'],
            power_distribution=max(solar,peakother)/1000*h['distribution_kg_kW'],
            warm_radiator=rad*pr['radiator_kg_m2'],warm_buffer=buffer/p['warm_buffer_J_kg'])
        rate=oldcoast/processing
        for k in ('refrigerator','product_heat_exchangers','separator','compressor_coast'):masses[k]=o0['masses_kg'][k]*rate
        amrad=0.
        if ammonia:
            aflux=cfg['ammonia']['radiator_K']**4*.85*5.670374419e-8-80.
            amrad=ammonia['rejected_J']/(coast if buffer_ammonia_rejection else available)/aflux
            if buffer_ammonia_rejection:
                # Warm-side thermal storage permits radiation while solar powers
                # thrust or while the craft is eclipsed. Piecewise exact periodic
                # storage range, with regeneration only in non-burn sunlight.
                halfsun=sun/2
                breaks=[0.,window_s,halfsun,coast-halfsun,coast-window_s,coast]
                cum=[0.]
                for left,right in zip(breaks[:-1],breaks[1:]):
                    mid=(left+right)/2
                    active=(window_s<mid<halfsun or coast-halfsun<mid<coast-window_s)
                    rateheat=ammonia['rejected_J']*(float(active)/available-1/coast)
                    cum.append(cum[-1]+rateheat*(right-left))
                amstore=max(cum)-min(cum)
                masses['ammonia_rejection_buffer']=amstore/p['warm_buffer_J_kg']
            masses['ammonia_radiator']=amrad*5.
            masses['ammonia_refrigerator']=ammoniaW/available/cfg['ammonia']['refrigerator_input_W_kg']
            # All power distribution is charged in the shared peak bus above.
            masses['ammonia_power_distribution']=0.
        solararea=solar/p['solar_W_m2'];warmphysical=rad/2
        travel=max(math.sqrt(solararea),math.sqrt(warmphysical),math.sqrt(o0['metal_panel_m2']),math.sqrt(amrad))/pack['deployment_speed_m_s']*pack['travel_over_sqrt_area']
        newmotion=max(p['deploy_s'],p['retract_s'],travel)
        if abs(newmotion-motion)<.005:break
        motion=.5*(motion+newmotion)
    else:raise ValueError('Direct-solar deployment fixed point did not converge')
    # Existing packing, with changed hardware volumes. Geometry/rack inventories
    # stay fixed. Rear processing stores the same full batch before liquefaction.
    volumes=dict(o0['packaging']['component_package_m3'])
    volumes['solar']=solar/pack['solar_W_m3'];volumes['warm_radiator']=warmphysical*pack['warm_radiator_stack_pitch_m']
    volumes['liquefaction_and_heat_exchangers']=sum(masses[k] for k in ('refrigerator','product_heat_exchangers','separator','warm_aftercooler'))/pack['machinery_bulk_kg_m3']
    volumes['battery']=max(battery*p['battery_Wh_kg']/pack['battery_Wh_m3'],battery/pack['battery_bulk_kg_m3'])
    volumes['warm_heat_buffer']=masses['warm_buffer']/pack['buffer_bulk_kg_m3']
    volumes['propulsion_and_distribution']=(masses['propulsion_hardware']+masses['power_distribution'])/pack['machinery_bulk_kg_m3']
    if ammonia:
        volumes['ammonia_radiator']=amrad*pack['warm_radiator_stack_pitch_m']
        if buffer_ammonia_rejection:volumes['ammonia_rejection_buffer']=masses['ammonia_rejection_buffer']/pack['buffer_bulk_kg_m3']
        volumes['ammonia_machinery']=sum(masses[k] for k in ('ammonia_refrigerator','ammonia_pump','ammonia_tank'))/pack['machinery_bulk_kg_m3']
    # Coast compressor case/motor volume scales with throughput as a screening
    # approximation (whole installed modules, no continuous blade redesign).
    coastbank=raw['compressor_analysis']['coast']['banks']
    vcase=sum(b.get('modules',0)*math.pi*b.get('module_diameter_m',0)**2/4*b.get('bank_length_m',0)/pack['module_packing_fraction'] for b in coastbank)
    vmotor=sum(b.get('motor_kg',0) for b in coastbank)/pack['machinery_bulk_kg_m3']
    volumes['compressor_cases']+=vcase*(rate-1);volumes['compressor_motors']+=vmotor*(rate-1)
    A=math.pi*cfg['design']['front_diameter_m']**2/4
    length=o0['front_depth_m']+o0['rear_depth_m']+o0['packaging']['interstage_rack_depth_m']+sum(volumes.values())/pack['equipment_bay_fill_fraction']/A
    diameter=o0['packaging']['outside_diameter_m'];masses['shell_TPS_allowance']=math.pi*diameter*length*h['shell_TPS_kg_m2']
    masses['design_margin']=sum(masses.values())*h['design_margin'];dry=sum(masses.values())
    margins=dict(length_m=pack['max_length_over_diameter']*diameter-length,
        propellant_kg=oxygen+nitrogen-prop,processing_s=processing,processing_sun_s=available,
        metal_recovery_s=coast-o0['ideal_metal_cooldown_s'])
    return dict(isp_s=isp_s,window_each_s=window_s,efficiency=eta,payoff_days=dry/(net*86400/orbit.period),
        dry_kg=dry,net_kg=net,propellant_kg=prop,nitrogen_propellant_kg=max(0.,prop-oxygen),
        thrust_peak_W=Pthrust,thrust_N=2*eta*Pthrust/v,solar_W=solar,solar_m2=solararea,
        battery_kg=battery,propulsion_energy_J=Eprop,processing_power_W=processP,
        required_solar_energy_J=solar_other+ammoniaW+ammoniaPump/.9+Eprop,available_solar_energy_J=solar*sun,
        processing_s=processing,processing_sun_s=available,coast_s=coast,sun_s=sun,
        motion_s=motion,burn_start_after_perigee_s=start,arc=arc,
        warm_buffer_required_J=buffer,warm_buffer_schedule_J=scheduled_buffer,
        warm_radiator_emitting_m2=rad,ammonia_radiator_m2=amrad,length_m=length,
        masses_kg=masses,margins=margins,screens=all(v>=0 for v in margins.values()),
        orbit_period_s=orbit.period,buffer_ammonia_rejection=buffer_ammonia_rejection,
        status='Fixed-capture first-order steered-orbit / duty-budget estimate; no circular delivery')


def trajectory_check(o,start,duration,drag_dv=1.):
    """Independent Newtonian integration of the steered arcs and perigee impulse.

    Constant mass and impulsive drag: checks first-order orbit restoration only,
    not atmospheric, electrical, attitude or finite-mass-flow dynamics.
    """
    from scipy.integrate import solve_ivp
    arc=arc_restore(o,start,duration,samples=1201);lam=arc['steering_lagrange_multiplier']
    vp=o.h/o.rp
    def reference(t):
        r,vr,vt=state_at(o,np.array([t]));r=float(r[0]);vr=float(vr[0]);vt=float(vt[0])
        f=math.atan2(vr*o.h/(MU*o.e),(o.h**2/(MU*r)-1)/o.e)
        er=np.array([math.cos(f),math.sin(f)]);et=np.array([-math.sin(f),math.cos(f)])
        return r,vr,vt,er,et
    def invariants(y):
        x=y[:2];v=y[2:];radius=np.linalg.norm(x)
        energy=np.dot(v,v)/2-MU/radius;angular=x[0]*v[1]-x[1]*v[0]
        ev=((np.dot(v,v)-MU/radius)*x-np.dot(x,v)*v)/MU
        aa=-MU/(2*energy);ecc=np.linalg.norm(ev)
        return dict(energy=energy,h=angular,rp=aa*(1-ecc),ra=aa*(1+ecc),omega=math.atan2(ev[1],ev[0]))
    r,vr,vt,er,et=reference(-start-duration);y=np.r_[r*er,vr*er+vt*et];initial=invariants(y)
    acceleration=drag_dv*arc['impulse_multiplier']/(2*duration)
    for a,b,burn in [(-start-duration,-start,True),(-start,0.,False),(0.,start,False),(start,start+duration,True)]:
        if a==0:y[3]-=drag_dv
        def rhs(t,y):
            pos=y[:2];acc=-MU*pos/np.linalg.norm(pos)**3
            if burn:
                r,vr,vt,er,et=reference(t);ar=lam*vr/vp;at=r/o.rp+lam*(vt/vp-r/o.rp)
                acc+=acceleration*(ar*er+at*et)/math.hypot(ar,at)
            return np.r_[y[2:],acc]
        sol=solve_ivp(rhs,(a,b),y,method='DOP853',rtol=2e-12,atol=1e-8,max_step=10.)
        if not sol.success:raise ValueError('Orbit verification integration failed')
        y=sol.y[:,-1]
    final=invariants(y)
    return dict(drag_dv_m_s=drag_dv,energy_residual_fraction_of_drag=(final['energy']-initial['energy'])/(vp*drag_dv),
        angular_residual_fraction_of_drag=(final['h']-initial['h'])/(o.rp*drag_dv),
        perigee_error_m=final['rp']-initial['rp'],apogee_error_m=final['ra']-initial['ra'],
        apsidal_rotation_deg=math.degrees(final['omega']-initial['omega']))
