"""Centered constant-thrust duration aside; frozen collection and duty windows.

Not a coupled spacecraft/cycle optimization. Reuses first-order steered arcs.
"""
from pathlib import Path
import json,math,os
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.integrate import solve_ivp
from ..orbit import Orbit,MU
from ..reboost import arc_restore,state_at
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/reboost/burn_duration'
DOC=ROOT/'investigations/reboost'

def penalty(orbit,duration,samples=2001):
 if not 0<duration<orbit.period:raise ValueError('Burn duration must fit within one orbit')
 return arc_restore(orbit,0.,duration/2,samples=samples)

def orbit_check(orbit,duration,dv=.1):
 """Independent planar Newtonian propagation: drag impulse applied exactly once."""
 arc=penalty(orbit,duration,8001);lam=arc['steering_lagrange_multiplier'];vp=orbit.h/orbit.rp
 def reference(t):
  r,vr,vt=[float(z[0]) for z in state_at(orbit,np.array([t]))]
  f=math.atan2(vr*orbit.h/(MU*orbit.e),(orbit.h**2/(MU*r)-1)/orbit.e)
  er=np.array([math.cos(f),math.sin(f)]);et=np.array([-math.sin(f),math.cos(f)])
  return r,vr,vt,er,et
 def invariants(y):
  x=y[:2];v=y[2:];r=np.linalg.norm(x);E=np.dot(v,v)/2-MU/r;h=np.cross(np.r_[x,0],np.r_[v,0])[2]
  evec=((np.dot(v,v)-MU/r)*x-np.dot(x,v)*v)/MU
  return E,h,math.atan2(evec[1],evec[0])
 r,vr,vt,er,et=reference(-duration/2);y=np.r_[r*er,vr*er+vt*et];initial=invariants(y)
 acceleration=dv*arc['impulse_multiplier']/duration
 def rhs(t,y):
  r,vr,vt,er,et=reference(t);ar=lam*vr/vp;at=r/orbit.rp+lam*(vt/vp-r/orbit.rp)
  acc=-MU*y[:2]/np.linalg.norm(y[:2])**3+acceleration*(ar*er+at*et)/math.hypot(ar,at)
  return np.r_[y[2:],acc]
 for left,right in [(-duration/2,0.),(0.,duration/2)]:
  if left==0:y[3]-=dv
  sol=solve_ivp(rhs,(left,right),y,method='DOP853',rtol=2e-12,atol=1e-8,max_step=5.)
  if not sol.success:raise RuntimeError(sol.message)
  y=sol.y[:,-1]
 E,h,w=invariants(y)
 return dict(dv_m_s=dv,energy_residual_relative_drag=(E-initial[0])/(vp*dv),angular_residual_relative_drag=(h-initial[1])/(orbit.rp*dv),apsidal_change_deg=math.degrees(w-initial[2]))

def budget(duration,anchor,audit):
 o=anchor['outputs'];inp=anchor['inputs'];p=inp['performance'];hw=inp['hardware'];pr=inp['process'];d=inp['design'];orbit=Orbit(d['perigee_km'],d['apogee_km'])
 arc=penalty(orbit,duration);K=arc['impulse_multiplier'];m=audit['parts_kg'].copy();m.pop('design_margin')
 E=audit['propulsion']['electric_GJ']*1e9;delta=(K-1)*E;P=K*E/duration
 m['propulsion_hardware']=P/1000*hw['thruster_kg_kW']
 m['solar']+=delta/(p['battery_charge_efficiency']*p['battery_discharge_efficiency']*o['cycle']['sunlit_s']*p['solar_W_kg'])
 m['battery']=max(m['battery']+delta/(p['battery_discharge_efficiency']*3600*p['battery_Wh_kg']*p['battery_usable']),(P+o['compressor_peak_MW']*1e6+p['auxiliary_W'])/p['battery_W_kg'])
 m['power_distribution']=max(P+o['compressor_peak_MW']*1e6+p['auxiliary_W'],m['solar']*p['solar_W_kg'])/1000*hw['distribution_kg_kW']
 retained=(1-p['thruster_efficiency'])*p['thruster_loss_retained']
 m['warm_buffer']+=delta*(retained+1/p['battery_discharge_efficiency']-1)/p['warm_buffer_J_kg']
 flux=pr['emissivity']*pr['view_factor']*5.670374419e-8*d['warm_radiator_K']**4-pr['environment_W_m2']
 m['warm_radiator']+=delta*(retained+1/(p['battery_discharge_efficiency']*p['battery_charge_efficiency'])-1)/o['cycle']['deployed_s']/flux*pr['radiator_kg_m2']
 m['design_margin']=sum(m.values())*hw['design_margin'];dry=sum(m.values())
 prop=audit['propulsion']['propellant_kg']*K
 batch=audit['propulsion']['net_kg']+audit['propulsion']['propellant_kg'];net=batch-prop
 return dict(duration_s=duration,impulse_multiplier=K,quadratic_multiplier=1+MU/orbit.rp**3*duration**2/24,power_GW=P/1e9,electric_GJ=E*K/1e9,propellant_kg=prop,net_kg=net,dry_t=dry/1000,proxy_days=dry/net*orbit.period/86400 if net>0 else 1e12,arc=arc,masses_kg=m)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 a=json.loads((ROOT/'results/reboost/solid_isp_optimum_1601.json').read_text());audit=json.loads((ROOT/'results/chamber_materials/mass_audit.json').read_text());orbit=Orbit(85,2000)
 rows=[budget(t,a,audit) for t in (60,300,600,900,1200,1800,2400,3000)]
 opt=minimize_scalar(lambda t:budget(t,a,audit)['proxy_days'],bounds=(120.,5000.),method='bounded',options={'xatol':.02})
 best=budget(float(opt.x),a,audit)
 check=orbit_check(orbit,best['duration_s']);refined=penalty(orbit,best['duration_s'],16001)
 assert abs(check['energy_residual_relative_drag'])<1e-3
 assert abs(check['angular_residual_relative_drag'])<1e-3
 data=dict(anchor='results/reboost/solid_isp_optimum_1601.json',mass_ledger='results/chamber_materials/mass_audit.json',rows=rows,best=best,orbit_check=check,refined_impulse_multiplier=refined['impulse_multiplier'],scope='Fixed-Isp, fixed-collection, fixed-duty, battery-fed centered burns; no new coupled payoff')
 (OUT/'comparison.json').write_text(json.dumps(data,indent=2)+'\n')
 text='''# Centered reboost duration: orbital penalty versus installed mass

**Isolated screening calculation, not a new coupled spacecraft result.** The old
300 s battery-fed burst was a fixed assumption, not an optimized duration. This
aside uses the existing 85 × 2000 km orbit, 1765.95 s Isp and the SiC/aluminum
proxy ledger. It does not evaluate the new fixed-L/D 317 m craft.

## Orbital penalty

Let tau be the **total** burn duration, centered on perigee, with constant thrust
magnitude and optimal in-plane steering. Approximate atmospheric momentum loss
by a perigee impulse J0. Let `K(tau) = required_total_impulse/J0`; this is an
orbital impulse multiplier, not a change in the thruster's electrical efficiency.

```
u = g0*Isp
propellant = J0*K/u
propulsion electricity = J0*K*u/(2*eta_thruster)
constant-burn electric power = J0*K*u/(2*eta_thruster*tau)
```

Both orbital energy and angular momentum must be restored. Symmetric radial
steering cancels the first-order apsidal change. Define along the unperturbed
orbit `ar=vr/vp`, `at=vt/vp`, and `b=r/rp`. For radial/tangential thrust direction
components `(ur,ut)`, the two efficiencies are

```
eta_E = average(ar*ur + at*ut)
eta_h = average(b*ut)
require eta_E = eta_h; maximize their common value; K = 1/eta_h.
```

The constant-magnitude optimum has direction proportional to
`(lambda*ar, b + lambda*(at-b))`. One scalar multiplier enforces equal energy and
angular-momentum restoration. Existing `reboost.arc_restore` evaluates this cheap
Kepler quadrature; it is not another full spacecraft simulation or an inner
cycle-closure iteration. This function may be tabulated as a reduced penalty
map over orbit and duration.

For a short centered burn, expansion around perigee gives

```
K(tau) = 1 + mu*tau²/(24*rp³) + O(tau⁴).
```

To leading order the steering angle from local prograde is `theta(t) ~ vp*t/rp`:
outward after perigee, inward before it. With `k=mu/rp³`, expanding both invariants
under that steering gives the same loss `k*average(t²)/2 = k*tau²/24`.
The exact quadrature should replace the quadratic at longer durations; the
quadratic is a near-perigee explanation, not a global fit or a universal law for
arbitrary thrust profiles/drag histories.

| Total burn, min | Impulse multiplier K | Peak power, GW | Maximum steering from local prograde, deg | Frozen-budget proxy days |
|---|---:|---:|---:|---:|
'''
 for r in rows:
  text+=f"| {r['duration_s']/60:.1f} | {r['impulse_multiplier']:.5f} | {r['power_GW']:.3f} | {r['arc']['steering_max_deg']:.1f} | {r['proxy_days']:.1f} |\n"
 text+=f'''
The short-burn coefficient here is **{MU/orbit.rp**3/24:.4g} s^-2**.
Five minutes costs only about 0.55% more impulse than an ideal perigee impulse;
its important penalty is the installed GW rating, not a large orbital loss.
Twenty minutes costs about 7.9% more impulse but cuts peak power to about 27%
of the old impulse-equivalent 300 s rating.

## A conditional mass/payoff optimum

Holding Isp and the captured/processed batch fixed, the one-variable minimum is
approximately **{best['duration_s']/60:.2f} minutes**, with **{best['impulse_multiplier']:.4f}× impulse**,
**{best['power_GW']:.3f} GW**, **{best['dry_t']:,.0f} t** proxy dry mass and
**{best['proxy_days']:.1f} proxy days**. Compare the finite-arc-corrected five-minute
case above, rather than silently calling the old impulsive 373-day case exact.

The calculation resizes thrusters and the shared bus from peak power. It also
charges additional propellant, battery energy, solar recharge energy, retained
thruster heat, battery losses, warm buffer and radiator heat, and reapplies the
existing margin once. Battery energy/power requirements are compared. Capture,
racks, compressor hardware, processing package, ordinary packaging and sunlight/
coast windows remain fixed. All propulsion energy is still charged through the
battery: no direct-solar thrust credit is introduced.

Schematically, before ratings/limits change branches, mass has the form
`M(tau) = A + B*K(tau)/tau + C*K(tau)` and useful mass is
`batch - (J0/u)*K(tau)`. This is the hardware-versus-energy/propellant trade the
300 s assumption omitted. Optimizing only thruster mass would favor much longer
burns and miss the energy and product penalties.

## Limitations and checks

This is not the final coupled payoff: the changing burn overlaps deployment and
processing, may require gimbal/attitude/plume accommodations, changes component
packing and propellant-reserve storage, and may affect battery/radiator thermal
schedules. Those effects are not fully resized here. At the selected burn
endpoints the steering is about {best['arc']['steering_max_deg']:.1f} degrees and altitude
about {best['arc']['altitude_end_km']:.0f} km. Distributed atmospheric drag should supply
the actual target energy/impulse/angular-momentum change in the coupled model.
Finite-gas-flow and mass-changing orbit propagation are not solved by the penalty.
Isp must ultimately be co-optimized, not held permanently at the earlier optimum.

An independent planar Newtonian trajectory with a single 0.1 m/s perigee drag
impulse checks the small-perturbation restoration: relative energy residual
{check['energy_residual_relative_drag']:.3g}, relative angular-momentum residual
{check['angular_residual_relative_drag']:.3g}, apsidal change
{check['apsidal_change_deg']:.3g} degrees. Refining orbital quadrature from 2,001 to
16,001 half-arc samples changes K by
{abs(refined['impulse_multiplier']-best['impulse_multiplier']):.3g}.
These validate the reduced orbital calculation, not the whole design.

## Disposition

**Release burn duration as an outer design variable.** Keep a symmetric centered
constant-magnitude burn family initially and use the orbital penalty/steering
relation for screening. Integrate its actual power/heat/inventory history in the
coupled model, with restoration constraints. Treat 300 s as a comparison point,
not a fixed design requirement; the approximately 20-minute optimum is a seed,
not a prescribed answer.

Reproduce with `.venv/bin/python -m atmo_scoops.studies.burn_duration`.
Inputs, ledgers and checks: `results/reboost/burn_duration/comparison.json`.
Related: [prior separated solar-arc study](SOLAR_ARCS.md),
[propulsion equations and references](../../modeling/propulsion/REBOOST_INVESTIGATIONS.md).
'''
 os.environ.setdefault('MPLCONFIGDIR','/tmp/atmo-burn-mpl')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 curve=[budget(float(t),a,audit) for t in np.linspace(120,3000,160)]
 minutes=np.array([z['duration_s']/60 for z in curve])
 fig,axes=plt.subplots(1,2,figsize=(11,4.3))
 axes[0].plot(minutes,[(z['impulse_multiplier']-1)*100 for z in curve],color='tab:orange');axes[0].set(xlabel='Total centered burn (minutes)',ylabel='Additional impulse (%)',title='Orbital penalty with restoring steering')
 axes[1].plot(minutes,[z['proxy_days'] for z in curve]);axes[1].scatter([best['duration_s']/60],[best['proxy_days']],color='tab:red',zorder=5,label=f"Best sampled family: {best['duration_s']/60:.1f} min, {best['proxy_days']:.0f} days")
 axes[1].set(xlabel='Total centered burn (minutes)',ylabel='Conditional proxy payoff (days)',title='Power hardware versus energy and product');axes[1].set_ylim(240,600);axes[1].legend(fontsize=8)
 for ax in axes:ax.grid(alpha=.2);ax.axvline(5,color='.5',ls='--',lw=1)
 fig.text(.5,.01,'Fixed collection, Isp and duty windows; not a coupled spacecraft result. Dashed line: former 5-minute assumption.',ha='center',fontsize=9)
 fig.tight_layout(rect=(0,.05,1,1));fig.savefig(DOC/'burn_duration.png',dpi=160);plt.close(fig)
 text+='\n![Duration penalty and conditional payoff](burn_duration.png)\n'
 (DOC/'BURN_DURATION.md').write_text(text)
 print(json.dumps(dict(best=best,check=check),indent=2))
if __name__=='__main__':main()
