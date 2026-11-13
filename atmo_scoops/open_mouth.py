"""Reduced post-perigee open-boundary model, NOT a fluid/shock simulation.

An effective pressure boundary and ideal-gas port law expose assumptions that
offline fluid studies can replace. Inbound prescribed capture remains the same
as in the sealed case. Outbound supply is limited by geometric interception.
"""
import math
import numpy as np
from scipy.integrate import solve_ivp


def port_flow(upstream_Pa, downstream_Pa, temperature_K, area_m2, gas_R, gamma, cd):
    """Positive reservoir-to-backpressure flow, including sonic choking (kg/s)."""
    if upstream_Pa <= downstream_Pa or upstream_Pa <= 0:
        return 0.
    ratio=max(0.,downstream_Pa/upstream_Pa)
    critical=(2/(gamma+1))**(gamma/(gamma-1))
    if ratio <= critical:
        factor=math.sqrt(gamma)*(2/(gamma+1))**((gamma+1)/(2*(gamma-1)))
    else:
        factor=math.sqrt(max(0.,2*gamma/(gamma-1)*
            (ratio**(2/gamma)-ratio**((gamma+1)/gamma))))
    return cd*area_m2*upstream_Pa/math.sqrt(gas_R*temperature_K)*factor


def recover_open(time, supply, support_Pa, incoming_h, speed, initial_front,
                 initial_rear, suction, volume, area, gas_R, temperature,
                 gamma, cd, minimum_Pa, oxygen_fraction, initial_oxygen_fraction):
    """Integrate admission, reverse flow and pumping until inlet floor or timeout.

    State integrals keep independent mass, incoming energy and impulse accounts.
    Boundary support pressure is a scenario input, not computed stagnation
    pressure. The inlet port uses the precooled gas state: no inlet energy or
    shock solution is implied by its flow-capacity screen.
    """
    RT=gas_R*temperature
    def rates(ti,m):
        p=max(0.,m)*RT/volume
        lid=float(np.interp(ti,time,support_Pa))
        admission=min(float(np.interp(ti,time,supply)),
            port_flow(lid,p,temperature,area,gas_R,gamma,cd))
        leak=port_flow(p,lid,temperature,area,gas_R,gamma,cd)
        pump=suction*max(0.,m)/volume
        return admission,leak,pump
    def rhs(ti,y):
        admission,leak,pump=rates(ti,y[0])
        ox=max(0.,y[6])/max(y[0],1e-30)
        return [admission-leak-pump,pump,admission,leak,
                admission*np.interp(ti,time,incoming_h),
                admission*np.interp(ti,time,speed),
                admission*np.interp(ti,time,oxygen_fraction)-(leak+pump)*ox,pump*ox]
    def floor(ti,y):return y[0]*RT/volume-minimum_Pa
    floor.terminal=True;floor.direction=-1
    y0=[initial_front,initial_rear,0.,0.,0.,0.,
        initial_front*initial_oxygen_fraction,initial_rear*initial_oxygen_fraction]
    if floor(0,y0)<=0:
        ts=np.array([0.,0.]);ys=np.array([y0,y0]).T;reason='inlet_pressure_floor'
    else:
        sol=solve_ivp(rhs,(time[0],time[-1]),y0,method='LSODA',events=floor,
            dense_output=True,rtol=2e-9,atol=1e-9,max_step=(time[-1]-time[0])/200)
        if not sol.success:raise ValueError(f'Open-mouth inventory failed: {sol.message}')
        # Resolve fast initial pressure relaxation as well as the full pass.
        # Uniform samples can hide a leakage burst between the first two points.
        ts=np.unique(np.r_[np.linspace(0,sol.t[-1],len(time)),
            np.geomspace(min(1e-6,sol.t[-1]),min(5.,sol.t[-1]),121)])
        ys=sol.sol(ts)
        reason='inlet_pressure_floor' if len(sol.t_events[0]) else 'recovery_time_limit'
    flows=np.array([rates(ti,m) for ti,m in zip(ts,ys[0])])
    if ts[-1]==0:flows[:]=0
    return dict(time=ts,front=ys[0],rear=ys[1],admitted=ys[2],leaked=ys[3],
        incoming_energy=ys[4],impulse=ys[5],admission_rate=flows[:,0],
        leakage_rate=flows[:,1],pump_rate=flows[:,2],stop_reason=reason,
        retained_oxygen=float(ys[7,-1]))
