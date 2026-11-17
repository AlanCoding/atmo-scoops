"""Gas-reserve volume and avoided refrigeration duties; not a payoff credit."""
import json,math
from pathlib import Path
import numpy as np
from atmo_scoops.transient.thermo import properties
from atmo_scoops.transient.cycle import PROP_Y
from atmo_scoops.compressor import RealAir


def main():
    r=json.loads(Path('results/transient/best.json').read_text());th=properties()
    mass=sum(r['ledger']['prop_'+s][-1] for s in ('N2','O2','Ar'));gas=RealAir();gas.fluid.set_mass_fractions(PROP_Y.tolist());gas.mass_fractions=PROP_Y.tolist()
    tanks=[]
    for p in (5000.,100000.,1000000.):
        a=gas.state(p,300.);v=mass/a['rho_kg_m3'];tanks.append(dict(pressure_Pa=p,gas_K=300.,volume_m3=v,equivalent_bore_depth_m=v/(math.pi*30**2/4),Z=a['Z']))
    duties=[]
    for sink in (340.,400.,445.):
        work,cold=th.liquid_duty(sink+20,PROP_Y,sink,.15)
        latent_work=float(PROP_Y@(th.latent*np.maximum((sink+20)/(th.boil-5)-1,0))/.15)
        duties.append(dict(warm_store_K=sink,avoided_latent_heat_GJ=mass*float(PROP_Y@th.latent)/1e9,avoided_latent_refrigerator_electric_GJ=mass*latent_work/1e9,avoided_full_refrigerator_electric_GJ=mass*work/1e9))
    out=dict(propellant_kg=mass,pre_perigee_burn_propellant_kg=mass/2,mean_burn_flow_kg_s=mass/r['inputs']['design']['burn_s'],gross_liquid_kg=sum(r['ledger']['made_'+s][-1] for s in ('N2','O2','Ar')),coast_train_and_plant_electric_GJ=r['ledger']['plant_MJ'][-1]/1000,thruster_electric_GJ=r['hardware']['thrust_W']*r['inputs']['design']['burn_s']/1e9,tanks=tanks,duties=duties,note='Avoided duties for the old propellant blend at assumed temperatures, before gas-buffer compression, hardware, changed chemistry/efficiency or process scheduling. No net payoff credit.')
    path=Path('results/propellant_feed/screen.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
