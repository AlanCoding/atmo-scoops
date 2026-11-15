# Solid-rack precooling trade

Active-model comparison with no nitrogen injection. The gas endpoint changes; metal hot endpoint follows gas minus the fixed 100 K approach. Automatic nominal suction changes with gas state. Actual admission is solved, so it need not remain constant. These rows are not optimized.

| Dry gas | Metal hot | Metal mass | Compressor mass | Dry mass | Net / pass | Payoff | Screens |
|---:|---:|---:|---:|---:|---:|---:|---|
| 650 K | 550 K | 253.94 t | 280.36 t | 2711.25 t | 177.25 kg | 1128.0 d | pass |
| 750 K | 650 K | 81.13 t | 321.56 t | 2438.27 t | 177.26 kg | 1014.4 d | pass |
| 850 K | 750 K | 48.10 t | 362.75 t | 2428.82 t | 177.26 kg | 1010.4 d | pass |
| 1000 K | 900 K | 27.42 t | 424.53 t | 2469.07 t | 177.26 kg | 1027.1 d | pass |
| 1100 K | 1000 K | 20.63 t | 465.72 t | 2509.08 t | 177.27 kg | 1043.8 d | pass |

Cooler gas changes volume flow and compression work but reduces useful metal heat capacity at fixed cold temperature. The [incremental mixing analysis](../../conclusions/incremental_mixing/ANALYSIS.md) adds a distinct liquid-coolant route with full restoration costs.

Reproduce with `.venv/bin/python -m atmo_scoops.studies.current_cycle`; resolved inputs are in [results](../../results/current_cycle.json).
