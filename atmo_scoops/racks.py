"""Finite ordinary-metal cross-wire racks; no pressure-drop model.

Alternating, nonintersecting wire planes spaced one pitch apart give phi=pi(r/p)^2.
The continuum cylinder correlation is bridged to a free-molecular conductance;
this bridge is an explicit engineering approximation, not a mesh calibration.
"""
from dataclasses import dataclass, asdict, replace
import math
import numpy as np
from scipy.integrate import cumulative_trapezoid, quad

@dataclass(frozen=True)
class Racks:
    enabled: bool = True
    wire_radius_m: float = .0001
    radius_over_pitch: float = .05
    wire_radii_m: tuple = ()  # Optional radius independently for each rack.
    mass_factors: tuple = (1.5, 1.5, 1.5, 1.5)
    masses_kg: tuple = ()  # Optional independently specified front + interstage racks.
    accommodation: float = .8
    heat_transfer_factor: float = 1.
    deployed_view_factor: float = .7
    metal_conductivity_W_m_K: float = 40.

    pcm_material: str = 'none'
    pcm_materials: tuple = ()  # Optional front / interstage identities independently.
    pcm_wall_m: float = .0005
    pcm_cell_length_m: float = .5
    pcm_fill_fraction: float = .8
    pcm_fin_volume_fraction: float = 0.
    pcm_contact_resistance_m2_K_W: float = .0001
    pcm_latent_fraction: float = 1.  # Zero isolates sensible capacity at identical geometry.

    def for_stage(self,i):
        return replace(self,pcm_material=self.pcm_materials[i] if self.pcm_materials else self.pcm_material,
            wire_radius_m=self.wire_radii_m[i] if self.wire_radii_m else self.wire_radius_m)

    def validate(self, blocks):
        if not isinstance(self.enabled,bool):raise ValueError('racks.enabled must be boolean')
        for key,value in asdict(self).items():
            if key in ('enabled','pcm_material','pcm_materials'):continue
            values=value if isinstance(value,(tuple,list)) else (value,)
            if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in values):
                raise ValueError(f'racks.{key} must contain finite numbers')
        from .pcm import MATERIALS
        names=self.pcm_materials or (self.pcm_material,)*blocks
        if self.wire_radii_m and (len(self.wire_radii_m)!=blocks or any(r<=0 for r in self.wire_radii_m)):raise ValueError('One positive radius per rack required')
        if self.pcm_materials and len(names)!=blocks:raise ValueError('One PCM identity per rack required')
        if any(name not in ('none',*MATERIALS) for name in names):raise ValueError('Unknown PCM material')
        if any(name!='none' for name in names):
            if not 0<self.pcm_wall_m<min(min(self.for_stage(i).wire_radius_m for i,n in enumerate(names) if n!='none'),self.pcm_cell_length_m/2):raise ValueError('PCM wall must fit inside radius and cell length')
            if not 0<self.pcm_fill_fraction<=1 or not 0<=self.pcm_fin_volume_fraction<.5:raise ValueError('Invalid PCM filling or fin fraction')
            if self.pcm_contact_resistance_m2_K_W<0 or not 0<=self.pcm_latent_fraction<=1:raise ValueError('Invalid contact or latent fraction')
            if any(self.pcm_fill_fraction*MATERIALS[x].density_kg_m3/MATERIALS[x].liquid_density_kg_m3>1 for x in names if x!='none'):raise ValueError('Insufficient PCM expansion volume')
        if self.wire_radius_m<=0 or not 0<self.radius_over_pitch<.25:raise ValueError('Invalid wire radius/pitch')
        if len(self.mass_factors)!=blocks or any(x<=0 for x in self.mass_factors):raise ValueError('One positive rack mass factor per compressor block required')
        if self.masses_kg and (len(self.masses_kg)!=blocks or any(x<=0 for x in self.masses_kg)):raise ValueError('One positive metal mass per compressor block required')
        for x in (self.accommodation,self.deployed_view_factor):
            if not 0<x<=1:raise ValueError('Accommodation/view factor must lie in (0,1]')
        if self.heat_transfer_factor<=0 or self.metal_conductivity_W_m_K<=0:raise ValueError('Positive heat-transfer capabilities required')


def geometry(mass, density, area, spec):
    extra={}
    solid=mass/density
    if spec.pcm_material!='none':
        from .pcm import cell_geometry
        extra=cell_geometry(mass,density,spec);solid=extra['displaced_m3']
    phi=math.pi*spec.radius_over_pitch**2
    envelope=solid/phi
    return dict(mass_kg=mass,solid_m3=solid,envelope_m3=envelope,gas_m3=envelope-solid,
        porosity=1-phi,wetted_m2=2*solid/spec.wire_radius_m,
        depth_m=envelope/area,frontal_m2=area,wire_radius_m=spec.wire_radius_m,
        pitch_m=spec.wire_radius_m/spec.radius_over_pitch,
        # Unfurl the existing wire planes at their original pitch; footprint
        # includes their gaps. Never equate wetted wire area and deployed footprint.
        deployed_physical_m2=solid/(math.pi*spec.wire_radius_m*spec.radius_over_pitch),**extra)


def conductance(p,T,mdot,area,geom,spec,R=287.,cp=1100.):
    T=max(200.,T);mu=1.716e-5*(T/273.15)**1.5*(273.15+110.4)/(T+110.4)
    k=mu*cp/.71;rho=max(p,1e-12)/(R*T);radius=geom['wire_radius_m'];ratio=radius/geom['pitch_m'];diameter=2*radius
    # Gap velocity through each plane, not bulk pore-volume velocity.
    v=abs(mdot)/(rho*area*(1-2*ratio))
    Re=rho*v*diameter/mu;Pr=.71
    Nu=.3+.62*math.sqrt(Re)*Pr**(1/3)/(1+(.4/Pr)**(2/3))**.25*(1+(Re/282000)**(5/8))**.8
    continuum=Nu*k/diameter
    gamma=cp/(cp-R)
    molecular=spec.accommodation/(2-spec.accommodation)*(gamma+1)/(gamma-1)*math.sqrt(R/(8*math.pi*T))*max(p,0.)
    h=spec.heat_transfer_factor/(1/continuum+1/max(molecular,1e-30))
    mean_path=mu/max(p,1e-30)*math.sqrt(math.pi*R*T/2)
    UA=h*geom['wetted_m2'];extra={}
    if 'liquid' in geom:
        from .ammonia import exchange
        UA,extra=exchange(UA,2*T-geom['liquid']['cold_K'],geom)
    return UA,dict(**extra,h_W_m2_K=h,Re=Re,Kn=mean_path/diameter,
        Bi=h*radius/(2*spec.metal_conductivity_W_m_K),velocity_m_s=v)


class Metal:
    def __init__(self,cold):
        from .two_volume import iron_cp
        self.T=np.linspace(298.,1042.,2001)
        self.H=cumulative_trapezoid([iron_cp(t) for t in self.T],self.T,initial=0.)
        self.cold=cold;self.hcold=self.enthalpy(cold)
    def enthalpy(self,T):return float(np.interp(T,self.T,self.H))
    def temperature(self,h):
        # Linear extension only lets an infeasible trial finish and be rejected.
        if h>self.H[-1]:return 1042+(h-self.H[-1])/700
        if h<0:return 298+h/450
        return float(np.interp(h,self.H,self.T))
    def cooldown(self,hot,geom,emissivity,spec):
        if hot<=self.cold:return 0.
        if hot>1042:return 1e30
        from .two_volume import iron_cp
        effective=geom['wetted_m2']*spec.deployed_view_factor
        return geom['mass_kg']/effective*quad(lambda T:iron_cp(T)/(emissivity*5.670374419e-8*T**4-80),self.cold,hot,points=[700] if self.cold<700<hot else None)[0]
