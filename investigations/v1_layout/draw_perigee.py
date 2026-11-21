"""Regenerate the scale figure from the accepted corrected-spacing checkpoint."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
result = ROOT / 'results/transient/staggered/thermal_equivalence/selected_validation/check_refined.json.gz'
env = dict(os.environ, PYTHONPATH=str(ROOT))
subprocess.run([sys.executable, str(ROOT / 'investigations/staggered_stage_a/draw_checkpoint.py'),
                str(result), '--output', str(ROOT / 'docs/images/v1_perigee_scale.svg')],
               cwd=ROOT, env=env, check=True)
