"""Consistent atmospheric-species enthalpy and equilibrium gas properties."""
from functools import lru_cache
import cantera as ct
import numpy as np

@lru_cache(maxsize=1)
def gas():
    species=ct.Species.list_from_file("airNASA9.yaml")
    species += [s for s in ct.Species.list_from_file("nasa_gas.yaml")
                if s.name in ("Ar","He","H","H2")]
    return ct.Solution(thermo="ideal-gas",species=species)

def composition(fractions):
    f=np.asarray(fractions)
    out={"N2":float(f[0]),"O2":float(f[1]),"O":float(f[2]+f[7]),
         "He":float(f[3]),"H":float(f[4]),"Ar":float(f[5]),"N":float(f[6]),"NO":float(f[8])}
    return {k:v for k,v in out.items() if v>0}

def enthalpy(temperature, fractions):
    g=gas();g.TPY=max(200.,temperature),1e5,fractions
    return g.enthalpy_mass+g.cp_mass*min(0.,temperature-200.)

