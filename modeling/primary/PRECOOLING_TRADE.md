# Solid-rack precooling trade

Active-model comparison with no nitrogen injection. The gas endpoint changes; metal hot endpoint follows gas minus the fixed 100 K approach. Automatic nominal suction changes with gas state. Actual admission is solved, so it need not remain constant. These rows are not optimized.

| Dry gas | Metal hot | Metal mass | Compressor mass | Dry mass | Net / pass | Payoff | Screens |
|---:|---:|---:|---:|---:|---:|---:|---|
| 650 K | 550 K | 253.92 t | 763.57 t | 3419.67 t | 177.24 kg | 1422.8 d | pass |
| 750 K | 650 K | 81.13 t | 872.54 t | 3242.49 t | 177.25 kg | 1349.0 d | pass |
| 850 K | 750 K | 48.10 t | 984.60 t | 3332.91 t | 177.25 kg | 1386.6 d | pass |
| 1000 K | 900 K | 27.42 t | 1136.91 t | 3501.41 t | 177.25 kg | 1456.7 d | pass |
| 1100 K | 1000 K | 20.63 t | 1244.80 t | 3635.58 t | 177.26 kg | 1512.5 d | FAIL |

Cooler gas changes volume flow and compression work but reduces useful metal heat capacity at fixed cold temperature. The [incremental mixing analysis](../../investigations/incremental_mixing/ANALYSIS.md) adds a distinct liquid-coolant route with full restoration costs.

Reproduce with `.venv/bin/python -m atmo_scoops.studies.current_cycle`; resolved inputs are in [results](../../results/current_cycle.json).
