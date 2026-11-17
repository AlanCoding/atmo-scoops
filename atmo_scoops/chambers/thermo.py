"""Thermally perfect frozen air and temperature-dependent iron caloric tables.

NASA caloric data, ideal gas EOS. Not reacting shock chemistry or dense-fluid HEOS.
A single consistent enthalpy reference is used on every flow boundary.
"""
import numpy as np
from scipy.integrate import cumulative_trapezoid
from ..thermochemistry import gas
from ..two_volume import iron_cp

class Air:
    def __init__(self):
        g=gas();g.TPY=298.,1e5,{'N2':.755,'O2':.232,'Ar':.013}
        self.R=8314.462618/g.mean_molecular_weight
        self.T=np.linspace(200.,15000.,14801)
        h=[];u=[];s=[];cp=[]
        for t in self.T:
            g.TP=t,1e5;h.append(g.enthalpy_mass);u.append(g.int_energy_mass);s.append(g.entropy_mass);cp.append(g.cp_mass)
        self.h=np.array(h);self.u=np.array(u);self.s=np.array(s);self.cp=np.array(cp)
    def at(self,T):
        return tuple(float(np.interp(T,self.T,x)) for x in (self.h,self.u,self.cp))
    def temperature(self,u):return float(np.interp(u,self.u,self.T))
    def compression(self,T,p1,p2,eta):
        if p2<=p1:return 0.
        entropy=np.interp(T,self.T,self.s)+self.R*np.log(p2/max(p1,1e-12))
        Ts=np.interp(entropy,self.s,self.T)
        return (self.at(Ts)[0]-self.at(T)[0])/eta

class Iron:
    def __init__(self):
        self.T=np.linspace(200,1500,2601)
        # Existing Fe correlation is qualified only over 298–1042 K here.
        cp=np.array([iron_cp(float(np.clip(t,298,1042))) for t in self.T])
        self.h=cumulative_trapezoid(cp,self.T,initial=0.)
    def energy(self,T):return float(np.interp(T,self.T,self.h))
    def temperature(self,h):return float(np.interp(h,self.h,self.T))
