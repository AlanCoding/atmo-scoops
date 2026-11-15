"""Continuous open-inlet encounter and finite-backflow compressor envelope.

The bidirectional cooled-port model is a reduced boundary, not shock CFD.
Pump limits and mass capabilities are engineering scenarios, not measured maps.
"""
from dataclasses import dataclass,asdict,replace
import math
import numpy as np
from scipy.integrate import solve_ivp
from .open_mouth import port_flow
from .encounter import orbit_state
from .thermochemistry import enthalpy,composition


@dataclass(frozen=True)
class FlowCapabilities:
    support_over_ram: float = 1.
    port_discharge_coefficient: float = .8
    effective_mouth_area_fraction: float = 1.
    ultimate_inlet_Pa: float = .03
    hot_train_max_compression: float = 1e6
    pump_idle_fraction: float = .05
    inlet_lag_s: float = 0.  # Uncalibrated support-response sensitivity only.
    rejected_air_impulse_fraction: float = 1.  # Of geometric intercepted momentum, while open.


@dataclass(frozen=True)
class EncounterControls:
    cutoff_Pa: float = .1
    suction_scale: float = 1.
    max_after_perigee_s: float = 1200.


def net_pump_rate(pressure,suction,ultimate,RT):
    """Finite-backflow envelope: S_eff/S_rated=max(1-p_ultimate/p,0)."""
    return suction*max(pressure-ultimate,0.)/RT


def validate(cap,control,c):
    for name,v in {**asdict(cap),**asdict(control)}.items():
        if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<0:
            raise ValueError(f'{name} must be finite and nonnegative')
    for k in ('support_over_ram','port_discharge_coefficient','effective_mouth_area_fraction'):
        if not 0<getattr(cap,k)<=1:raise ValueError(f'{k} must be in (0,1]')
    if cap.hot_train_max_compression<=1:raise ValueError('Compression ceiling must exceed one')
    if control.suction_scale<=0:raise ValueError('Pump capacity must be positive')
    if control.max_after_perigee_s<=0:raise ValueError('Positive time budget required')
    ultimate=max(cap.ultimate_inlet_Pa,c.intermediate_Pa/cap.hot_train_max_compression)
    if control.cutoff_Pa<=ultimate:raise ValueError('Cutoff must exceed the effective ultimate pressure')
    return ultimate


class ContinuousEncounter:
    def __init__(self,capabilities=FlowCapabilities(),controls=EncounterControls()):
        self.capabilities=capabilities;self.controls=controls;self.last=None
        self.injection_ratio=0.;self.injection_h=0.

    def __call__(self,c,o,atm,R,gamma,pumping,n):
        cap=self.capabilities;ctl=self.controls;ultimate=validate(cap,ctl,c)
        A=math.pi*c.mouth_m**2/4;V=math.pi*c.front_bore_m**2/4*c.front_length_m;RT=R*c.gas_K
        start=-float(o.time_at_altitude(200.));end=ctl.max_after_perigee_s
        if end>=o.period/2:raise ValueError('Encounter budget must end before apogee')
        # Common physical start; no perigee boundary-law switch.
        grid=np.unique(np.r_[np.linspace(start,end,max(n,401)),0.])
        state=orbit_state(o,grid,atm);supply=A*state['density_kg_m3']*state['speed_m_s']
        support=cap.support_over_ram*state['ram_Pa']
        incoming_h=np.array([enthalpy(float(T),composition(y))+.5*u*u for T,y,u in
            zip(state['temperature_K'],state['fractions'],state['speed_m_s'])])
        ox=state['fractions'][:,1]+state['fractions'][:,2]+state['fractions'][:,7]+state['fractions'][:,8]*15.9994/30.0061
        rated=pumping*ctl.suction_scale
        p_ref=c.inlet_pressure_fraction*float(orbit_state(o,0,atm)['ram_Pa'])
        idle=cap.pump_idle_fraction*rated*p_ref*max(0.,math.log(c.intermediate_Pa/p_ref))/c.isothermal_efficiency/c.motor_efficiency
        if ctl.cutoff_Pa>=float(support.max()):raise ValueError('Cutoff is above the supported pressure pulse')
        def rates(t,y):
            pressure=max(y[0],0.)*RT/V
            pext=max(0.,y[9]) if cap.inlet_lag_s>0 else float(np.interp(t,grid,support))
            area=A*cap.effective_mouth_area_fraction
            admission=min(float(np.interp(t,grid,supply)),
                port_flow(pext,pressure,c.gas_K,area,R,gamma,cap.port_discharge_coefficient))
            leakage=port_flow(pressure,pext,c.gas_K,area,R,gamma,cap.port_discharge_coefficient)
            suction=rated
            pumped=net_pump_rate(pressure,suction,ultimate,RT)
            gross=suction*pressure/RT if pressure>ultimate else 0.
            extra_work=(gross-pumped)*RT/c.isothermal_efficiency*max(0.,math.log(c.intermediate_Pa/max(pressure,1e-30)))
            # Equivalent upstream-facing nozzle momentum; this does not supply
            # the exterior body's missing pressure/shear forces.
            recoil=0.
            if leakage>0:
                r=max(pext/pressure,(2/(gamma+1))**(gamma/(gamma-1)))
                exit_T=c.gas_K*r**((gamma-1)/gamma)
                exhaust=math.sqrt(max(0.,2*gamma/(gamma-1)*R*(c.gas_K-exit_T)))
                recoil=leakage*exhaust+cap.port_discharge_coefficient*area*max(0.,pressure*r-pext)
            return admission,leakage,pumped,pressure,pext,extra_work,idle,recoil
        def rhs(t,y):
            admission,leakage,pump,_,_,_,_,recoil=rates(t,y)
            fraction=max(y[6],0.)/max(y[0],1e-30)
            lag=(np.interp(t,grid,support)-y[9])/cap.inlet_lag_s if cap.inlet_lag_s>0 else 0.
            return [(1+self.injection_ratio)*admission-leakage-pump,pump,admission,leakage,
                admission*(np.interp(t,grid,incoming_h)+self.injection_ratio*self.injection_h),admission*np.interp(t,grid,state['speed_m_s']),
                admission*np.interp(t,grid,ox)-(leakage+pump)*fraction,pump*fraction,recoil,lag]
        def stop(t,y):
            # Pump starts from an empty front chamber; do not falsely terminate
            # at startup. Cutoff is a downward crossing on the outbound leg.
            return 1. if t<0 else y[0]*RT/V-ctl.cutoff_Pa
        stop.terminal=True;stop.direction=-1
        y0=np.zeros(10);y0[9]=support[0]
        breaks=[start,0.,end]
        breaks=sorted(set(breaks));segments=[];reason='time_limit'
        for a,b in zip(breaks[:-1],breaks[1:]):
            if a>=0 and y0[0]*RT/V<=ctl.cutoff_Pa:
                reason='cutoff_pressure';break
            sol=solve_ivp(rhs,(a,b),y0,method='LSODA',rtol=2e-8,atol=1e-10,
                          events=stop if a>=0 else None,dense_output=True,max_step=4.)
            if not sol.success:raise ValueError(sol.message)
            segments.append(sol);y0=sol.y[:,-1]
            if a>=0 and len(sol.t_events[0]):reason='cutoff_pressure';break
        if not segments:raise ValueError('No encounter integration')
        # Include accepted adaptive steps and uniform samples: short reversals
        # and actuation transitions must remain visible in plots/quadratures.
        all_t=[];all_y=[]
        for sol in segments:
            tt=np.unique(np.r_[sol.t,np.linspace(sol.t[0],sol.t[-1],max(12,n//len(segments)))])
            all_t.extend(tt);all_y.extend(sol.sol(tt).T)
        tt=np.array(all_t);ys=np.array(all_y).T
        unique=np.r_[True,np.diff(tt)>1e-10];tt=tt[unique];ys=ys[:,unique]
        flows=np.array([rates(t,y) for t,y in zip(tt,ys.T)]).T
        if not np.any(np.isclose(tt,0,atol=1e-12)):raise ValueError('Perigee sample missing')
        k=int(np.flatnonzero(np.isclose(tt,0,atol=1e-12))[0]);pre=slice(0,k+1);post=slice(k,None)
        def pack(mask):
            return dict(time=tt[mask],front=ys[0,mask],rear=ys[1,mask],admitted=ys[2,mask],
                leakage=ys[3,mask],energy=ys[4,mask],impulse=ys[5,mask],
                admission_rate=flows[0,mask],leakage_rate=flows[1,mask],pump_rate=flows[2,mask],
                extra_hot_work=flows[5,mask],idle_electric=flows[6,mask],
                incoming_h=np.interp(tt[mask],grid,incoming_h))
        out=dict(pre=pack(pre),post=pack(post),retained_oxygen=float(ys[7,-1]),
            rated_suction=rated,stop_reason=reason,ultimate_Pa=ultimate,
            total_energy=float(ys[4,-1]),capture_impulse=float(ys[5,-1]),escape_impulse=float(ys[8,-1]),
            total_leak=float(ys[3,-1]),final_pressure=float(flows[3,-1]),
            coefficients=asdict(cap),controls=asdict(ctl),
            history=dict(time_s=tt.tolist(),front_Pa=flows[3].tolist(),support_Pa=flows[4].tolist(),
                admission_kg_s=flows[0].tolist(),leakage_kg_s=flows[1].tolist(),pump_kg_s=flows[2].tolist(),
                admitted_kg=ys[2].tolist(),leaked_kg=ys[3].tolist(),front_kg=ys[0].tolist(),rear_kg=ys[1].tolist()))
        # Intercepted but uncollected gas still contributes a declared drag allowance.
        drag_end=max(-start,float(tt[-1]))
        drag_t=np.linspace(start,drag_end,4001)
        drag_state=orbit_state(o,drag_t,atm)
        geometric=A*drag_state['density_kg_m3']*drag_state['speed_m_s']**2
        impulse=float(np.trapezoid(geometric,drag_t))
        out['uncollected_mouth_impulse']=cap.rejected_air_impulse_fraction*max(0.,impulse-out['capture_impulse'])
        out['geometric_intercept_impulse']=impulse
        self.last=out
        return out

