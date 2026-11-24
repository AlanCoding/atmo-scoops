from pathlib import Path
import json
s=json.loads(Path('results/transient/flat_plate_skin/screen.json').read_text())
a,b=s['compiled_comparison'];r=min((r for r in s['rows'] if r['wall_K']==600),key=lambda r:abs(r['perigee_km']-85.098))
lines=['# Flat-plate side friction and the lower-altitude question','','[Equations, sources and applicability](../../modeling/aerodynamics/FLAT_PLATE_SHEAR.md). This is a conditional shear estimate, not a new cycle optimum or release. Geometry, apogee and atmosphere follow the widened-bounds candidate. No integrated cycle was rerun for these compiler comparisons.','',
'## Current candidate','',f'At {r["perigee_km"]:.5f} km and a 600 K exterior wall, the full-pass effective Cf is **{r["coefficient"]:.7f}** and skin impulse is **{100*r["skin_to_incident_impulse"]:.3f}%** of incident-mouth impulse. The selected candidate already used Cf=0.002, equivalent to 4.466%; do not add these penalties together.','',
'| Compiler quantity | Existing constant Cf | Optional laminar plate |','|---|---:|---:|']
for label,key,scale in [('Skin impulse, MN s','skin',1),('Reference propellant, kg','propellant_reference_kg',1),('Installed thrust electrical power, MW','thrust_W',1e-6)]:
 vals=[z['skin']['impulse_Ns']/1e6 if key=='skin' else z[key]*scale for z in [a,b]]
 lines.append(f'| {label} | {vals[0]:.3f} | {vals[1]:.3f} |')
lines+=['','The compiler derives thrust-related hardware from required impulse; other capacity inputs remain unchanged. This is not a closed replacement cycle. The roughly 80 kg propellant reduction and 17 MW rating reduction are conditional compiler consequences, not a validated payoff improvement.','',
'Wall-temperature sensitivity at the current perigee:','', '| Assumed wall K | Skin / mouth impulse % |','|---|---:|']
for z in s['rows']:
 if z['perigee_km']==r['perigee_km']:lines.append(f'| {z["wall_K"]:.0f} | {100*z["skin_to_incident_impulse"]:.3f} |')
lines+=['','## Altitude scaling, same geometry and 2,000 km apogee','','| Perigee km | Peak Re_L | Peak q Pa | Skin / incident-mouth impulse % |','|---|---:|---:|---:|']
for z in s['rows']:
 if z['wall_K']==600 and z['perigee_km']<=100:
  p=z['peak_dynamic_state'];lines.append(f'| {z["perigee_km"]:.3f} | {p["Re_L"]:.3g} | {p["dynamic_Pa"]:.2f} | {100*z["skin_to_incident_impulse"]:.3f} |')
lines+=['','These rows assume laminar flow at every altitude; they are not validated transition predictions. The saved 120/150 km extrapolations are excluded from this table because continuum applicability is particularly poor. The 100 km full-pass result already has major rarefaction/curvature limitations.','',
'## Does lower altitude eventually become worse?','','Not established by the current optimizations. At fixed velocity and temperature profile, capture and its momentum/thermal burden scale approximately as density. If hardware scales proportionally with batch mass, dry-mass payoff can approach a floor without developing an interior optimum. Fixed overhead can make deeper dives look progressively better.',
'', 'For this laminar equation Fskin ∝ D sqrt(L) sqrt(ρ μ) U^(3/2) sqrt(C*). Collection momentum scales as ρ U² D_mouth². Thus their ratio scales approximately as ρ^(−1/2), not as increasing density. A conventional turbulent one-fifth-power scaling would give ρ^(−1/5) instead; this scaling observation is not a turbulent coefficient estimate. Transition can cause a finite change, but side friction alone supplies no theorem of an ultimate altitude penalty.',
'', 'Real restrictions include maximum local heat flux and reusable lip temperature/erosion, side heating and catalysis, peak force/bending/buckling, qualified tank pressure, compressor throughput/head, finite thermal storage and heat transfer, finite electric power and available coast time. The model includes some capacity constraints but not qualified limits for all of these. Fixed total gas volume with a genuinely fixed pressure rating and minimum temperature also bounds batch inventory through m≈pV/(RT). If pressure rating and installed hardware are allowed to grow, that particular bound changes.',
'', 'The numerical package itself currently rejects perigees outside 75–110 km as a molecular-air study scope. That is another artificial domain boundary, distinct from the local 85.098 km optimization floor and not a survivability claim. The offline shear screen can show equations below this domain without declaring those trajectories feasible collection designs.',
'', 'Consequently: expand altitude only with explicit complete-capture/pressure/thermal/power constraints and documented capabilities. Do not expect this new side-shear law by itself to stop the optimizer from descending. Keep the published design and the constant-Cf comparison intact while the boundary-layer assumptions are reviewed.',
'', '## Reproduction','', '```sh','PYTHONPATH=. .venv/bin/python investigations/flat_plate_skin/run.py','PYTHONPATH=. .venv/bin/python investigations/flat_plate_skin/report.py','```','',
'- [Numerical screen and compiler comparison](../../results/transient/flat_plate_skin/screen.json).','- [Optional candidate inputs, not a closed optimized cycle](../../results/transient/flat_plate_skin/candidate_config.json).']
Path('investigations/flat_plate_skin/RESULTS.md').write_text('\n'.join(lines)+'\n')
