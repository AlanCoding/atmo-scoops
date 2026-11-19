"""Stable HEOS gas update without a pressure-flash root in the dilute limit.

Below 100 Pa, initialize density from p=R rho T, then Newton-correct against
HEOS's pressure and its analytic density derivative. Returned caloric properties
remain full HEOS properties, not an ideal-gas replacement. No failure fallback.
"""
import math
import CoolProp.CoolProp as CP

_BACKENDS = {}


def gas_update(fluid,p,T):
    # Exact-zero constituents are removed, not replaced by artificial traces.
    fractions=fluid.get_mass_fractions()
    if any(z==0 for z in fractions):
        ids=[i for i,z in enumerate(fractions) if z>0]
        names=fluid.fluid_names();key=tuple(names[i] for i in ids)
        if not key:raise ValueError('Empty HEOS composition')
        if key not in _BACKENDS:
            f=CP.AbstractState('HEOS','&'.join(key));f.specify_phase(CP.iphase_gas);_BACKENDS[key]=f
        fluid=_BACKENDS[key]
        if len(ids)>1:fluid.set_mass_fractions([fractions[i]/sum(fractions[j] for j in ids) for i in ids])
    try:
        _gas_update(fluid,p,T)
        return fluid
    except ValueError as exc:
        raise ValueError(f"HEOS gas_update at p={p!r} Pa, T={T!r} K, mass_fractions={fluid.get_mass_fractions()!r}, R={fluid.gas_constant()/fluid.molar_mass()!r}: {exc}") from exc


def _gas_update(fluid,p,T):
    p=float(p);T=float(T)
    if p>=100.:
        fluid.update(CP.PT_INPUTS,p,T)
        return
    if not p>0 or not T>0:raise ValueError('Positive dilute gas state required')
    rho=p/(fluid.gas_constant()/fluid.molar_mass()*T)
    for _ in range(6):
        fluid.update(CP.DmassT_INPUTS,rho,T)
        residual=fluid.p()-p
        if abs(residual)<=p*1e-11:return
        slope=fluid.first_partial_deriv(CP.iP,CP.iDmass,CP.iT)
        rho-=residual/slope
        if not math.isfinite(rho) or rho<=0:raise ValueError('Invalid dilute HEOS density correction')
    raise ValueError('Dilute HEOS density correction did not converge')
