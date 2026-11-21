"""Exact independent-coordinate register for the terminal constrained result."""
import argparse
import json
import math
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('folder', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
m = json.loads((a.folder / 'search.json').read_text())
done = json.loads((a.folder / 'termination.json').read_text())
if not done.get('success'):
    raise SystemExit('No successful solver termination')
lines = ['# Independent coordinates at constrained termination', '',
         'All values use SI units except the explicitly named MW/MWh quantities. '
         '`solid_depth` means solid material volume divided by full bore area; '
         'it is not the physical rack length. Thermal gaps, thicknesses and '
         'solid inventories determine physical gaps and rack lengths.', '',
         '| Coordinate | Lower | Selected | Upper | At a bound? |',
         '|---|---:|---:|---:|---|']
for s, x in zip(m['coordinates'], done['x']):
    value = s['low'] * math.exp(x * math.log(s['high'] / s['low']))
    bound = 'lower' if x < 1e-6 else 'upper' if x > 1 - 1e-6 else 'no'
    lines.append(f"| {s['key']} | {s['low']:.7g} | {value:.7g} | {s['high']:.7g} | {bound} |")
lines += ['', 'Fixed for this comparison: 85 × 2,000 km orbit; 30 m bore; '
          '31.7 m outer diameter and 317 m hull; full-bore rack frontal areas; '
          'four serial rows per rack; SiC first, aluminum downstream; 10 m '
          'front empty depth; 1 m hatch buffers; compressor suction and head '
          'ratings; gas reserve hardware; collection/plant cutoff schedule; '
          '0.1 Pa compressor cutoff; capability coefficients. Receiver free '
          'volume is derived after subtracting chambers and equipment. '
          'Pressure and gas temperature are simulated states, not independent '
          'input coordinates.', '',
          'See `search.json` for exact fixed settings, `selected_summary.json` '
          'for every individual constraint residual, and `termination.json` '
          'for solver status. Geometry bounds are study bounds, not material '
          'qualification limits.']
a.output.write_text('\n'.join(lines) + '\n')
