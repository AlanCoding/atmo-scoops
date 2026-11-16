"""Kepler geometry, orbital timing and circularization velocity."""
from dataclasses import dataclass
import numpy as np

MU = 3.986004418e14
R_EARTH = 6378137.
OMEGA = 7.2921150e-5

@dataclass(frozen=True)
class Orbit:
    perigee_km: float
    apogee_km: float

    def __post_init__(self):
        if not 50 <= self.perigee_km < self.apogee_km:
            raise ValueError("Require 50 km <= perigee < apogee")

    @property
    def rp(self): return R_EARTH + self.perigee_km*1000
    @property
    def ra(self): return R_EARTH + self.apogee_km*1000
    @property
    def a(self): return (self.rp+self.ra)/2
    @property
    def e(self): return (self.ra-self.rp)/(self.ra+self.rp)
    @property
    def h(self): return np.sqrt(MU*self.a*(1-self.e**2))
    @property
    def period(self): return 2*np.pi*np.sqrt(self.a**3/MU)
    @property
    def circularization_dv(self): return np.sqrt(MU/self.ra)-self.h/self.ra

    def eccentric_grid(self, n=240):
        edges = np.linspace(0, 2*np.pi, n+1)
        E = (edges[:-1]+edges[1:])/2
        times = (edges-self.e*np.sin(edges))*self.period/(2*np.pi)
        t = (E-self.e*np.sin(E))*self.period/(2*np.pi)
        r = self.a*(1-self.e*np.cos(E))
        f = 2*np.arctan2(np.sqrt(1+self.e)*np.sin(E/2), np.sqrt(1-self.e)*np.cos(E/2))
        vr = MU/self.h*self.e*np.sin(f)
        vt = self.h/r
        return t, np.diff(times), r, f, vr, vt

    def time_at_altitude(self, altitude_km):
        r = R_EARTH+1000*altitude_km
        if r <= self.rp: return 0.
        if r >= self.ra: return self.period/2
        E = np.arccos(np.clip((1-r/self.a)/self.e, -1, 1))
        return (E-self.e*np.sin(E))*self.period/(2*np.pi)

