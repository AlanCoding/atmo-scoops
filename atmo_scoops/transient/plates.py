"""Parallel plates aligned with flow: homogenized geometry and laminar channels.

No-slip plane Poiseuille friction, Darcy f Re_Dh=96, Dh=2*clear gap.
Fully-developed isothermal-wall Nu=7.54. See modeling/metal_coolers/PLATES.md.
"""
import math
from .porous import viscosity


def geometry(area, depth, thickness, gap, density):
    if min(area, depth, thickness, gap, density)<=0:
        raise ValueError('Positive plate dimensions required')
    phi=thickness/(thickness+gap)
    solid=area*depth*phi
    return dict(lattice='parallel_plates',frontal_m2=area,rack_depth_m=depth,
                thickness_m=thickness,gap_m=gap,pitch_m=thickness+gap,
                porosity=1-phi,solid_m3=solid,envelope_m3=area*depth,
                gas_m3=area*depth-solid,gross_m3=area*depth,depth_m=depth,
                mass_kg=solid*density,wetted_m2=2*solid/thickness,
                deployed_physical_m2=solid/thickness,hydraulic_diameter_m=2*gap)


def diagnostics(mdot,p,T,rho,g,R=287.):
    mu=viscosity(T);gap=g['gap_m'];dh=2*gap
    u=max(mdot,0)/(max(rho,1e-30)*g['frontal_m2']*g['porosity'])
    dp=12*mu*g['rack_depth_m']*u/gap**2
    return dict(drop_Pa=dp,Re=rho*u*dh/mu,
                Kn=mu/max(p,1e-30)*math.sqrt(math.pi*R*T/2)/gap,
                pore_Mach=u/math.sqrt(1.4*R*T))


def charge(mdot,p,T,rho,g,eta):
    if mdot<=0:return 0.,0.
    if min(p,T,rho,eta)<=0:raise ValueError('Positive flowing state required')
    dp=diagnostics(mdot,p,T,rho,g)['drop_Pa']
    return dp*mdot/rho/eta,2*dp/p


def conductance(p,T,mdot,area,g,spec,R=287.,cp=1100.):
    T=max(200.,T);mu=viscosity(T);rho=max(p,1e-12)/(R*T)
    info=diagnostics(abs(mdot),p,T,rho,g,R)
    k=mu*cp/.71;hc=7.54*k/g['hydraulic_diameter_m']
    gamma=cp/(cp-R)
    hm=spec.accommodation/(2-spec.accommodation)*(gamma+1)/(gamma-1)*math.sqrt(R/(8*math.pi*T))*max(p,0.)
    h=spec.heat_transfer_factor/(1/hc+1/max(hm,1e-30))
    info.update(h_W_m2_K=h,Bi=h*g['thickness_m']/(2*spec.metal_conductivity_W_m_K))
    return h*g['wetted_m2'],info
