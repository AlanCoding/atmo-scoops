"""Axial skin-friction impulse screen; coefficient is an engineering scenario.

Cf is an effective, wetted-area mean coefficient referenced to freestream
q = rho*v_relative**2/2. It is not a frontal-area drag coefficient, a calibrated
hypersonic correlation, or a model of wall heating.
"""
import math
import numpy as np


def skin_impulse(time_s, density_kg_m3, speed_m_s, diameter_m, length_m,
                 coefficient=0., area_multiplier=1.):
    if min(diameter_m,length_m)<=0 or min(coefficient,area_multiplier)<0:
        raise ValueError('Invalid external skin geometry/coefficient')
    area=math.pi*diameter_m*length_m*area_multiplier
    force=.5*np.asarray(density_kg_m3)*np.asarray(speed_m_s)**2*coefficient*area
    return dict(coefficient=coefficient,wetted_area_m2=area,
                impulse_Ns=float(np.trapezoid(force,time_s)),
                peak_force_N=float(np.max(force)),
                mechanical_work_J=float(np.trapezoid(force*np.asarray(speed_m_s),time_s)))
