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
    port_linearization_fraction: float = 1e-3  # Numerical regularization near equal pressures.
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


def validate(cap,control,c,compressor_spec=None):
    for name,v in {**asdict(cap),**asdict(control)}.items():
        if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<0:
            raise ValueError(f'{name} must be finite and nonnegative')
    for k in ('support_over_ram','port_discharge_coefficient','effective_mouth_area_fraction'):
        if not 0<getattr(cap,k)<=1:raise ValueError(f'{k} must be in (0,1]')
    if cap.port_linearization_fraction>=.1:raise ValueError('Port numerical smoothing must remain below 0.1')
    if cap.hot_train_max_compression<=1:raise ValueError('Compression ceiling must exceed one')
    if control.suction_scale<=0:raise ValueError('Pump capacity must be positive')
    if control.max_after_perigee_s<=0:raise ValueError('Positive time budget required')
    ultimate=cap.ultimate_inlet_Pa if compressor_spec else max(cap.ultimate_inlet_Pa,c.intermediate_Pa/cap.hot_train_max_compression)
    if control.cutoff_Pa<=ultimate:raise ValueError('Cutoff must exceed the effective ultimate pressure')
    return ultimate


class ContinuousEncounter:
    def __init__(self,capabilities=FlowCapabilities(),controls=EncounterControls()):
        self.capabilities=capabilities;self.controls=controls;self.last=None
        self.injection_ratio=0.;self.injection_h=0.

    def __call__(self,c,o,atm,R,gamma,pumping,n):
        cap=self.capabilities;ctl=self.controls;ultimate=validate(cap,ctl,c,getattr(self,'compressor_spec',None))
        A=math.pi*c.mouth_m**2/4;V=math.pi*c.front_bore_m**2/4*c.front_length_m;RT=R*c.gas_K
        thermal=getattr(self,'rack_context',None)
        if thermal:
            from .racks import conductance
            geom=thermal['geometry'];metal=thermal['metal'];rack_spec=thermal['spec']
            V-=geom['solid_m3']
            if V<=0:raise ValueError('Metal solid exceeds front chamber')
            def temperatures(y):
                Tg=float(np.interp(y[10]*1e6/max(y[0],1e-30),thermal['u'],thermal['T']))
                Ts=metal.surface_temperature(y[11],y[14]) if hasattr(metal,'pcm') else metal.temperature(y[11])
                return Tg,Ts
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
        def port(up,down,T,area):
            eps=cap.port_linearization_fraction
            if thermal and eps>0 and up>down and (up-down)<up*eps:
                edge=port_flow(up,up*(1-eps),T,area,R,gamma,cap.port_discharge_coefficient)
                return edge*(up-down)/(up*eps)
            return port_flow(up,down,T,area,R,gamma,cap.port_discharge_coefficient)
        def rates(t,y):
            Tg,Ts=temperatures(y) if thermal else (c.gas_K,0.)
            localRT=R*Tg
            pressure=max(y[0],0.)*localRT/V
            pext=max(0.,y[9]) if cap.inlet_lag_s>0 else float(np.interp(t,grid,support))
            area=A*cap.effective_mouth_area_fraction
            admission=min(float(np.interp(t,grid,supply)),
                port(pext,pressure,Tg,area))
            leakage=port(pressure,pext,Tg,area)
            suction=rated
            spec=getattr(self,'compressor_spec',None)
            floor=max(ultimate,max(y[1],0.)*R*c.receiver_K/c.receiver_m3/spec.head_limit_ratio) if spec else ultimate
            pumped=net_pump_rate(pressure,suction,floor,localRT)
            gross=suction*pressure/localRT if pressure>floor else 0.
            extra_work=(gross-pumped)*RT/c.isothermal_efficiency*max(0.,math.log(c.intermediate_Pa/max(pressure,1e-30)))
            # Equivalent upstream-facing nozzle momentum; this does not supply
            # the exterior body's missing pressure/shear forces.
            recoil=0.
            if leakage>0:
                r=max(pext/pressure,(2/(gamma+1))**(gamma/(gamma-1)))
                exit_T=Tg*r**((gamma-1)/gamma)
                exhaust=math.sqrt(max(0.,2*gamma/(gamma-1)*R*(Tg-exit_T)))
                recoil=leakage*exhaust+cap.port_discharge_coefficient*area*max(0.,pressure*r-pext)
            return admission,leakage,pumped,pressure,pext,extra_work,idle,recoil,floor
        calls=[0]
        def rhs(t,y):
            calls[0]+=1
            if calls[0]>200000:raise ValueError(f'Encounter integration stalled at {t:g} seconds, {temperatures(y) if thermal else None}, {rates(t,y)}, mass {y[0]}')
            admission,leakage,pump,_,_,_,_,recoil,_=rates(t,y)
            fraction=max(y[6],0.)/max(y[0],1e-30)
            lag=(np.interp(t,grid,support)-y[9])/cap.inlet_lag_s if cap.inlet_lag_s>0 else 0.
            result=[(1+self.injection_ratio)*admission-leakage-pump,pump,admission,leakage,
                admission*(np.interp(t,grid,incoming_h)+self.injection_ratio*self.injection_h),admission*np.interp(t,grid,state['speed_m_s']),
                admission*np.interp(t,grid,ox)-(leakage+pump)*fraction,pump*fraction,recoil,lag]
            if thermal:
                Tg,Ts=temperatures(y);p=max(y[0],0.)*R*Tg/V
                cp=float(np.interp(Tg,thermal['T'],thermal['cp']))
                UA,exchange_detail=conductance(p,(Tg+Ts)/2,max((1+self.injection_ratio)*admission,pump+leakage),A,geom,rack_spec,R,cp)
                heat=UA*(Tg-Ts)
                h=float(np.interp(Tg,thermal['T'],thermal['h']))
                incoming=admission*(np.interp(t,grid,incoming_h)+self.injection_ratio*self.injection_h)
                result.extend([(incoming-(pump+leakage)*h-heat)/1e6,heat/geom['mass_kg'],pump*h/1e6,leakage*h/1e6])
                if hasattr(metal,'pcm'):result.append(metal.core_rate(y[11],y[14],geom))
                if hasattr(metal,'liquid'):result.extend([exchange_detail['liquid_flow_kg_s'],exchange_detail['liquid_pump_W']/1e6])
            return result
        def thermal_jac(t,y):
            # Only six states feed back into rates. Explicit differencing avoids
            # SciPy's step-growth overflow on the identically zero ledger columns.
            J=np.zeros((len(y),len(y)))
            for k in ((0,1,6,9,10,11,14) if hasattr(metal,'pcm') else (0,1,6,9,10,11)):
                step=1e-8*max(abs(y[k]),1e-9 if k in (0,6,10) else 1e-3)
                yy=y.copy();yy[k]+=step
                zz=y.copy();zz[k]-=step
                J[:,k]=(np.asarray(rhs(t,yy))-np.asarray(rhs(t,zz)))/(2*step)
            return J
        def stop(t,y):
            # Pump starts from an empty front chamber; do not falsely terminate
            # at startup. Cutoff is a downward crossing on the outbound leg.
            return 1. if t<0 else rates(t,y)[3]-ctl.cutoff_Pa
        stop.terminal=True;stop.direction=-1
        y0=np.zeros((16 if hasattr(metal,'liquid') else 15 if hasattr(metal,'pcm') else 14) if thermal else 10);y0[9]=support[0]
        if thermal:
            # Tiny seed avoids U/m at exactly zero; explicitly reported in balances.
            y0[0]=1e-9
            y0[10]=y0[0]*float(np.interp(metal.cold,thermal['T'],thermal['u']))/1e6
            y0[11]=metal.hcold
            if hasattr(metal,'pcm'):y0[14]=metal.hcore_cold
        breaks=[start,0.,end]
        breaks=sorted(set(breaks));segments=[];reason='time_limit'
        for a,b in zip(breaks[:-1],breaks[1:]):
            if a>=0 and rates(a,y0)[3]<=ctl.cutoff_Pa:
                reason='cutoff_pressure';break
            sol=solve_ivp(rhs,(a,b),y0,method='Radau' if thermal else 'LSODA',rtol=2e-6 if thermal else 2e-8,atol=1e-9 if thermal else 1e-10,
                          events=stop if a>=0 else None,dense_output=True,max_step=4.,
                          jac=thermal_jac if thermal else None)
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
            extra={}
            if thermal:
                temps=np.array([temperatures(y) for y in ys[:,mask].T])
                extra=dict(gas_temperature=temps[:,0],metal_temperature=temps[:,1],
                    gas_energy=ys[10,mask]*1e6,metal_energy=ys[11,mask]*geom['mass_kg'],pressure=flows[3,mask])
            return dict(time=tt[mask],front=ys[0,mask],rear=ys[1,mask],admitted=ys[2,mask],
                leakage=ys[3,mask],energy=ys[4,mask],impulse=ys[5,mask],
                admission_rate=flows[0,mask],leakage_rate=flows[1,mask],pump_rate=flows[2,mask],
                extra_hot_work=flows[5,mask],idle_electric=flows[6,mask],
                pump_floor=flows[8,mask],
                incoming_h=np.interp(tt[mask],grid,incoming_h),**extra)
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
        if thermal:
            out['thermal']=dict(initial_mass_kg=1e-9,
                initial_energy_J=1e-9*float(np.interp(metal.cold,thermal['T'],thermal['u'])),
                pumped_enthalpy_J=float(ys[12,-1]*1e6),leaked_enthalpy_J=float(ys[13,-1]*1e6),front_gas_m3=V,geometry=geom,
                absorbed_J=float((ys[11,-1]-metal.hcold)*geom['mass_kg']),
                final_gas_energy_J=float(ys[10,-1]*1e6),
                max_metal_K=max(temperatures(y)[1] for y in ys.T))
        if thermal and hasattr(metal,'liquid'):
            details=[]
            for sample_time,yy in zip(tt,ys.T):
                Tg,Ts=temperatures(yy);ad,le,pu,pr,*_=rates(sample_time,yy)
                cp=float(np.interp(Tg,thermal['T'],thermal['cp']))
                _,dd=conductance(pr,(Tg+Ts)/2,max((1+self.injection_ratio)*ad,pu+le),A,geom,rack_spec,R,cp)
                details.append(dd)
            out['thermal'].update(liquid_used_kg=float(ys[14,-1]),liquid_pump_J=float(ys[15,-1])*1e6,
                liquid_peak_flow_kg_s=max(d['liquid_flow_kg_s'] for d in details),
                liquid_peak_pump_W=max(d['liquid_pump_W'] for d in details),
                liquid_max_wall_K=max(d['liquid_wall_K'] for d in details),
                liquid_max_dp_Pa=max(d['liquid_dp_Pa'] for d in details))
        if thermal and hasattr(metal,'pcm'):
            out['thermal'].update(final_core_h_J_kg=float(ys[14,-1]),
                max_core_K=max(metal.pcm.temperature(h) for h in ys[14]),
                max_melt_fraction=max(metal.pcm.melt_fraction(h) for h in ys[14]))
        self.last=out
        return out

