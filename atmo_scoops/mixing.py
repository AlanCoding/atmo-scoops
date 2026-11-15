"""Incremental LN2 mixing with explicit enthalpy and restored coolant inventory.

Two controlled paths: hold the dry stream's rack outlet temperature, or hold
mixed compressor-inlet temperature. Neither substitutes for exchanger CFD.
"""
from dataclasses import dataclass,asdict
import math
import numpy as np
from scipy.optimize import brentq
from .nitrogen import BOIL_K,LATENT_J_KG,sensible_enthalpy


@dataclass(frozen=True)
class Mixing:
    ratio: float = 0.  # Injected LN2 / newly admitted atmospheric mass.
    thermal_path: str = 'fixed_rack'
    # Explicit development allowances, not catalog component fits.
    storage_kg_per_kg_inventory: float = .15
    injector_fixed_kg: float = 25.
    injector_kg_per_kg_s: float = 10.
    injection_pressure_Pa: float = 1e6
    liquid_density_kg_m3: float = 806.
    pump_efficiency: float = .6
    pump_W_kg: float = 500.


def validate(m):
    if m.thermal_path not in ('fixed_rack','fixed_inlet'):
        raise ValueError('Mixing path must be fixed_rack or fixed_inlet')
    for k,v in asdict(m).items():
        if k=='thermal_path':continue
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
            raise ValueError(f'mixing.{k} must be finite and nonnegative')
    if min(m.liquid_density_kg_m3,m.pump_efficiency,m.pump_W_kg)<=0 or m.pump_efficiency>1:
        raise ValueError('Invalid mixing pump/density capability')


def endpoint(g,air_Y,dry_K,m):
    """Keep molecular species fixed; solve total enthalpy, not a Cp-weighted guess.

    LN2 enthalpy is tied to the Cantera N2 reference at 298.15 K using NIST's
    low-temperature sensible and latent heat. No NASA-polynomial extrapolation
    to liquid temperatures is used. Injection work is subsequently charged.
    """
    validate(m)
    g.TPY=dry_K,30.,air_Y;h_dry=float(g.enthalpy_mass)
    if m.ratio==0:return dry_K,air_Y.copy(),0.,0.
    g.TPX=298.15,1e5,'N2:1'
    h_liquid=float(g.enthalpy_mass)-sensible_enthalpy(BOIL_K,298.15)-LATENT_J_KG
    work=m.injection_pressure_Pa/(m.liquid_density_kg_m3*m.pump_efficiency)
    Y=air_Y.copy();Y[g.species_index('N2')]+=m.ratio;Y/=1+m.ratio
    target=(h_dry+m.ratio*(h_liquid+work))/(1+m.ratio)
    def residual(T):
        g.TPY=T,30.,Y
        return g.enthalpy_mass-target
    if m.thermal_path=='fixed_rack':
        if residual(200)>0:raise ValueError('Mixed endpoint below 200 K property domain')
        T=brentq(residual,200.,dry_K)
    else:T=dry_K
    return float(T),Y,h_liquid,work
