# Front-volume provenance: frozen plate case 72

Reproduce: `PYTHONPATH=. .venv/bin/python investigations/v1_layout/trace_front_geometry.py`.

The 33-coordinate saved COBYLA manifest contains no clear-depth coordinate. Decoding evaluation 72 reproduces the saved materials, rack depths, plate gaps, thicknesses and zero clear depths exactly.

| Chamber | Material | Rack depth m | Rack gas gaps m³ | Head gas m³ | Total gas m³ | Axial envelope m | Rack mass t |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | sic | 0.896424 | 514.383 | 0.000 | 514.383 | 0.896424 | 382.828 |
| 2 | aluminum | 0.055570 | 29.418 | 1063.822 | 1093.240 | 3.055570 | 26.629 |
| 3 | aluminum | 0.032406 | 18.126 | 1063.822 | 1081.948 | 3.032406 | 12.907 |
| 4 | aluminum | 0.023283 | 12.087 | 1063.822 | 1075.909 | 3.023283 | 11.800 |

Fixed head pair: 1063.821812 m³. At the 30 m bore, just 1 m of extra front clear depth adds 706.858347 m³ (front total would be 1221.241702 m³). This is an arithmetic illustration, not an evaluated candidate.
