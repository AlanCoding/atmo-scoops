"""Sensible rack properties for the isolated transient only.

Sources and capability assumptions: modeling/chambers/MATERIALS.md.
Temperature caps are study constraints, not qualified flight allowables.
"""
from functools import lru_cache
import numpy as np
from scipy.integrate import cumulative_trapezoid, quad
from ..two_volume import iron_cp

PROPERTIES = {
    'iron': (7870., 1042., .8, 40.),
    'fecral': (7100., 1042., .7, 11.),
    'sic': (3210., 1000., .8, 40.),
    'aluminum': (2700., 550., .8, 150.),
}

class Material:
    def __init__(self, name):
        self.name=name
        self.density,self.limit_K,self.emissivity,self.conductivity=PROPERTIES[name]
        self.T=np.linspace(200.,1500.,2601)
        self.h=cumulative_trapezoid([self.cp(t) for t in self.T],self.T,initial=0.)
    def cp(self,T):
        T=float(np.clip(T,298.,1042. if self.name=='iron' else 1000. if self.name=='sic' else 933. if self.name=='aluminum' else 1673.15))
        if self.name=='iron':return iron_cp(T)
        if self.name=='fecral':return float(np.interp(T,np.array([20,200,400,600,800,1000,1200,1400])+273.15,np.array([.46,.56,.63,.75,.71,.72,.74,.80])*1000))
        A,B,C,D,E,mw = (20.55859,64.57962,-52.98827,16.95813,-.781847,.0400962) if self.name=='sic' else (28.08920,-5.414849,8.560423,3.427370,-.277375,.0269815386)
        t=T/1000
        return (A+B*t+C*t*t+D*t**3+E/t**2)/mw
    def energy(self,T):return float(np.interp(T,self.T,self.h))
    def temperature(self,h):return float(np.interp(h,self.h,self.T))
    def cooldown(self,hot,cold,geom,emissivity,view_factor=.7):
        if hot<=cold:return 0.
        if hot>self.limit_K or emissivity*5.670374419e-8*cold**4<=80:return 1e30
        # Same absorbed 80 W/m² environmental load as the preceding iron study.
        return geom['mass_kg']/(geom['wetted_m2']*view_factor)*quad(lambda t:self.cp(t)/(emissivity*5.670374419e-8*t**4-80),cold,hot,epsabs=.01)[0]

@lru_cache(None)
def material(name):
    if name not in PROPERTIES:raise ValueError(f'Unknown rack material: {name}')
    return Material(name)
