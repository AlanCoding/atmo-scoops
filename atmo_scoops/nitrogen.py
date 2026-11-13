"""NIST molecular-nitrogen heat capacity and phase anchors for product cooling."""
import math
from scipy.integrate import quad

MOLAR_KG = .0280134
BOIL_K = 77.34
LATENT_J_KG = 5600 / MOLAR_KG  # NIST 5.6 kJ/mol at 77 K; rounded phase anchor.
# NIST Shomate Cp, 100–500 and 500–2000 K (J/mol/K).
COEFFICIENTS = ((28.98641, 1.853978, -9.647459, 16.63537, .000117),
                (19.50583, 19.88705, -8.598535, 1.369784, .527601))

def nitrogen_cp(temperature):
    """Ideal molecular nitrogen; constant Cp bridge from 77.34 to 100 K."""
    if not math.isfinite(temperature) or not BOIL_K <= temperature <= 2000:
        raise ValueError("Nitrogen property screen supports 77.34–2000 K only")
    t = max(100., temperature) / 1000
    a,b,c,d,e = COEFFICIENTS[0 if temperature < 500 else 1]
    return (a+b*t+c*t*t+d*t**3+e/t**2)/MOLAR_KG

def sensible_enthalpy(low, high):
    nitrogen_cp(low); nitrogen_cp(high)
    if high < low: raise ValueError("Expected increasing temperature")
    return quad(nitrogen_cp, low, high,
                points=[t for t in (100.,500.) if low < t < high], epsabs=1e-5)[0]

