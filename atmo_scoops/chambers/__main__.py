"""Run an editable chamber experiment: python -m atmo_scoops.chambers."""
import argparse,json,math
from pathlib import Path
import numpy as np
from .model import Chamber,Pump,Schedule,Boundary,simulate
from .thermo import Air
from ..orbit import Orbit
from ..atmosphere import make_profile
from ..encounter import orbit_state

def run(config):
    orbit=Orbit(**config['orbit']);atm=make_profile(config.get('atmosphere','reference'));air=Air()
    edge=max(orbit.time_at_altitude(200.),min(orbit.time_at_altitude(min(1000.,orbit.apogee_km)),abs(config['schedule']['start_s'])))
    times=np.linspace(-edge,edge,1801);state=orbit_state(orbit,times,atm)
    area=math.pi*config['mouth_diameter_m']**2/4
    # Fixed-composition air throughout; incident kinetic energy remains explicit.
    hin=np.array([air.at(t)[0] for t in state['temperature_K']])+state['speed_m_s']**2/2
    boundary=Boundary(times,area*state['density_kg_m3']*state['speed_m_s'],state['ram_Pa'],hin,area)
    result=simulate([Chamber(**x) for x in config['chambers']],[Pump(**x) for x in config['pumps']],boundary,Schedule(**config['schedule']),config.get('samples',1501))
    result['experiment_config']=config
    result['boundary']=dict(time_s=times.tolist(),support_Pa=state['ram_Pa'].tolist(),supply_kg_s=(area*state['density_kg_m3']*state['speed_m_s']).tolist(),altitude_km=state['altitude_km'].tolist(),incident_total_enthalpy_J_kg=hin.tolist())
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='configs/chamber_transient_reference.json');parser.add_argument('--output',default='results/chamber_transient/reference.json')
    args=parser.parse_args();result=run(json.loads(Path(args.config).read_text()));p=Path(args.output);p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['checks'],indent=2))
if __name__=='__main__':main()
