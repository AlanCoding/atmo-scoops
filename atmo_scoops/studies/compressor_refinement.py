"""Reproducible paired cycle comparisons, not a globally optimized vehicle."""
from dataclasses import replace,asdict
from pathlib import Path
import hashlib,json,time
from ..system import simulate,inputs_from_dict
from ..compressor import Compressor


def main():
    root=Path(__file__).resolve().parents[2]
    out=root/'results/compressor_refinement';out.mkdir(exist_ok=True)
    reference=inputs_from_dict(json.loads((root/'configs/reference.json').read_text()))
    candidate=inputs_from_dict(json.loads((root/'configs/candidate_geometry.json').read_text()))
    # Ample declared machinery space, charged to hull mass. No optimization claim.
    # This is explicit because the old 20 m allowance need not fit resolved rows.
    layouts={'reference':reference,'candidate':candidate}
    cases=[]
    for name,inputs in layouts.items():
        cases.append((name+'_legacy', {**inputs,'design':replace(inputs['design'],machinery_depth_m=20.),'compressor':Compressor(mode='legacy')}))
        generous={**inputs,'design':replace(inputs['design'],machinery_depth_m=100.)}
        cases.append((name+'_real_standard', {**generous,'compressor':Compressor()}))
        compact=replace(Compressor(),module_diameter_m=.5,tip_speed_m_s=350.,axial_velocity_m_s=100.)
        cases.append((name+'_real_compact', {**generous,'compressor':compact}))
        cases.append((name+'_real_compact_light', {**generous,'compressor':replace(compact,mass_multiplier=.5)}))
        cases.append((name+'_real_compact_heavy', {**generous,'compressor':replace(compact,mass_multiplier=2.)}))
        cases.append((name+'_real_compact_low_eff', {**generous,'compressor':replace(compact,isentropic_efficiency=.6)}))
    # Receiver depth and cutoff studies at candidate geometry, fixed compact hardware assumptions.
    base={**candidate,'design':replace(candidate['design'],machinery_depth_m=100.),'compressor':compact}
    for depth in (100.,200.):
        cases.append((f'candidate_rear_{depth:g}m',{**base,'design':replace(base['design'],rear_depth_m=depth)}))
    for cutoff in (.3,1.,3.,10.):
        cases.append((f'candidate_cutoff_{cutoff:g}Pa',{**base,'controls':replace(base['controls'],cutoff_Pa=cutoff)}))
    cases.append(('candidate_eta40_cutoff3', {
        **base, 'controls':replace(base['controls'],cutoff_Pa=3.),
        'compressor':replace(compact,isentropic_efficiency=.4)}))
    rows=[]
    for label,inputs in cases:
        start=time.monotonic()
        try:
            r=simulate(**inputs,n=401)
            (out/(label+'.json')).write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
            o=r['outputs']
            row=dict(label=label,dry_t=o['total_dry_kg']/1000,compressor_t=o['compressor_mass_kg']/1000,
                net_kg_pass=o['net_liquid_equivalent_kg'],payoff_days=o['operating_mass_payoff_days'],
                screens_pass=r['constraints']['all_implemented_screens_pass'],
                compressor_kWh=o['compressor_kWh'],input_file=label+'.json')
        except ValueError as exc:row=dict(label=label,error=str(exc),inputs={k:asdict(v) for k,v in inputs.items()})
        rows.append(row);print(row,'seconds',round(time.monotonic()-start,1),flush=True)
        (out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    sources=list((root/'atmo_scoops').rglob('*.py'))+[root/'pyproject.toml',root/'configs/reference.json',root/'configs/candidate_geometry.json']
    (out/'manifest.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n')


if __name__=='__main__':main()
