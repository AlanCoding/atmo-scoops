"""Configurable current spacecraft cycle and precooling sensitivity CLI."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

from .system import defaults,inputs_from_dict,simulate


def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main(argv=None):
    p=argparse.ArgumentParser(description='Two-compartment atmospheric scoop: inputs -> cycle, areas, mass and constraints')
    p.add_argument('--config',type=Path,help='JSON with design, hardware, performance, process and scenario sections')
    p.add_argument('--write-config',type=Path,help='Write a complete editable input file and exit')
    p.add_argument('--front-depth',type=float,help='Physical front depth, metres')
    p.add_argument('--rear-depth',type=float,help='Physical rear depth including rounded ends, metres')
    p.add_argument('--inlet-temperature',type=float,help='Dry-stream temperature before optional mixing, K')
    p.add_argument('--mixing-ratio',type=float,help='Injected LN2 kg per kg of newly admitted air')
    p.add_argument('--mixing-path',choices=['fixed_rack','fixed_inlet'],help='Solve mixed temperature, or replace rack cooling at fixed mixed temperature')
    p.add_argument('--sweep-precooling',nargs='+',type=float,metavar='K',help='Run each gas temperature with other input choices fixed')
    p.add_argument('--samples',type=int,default=801)
    p.add_argument('--output',type=Path,default=Path('results/system.json'))
    a=p.parse_args(argv)
    if a.write_config:
        write_json(a.write_config,defaults());print(f'Wrote {a.write_config}');return
    try:
        config=json.loads(a.config.read_text()) if a.config else {}
        inputs=inputs_from_dict(config)
        changes={k:v for k,v in [('front_depth_m',a.front_depth),('rear_depth_m',a.rear_depth),('compressor_inlet_K',a.inlet_temperature)] if v is not None}
        inputs['design']=replace(inputs['design'],**changes)
        mix_changes={k:v for k,v in [('ratio',a.mixing_ratio),('thermal_path',a.mixing_path)] if v is not None}
        inputs['mixing']=replace(inputs['mixing'],**mix_changes)
        if a.sweep_precooling:
            runs=[simulate(**{**inputs,'design':replace(inputs['design'],compressor_inlet_K=T)},n=a.samples) for T in a.sweep_precooling]
            result=dict(swept_variable='design.compressor_inlet_K',runs=runs)
        else:
            result=simulate(**inputs,n=a.samples);runs=[result]
        write_json(a.output,result)
    except (ValueError,TypeError,OSError) as exc:p.error(str(exc))
    print('Dry K | Mixed K | Metal hot K | Metal t | Compressors t | Total dry t | Net kg/cycle | Operating payoff days | Screens')
    for r in runs:
        o=r['outputs'];d=r['inputs']['design']
        payoff=o['operating_mass_payoff_days']
        payoff_text=f'{payoff:.1f}' if payoff is not None else 'undefined'
        print(f"{d['compressor_inlet_K']:5.0f} | {o['compressor_inlet_K']:7.0f} | {o['metal_hot_K']:11.0f} | {o['masses_kg']['hot_metal']/1000:7.2f} | {o['compressor_mass_kg']/1000:13.2f} | {o['total_dry_kg']/1000:11.2f} | {o['net_liquid_equivalent_kg']:12.2f} | {payoff_text:>21s} | {r['constraints']['all_implemented_screens_pass']}")
    print('Operating payoff excludes circular-apogee delivery.')
    print(f'Saved {a.output}')


if __name__=='__main__':main()
