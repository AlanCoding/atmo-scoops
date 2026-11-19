"""Compressible resistance for inline banks and legacy transverse-rod planes.

Independent-plane cylinder drag is a transparent provisional resistance model,
not a validated woven-screen or rarefied multirow correlation. A multiplier
exposes wake/shielding/correlation uncertainty. The inline bank instead uses
the published low-Re array coefficient. No pressure loss removes energy.
"""
import math
from functools import lru_cache
from scipy.optimize import brentq


def laminar_bank_coefficient(Re,a,b):
    """Gaddis-Gnielinski laminar term, Martin/Gnielinski (2000) Eq. A8.

    Gap-velocity convention; standard inline array. Low-Re continuum model,
    extrapolated below Re=1. No slip drag-reduction credit is assumed.
    """
    return 280*math.pi*((math.sqrt(b)-.6)**2+.75)/(a**1.6*(4*a*b-math.pi)*max(Re,1e-30))


def viscosity(T):
    return 1.716e-5*(max(T,200.)/273.15)**1.5*(273.15+110.4)/(max(T,200.)+110.4)


def suction_pressure(mdot,p,T,R,geom,multiplier=1.):
    if mdot<=0 or multiplier==0:return max(p,0.),dict(drop_Pa=0.,Re=0.,Kn=0.,pore_Mach=0.)
    radius=geom['wire_radius_m'];pitch=geom['pitch_m'];beta=1-2*radius/pitch
    g=mdot/geom['frontal_m2'];mu=viscosity(T)
    Re=g*2*radius/(beta*mu)
    # Smooth cylinder-drag screen (low-Re growth and an order-unity inertial term).
    Cd=1.+10./max(Re,1e-20)**(2/3)
    if geom.get('lattice')=='inline_square_bank' or geom.get('pressure_model')=='inline_laminar':
        a=pitch/(2*radius)
        zeta=laminar_bank_coefficient(Re,a,a)
        # Low-Re viscous drag plus finite-row exit mixing. No fitted turbulent term.
        K=multiplier*(geom['row_count']*zeta+(1-beta)**2)/beta**2
    else:K=multiplier*geom['row_count']*Cd*(2*radius/pitch)/beta**2
    ps=math.sqrt(max(0.,p*p-K*g*g*R*T))
    pm=max((p+ps)/2,1e-20)
    Kn=mu/pm*math.sqrt(math.pi*R*T/2)/(2*radius)
    rho_s=max(ps,1e-20)/(R*T)
    Mach=g/(rho_s*beta*math.sqrt(1.4*R*T))
    return ps,dict(drop_Pa=p-ps,Re=Re,Kn=Kn,pore_Mach=Mach)


def pump_flow(p,T,pout,R,y,geom,S,head,motor_W,eta_motor,eta_comp,thermo,cutoff,multiplier):
    """Solve rack suction pressure, finite pump map and motor limit together."""
    # State is fixed for this root solve. Brent revisits its endpoints and the
    # caller requests the converged point again; reuse those exact evaluations.
    @lru_cache(maxsize=64)
    def at(m):
        ps,info=suction_pressure(m,p,T,R,geom,multiplier)
        if ps<=cutoff:return 0.,ps,0.,info
        work=thermo.compression(T,ps,pout,y,eta_comp)
        cap=max(0.,1-(work/max(head,1.))**2)
        flow=S*max(ps-.03,0)/(R*T)*cap*min(1.,max(0.,(ps-cutoff)/cutoff))
        flow=min(flow,motor_W/max(work/eta_motor,1e-30))
        return flow,ps,work,info
    upper=at(0.)[0]
    if upper<=0:return 0.,max(p,0.),0.,dict(drop_Pa=0.,Re=0.,Kn=0.,pore_Mach=0.)
    if multiplier==0:m=upper
    else:m=brentq(lambda m:at(m)[0]-m,0.,upper,xtol=1e-12,rtol=1e-10)
    _,ps,w,info=at(m)
    return m,ps,w,info
