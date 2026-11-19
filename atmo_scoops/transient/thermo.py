"""Frozen molecular gas caloric tables and species-resolved liquid duty.

Gas EOS is explicitly ideal at low density; pure-species real-fluid phase
properties come from HEOS. Not a nonideal mixture flash or reacting inlet.
"""
from functools import lru_cache
import numpy as np
import CoolProp.CoolProp as CP
from ..thermochemistry import gas
from ..low_density import gas_update
NAMES=('N2','O2','Ar');FLUIDS=('Nitrogen','Oxygen','Argon');Y=np.array([.755,.232,.013])

class Properties:
 def __init__(self):
  g=gas();self.T=np.r_[np.arange(60.,2000.1,2),np.arange(2010.,15001.,10.)]
  hh=[];ss=[];cc=[];rr=[];liq=[];boil=[];latent=[];rho=[]
  for name,fluid in zip(NAMES,FLUIDS):
   g.TPY=298.15,1e5,{name:1.};R=8314.462618/g.mean_molecular_weight;href=g.enthalpy_mass
   h=[];s=[];cp=[]
   for T in self.T:
    g.TP=max(T,200.),1e5;cv=g.cp_mass
    h.append(g.enthalpy_mass+cv*min(0.,T-200));s.append(g.entropy_mass+cv*np.log(min(T,200)/200));cp.append(cv)
   hb=CP.PropsSI('H','P',1e5,'Q',0,fluid);hr=CP.PropsSI('H','P',1e5,'T',298.15,fluid)
   liq.append(href+hb-hr);tb=CP.PropsSI('T','P',1e5,'Q',0,fluid);boil.append(tb);latent.append(CP.PropsSI('H','P',1e5,'Q',1,fluid)-hb);rho.append(CP.PropsSI('D','P',1e5,'Q',0,fluid))
   hh.append(h);ss.append(s);cc.append(cp);rr.append(R)
  self.h=np.array(hh);self.s=np.array(ss);self.cp=np.array(cc);self.R=np.array(rr);self.u=self.h-self.R[:,None]*self.T
  self.table_enabled=False;self.table=None
  self.real=CP.AbstractState('HEOS','Nitrogen&Oxygen&Argon');self.real.specify_phase(CP.iphase_gas);self.real_y=None
  self.liquid_h=np.array(liq);self.boil=np.array(boil);self.latent=np.array(latent);self.liquid_density=np.array(rho)
 def at(self,T,y=Y):
  h=np.array([np.interp(T,self.T,a) for a in self.h]);cp=np.array([np.interp(T,self.T,a) for a in self.cp])
  return h,float(y@cp),float(y@self.R)
 @lru_cache(maxsize=512)
 def mixture(self,key):
  y=np.array(key);return y@self.u,y@self.s,y@self.h
 def temperature(self,U,m):
  total=float(sum(m))
  if total<1e-30:return 300.
  return float(np.interp(U/total,self.mixture(tuple(np.round(m/total,12)))[0],self.T))
 def compression(self,T,p1,p2,y=Y,eta=.75):
  if p2<=p1:return 0.
  _,sm,hm=self.mixture(tuple(np.round(y,12)));R=float(y@self.R)
  target=np.interp(T,self.T,sm)+R*np.log(p2/max(p1,1e-12))
  Ts=np.interp(target,sm,self.T)
  ideal=max(0.,float((np.interp(Ts,self.T,hm)-np.interp(T,self.T,hm))/eta))
  # HEOS mixture isentropic work; the ideal table supplies a Newton seed and
  # a continuation for rejected high-temperature / vanishing-pressure trials.
  if p1<1e-4 or not 200<=T<=2000 or Ts>2000:return ideal
  if self.table_enabled and max(abs(y-Y))<1e-10:
   if self.table is None:
    from .property_table import Table
    self.table=Table()
   w=self.table.work(T,p1,p2,Ts,eta)
   if w is not None:return w
  f=self.real;key=tuple(float(z) for z in y)
  if key!=self.real_y:f.set_mass_fractions(list(key));self.real_y=key
  f=gas_update(f,p1,T);h1=f.hmass();s1=f.smass()
  for _ in range(7):
   f=gas_update(f,p2,Ts);ds=f.smass()-s1
   if abs(ds)<1e-6:break
   Ts=float(np.clip(Ts-ds*Ts/f.cpmass(),200.,2000.))
  return max(0.,float((f.hmass()-h1)/eta))
 def liquid_duty(self,T,y,reject_K,eta):
  # Piecewise sensible cooling plus species latent load at real boiling points.
  work=np.zeros(3);cold=np.zeros(3)
  sink=reject_K+20.
  for k,tb in enumerate(self.boil):
   lo=tb;hi=max(tb,T);grid=np.linspace(lo,hi,30);cp=np.interp(grid,self.T,self.cp[k]);lift=np.maximum(sink/(grid-5)-1,0.)
   work[k]=np.trapezoid(cp*lift,grid)/eta+self.latent[k]*max(sink/(tb-5)-1,0)/eta
   cold[k]=np.interp(T,self.T,self.h[k])-self.liquid_h[k]
  return float(y@work),float(y@cold)

@lru_cache(None)
def properties():return Properties()
