# Active optimization model

The optimizer calls the same continuous open-inlet `system.simulate` as the CLI.
Its objective is operating-orbit dry mass divided by net daily new liquid;
circular-apogee delivery remains excluded.

`atmo_scoops.optimization.search.BOUNDS` defines 17 coordinates, or 15 at fixed
orbit: physical depths and diameters, perigee/apogee, dry gas/rack temperature,
metal cold temperature and approach, sheet thickness, intermediate pressure,
warm-radiator temperature, Isp and thrust duration, installed suction multiplier
and commanded cutoff. The nominal pressure-sizing factor is fixed to avoid
optimizing two redundant capacity controls. Mixing ratio/path are held at the
configuration values; the dedicated incremental study compares ratios with
identical control freedom.

The layout family retains front bore >= mouth and a 520 m overall-length bound.
Oxygen reserve can be imposed separately. Hardware, atmosphere and capability
assumptions remain fixed. Finite-thrust, cooler conductance and physical pump/inlet
maps are unresolved, so a feasible numerical point is not a qualified spacecraft.

```sh
.venv/bin/python -m atmo_scoops.optimization.search --mode fixed_orbit --iterations 100 --seeds 11 29
.venv/bin/python -m atmo_scoops.optimization.search --mode free_orbit --iterations 100 --seeds 11 29
```

No new full-geometry optimum is claimed for this revised model. The earlier
geometry-search inputs and results remain in the frozen source/data snapshot
under [conclusions](../../conclusions/README.md); `configs/candidate_geometry.json`
is a geometry comparison input, not an optimum of the current equations.
Current controlled design studies are indexed in [conclusions](../../conclusions/README.md).
