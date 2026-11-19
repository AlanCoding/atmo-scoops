"""Fixed-geometry hydraulic homotopy; multiplier is not an optimized capability."""
import argparse
import copy
import json
from pathlib import Path
from .staged_search import batch

def proposals(base, factors):
    out = {}
    for factor in factors:
        if not 0 <= factor <= 1:
            raise ValueError('Continuation factors must be between zero and one')
        candidate = copy.deepcopy(base)
        candidate['design']['rack_pressure_model'] = 'inline_laminar'
        candidate['capabilities']['rack_loss_multiplier'] = factor
        out[f'loss_{factor:g}'] = candidate
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, default=Path('configs/transient_staged_bypass.json'))
    p.add_argument('--output', type=Path, default=Path('results/transient/loss_continuation/scan'))
    p.add_argument('--factors', type=float, nargs='+', default=[.01, .05, .1])
    p.add_argument('--workers', type=int, default=3)
    p.add_argument('--seconds', type=int, default=300)
    a = p.parse_args()
    batch(proposals(json.loads(a.config.read_text()), a.factors), a.output, a.workers, a.seconds)

if __name__ == '__main__':
    main()
