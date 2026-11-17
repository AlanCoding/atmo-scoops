"""A long rear tank under the same diameter/length and packaging assumptions."""
from pathlib import Path
from dataclasses import replace
import json
from ..system import inputs_from_dict,simulate

def main():
 root=Path(__file__).resolve().parents[2];folder=root/'results/finite_rack_limits'
 x=inputs_from_dict(json.loads((folder/'reference_1mm/apogee_2000.json').read_text())['inputs'])
 x['design']=replace(x['design'],perigee_km=85.,rear_depth_m=95.)
 x['compressor']=replace(x['compressor'],thermodynamic_samples=801)
 r=simulate(**x,n=801);(folder/'long_rear.json').write_text(json.dumps(r,indent=2)+'\n')
 o=r['outputs'];print(o['overall_length_allowance_m'],o['rear_pressure_Pa'],o['operating_mass_payoff_days'],r['constraints'],flush=True)

if __name__=='__main__':main()
