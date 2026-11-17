"""Independent lumped-volume gas/solid transient, not the payoff model."""
from dataclasses import dataclass,asdict
import math
import numpy as np
from scipy.integrate import solve_ivp
from ..racks import conductance,Racks
from ..open_mouth import port_flow
from .thermo import Air
from .materials import material

@dataclass(frozen=True)
class Chamber:
    name: str
    diameter_m: float
    depth_m: float
    rack_depth_m: float=0.
    rod_radius_m: float=.001
    rod_pitch_m: float=.01
    initial_metal_K: float=298.
    initial_gas_K: float=298.
    initial_pressure_Pa: float=.03
    coast_mixing_m_s: float=0.
    external_emitting_m2: float=0.
    material: str="iron"
    rack_emissivity: float | None=None
    def geometry(self):
        mat=material(self.material)
        if self.rack_emissivity is not None and not 0<self.rack_emissivity<=1:raise ValueError("Invalid rack emissivity")
        if not (self.diameter_m>0 and self.depth_m>0 and 0<=self.rack_depth_m<=self.depth_m and 0<self.rod_radius_m/self.rod_pitch_m<.25):raise ValueError('Invalid chamber/rack geometry')
        if min(self.initial_metal_K,self.initial_gas_K)<200 or self.initial_pressure_Pa<=0 or min(self.coast_mixing_m_s,self.external_emitting_m2)<0:raise ValueError('Invalid chamber state')
        area=math.pi*self.diameter_m**2/4;envelope=area*self.rack_depth_m
        solid=envelope*math.pi*(self.rod_radius_m/self.rod_pitch_m)**2
        return dict(frontal_m2=area,gas_m3=area*self.depth_m-solid,solid_m3=solid,
            envelope_m3=envelope,mass_kg=solid*mat.density,wetted_m2=2*solid/self.rod_radius_m,
            wire_radius_m=self.rod_radius_m,pitch_m=self.rod_pitch_m)

@dataclass(frozen=True)
class Pump:
    suction_m3_s: float
    max_shaft_J_kg: float
    efficiency: float=.75
    ultimate_Pa: float=.03
    stop_s: float=600.
    cutoff_Pa: float=.1

@dataclass(frozen=True)
class Schedule:
    start_s: float=-440.
    end_s: float=2400.
    withdrawal_start_s: float=600.
    withdrawal_kg_s: float=1.
    withdrawal_floor_Pa: float=100.
    contact_stop_s: float=1e30
    radiation_start_s: float=600.
    radiation_ramp_s: float=120.
    radiation_sink_K: float=200.
    emissivity: float=.8
    max_step_s: float=2.
    rtol: float=2e-6

class Boundary:
    """Prescribed external support, incident supply and total incoming enthalpy."""
    def __init__(self,time_s,supply_kg_s,support_Pa,enthalpy_J_kg,mouth_area_m2):
        self.t=np.asarray(time_s);self.supply=np.asarray(supply_kg_s);self.support=np.asarray(support_Pa);self.h=np.asarray(enthalpy_J_kg);self.area=mouth_area_m2
        if len(self.t)<2 or np.any(np.diff(self.t)<=0) or any(len(a)!=len(self.t) for a in (self.supply,self.support,self.h)):raise ValueError('Invalid boundary table')
        if self.area<0 or np.any(self.supply<0) or np.any(self.support<0):raise ValueError('Negative boundary')
    def at(self,t):
        return (float(np.interp(t,self.t,self.supply,left=0,right=0)),float(np.interp(t,self.t,self.support,left=0,right=0)),float(np.interp(t,self.t,self.h)))


def simulate(chambers,pumps,boundary,schedule=Schedule(),samples=1501):
    """Integrate m, gas U and solid E in every fixed chamber, plus audit ledgers.

    Pump discharge adds shaft work as enthalpy. Off pumps seal; inlet stays open.
    Withdrawal removes gas enthalpy, not just mass. No liquefaction power credit.
    External radiation is optional effective thermal coupling, NOT an open hatch.
    """
    n=len(chambers);cfg=schedule;air=Air();metals=[material(c.material) for c in chambers];geom=[c.geometry() for c in chambers]
    if len(pumps)!=n-1:raise ValueError('One pump between each pair of chambers')
    if cfg.end_s<=cfg.start_s or min(cfg.max_step_s,cfg.rtol)<=0 or cfg.withdrawal_kg_s<0 or cfg.withdrawal_floor_Pa<=0 or cfg.radiation_ramp_s<=0:raise ValueError('Invalid schedule')
    for p in pumps:
        if p.suction_m3_s<=0 or p.max_shaft_J_kg<=0 or not 0<p.efficiency<=1 or not 0<=p.ultimate_Pa<p.cutoff_Pa:raise ValueError('Invalid pump')
    y0=np.zeros(3*n+7)
    for i,(c,g) in enumerate(zip(chambers,geom)):
        m=c.initial_pressure_Pa*g['gas_m3']/(air.R*c.initial_gas_K)
        y0[3*i:3*i+3]=[m,m*air.at(c.initial_gas_K)[1]/1e6,g['mass_kg']*metals[i].energy(c.initial_metal_K)/1e6]
    def states(y):
        mass=np.maximum(y[:3*n:3],0.)
        T=np.array([air.temperature(y[3*i+1]*1e6/mass[i]) if mass[i]>1e-9 else chambers[i].initial_gas_K for i in range(n)])
        Tm=np.array([metals[i].temperature(y[3*i+2]*1e6/g['mass_kg']) if g['mass_kg'] else chambers[i].initial_metal_K for i,g in enumerate(geom)])
        rho=mass/np.array([g['gas_m3'] for g in geom]);pressure=rho*air.R*T
        return mass,T,Tm,rho,pressure
    def rates(t,y):
        m,T,Tm,rho,p=states(y);d=np.zeros_like(y);h=np.array([air.at(x)[0] for x in T]);cp=np.array([air.at(x)[2] for x in T]);gamma=cp/(cp-air.R)
        supply,support,hin=boundary.at(t)
        def port(up,down):
            if up<=down:return 0.
            eps=.001
            if up-down<eps*up:return port_flow(up,up*(1-eps),T[0],boundary.area,air.R,gamma[0],.8)*(up-down)/(eps*up)
            return port_flow(up,down,T[0],boundary.area,air.R,gamma[0],.8)
        admitted=min(supply,port(support,p[0]));leaked=port(p[0],support)
        d[0]+=admitted-leaked;d[1]+=(admitted*hin-leaked*h[0])/1e6
        d[3*n:3*n+4]=[admitted,leaked,0.,(admitted*hin-leaked*h[0])/1e6]
        flows=np.zeros(n-1);shaft=0.
        for i,pump in enumerate(pumps):
            if t>=pump.stop_s:continue
            work=air.compression(T[i],p[i],p[i+1],pump.efficiency)
            capacity=max(0.,1-(work/pump.max_shaft_J_kg)**2)
            # Smooth low-pressure cutoff avoids resetting inventories at shutdown.
            cutoff=np.clip((p[i]-pump.cutoff_Pa)/max(pump.cutoff_Pa,.01),0,1)
            f=pump.suction_m3_s*max(p[i]-pump.ultimate_Pa,0)/(air.R*T[i])*capacity*cutoff
            flows[i]=f;d[3*i]-=f;d[3*(i+1)]+=f
            d[3*i+1]-=f*h[i]/1e6;d[3*(i+1)+1]+=f*(h[i]+work)/1e6;shaft+=f*work
        withdrawn=cfg.withdrawal_kg_s*max(0.,1-cfg.withdrawal_floor_Pa/max(p[-1],1e-30)) if t>=cfg.withdrawal_start_s else 0.
        d[3*(n-1)]-=withdrawn;d[3*(n-1)+1]-=withdrawn*h[-1]/1e6
        d[3*n+2]=withdrawn;d[3*n+4]=shaft/1e6;d[3*n+5]=withdrawn*h[-1]/1e6
        heat=np.zeros(n);biot=np.zeros(n);radiated=0.
        for i,(c,g) in enumerate(zip(chambers,geom)):
            if not g['mass_kg']:continue
            flow=max(flows[i-1] if i else admitted+leaked,flows[i] if i<n-1 else withdrawn)
            flow=max(flow,rho[i]*g['frontal_m2']*c.coast_mixing_m_s)
            UA,ht=conductance(p[i],(T[i]+Tm[i])/2,flow,g['frontal_m2'],g,Racks(metal_conductivity_W_m_K=metals[i].conductivity),R=air.R,cp=cp[i])
            biot[i]=ht['Bi']
            heat[i]=UA*(T[i]-Tm[i]) if t<cfg.contact_stop_s else 0.
            exposed=np.clip((t-cfg.radiation_start_s)/cfg.radiation_ramp_s,0,1)
            emissivity=c.rack_emissivity if c.rack_emissivity is not None else (cfg.emissivity if c.material=="iron" else metals[i].emissivity)
            rad=exposed*emissivity*5.670374419e-8*c.external_emitting_m2*(Tm[i]**4-cfg.radiation_sink_K**4)
            d[3*i+1]-=heat[i]/1e6;d[3*i+2]+=(heat[i]-rad)/1e6;radiated+=rad
        d[3*n+6]=radiated/1e6
        return d,dict(admitted_kg_s=admitted,leaked_kg_s=leaked,withdrawal_kg_s=withdrawn,pump_kg_s=flows.tolist(),shaft_W=shaft,gas_to_metal_W=heat.tolist(),rack_Biot=biot.tolist())
    # Integrate discontinuous control schedules as separate continuous segments.
    breaks=sorted(set([cfg.start_s,cfg.end_s]+[x for x in [cfg.withdrawal_start_s,cfg.contact_stop_s,cfg.radiation_start_s,*[p.stop_s for p in pumps]] if cfg.start_s<x<cfg.end_s]))
    times=np.unique(np.r_[np.linspace(cfg.start_s,cfg.end_s,samples),breaks,0.]);times=times[(times>=cfg.start_s)&(times<=cfg.end_s)]
    yy=[];tt=[];current=y0
    for left,right in zip(breaks[:-1],breaks[1:]):
        def rhs(t,y):return rates(min(t,np.nextafter(right,left)),y)[0]
        def jac(t,y):
            # Ledger columns have exactly zero derivatives. Supplying them
            # explicitly avoids finite-difference step growth on passive states.
            base=rhs(t,y);J=np.zeros((len(y),len(y)))
            for j in range(3*n):
                delta=1e-6*max(abs(y[j]),1e-5)
                z=y.copy();z[j]+=delta;J[:,j]=(rhs(t,z)-base)/delta
            return J
        sol=solve_ivp(rhs,(left,right),current,method='BDF',jac=jac,rtol=cfg.rtol,atol=1e-10,max_step=cfg.max_step_s,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        selected=times[(times>=left)&(times<right if right<cfg.end_s else times<=right)]
        yy.extend(sol.sol(selected).T);tt.extend(selected);current=sol.y[:,-1]
    yy=np.array(yy);tt=np.array(tt);decoded=[states(y) for y in yy]
    mass,T,Tm,rho,p=[np.array([z[j] for z in decoded]) for j in range(5)]
    E=yy[:,1:3*n:3].sum(axis=1)+yy[:,2:3*n:3].sum(axis=1);L=yy[:,3*n:]
    mr=yy[:,:3*n:3].sum(axis=1)-y0[:3*n:3].sum()-L[:,0]+L[:,1]+L[:,2]
    er=E-E[0]-L[:,3]-L[:,4]+L[:,5]+L[:,6]
    diagnostics=[rates(t,y)[1] for t,y in zip(tt,yy)]
    return dict(inputs=dict(chambers=[asdict(c) for c in chambers],pumps=[asdict(p) for p in pumps],schedule=asdict(cfg)),geometry=geom,
        time_s=tt.tolist(),gas_mass_kg=mass.tolist(),gas_temperature_K=[[float(T[j,i]) if mass[j,i]>1e-8 else None for i in range(n)] for j in range(len(tt))],metal_temperature_K=Tm.tolist(),density_kg_m3=rho.tolist(),pressure_Pa=p.tolist(),
        diagnostics=diagnostics,ledger=dict(admitted_kg=L[:,0].tolist(),leaked_kg=L[:,1].tolist(),withdrawn_kg=L[:,2].tolist(),net_boundary_enthalpy_MJ=L[:,3].tolist(),shaft_work_MJ=L[:,4].tolist(),withdrawn_enthalpy_MJ=L[:,5].tolist(),radiated_MJ=L[:,6].tolist(),total_internal_MJ=E.tolist()),
        checks=dict(max_mass_residual_kg=float(abs(mr).max()),max_energy_residual_MJ=float(abs(er).max()),min_gas_mass_kg=float(yy[:,:3*n:3].min()),
          caloric_table_boundary_reached=bool(np.any(((T<=200.001)|(T>=14999.))&(mass>1e-8))),metal_outside_reference_range=bool(any(np.any((Tm[:,i]<297.99)|(Tm[:,i]>metals[i].limit_K)) for i,g in enumerate(geom) if g['mass_kg'])),
          significant_hot_molecular_gas=bool(np.any((T>2000)&(mass>.01)))) )
