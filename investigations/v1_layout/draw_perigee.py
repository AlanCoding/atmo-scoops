"""Regenerate the current working valve-connected layout, not the rejected archive."""
from pathlib import Path
import os, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
env=dict(os.environ,PYTHONPATH=str(ROOT))
subprocess.run([sys.executable,str(ROOT/'investigations/v1_layout/draw_valve_working.py')],cwd=ROOT,env=env,check=True)
