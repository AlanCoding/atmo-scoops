"""Generate the skin-friction investigation table from recorded trajectories."""
import json
from pathlib import Path
from .io import read_result


def main():
    folder=Path('results/transient/skin_friction');rows=json.loads((folder/'comparison.json').read_text());baseline=json.loads(Path('results/transient/best.json').read_text())
    lines=['# External skin-friction impulse sensitivity','',
      '**Implemented:** an effective skin-friction coefficient adds hull drag impulse to the coupled model. These are coefficient scenarios, not a calibrated aerodynamic prediction or reoptimized vehicle. The 285-day comparison has zero external skin friction.','',
      '## Impulse calculation','',
      'For axial flight and a cylindrical external envelope:', '',
      '```text\nq(t) = 0.5 rho(t) v_relative(t)^2\nS_wetted = pi D_out L × area_multiplier\nJ_skin = integral Cf_effective q(t) S_wetted dt\nJ_total = J_incident_mouth + J_skin\n```','',
      'The existing prescribed Kepler/atmosphere history supplies the integral; no additional trajectory iteration is introduced. Total impulse feeds the same finite-burn steering penalty, installed thruster rating, propellant expenditure, electrical load and thermal cycle. It cannot create captured gas.','',
      'At 30 m mouth diameter, 31.7 m outside diameter and 317 m length, the ratio is `J_skin/J_mouth = Cf × S_wetted/(2 A_mouth) = 22.3309 Cf`. The factor of one-half belongs to dynamic pressure; the incident-air capture impulse uses `rho v² A_mouth`.','',
      'The capability inputs are `skin_friction_coefficient` and `skin_area_multiplier`. They are scenario assumptions, **not optimizer variables allowed to drift to zero**. Zero remains the backwards-compatible value for saved historical inputs. The new `configs/transient_skin_reference.json` explicitly uses 0.002.','',
      '## Coupled results','',
      '| Effective Cf | Added impulse | Electrical/thermal capacity proposal | Dry mass (t) | Net liquid (kg/orbit) | Accepted payoff (days) |',
      '|---:|---:|---|---:|---:|---:|',
      f'| 0 | 0% | Historical comparison | {baseline["dry_kg"]/1000:,.0f} | {baseline["net_liquid_kg"]:,.1f} | {baseline["operating_payoff_days"]:.2f} |']
    audits={}
    for row in rows:
        value=row.get('operating_payoff_days');pay=f'{value:.2f}' if value else 'Rejected'
        lines.append(f'| {row["coefficient"]:.3f} | {(row["impulse_multiplier"]-1)*100:.2f}% | {"Energy-scaled proposal" if row["capacity_proposal"] else "Unchanged capacities"} | {row["dry_kg"]/1000:,.0f} | {row["net_liquid_kg"]:,.1f} | {pay} |')
        r=read_result(folder/f'cycle_{row["case"]}.json');audits[str(row['case'])]=r['thermodynamic_audit']
    lines+=['',
      'The unchanged-capacity Cf=0.002 case exceeds the 450 K warm-store limit by about 0.37 K and finishes with a 216 MJ (0.060 MWh) battery deficit, beyond the declared 100 MJ closure tolerance. Its diagnostic payoff is not an accepted repeatable-cycle result. Thruster rating/mass still derives from the increased required impulse even when the other capacities are held fixed.','',
      'For the capacity proposals, solar area, battery energy/power, bus rating, warm-store mass and warm-radiator area are each multiplied by the drag-impulse ratio **before integration**. Other stage and plant capacities remain fixed. This restores closure in the tested cases but is not a minimum-mass resizing or a fresh optimum.','',
      '## Meaning and limits of Cf','',
      'Cf is the wetted-area mean shear coefficient referenced to freestream dynamic pressure. It is not the usual whole-vehicle frontal-area drag coefficient. The multiplier can represent extra exposed area, but cannot by itself model fin pressure drag.','',
      'At reference perigee, the free-stream length-based Reynolds number is approximately 1.43 million using Sutherland viscosity. Classical incompressible flat-plate averages would be about 0.0011 (laminar) or 0.0043 (turbulent); these are scale checks, **not hypersonic predictions**. Compressibility, actual boundary-layer-edge state, wall temperature, transition, roughness, rarefaction and shape must be resolved before choosing an aerodynamic coefficient.','',
      '[NASA TN D-3969](https://ntrs.nasa.gov/citations/19670016466) develops skin-friction/heat-transfer charts for compressible turbulent flat plates. It establishes the need for Mach, Reynolds and wall-temperature dependence; it does not validate our constant coefficient, a 317 m scoop geometry, or extrapolation beyond its stated chart domain.','',
      'The current cases therefore span Cf=0.001–0.005 as **illustrative sensitivity scenarios**, not confidence bounds. Offline aerothermal calculations should produce an impulse-weighted coefficient or a time-dependent shear table for the optimizer. Keep L/D fixed until that calibration is sufficiently defensible.','',
      'This change includes skin drag only. It does not yet include inlet/spillage pressure drag beyond the existing mouth-incident momentum allowance, skirt/fin pressure drag, base drag, attitude error or wall heating/TPS mass. `mechanical_work_J` is drag work, not heat deposited into the wall; do not assign all of it to a coolant loop. Local convective heat flux requires a separate aerothermal calculation.','',
      '## Reproduction','',
      '```bash\nOPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.skin_study --workers 2\n.venv/bin/python -m atmo_scoops.transient.skin_report\n.venv/bin/python -m atmo_scoops.transient --config configs/transient_skin_reference.json --output results/transient/skin_example.json\n```','',
      'Inputs and all four trajectories are retained in `results/transient/skin_friction/`. The frozen zero-skin comparison is preserved; do not silently relabel it as including external drag.']
    Path('investigations/skin_friction/ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    (folder/'property_audits.json').write_text(json.dumps(audits,indent=2)+'\n')
    chosen=next(r for r in rows if r['coefficient']==.002 and r['capacity_proposal'])
    Path('configs/transient_skin_reference.json').write_text(json.dumps(chosen['inputs'],indent=2)+'\n')

if __name__=='__main__':main()
