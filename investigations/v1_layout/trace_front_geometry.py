"""Trace frozen plate-search coordinates to gas volumes; no cycle rerun."""
import gzip,json,math
from pathlib import Path
from atmo_scoops.transient.plate_optimize import decode
ROOT=Path(__file__).resolve().parents[2]
r=json.load(gzip.open(ROOT/'results/transient/plates/reference_validation/case_72.json.gz'))
s=json.loads((ROOT/'results/transient/plates/cobyla_stable/search.json').read_text())
rows=json.loads((ROOT/'results/transient/plates/cobyla_stable/evaluations.json').read_text())
row=next(q for q in rows if q['index']==72)
d=decode(row['x'],s['base'],s['coordinates'])['design']
for key in ['rack_depth_m','clear_depth_m','materials','plate_thickness_m','plate_gap_m']:
 assert d[key]==r['inputs']['design'][key],key
assert not any(q['key'].startswith('clear_depth_m') for q in s['coordinates'])
A=math.pi*d['bore_m']**2/4;h=r['inputs']['capabilities']['head_depth_m'];rad=d['bore_m']/2
heads=2*math.pi*h*(3*rad**2+h*h)/6
out=['# Front-volume provenance: frozen plate case 72','','Reproduce: `PYTHONPATH=. .venv/bin/python investigations/v1_layout/trace_front_geometry.py`.','','The 33-coordinate saved COBYLA manifest contains no clear-depth coordinate. Decoding evaluation 72 reproduces the saved materials, rack depths, plate gaps, thicknesses and zero clear depths exactly.','','| Chamber | Material | Rack depth m | Rack gas gaps m³ | Head gas m³ | Total gas m³ | Axial envelope m | Rack mass t |','|---|---|---:|---:|---:|---:|---:|---:|']
for i,g in enumerate(r['hardware']['geometry'][:4]):
 rackgas=A*d['rack_depth_m'][i]-g['solid_m3'];hv=heads if i else 0
 expected=rackgas+A*d['clear_depth_m'][i]+hv
 assert math.isclose(expected,g['gas_m3'],abs_tol=1e-8)
 assert math.isclose(g['depth_m'],d['rack_depth_m'][i]+d['clear_depth_m'][i]+(2*h if i else 0),abs_tol=1e-10)
 out.append(f"| {i+1} | {d['materials'][i]} | {g['rack_depth_m']:.6f} | {rackgas:.3f} | {hv:.3f} | {g['gas_m3']:.3f} | {g['depth_m']:.6f} | {g['mass_kg']/1000:.3f} |")
out+=['',f'Fixed head pair: {heads:.6f} m³. At the 30 m bore, just 1 m of extra front clear depth adds {A:.6f} m³ (front total would be {A+r["hardware"]["geometry"][0]["gas_m3"]:.6f} m³). This is an arithmetic illustration, not an evaluated candidate.']
(Path(__file__).parent/'FRONT_GEOMETRY_NUMBERS.md').write_text('\n'.join(out)+'\n')
print('\n'.join(out))
