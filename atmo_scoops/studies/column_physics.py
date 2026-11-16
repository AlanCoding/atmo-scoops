"""Reproducible atmospheric-column dimensional analysis; no vehicle search.

The ideal N2-equivalent gas constant is explicit. Density normalization is tested
without changing the atmosphere or cycle model. Generates the academic note.
"""
import json
import math
from pathlib import Path
import numpy as np
from ..atmosphere import make_profile
from ..encounter import orbit_state, pressure_window
from ..orbit import Orbit

R_GAS=296.8  # J/(kg K), nitrogen-equivalent ideal-gas proxy for this derivation.


def column(perigee,apogee,fraction=.5,kappa=.7,temperature=1000.,n=8001,density_scale=1.):
    atm=make_profile('reference');o=Orbit(perigee,apogee)
    edge,_=pressure_window(o,atm,fraction)
    t=np.linspace(-edge,0,n);s=orbit_state(o,t,atm);peak=orbit_state(o,0.,atm)
    rho=np.asarray(s['density_kg_m3'])*density_scale
    rho_p=float(peak['density_kg_m3'])*density_scale;u=float(peak['speed_m_s'])
    sigma=float(np.trapezoid(rho*s['speed_m_s'],t));q=.5*rho_p*u*u
    path=float(np.trapezoid(s['speed_m_s'],t));effective=sigma/rho_p
    pressure=2*kappa*q;confined_density=pressure/(R_GAS*temperature)
    ratio=confined_density/rho_p;depth=sigma/confined_density
    area=math.pi*18.3**2/4
    return dict(perigee_km=perigee,apogee_km=apogee,opening_ram_fraction=fraction,
        kappa_pressure_over_rho_u2=kappa,gas_R_J_kg_K=R_GAS,confined_temperature_K=temperature,
        density_scale=density_scale,orbit_period_s=o.period,inbound_s=edge,
        geometric_path_m=path,column_kg_m2=sigma,effective_column_m=effective,
        perigee_density_kg_m3=rho_p,perigee_speed_m_s=u,dynamic_pressure_Pa=q,
        confinement_pressure_Pa=pressure,confined_density_kg_m3=confined_density,
        density_compression_ratio=ratio,equal_area_required_depth_m=depth,
        mass_through_18_3m_mouth_kg=area*sigma,peak_equivalent_fill_s=effective/u,
        constant_peak_fill_time_500m_s=500*ratio/u)


def main():
    base=column(100,2000)
    rows=[base,column(100,2000,.1),column(90,937.1912423634607,.1,.8)]
    thermal=[column(100,2000,temperature=T) for T in (300.,710.,1000.)]
    altitude=[column(h,2000) for h in (90.,100.,110.)]
    doubled=column(100,2000,density_scale=10)
    assert math.isclose(doubled['equal_area_required_depth_m'],base['equal_area_required_depth_m'],rel_tol=1e-12)
    assert math.isclose(doubled['column_kg_m2'],10*base['column_kg_m2'],rel_tol=1e-12)
    coarse=column(100,2000,n=4001)
    error=abs(coarse['column_kg_m2']/base['column_kg_m2']-1)
    assert error<1e-6
    report=dict(scope='Unpumped ideal-gas column capacity, not a vehicle feasibility calculation',
        cases=rows,temperature_sensitivity=thermal,actual_altitude_sensitivity=altitude,
        checks=dict(uniform_density_scaling='10x mass and pressure; unchanged ratio/depth',
                    relative_column_quadrature_error=error),samples=8001)
    Path('results/column_physics.json').write_text(json.dumps(report,indent=2)+'\n')
    b=base
    lines=[f'''# Atmospheric column, confinement and the need for compression

## The question

How can a spacecraft fly through hundreds of kilometres of atmosphere and keep
that air in a chamber only hundreds of metres deep? Before solving shocks or
choosing a compressor, conservation of mass gives a useful scale.

For the **100 × 2,000 km** comparison orbit, collection from half the peak ram
pressure inbound to perigee lasts **{b['inbound_s']:.1f} s**. The atmosphere-relative
travel distance is **{b['geometric_path_m']/1000:.1f} km**. Because density rises
through that interval, the collected mass is equivalent to a column only
**{b['effective_column_m']/1000:.1f} km long at perigee density**. That approximately
500 km quantity is an atmospheric-column length, not a spacecraft dimension.

The column length and the required spacecraft depth are different quantities.
Under the explicit cooled, unmixed inputs below, the unpumped equal-area chamber
is **{b['equal_area_required_depth_m']/1000:.2f} km** deep. Added coolant gas and
different temperature/pressure assumptions can make that required depth much
larger. The derivation below relates all of these quantities.

![Column mass compressed into a cooled chamber](../../docs/images/column_physics.svg)

## 1. Specify the compression ratio we actually need

Dynamic pressure is `q = ½ rho_inf u²`. It is a pressure scale, not by definition
the pressure available inside this inlet. Introduce a recovery/control factor:

    p_c = C_q q = kappa rho_inf u²,       C_q = 2 kappa

The code's `inlet_pressure_fraction` multiplies **rho u²**, not q. Thus kappa=0.7
means p_c=1.4q. This convention does not assert that the shock provides that
pressure: inlet flow analysis must determine the admissible value. See
[NASA's dynamic-pressure definition](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/).

Using `p_c = rho_c R_c T_c`, the **density compression ratio** is

    chi = rho_c / rho_inf
        = kappa u² / (R_c T_c)
        = C_q u² / (2 R_c T_c).

The density cancels. Units also cancel: both u² and R_c T_c have units m²/s².
This is the ratio that shrinks an upstream volume of the same mass. A pressure
ratio alone is insufficient when the gas changes temperature. For example,
`p_c/p_inf = kappa u²/(R_inf T_inf)`, whereas the confined volume depends on T_c.
The ideal-gas density relation is given in
[NASA's equation of state](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/equation-of-state/).

**At fixed composition, confined temperature and pressure-recovery factor,
speed fixes chi.** Speed alone does not fix it if cooling or chemistry changes.
This note uses an explicit nitrogen-equivalent R_c={R_GAS:g} J/(kg K) to isolate
the scaling; the system model uses a composition-dependent mixture instead.

This cooled-plenum density ratio is not the instantaneous jump across a normal
shock. In the calorically perfect gamma=1.4 limit that jump tends to six, with
much of the encounter energy left as heat. Subsequent heat removal can raise
density at a given pressure. Real hypersonic chemistry needs a richer model;
[NASA's normal-shock relations](https://www.grc.nasa.gov/WWW/BGH/normal.html)
state the perfect/imperfect-gas distinction. We do not use an incompressible
Bernoulli relation across a shock.

## 2. Turn a changing atmosphere into one representative column

For atmosphere-relative distance ds=u dt, define column mass per mouth area:

    Sigma = integral rho(t) u(t) dt                         [kg/m²]
    ell_geometric = integral u(t) dt                       [m]
    ell_effective = Sigma / rho_reference                  [m]

Choose perigee density as rho_reference. Then ell_effective is the length of a
uniform column at that density with exactly the same mass as the sampled pass.
There is no single “distance through the atmosphere” without a time/pressure
window: atmosphere has no sharp collection edge. This convention makes the
window and density weighting explicit.

Let A_m be mouth area and A_c the unpumped chamber cross-section. If all admitted
air is held at the perigee pressure allowance and at T_c, mass conservation gives

    M = A_m Sigma = rho_c A_c L
    L = (A_m/A_c) ell_effective / chi_perigee.

Dividing column length by chi yields **V/A_m**, an equivalent depth. It is a
physical axial chamber depth only when A_c=A_m and the chamber is prismatic.
For a bulb or varying area, use its actual volume integral; volume does not
remove the required material, surface and load budgets.

## 3. Numerical example: 100 × 2,000 km, inbound half-peak window

| Quantity | Value |
|---|---:|
| Perigee atmosphere-relative speed | {b['perigee_speed_m_s']/1000:.4f} km/s |
| Perigee atmospheric density | {b['perigee_density_kg_m3']:.5g} kg/m³ |
| Dynamic pressure q | {b['dynamic_pressure_Pa']:.2f} Pa |
| Assumed confinement p_c = 0.7 rho u² | {b['confinement_pressure_Pa']:.2f} Pa |
| Confined gas temperature | 1,000 K |
| Confined density | {b['confined_density_kg_m3']:.5g} kg/m³ |
| Density compression chi | {b['density_compression_ratio']:.2f} |
| Column mass Sigma | {b['column_kg_m2']:.5f} kg/m² |
| Mass through an 18.3 m mouth | {b['mass_through_18_3m_mouth_kg']:.2f} kg |
| Geometric / effective column | {b['geometric_path_m']/1000:.1f} / {b['effective_column_m']/1000:.1f} km |
| Unpumped physical depth at equal mouth/chamber area | {b['equal_area_required_depth_m']/1000:.3f} km |
| Full orbital period | {b['orbit_period_s']/60:.2f} min |

So the scale is **about 520 km / 146 = 3.57 km**, despite collecting only about
85 kg. The small mass and large volume are compatible: the permitted pressure
is only tens of pascals.

For a uniform peak-density encounter, filling time is

    t_fill = (A_c/A_m) chi L / u
           = (A_c/A_m) kappa u L / (R_c T_c).

Again density cancels. An equal-area **500 m chamber fills in
{b['constant_peak_fill_time_500m_s']:.2f} s** at the peak conditions. The inbound
mass column corresponds to **{b['peak_equivalent_fill_s']:.1f} s** at peak mass
flux, spread across {b['inbound_s']:.1f} s of actual travel. This is why a few
hundred metres of unpumped, cooled chamber cannot simply retain the entire
selected batch under that pressure allowance. Finite filling transients and
changing confinement pressure still need analysis.

## 4. Window and thermal sensitivity

Every row below is inbound-only, ending at perigee; T_c=1,000 K and the same
nitrogen-equivalent gas constant. These are column calculations, not new
optimized spacecraft results.

| Orbit km | Opening / peak ram | kappa | Inbound time | Geometric column | Effective column | Equal-area depth |
|---|---:|---:|---:|---:|---:|---:|''']
    for r in rows:
        lines.append(f"| {r['perigee_km']:g} × {r['apogee_km']:.0f} | {r['opening_ram_fraction']:.1f} | {r['kappa_pressure_over_rho_u2']:.1f} | {r['inbound_s']:.1f} s | {r['geometric_path_m']/1000:.1f} km | {r['effective_column_m']/1000:.1f} km | {r['equal_area_required_depth_m']/1000:.2f} km |")
    lines.append('''
A symmetric inbound-plus-outbound window doubles these mass columns in the
prescribed atmosphere. Dividing that mass by peak supported density gives twice
the displayed capacity depth, but that is **not** a feasible open-bottle storage
protocol: support pressure falls outbound. For arbitrary final time t_f, use
`V_required = A_m Sigma(t_f) R_c T_c / p_support(t_f)` and track backflow.

Holding the first row's orbit/window and kappa=0.7 fixed:

| Confined gas temperature | Density ratio chi | Equal-area depth |
|---|---:|---:|''')
    for r in thermal:
        lines.append(f"| {r['confined_temperature_K']:.0f} K | {r['density_compression_ratio']:.1f} | {r['equal_area_required_depth_m']/1000:.2f} km |")
    lines.append('''
These temperature endpoints require heat removal; they are not free compression.
The metal rack makes denser front gas possible without adding gas mass. The
compressor then transfers it into a rear pressure vessel whose pressure need
not be supported by the atmosphere. Its flow/work requirements and the vessel's
mass replace the enormous unpumped storage volume. Together, precooling and
active transfer address different parts of the same column problem.

If r kilograms of circulating coolant gas accompany each kilogram of captured
air, capacity at a common temperature becomes
`V = (1+r) M_air R_mix T_mix / p_c`. Compare `(1+r)R_mix T_mix`, not temperature
alone. For r=10 at the same 1,000 K and R, the first row would require eleven
times the volume. Whether mixing changes the required temperature, admissible
pressure, heat-transfer performance or compressor map enough to compensate is
a separate [planned study](../../docs/DESIGN_STUDIES_PLAN.md).

## 5. What the altitude cancellation does and does not say

Multiplying the entire density history by a constant a multiplies Sigma and
p_support by a. At fixed trajectory, R, T and kappa, their ratio—and required
volume per mouth area—is unchanged. Admitted mass, heat and encounter impulse
all increase. Lower altitude is therefore not a free solution to unpumped
volume: stronger pressure support arrives with more gas to confine.

Changing perigee is not exactly the same operation. It changes speed, the shape
and duration of the density pulse, composition, chemistry, heat transfer and
possibly pressure recovery. The same profile model, fixed 2,000 km apogee,
half-peak inbound window, kappa=0.7 and T_c=1,000 K gives:

| Perigee | Effective column | Density ratio | Equal-area depth |
|---|---:|---:|---:|''')
    for r in altitude:
        lines.append(f"| {r['perigee_km']:.0f} km | {r['effective_column_m']/1000:.1f} km | {r['density_compression_ratio']:.1f} | {r['equal_area_required_depth_m']/1000:.2f} km |")
    lines.append('''
Those differences are compatible with cancellation of the **density amplitude**.
They do not establish an altitude-independent mission payoff or a minimum
survivable altitude. In particular, active leading-edge cooling and repeated
life remain essential design constraints as perigee is lowered.

## Reproduce

```sh
.venv/bin/python -m atmo_scoops.studies.column_physics
```

Inputs and numerical results are in `results/column_physics.json`. The generator
uses the repository's reference NRLMSIS profile and atmosphere-relative Kepler
trajectory. It checks 4,001→8,001-point quadrature and an exact 10× density
rescaling. It does not alter the cycle kernel or run an optimization.
''')
    Path('modeling/primary/ATMOSPHERIC_COLUMN.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report['checks'],indent=2))
    print('Reference effective column km:',b['effective_column_m']/1000,'depth km:',b['equal_area_required_depth_m']/1000)


if __name__=='__main__':main()
