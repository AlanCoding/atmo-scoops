"""Encapsulated PCM: separate shell and core enthalpy states, finite conduction.

Material constants are screening approximations with provenance in PCM_MODEL.md.
No liquid convection or zero-cost enhancement of conductivity is credited.
"""
from dataclasses import dataclass,asdict
import math
from scipy.optimize import brentq
from scipy.integrate import solve_ivp

@dataclass(frozen=True)
class PCM:
    melt_K: float
    latent_J_kg: float
    cp_s_J_kg_K: float
    cp_l_J_kg_K: float
    density_kg_m3: float
    liquid_density_kg_m3: float
    k_s_W_m_K: float
    k_l_W_m_K: float
    max_core_K: float

    def enthalpy(self,T):
        if T<=self.melt_K:return self.cp_s_J_kg_K*(T-298.)
        return self.cp_s_J_kg_K*(self.melt_K-298.)+self.latent_J_kg+self.cp_l_J_kg_K*(T-self.melt_K)
    def temperature(self,h):
        onset=self.cp_s_J_kg_K*(self.melt_K-298.)
        if h<onset:return 298.+h/self.cp_s_J_kg_K
        if h<=onset+self.latent_J_kg:return self.melt_K
        return self.melt_K+(h-onset-self.latent_J_kg)/self.cp_l_J_kg_K
    def melt_fraction(self,h):
        if self.latent_J_kg==0:return float(self.temperature(h)>self.melt_K)
        return min(1.,max(0.,(h-self.cp_s_J_kg_K*(self.melt_K-298.))/self.latent_J_kg))

MATERIALS={
 'sodium_nitrate':PCM(579.15,178000.,1384.,1655.,2260.,1908.,.73,.514,623.15),
 'nitrate_eutectic':PCM(495.15,108000.,1355.,1492.,2055.,1965.,.3835,.4574,623.15),
 'tin':PCM(505.10,60220.,230.,250.,7290.,6970.,60.,30.,1042.),
}


def cell_geometry(mass,density,spec):
    r=spec.wire_radius_m;t=spec.pcm_wall_m;length=spec.pcm_cell_length_m
    cavity=(1-t/r)**2*(1-2*t/length)
    fin=cavity*spec.pcm_fin_volume_fraction
    metal_fraction_volume=1-cavity+fin
    core_fraction_volume=(cavity-fin)*spec.pcm_fill_fraction
    pcm=MATERIALS[spec.pcm_material]
    bulk=density*metal_fraction_volume+pcm.density_kg_m3*core_fraction_volume
    outer=mass/bulk;metal_mass=outer*density*metal_fraction_volume
    core_mass=mass-metal_mass;wire_length=outer/(math.pi*r*r)
    # The 4*pi*k*L core conductance matches the constant-wall cylindrical
    # Stefan latent-freezing time rho*L*r_core^2/(4*k*deltaT) (ideal contact).
    # Effective radial fin conduction is a declared parallel-path approximation.
    k=min(pcm.k_s_W_m_K,pcm.k_l_W_m_K)*(1-spec.pcm_fin_volume_fraction)+spec.metal_conductivity_W_m_K*spec.pcm_fin_volume_fraction
    contact_length=wire_length*spec.pcm_fill_fraction
    resistance=(1/(4*math.pi*k*contact_length)
        +math.log(r/(r-t))/(2*math.pi*spec.metal_conductivity_W_m_K*contact_length)
        +spec.pcm_contact_resistance_m2_K_W/(2*math.pi*(r-t)*contact_length))
    return dict(displaced_m3=outer,material_m3=outer*(metal_fraction_volume+core_fraction_volume),
        sealed_void_m3=outer*(1-metal_fraction_volume-core_fraction_volume),
        shell_and_fin_kg=metal_mass,pcm_kg=core_mass,bulk_density_kg_m3=bulk,
        core_mass_fraction=core_mass/mass,core_conductance_W_K=1/resistance,
        pcm_material=spec.pcm_material,pcm_properties=asdict(pcm),
        liquid_fill_fraction=spec.pcm_fill_fraction*pcm.density_kg_m3/pcm.liquid_density_kg_m3,
        wall_m=t,cell_length_m=length,fin_volume_fraction=spec.pcm_fin_volume_fraction)


class Cell:
    """One shell temperature and one phase-resolved core enthalpy per rack.

    Shell/fin material retains the existing Fe heat-capacity proxy. Core geometry
    comes from sealed finite cells, including end caps, ullage and optional fins.
    """
    def __init__(self,cold,spec,density):
        from .racks import Metal
        from dataclasses import replace
        self.shell=Metal(cold);self.pcm=MATERIALS[spec.pcm_material]
        if cold>=self.pcm.melt_K:raise ValueError('PCM cold start must be below its melting point')
        self.pcm=replace(self.pcm,latent_J_kg=self.pcm.latent_J_kg*spec.pcm_latent_fraction)
        self.unit=cell_geometry(1.,density,spec);self.f=self.unit['core_mass_fraction']
        self.cold=cold;self.hcore_cold=self.pcm.enthalpy(cold)
        self.hcold=self.enthalpy(cold)
    def enthalpy(self,T):return (1-self.f)*self.shell.enthalpy(T)+self.f*self.pcm.enthalpy(T)
    def temperature(self,h):
        # Equilibrated temperature is only used for the initial sizing rule.
        return brentq(lambda T:self.enthalpy(T)-h,200.,1600.)
    def surface_temperature(self,total_h,core_h):
        return self.shell.temperature((total_h-self.f*core_h)/(1-self.f))
    def core_rate(self,total_h,core_h,geom):
        return geom['core_conductance_W_K']*(self.surface_temperature(total_h,core_h)-self.pcm.temperature(core_h))/geom['pcm_kg']
    def advance_core(self,total_h,core_h,dt,geom):
        if dt<=0:return core_h
        # Backward Euler internal exchange; total energy is separately balanced.
        # Monotone enthalpy laws retain an exact isothermal phase plateau.
        fun=lambda h:h-core_h-dt*self.core_rate(total_h,h,geom)
        lo=min(core_h,self.pcm.enthalpy(100.));hi=max(core_h,self.pcm.enthalpy(3000.))
        return brentq(fun,lo,hi,xtol=1e-7)
    def cooldown_state(self,total_h,core_h,geom,emissivity,spec):
        target=self.cold+.1  # Explicit recovery tolerance; no latent heat is skipped.
        area=geom['wetted_m2']*spec.deployed_view_factor
        def rhs(t,y):
            Ts=self.surface_temperature(y[0],y[1])
            flux=emissivity*5.670374419e-8*max(Ts,1.)**4-80.
            return [-area*flux/geom['mass_kg'],self.core_rate(y[0],y[1],geom)]
        def event(t,y):
            return max(self.surface_temperature(y[0],y[1]),self.pcm.temperature(y[1]))-target
        event.terminal=True;event.direction=-1
        if event(0,[total_h,core_h])<=0:
            return dict(cooldown_s=0.,recovered_melt_fraction=self.pcm.melt_fraction(core_h),cooldown_energy_residual_J=0.)
        sol=solve_ivp(rhs,(0.,2e5),[total_h,core_h],method='Radau',rtol=1e-7,atol=1e-5,events=event,max_step=100.)
        if not sol.success:raise ValueError('PCM coast cooling failed')
        recovered=self.pcm.melt_fraction(sol.y[1,-1])
        # Complete recovery is required, not just a cold skin around a molten core.
        return dict(cooldown_s=float(sol.t[-1]) if sol.t_events[0].size else 1e30,
            recovered_melt_fraction=recovered,coast_max_melt_fraction=max(self.pcm.melt_fraction(h) for h in sol.y[1]),coast_end_core_K=self.pcm.temperature(sol.y[1,-1]),
            coast_end_shell_K=self.surface_temperature(sol.y[0,-1],sol.y[1,-1]),
            rejected_coast_J=(total_h-sol.y[0,-1])*geom['mass_kg'])
