"""Rear-depth investigation: analytic four-block sizing + unchanged cycle model.

Run from repository root with .venv/bin/python conclusions/rear_storage_depth/calculate.py.
No optimization or new compressor physics is implemented here.
"""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from atmo_scoops.physical_cycle import rear_geometry
from atmo_scoops.system import inputs_from_dict, simulate


def main():
    config = json.loads((ROOT / 'configs/reference.json').read_text())
    inputs = inputs_from_dict(config)
    R, gamma, eta, mdot, pin = 287., 1.35, .8, 1.283, 26.8
    cp = gamma * R / (gamma - 1)
    exponent = (gamma - 1) / gamma
    temps = [1000., 600., 600., 600.]
    base_volume = rear_geometry(25.)['volume_m3']
    pbase = 3753.
    rows = []
    for depth in [25., 50., 100., 150., 180., 200., 300., 500., 1000., 3000.]:
        geom = rear_geometry(depth)
        pressure = pbase * base_volume / geom['volume_m3']
        ratio = max(1., pressure / pin)**.25
        stages = []
        for i, temp in enumerate(temps):
            work = cp * temp / eta * (ratio**exponent - 1)
            stages.append(dict(block=i+1, inlet_K=temp, inlet_Pa=pin*ratio**i,
                shaft_work_J_kg=work, shaft_power_W=mdot*work,
                suction_m3_s=mdot*R*temp/(pin*ratio**i),
                discharge_K=temp+work/cp))
        # Illustrative equal-coefficient volume sizing, NOT a hardware prediction.
        sumQ = sum(s['suction_m3_s'] for s in stages)
        gauge = max(.001, 1.5*pressure*18.3/(2*150e6))
        tank_mass = geom['surface_m2']*(gauge*2700*1.5+1.)
        rows.append(dict(depth_m=depth, receiver_pressure_Pa=pressure,
            fixed_inventory_kg=pbase*base_volume/(R*340), block_ratio=ratio,
            stages=stages, total_shaft_MW=sum(s['shaft_power_W'] for s in stages)/1e6,
            sum_bank_suction_m3_s=sumQ,
            volume_only_compressor_proxy_kg=sumQ*30.,
            receiver_tank_support_insulation_kg=tank_mass,
            rear_gauge_mm=gauge*1000,
            extra_outer_shell_kg=math.pi*20*(depth-25)*4,
            coast_extra_isothermal_J_kg=R*340*math.log(geom['volume_m3']/base_volume)))
    runs = []
    for depth in [25., 50., 100., 150., 180., 200., 300., 500., 1000.]:
        run = simulate(**{**inputs, 'design': replace(inputs['design'], rear_depth_m=depth)}, n=1601)
        runs.append(run)
        o = run['outputs']
        print(f"rear {depth:5.0f} m: {o['rear_pressure_Pa']:8.1f} Pa, "
              f"dry {o['total_dry_kg']/1000:8.2f} t, "
              f"payoff {o['operating_mass_payoff_days']:8.2f} d", flush=True)
    layouts = []
    for front, rear in [(175.,100.),(125.,150.),(75.,200.),(25.,250.),(30.,150.)]:
        run = simulate(**{**inputs, 'design': replace(inputs['design'], front_depth_m=front, rear_depth_m=rear)}, n=1601)
        layouts.append(run)
        o = run['outputs']
        print(f"layout {front:.0f}+{rear:.0f}+20 m: dry {o['total_dry_kg']/1000:.2f} t, "
              f"net {o['net_liquid_equivalent_kg']:.3f} kg, payoff {o['operating_mass_payoff_days']:.2f} d", flush=True)
    check = simulate(**{**inputs, 'design': replace(inputs['design'], rear_depth_m=200.)}, n=3201)
    source_paths = sorted((ROOT/'atmo_scoops').rglob('*.py')) + [Path(__file__).resolve(), ROOT/'configs/reference.json']
    result = dict(scope='Separate illustrative four-block point sizing and unchanged active-model depth sweep; not a staged-cycle prediction',
        analytical_inputs=dict(R=R,gamma=gamma,isentropic_efficiency=eta,mass_flow_kg_s=mdot,
            inlet_Pa=pin,block_inlet_K=temps,reference_receiver_Pa=pbase,
            receiver_K=340.,diameter_m=18.3,reference_depth_m=25.),
        analytic=rows,active_model_runs=runs,layout_diagnostics=layouts,resolution_check_200m=check,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
    target = Path(__file__).with_name('results.json')
    target.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
