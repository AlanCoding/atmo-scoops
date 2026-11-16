"""Reproducible NRLMSIS 2.1 profiles; explicit drivers, no weather downloads."""
from dataclasses import dataclass
from pathlib import Path
import csv
import numpy as np
import pymsis

AMU = 1.66053906660e-27
SPECIES = ("N2", "O2", "O", "He", "H", "Ar", "N", "anomalous_O", "NO")
MASSES = np.array([28.0134, 31.9988, 15.9994, 4.0026, 1.00794, 39.948, 14.0067, 15.9994, 30.0061])

@dataclass
class Atmosphere:
    name: str
    alt_km: np.ndarray
    density: np.ndarray
    fractions: np.ndarray
    temperature: np.ndarray
    metadata: dict

    def at(self, altitude_km):
        h = np.asarray(altitude_km)
        if np.any(h < self.alt_km[0]) or np.any(h > self.alt_km[-1]):
            raise ValueError("Atmosphere query outside tabulated range")
        rho = np.exp(np.interp(h, self.alt_km, np.log(self.density)))
        fractions = np.stack([np.interp(h, self.alt_km, self.fractions[:, i])
                              for i in range(9)], axis=-1)
        return rho, fractions

    def save(self, folder):
        path = Path(folder) / f"atmosphere_{self.name}.csv"
        with path.open("w", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["altitude_km", "density_kg_m3", "temperature_K"] + [s+"_mass_fraction" for s in SPECIES])
            writer.writerows(np.column_stack([self.alt_km, self.density, self.temperature, self.fractions]))

def make_profile(name="reference"):
    # Sensitivity cases, NOT confidence intervals or forecasts.
    cases = {
        "reference": ("2020-03-20T12:00", 0., 0., 150., 4.),
        "quiet": ("2020-03-20T12:00", 0., 0., 70., 4.),
        "active": ("2020-03-20T12:00", 0., 0., 220., 40.),
        "winter_midnight": ("2020-12-21T00:00", 0., 45., 150., 4.),
    }
    date, lon, lat, flux, ap = cases[name]
    h = np.arange(50., 1001., .5)
    output = pymsis.calculate([date], [lon], [lat], h, f107s=[flux],
                             f107as=[flux], aps=[[ap]*7], version=2.1).reshape(-1, 11)
    species_rho = np.nan_to_num(output[:, 1:10]) * MASSES * AMU
    fractions = species_rho / output[:, :1]
    # Normalize small atomic-mass / model convention discrepancies.
    fractions /= fractions.sum(axis=1, keepdims=True)
    return Atmosphere(name, h, output[:, 0].astype(float), fractions,
                      output[:, 10], dict(date=date, longitude_deg=lon, latitude_deg=lat,
                      f107=flux, f107a=flux, ap=ap, version="NRLMSIS 2.1", pymsis=pymsis.__version__))
