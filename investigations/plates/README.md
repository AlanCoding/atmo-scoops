# Parallel plates and the nonlinear constrained optimizer

The preceding rod/pitch study used a finite pattern search. It was not evidence that a nonlinear constrained optimizer had converged, nor that the power-only approximation cured the forward solver. The minimum-five-row rejections concerned thick rods and combined geometries, not a selected 0.2 mm radius.

This investigation uses [parallel-plate coolers](../../modeling/metal_coolers/PLATES.md) and `scipy.optimize.minimize(method="COBYLA")`, with a separate vector of forward-cycle inequality constraints. All resistance is at 100% of the plane-Poiseuille formula, charged as extra compressor electricity; suction pressure is unchanged.

## Solver result

The original run stopped on evaluation 14 with a HEOS pressure-flash error at about 0.008 Pa. A density-based HEOS update fixed that exact case without replacing real-gas caloric properties; it passed the paired resolution check. A second failure involved exactly zero species in a three-species HEOS backend during a near-vacuum implicit-solver trial. Routing to the actual nonzero-species backend fixed it; both resolutions completed with consistent physical infeasibility. This report uses `cobyla_stable`, whose requested vertices were recomputed under both fixes, and preserves both interrupted runs separately.

```json
{
  "success": true,
  "status": 0,
  "message": "Return from COBYLA because the trust region radius reaches its lower bound.",
  "nfev": 99,
  "maxcv": 0.0,
  "objective_days": 277.66077962307116,
  "best_feasible_days": 277.66077962307116
}
```

Logged evaluations: 99. Complete forward cycles: 99. Feasible cycles: 41. Numerical or input failures: 0.

Validated working reference (actual optimizer-history evaluation): 72; **278.019 days** operating-orbit payoff; dry mass **13250.0 t**, product **3509.1 kg/orbit**. This is not delivered circular-apogee payoff.

Added friction electricity: 2.2121 MWh/orbit; ordinary compressor electricity: 3.4260 MWh/orbit. Ratio: **64.6%** across the train, **396.7%** for the front stage.

| Stage | Full thickness, mm | Clear gap, mm | Center pitch, mm | Axial stack depth, m | Initial K |
|---|---:|---:|---:|---:|---:|
| 1 | 1.4351 | 6.1897 | 7.6248 | 0.8964 | 300.006 |
| 2 | 0.9971 | 2.9740 | 3.9711 | 0.0556 | 300.022 |
| 3 | 0.9503 | 3.6034 | 4.5538 | 0.0324 | 300.000 |
| 4 | 1.2717 | 3.5170 | 4.7887 | 0.0233 | 300.000 |
| 5 | 1.2239 | 3.3306 | 4.5545 | 0.0401 | 300.000 |

Optimized controls/capacities: Isp 1794.94 s; burn 1222.83 s; solar 1844347 m²; battery 334.195 MWh; warm store 521.14 t; warm radiator 33624 m² physical panel area. Dive motor ratings [30.9242672582269, 10.114384591313126, 7.949804033914085, 12.999344846599659] MW; coast motor 21.672 MW.

Coordinates at a declared search bound (within 1e-5 in unit coordinates; initial rack temperatures are near the 300 K lower bounds): rack_initial_K:2, rack_initial_K:3, rack_initial_K:4.


Closure residuals (limits: rack 500 J/kg; battery/warm store 100 MJ; chamber gas 0.1 kg / 0.01 MJ; rotors 0.01 MJ; impulse relative 1e-4; gas reserve 0.1 kg/species and 1 MJ):

```json
{
  "rack_enthalpy_J_kg": [
    -0.5005996443651384,
    -0.07226232983521186,
    -0.0638344647741178,
    -0.022961998227401637,
    -0.15060026766150258
  ],
  "battery_MJ": -79.71924919006415,
  "warm_MJ": 17.567344268551096,
  "gas_kg": -0.0020617293630916396,
  "gas_MJ": 0.00017372637785559436,
  "rotor_MJ": 2.177963334762946e-12,
  "thrust_relative": 0.0,
  "reserve_deficit_kg": [
    0.0,
    0.0,
    0.0
  ],
  "gas_reserve_species_kg": [
    3.092281986027956e-11,
    -2.955857780762017e-11,
    -2.2168933355715126e-12
  ],
  "gas_reserve_MJ": 0.5617793481096953
}
```

Minimum scaled constraint margin: -1.4616904e-17.

## Reference selection and resolution check

COBYLA returned evaluation 98 at 277.6608 days. Its refined simulation completed, but battery closure was -103.286 MJ against the unchanged 100 MJ limit (nominal -97.509 MJ). It is therefore not the released reference. We selected the lowest-payoff feasible point from the actual optimizer history with at least 20 MJ nominal reserve inside that limit, without adjusting any inputs. This is a nearby validated feasible design, not the exact returned local optimum. All three resolutions must pass the same physical, closure and conservation gates. The rule is implemented in `plate_reference.py`.

```json
{
  "coarse_to_refined": {
    "passed": true,
    "checks": {
      "two_complete_trajectories": true,
      "conservation_and_nonnegative_inventory": true,
      "resolution_within_half_percent": true,
      "two_feasible_cycles": true
    },
    "relative_changes": {
      "net_liquid_kg": 7.753624694217674e-06,
      "admitted_kg": 3.833312431231617e-06,
      "lost_kg": 5.726081302190437e-06,
      "propellant_kg": 7.0866012841880746e-15
    }
  },
  "refined_to_finer": {
    "passed": true,
    "checks": {
      "two_complete_trajectories": true,
      "conservation_and_nonnegative_inventory": true,
      "resolution_within_half_percent": true,
      "two_feasible_cycles": true
    },
    "relative_changes": {
      "net_liquid_kg": 1.4296279861657291e-05,
      "admitted_kg": 7.173499965603888e-06,
      "lost_kg": 8.870140100346407e-05,
      "propellant_kg": 3.4167541905906547e-15
    }
  },
  "payoffs": [
    278.0185894036864,
    278.0164337686001,
    278.0204084261662
  ],
  "battery_MJ": [
    -79.71924919006415,
    -79.94513165438548,
    -78.08374754339457
  ]
}
```

## Reproduction and scope

The 33 scalar coordinates are five gaps, five full thicknesses, five metal inventories, five initial metal temperatures, solar area, battery energy, warm-store mass, warm-radiator area, plant flow and electrical ratings, four dive motor ratings, coast motor rating, thruster Isp and burn duration. Diameter, length, orbit, suction capacities, compressor head capability, vessel ratings and processing schedule stay fixed. Fixed-thickness mode is also available.

Coordinates are logarithmically scaled to unit bounds. The initial trust-region radius is 0.03 and terminal radius 0.01; the latter is a few percent in some physical dimensions, not a high-precision optimum. Constraint tolerance is 1e-7 in scaled coordinates. The 300-evaluation maximum is an emergency budget, not a success condition. Numerical failures terminate the run explicitly. Each candidate runs once; paired resolution checks are separate validation, not inner closure iterations.

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.staged_search --action baseline --config configs/transient_plates_seed.json --output results/transient/plates/seed --workers 2 --seconds 300
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.plate_optimize --config configs/transient_plates_optimization_seed.json --output results/transient/plates/cobyla_stable --maxiter 300 --tol 0.01 --rhobeg 0.03 --seconds 240
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m atmo_scoops.transient.plate_reference
.venv/bin/python -m atmo_scoops.transient.plate_report
```

Numerical gate `seed`:
```json
{
  "passed": true,
  "checks": {
    "two_complete_trajectories": true,
    "conservation_and_nonnegative_inventory": true,
    "resolution_within_half_percent": true,
    "two_feasible_cycles": true
  },
  "relative_changes": {
    "net_liquid_kg": 0.00015824957875053947,
    "admitted_kg": 5.642935169673814e-05,
    "lost_kg": 0.00014962097383557318,
    "propellant_kg": 6.739983469096074e-15
  }
}
```

Numerical gate `density_probe`:
```json
{
  "passed": true,
  "checks": {
    "two_complete_trajectories": true,
    "conservation_and_nonnegative_inventory": true,
    "resolution_within_half_percent": true,
    "two_feasible_cycles": true
  },
  "relative_changes": {
    "net_liquid_kg": 1.5687186780065458e-05,
    "admitted_kg": 6.344634380938558e-06,
    "lost_kg": 5.6974887515143016e-05,
    "propellant_kg": 8.737015608087459e-16
  }
}
```

Numerical gate `zero_species_probe`:
```json
{
  "passed": false,
  "checks": {
    "two_complete_trajectories": true,
    "conservation_and_nonnegative_inventory": true,
    "resolution_within_half_percent": true,
    "two_feasible_cycles": false
  },
  "relative_changes": {
    "net_liquid_kg": 5.944882491193444e-05,
    "admitted_kg": 2.617370899864672e-05,
    "lost_kg": 0.00012715107112069946,
    "propellant_kg": 1.7474031216174906e-15
  }
}
```

Numerical gate `verify_initialization`:
```json
{
  "passed": true,
  "checks": {
    "two_complete_trajectories": true,
    "conservation_and_nonnegative_inventory": true,
    "resolution_within_half_percent": true,
    "two_feasible_cycles": true
  },
  "relative_changes": {
    "net_liquid_kg": 7.299730928105731e-06,
    "admitted_kg": 3.1409693535353767e-06,
    "lost_kg": 7.222635794064764e-05,
    "propellant_kg": 4.74295133010461e-15
  }
}
```

Numerical gate `verify_final`:
```json
{
  "passed": false,
  "checks": {
    "two_complete_trajectories": true,
    "conservation_and_nonnegative_inventory": true,
    "resolution_within_half_percent": true,
    "two_feasible_cycles": false
  },
  "relative_changes": {
    "net_liquid_kg": 1.1270769899789463e-05,
    "admitted_kg": 5.508338199083659e-06,
    "lost_kg": 4.309833086758707e-05,
    "propellant_kg": 6.081115425279535e-15
  }
}
```

For a publication-oriented inventory of every scalar coordinate, fixed choice and constraint, see [the v1.0 optimization register](../../modeling/optimization/V1_VARIABLES.md).
