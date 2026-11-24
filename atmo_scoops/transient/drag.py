"""Axial skin-friction impulse screen; coefficient is an engineering scenario.

Cf is an effective, wetted-area mean coefficient referenced to freestream
q = rho*v_relative**2/2. It is not a frontal-area drag coefficient, a calibrated
hypersonic correlation, or a model of wall heating.
"""
import math
import numpy as np


def skin_impulse(time_s, density_kg_m3, speed_m_s, diameter_m, length_m,
                 coefficient=0., area_multiplier=1.):
    if min(diameter_m,length_m)<=0 or min(coefficient,area_multiplier)<0:
        raise ValueError('Invalid external skin geometry/coefficient')
    area=math.pi*diameter_m*length_m*area_multiplier
    force=.5*np.asarray(density_kg_m3)*np.asarray(speed_m_s)**2*coefficient*area
    return dict(coefficient=coefficient,wetted_area_m2=area,
                impulse_Ns=float(np.trapezoid(force,time_s)),
                peak_force_N=float(np.max(force)),
                mechanical_work_J=float(np.trapezoid(force*np.asarray(speed_m_s),time_s)))


def air_viscosity(T):
    """Sutherland molecular-air approximation (SI); high-T extrapolation flagged."""
    T=np.asarray(T,dtype=float)
    return 1.716e-5*(T/273.15)**1.5*(273.15+110.4)/(T+110.4)


def flat_plate_laminar(time_s, density_kg_m3, speed_m_s, temperature_K,
                       diameter_m, length_m, wall_K=600., area_multiplier=1.):
    """Finite plate, frozen-air Eckert enthalpy/Blasius shear screening model.

    Boundary-layer edge is assumed equal to freestream. Not a transition,
    reacting-flow, shock-interaction or rarefied-flow solution. See
    modeling/aerodynamics/FLAT_PLATE_SHEAR.md before selecting this option.
    """
    from .thermo import properties,Y
    t,rho,U,T=np.broadcast_arrays(*[np.asarray(x,dtype=float) for x in
                                  (time_s,density_kg_m3,speed_m_s,temperature_K)])
    if t.ndim!=1 or len(t)<2 or np.any(np.diff(t)<=0):
        raise ValueError('Skin history requires increasing one-dimensional times')
    if (min(diameter_m,length_m,wall_K)<=0 or area_multiplier<0 or
        np.any(rho<=0) or np.any(U<=0) or np.any(T<=0) or
        not all(np.all(np.isfinite(x)) for x in (t,rho,U,T))):
        raise ValueError('Invalid skin-flow state or geometry')
    p=properties();R=float(Y@p.R);hh=Y@p.h
    if min(T.min(),wall_K)<p.T[0] or max(T.max(),wall_K)>p.T[-1]:
        raise ValueError('Skin temperature outside caloric table')
    he=np.interp(T,p.T,hh);hw=float(np.interp(wall_K,p.T,hh));Pr=.72
    haw=he+np.sqrt(Pr)*U**2/2
    href=.28*he+.5*hw+.22*haw
    if href.max()>hh[-1]:raise ValueError('Reference enthalpy outside caloric table')
    Ts=np.interp(href,hh,p.T)
    mu=air_viscosity(T);mus=air_viscosity(Ts)
    ratio=T/Ts;C=ratio*mus/mu
    Re=rho*U*length_m/mu
    cf=1.328*np.sqrt(C/Re)  # length average; local coefficient is half this
    area=math.pi*diameter_m*length_m*area_multiplier
    q=.5*rho*U**2;force=q*area*cf
    J=float(np.trapezoid(force,t));qdt=float(np.trapezoid(q,t))
    peak=int(np.argmax(q));mfp=mu/rho*np.sqrt(np.pi/(2*R*T))
    # Reference-state thickness is a scale diagnostic, not a compressible profile.
    Restar=Re*ratio*mu/mus;delta_proxy=5*length_m/np.sqrt(Restar)
    def weighted(mask):return float(np.trapezoid(force*np.asarray(mask),t)/J) if J else 0.
    return dict(model='flat_plate_laminar',wall_K=wall_K,Pr=Pr,
      coefficient=J/(area*qdt) if area*qdt else 0.,wetted_area_m2=area,
      impulse_Ns=J,peak_force_N=float(force.max()),
      mechanical_work_J=float(np.trapezoid(force*U,t)),
      peak_dynamic_state=dict(time_s=float(t[peak]),rho_kg_m3=float(rho[peak]),
        speed_m_s=float(U[peak]),temperature_K=float(T[peak]),dynamic_Pa=float(q[peak]),
        Re_L=float(Re[peak]),Re_reference_L=float(Restar[peak]),
        reference_K=float(Ts[peak]),Cf=float(cf[peak]),
        mean_free_path_m=float(mfp[peak]),Kn_D=float(mfp[peak]/diameter_m),
        reference_thickness_proxy_m=float(delta_proxy[peak])),
      impulse_fraction_Kn_D_above_001=weighted(mfp/diameter_m>.01),
      impulse_fraction_reference_above_2000K=weighted(Ts>2000),
      assumptions=['laminar attached smooth wall; zero pressure gradient',
        'freestream edge; frozen molecular air calorics; Sutherland viscosity',
        'no rarefaction correction or transition prediction; no wall-heating budget'])
