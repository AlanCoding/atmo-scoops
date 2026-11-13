"""Separated product condenser, refrigerator, heat exchangers and heat rejection.

Nitrogen-equivalent thermal duty, with no fictitious credit for recycling coolant
as new product. This module starts with a PRESSURIZED gas feed: low-pressure
chamber evacuation/compression, capture and delivery are separate duties.
"""
from dataclasses import dataclass, asdict
import math

from scipy.integrate import quad
from .nitrogen import BOIL_K, LATENT_J_KG, sensible_enthalpy, nitrogen_cp
SIGMA_SB = 5.670374419e-8


@dataclass(frozen=True)
class ProcessTargets:
    carnot_fraction: float = .15
    heat_pump_kg_W_equivalent_cold: float = .25
    exchanger_conductance_W_K_kg: float = 200.
    condenser_approach_K: float = 5.
    precooler_effective_approach_K: float = 20.
    radiator_kg_m2: float = 5.
    emissivity: float = .85
    view_factor: float = .8
    environment_W_m2: float = 80.
    solar_W_kg: float = 150.
    reject_approach_K: float = 20.


def liquefaction_train(new_air_kg_s, radiator_K=320., targets=None):
    """Explicit duty per operating second, N2-equivalent pressurized feed.

    77.34 K / ~1 bar is a pure-N2 benchmark, not a mixed-air phase separator.
    The fluid approaches the reject temperature before staged refrigeration.
    Product condenser mass is an explicit heat-transfer allowance. Refrigerator
    specific mass includes its compressor/expander/internal recuperator package;
    those are NOT also charged as external process heat exchangers.
    """
    t=targets or ProcessTargets()
    if new_air_kg_s <= 0 or radiator_K <= BOIL_K:
        raise ValueError("Positive flow and a warm rejection temperature required")
    if not 0<t.carnot_fraction<=1 or min(t.solar_W_kg,t.exchanger_conductance_W_K_kg)<=0:
        raise ValueError("Invalid process targets")
    hot=radiator_K+t.reject_approach_K
    cold_refrigerant=BOIL_K-t.condenser_approach_K
    if cold_refrigerant<=0 or t.condenser_approach_K<=0:
        raise ValueError("Invalid cold-side approach")
    flow=new_air_kg_s
    sensible=sensible_enthalpy(BOIL_K,hot)
    # Finite approach is charged thermodynamically, not only in exchanger mass.
    # Distributed cold stages track the gas 5 K below its temperature.
    reversible_sensible=quad(lambda T:nitrogen_cp(T)*(hot/(T-t.condenser_approach_K)-1),
        BOIL_K,hot,points=[x for x in (100.,500.) if BOIL_K<x<hot])[0]
    work=(reversible_sensible+LATENT_J_KG*(hot/cold_refrigerant-1))/t.carnot_fraction
    sensible_W=flow*sensible
    latent_W=flow*LATENT_J_KG
    electric_W=flow*work
    cold_W=sensible_W+latent_W
    rejected_W=cold_W+electric_W
    flux=t.emissivity*t.view_factor*SIGMA_SB*radiator_K**4-t.environment_W_m2
    if flux<=0:raise ValueError("No net radiator rejection")
    # Convert staged cooling work to 77 K equivalent lift; never report this as
    # the actual sensible + latent cold duty. The assumed kg/W applies here.
    cop_cold=t.carnot_fraction*cold_refrigerant/(hot-cold_refrigerant)
    equivalent_cold_W=electric_W*t.carnot_fraction*BOIL_K/(hot-BOIL_K)
    parts=dict(
        product_condenser=latent_W/(t.exchanger_conductance_W_K_kg*t.condenser_approach_K),
        process_precooler=sensible_W/(t.exchanger_conductance_W_K_kg*t.precooler_effective_approach_K),
        refrigeration_package=equivalent_cold_W*t.heat_pump_kg_W_equivalent_cold,
        refrigerator_radiator=rejected_W/flux*t.radiator_kg_m2,
        refrigerator_solar=electric_W/t.solar_W_kg)
    return dict(new_air_kg_s=new_air_kg_s,
        gas_in_kg_s=flow,liquid_out_kg_s=flow,
        new_liquid_before_losses_and_propulsion_kg_s=new_air_kg_s,
        feed_temperature_K=hot,product_temperature_K=BOIL_K,
        coldest_refrigerant_K=cold_refrigerant,
        radiator_temperature_K=radiator_K,refrigerator_rejection_K=hot,
        latent_heat_J_kg=LATENT_J_KG,sensible_heat_J_kg=sensible,
        sensible_cooling_W=sensible_W,condensation_W=latent_W,
        actual_cold_duty_W=cold_W,electricity_W=electric_W,
        radiator_heat_W=rejected_W,energy_residual_W=rejected_W-cold_W-electric_W,
        effective_overall_COP=cold_W/electric_W,final_stage_COP=cop_cold,
        equivalent_77K_lift_W=equivalent_cold_W,
        radiator_emitting_m2=rejected_W/flux,mass_breakdown_kg=parts,
        refrigerator_own_mass_liquefaction_hours=parts["refrigeration_package"]/flow/3600,
        refrigerator_mass_over_new_liquid_hours=parts["refrigeration_package"]/new_air_kg_s/3600,
        plant_mass_over_new_liquid_hours=sum(parts.values())/new_air_kg_s/3600,
        assumptions=asdict(t),
        excluded=["Low-pressure feed collection/compression", "Gas cooling above feed temperature",
            "Species separation and cleanup", "Storage tanks and pumps", "Propulsion and delivery",
            "Duty cycle, standby heat leaks and deployment", "O2/Ar separate phase equilibria"])


def coast_compressor(mixture_kg, chamber_volume_m3, temperature_K, duration_s,
                     gas_R=296.8, output_Pa=1e5, residual_fraction=1e-4,
                     efficiency=.5, volumetric_m3_s_kg=.1, electrical_W_kg=1000.):
    """Isothermal chamber evacuation at CONSTANT volumetric pumping speed.

    p(t)=p0 exp(-S t/V). Includes declining inlet pressure, finite residual and
    coast duty. It cannot instantly swallow the dive stream. Pressure work is
    integrated over the withdrawn mass; peak power may occur partway through.
    No claim that ideal-gas high-vacuum pumping stays at the assumed efficiency.
    """
    if min(mixture_kg,chamber_volume_m3,temperature_K,duration_s,gas_R,output_Pa,
           efficiency,volumetric_m3_s_kg,electrical_W_kg)<=0 or not 0<residual_fraction<1:
        raise ValueError("Invalid compressor boundary conditions")
    p0=mixture_kg*gas_R*temperature_K/chamber_volume_m3
    if p0>=output_Pa:raise ValueError("This helper expects a low-pressure chamber")
    f=residual_fraction
    S=chamber_volume_m3*math.log(1/f)/duration_s
    c=math.log(output_Pa/p0)
    energy=mixture_kg*gas_R*temperature_K/efficiency*((1-f)*c+1-f+f*math.log(f))
    # x exp(-x) shape in pressure work, clipped to actual mass remaining range.
    remaining_at_peak=1. if c>=1 else max(f,math.exp(c-1))
    peak=mixture_kg*S/chamber_volume_m3*remaining_at_peak*gas_R*temperature_K/efficiency*(c-math.log(remaining_at_peak))
    mass=max(S/volumetric_m3_s_kg,peak/electrical_W_kg)
    return dict(input_pressure_start_Pa=p0,input_pressure_end_Pa=p0*f,
        output_pressure_Pa=output_Pa,temperature_K=temperature_K,
        withdrawn_kg=mixture_kg*(1-f),residual_kg=mixture_kg*f,
        electricity_J=energy,rejected_heat_J=energy,peak_power_W=peak,
        mean_power_W=energy/duration_s,pumping_speed_m3_s=S,hardware_mass_kg=mass,
        duration_s=duration_s,residual_fraction=f)
