"""Dedicated mixed-gas propellant storage and booster hardware.

No separation or liquefaction is credited on this branch. Vessel construction
uses the same conditional stress/support capabilities as the main model.
"""
import math
from ..compressor import bank_mass


def hardware(d,c,spec,dummy):
    if d.propellant_storage=='liquid':
        return dict(enabled=False,fill_bank=dict(total_kg=0.,spin_energy_J=0.),mass_kg=0.,package_m3=0.)
    if d.propellant_storage=='valve':
        # Tank shell is charged with the pressure vessels, not as a folded package.
        valves=500.+500.*d.reserve_valve_area_m2
        return dict(enabled=True,architecture='valve',fill_bank=dict(total_kg=0.,spin_energy_J=0.),
                    mass_kg=valves,package_m3=valves/c.machinery_kg_m3,
                    feed_hardware_kg=valves,rated_Pa=d.rated_pressure_Pa[-1])
    n=d.gas_tank_count
    radius=(3*d.gas_volume_m3/(4*math.pi*n))**(1/3)
    thickness=max(.001,1.5*d.gas_rated_Pa*radius/(2*150e6))
    outer=radius+thickness
    shell=n*4*math.pi*radius**2*thickness*2700*1.5
    bank=bank_mass(d.gas_fill_suction_m3_s,d.gas_fill_head_J_kg,d.gas_fill_motor_MW*1e6,spec,dummy)
    exchanger=(d.gas_thermal_UA_W_K+d.gas_fill_UA_W_K)/c.exchanger_UA_per_kg
    valves=500. # provisional regulator/isolation/manifold allowance, not qualification
    return dict(enabled=True,tank_count=n,internal_radius_m=radius,outer_diameter_m=2*outer,
                wall_m=thickness,rated_Pa=d.gas_rated_Pa,usable_internal_m3=d.gas_volume_m3,
                shell_and_support_kg=shell,exchangers_kg=exchanger,feed_hardware_kg=valves,
                fill_bank=bank,mass_kg=shell+exchanger+valves+bank['total_kg'],
                package_m3=n*(2*outer+.2)**3+(exchanger+valves+bank['total_kg'])/c.machinery_kg_m3)


def state(th,species,U_MJ,volume):
    mass=max(float(sum(species)),1e-12)
    y=species/mass
    T=th.temperature(U_MJ*1e6,species)
    h,cp,R=th.at(T,y)
    return dict(mass=mass,fractions=y,T=T,p=mass*R*T/volume,h=float(y@h),cp=cp,R=R)


def valve_flow(up,down,T,area,R,cp):
    """Finite ideal-gas orifice, regularized only within 0.1% pressure equality.

    This computes a positive donor-to-recipient magnitude. The cycle selects
    either donor after the pressure-triggered valve opens, allowing both directions.
    """
    from ..open_mouth import port_flow
    if up<=down or up<=0:return 0.
    fraction=min(1.,(up-down)/(.001*up))
    return port_flow(up,min(down,up*.999),T,area,R,cp/(cp-R),.8)*fraction
