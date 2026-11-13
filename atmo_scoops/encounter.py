"""Atmosphere-relative Kepler kinematics and the pressure-defined entry window."""
import numpy as np
from scipy.optimize import brentq
from .orbit import MU, OMEGA, R_EARTH

def orbit_state(orbit, t, atmosphere):
    t=np.asarray(t,dtype=float)
    mean=2*np.pi*t/orbit.period
    E=mean/(1-orbit.e)
    for _ in range(12):
        E-=(E-orbit.e*np.sin(E)-mean)/(1-orbit.e*np.cos(E))
    r=orbit.a*(1-orbit.e*np.cos(E))
    vr=np.sqrt(MU*orbit.a)*orbit.e*np.sin(E)/r
    vt=orbit.h/r
    speed=np.hypot(vr,vt-OMEGA*r)
    altitude=(r-R_EARTH)/1000
    # Roundoff at the bottom of the atmosphere grid is not physical extrapolation.
    rho,f=atmosphere.at(np.maximum(altitude,atmosphere.alt_km[0]))
    T=np.interp(altitude,atmosphere.alt_km,atmosphere.temperature)
    nR=np.sum(f/(np.array([28.0134,31.9988,15.9994,4.0026,1.00794,39.948,14.0067,15.9994,30.0061])),axis=-1)*8314.462618
    return dict(time_s=t,altitude_km=altitude,speed_m_s=speed,density_kg_m3=rho,
                fractions=f,temperature_K=T,ram_Pa=rho*speed**2,
                dynamic_Pa=.5*rho*speed**2,ambient_Pa=rho*nR*T)


def pressure_window(orbit,atmosphere,fraction):
    if not 0<fraction<1:raise ValueError('Pressure fraction must be between 0 and 1')
    peak=float(orbit_state(orbit,0,atmosphere)['ram_Pa'])
    upper=orbit.time_at_altitude(min(500,orbit.apogee_km))
    edge=brentq(lambda t:float(orbit_state(orbit,t,atmosphere)['ram_Pa'])/peak-fraction,0,upper)
    return edge,peak


