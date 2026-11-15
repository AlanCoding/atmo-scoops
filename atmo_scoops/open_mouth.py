"""Ideal compressible port relation; not a hypersonic inlet solution."""
import math

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
