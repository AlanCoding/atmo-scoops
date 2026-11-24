"""Reduced coordinates for the existing cycle; no changes to cycle physics.

Freeze a reference's five rack mass fractions and expose one total rack mass.
Sheet thickness, gap, row count, materials and initial temperatures stay fixed.
"""
from copy import deepcopy
import math
from .hardware import compile_hardware
from .inputs import read_config


def rack_allocation(reference):
    """Return the actual compiled masses, not volume fractions across materials."""
    d, c = read_config(reference)
    if d.rack_flow_layout != 'parallel_plates':
        raise ValueError('Reduced mass coordinate currently requires parallel plates')
    hw = compile_hardware(d, c)
    masses = [g['mass_kg'] for g in hw['geometry']]
    total = sum(masses)
    return dict(total_kg=total, masses_kg=masses,
                fractions=[m / total for m in masses])


def with_total_rack_mass(reference, total_kg):
    """Map one physical mass coordinate into a fresh ordinary cycle config.

    For fixed plate spacing/thickness and frontal area, solid mass is linear in
    core depth. Hardware compilation still derives installed depths, deployment
    area, mechanism mass and available receiver volume; none is held artificially
    fixed. This mapping performs no cycle integration or closure restoration.
    """
    if not math.isfinite(total_kg) or total_kg <= 0:
        raise ValueError('Total rack mass must be finite and positive')
    allocation = rack_allocation(reference)
    config = deepcopy(reference)
    scale = total_kg / allocation['total_kg']
    config['design']['rack_depth_m'] = [
        depth * scale for depth in reference['design']['rack_depth_m']]
    return config
