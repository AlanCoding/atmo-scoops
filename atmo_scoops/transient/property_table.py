"""Real-mixture HEOS h/s interpolation, not an ideal-gas work surrogate."""
from pathlib import Path
import json
import numpy as np
import CoolProp.CoolProp as CP
from scipy.interpolate import RectBivariateSpline
PATH=Path(__file__).resolve().parents[2]/'results/properties/air_heos.npz'

class Table:
    def __init__(self):
        z=np.load(PATH);self.T=z['T'];self.lp=z['lp']
        self.h=RectBivariateSpline(self.T,self.lp,z['h'],s=0)
        self.s=RectBivariateSpline(self.T,self.lp,z['s'],s=0)
    def work(self,T,p1,p2,seed,eta):
        l1=np.log(p1);l2=np.log(p2)
        if not (self.T[0]<=T<=self.T[-1] and self.T[0]<=seed<=self.T[-1] and self.lp[0]<=l1<=l2<=self.lp[-1]):return None
        h1=float(self.h.ev(T,l1));s1=float(self.s.ev(T,l1));ts=seed
        for _ in range(6):
            ds=float(self.s.ev(ts,l2))-s1
            if abs(ds)<1e-7:break
            ts-=ds/float(self.s.ev(ts,l2,dx=1))
            if not self.T[0]<=ts<=self.T[-1]:return None
        return max(0.,(float(self.h.ev(ts,l2))-h1)/eta)

def main():
    T=np.linspace(200,2000,901);lp=np.linspace(np.log(1e-4),np.log(2e6),121)
    f=CP.AbstractState('HEOS','Nitrogen&Oxygen&Argon');f.set_mass_fractions([.755,.232,.013]);f.specify_phase(CP.iphase_gas)
    h=np.empty((len(T),len(lp)));s=h.copy()
    for i,t in enumerate(T):
        for j,l in enumerate(lp):
            f.update(CP.PT_INPUTS,float(np.exp(l)),float(t));h[i,j]=f.hmass();s[i,j]=f.smass()
    PATH.parent.mkdir(exist_ok=True,parents=True);np.savez_compressed(PATH,T=T,lp=lp,h=h,s=s)
    PATH.with_suffix('.json').write_text(json.dumps(dict(provider='CoolProp HEOS',version=CP.get_global_param_string('version'),mass_fractions=[.755,.232,.013],temperature_K=[200,2000],pressure_Pa=[1e-4,2e6],shape=list(h.shape),method='bicubic h and s; isentropic entropy inversion'),indent=2)+'\n')
if __name__=='__main__':main()
