# Fixed rack-allocation probe results

These are unchanged-hardware perturbations around the refined v1.0.1 cycle, not reoptimized designs. See [method](README.md).

| Case | Rack mass t | Dry mass t | Liquid kg/cycle | Diagnostic days | Feasible | Runtime s |
|---|---:|---:|---:|---:|---|---:|
| baseline | 453.192 | 12840.222 | 3085.886172 | 306.398724 | True | 71.2 |
| rack_minus_1pct | 448.660 | 12833.250 | 3085.765417 | 306.244337 | True | 75.1 |
| rack_plus_1pct | 457.724 | 12847.194 | 3086.005960 | 306.553196 | True | 78.9 |

A diagnostic payoff is arithmetic from this single cycle. All three probes pass the current model feasibility checks, but only the baseline remains the published reference; no optimization or new design release is claimed. Small negative constraint values within numerical roundoff are listed in raw summaries but are not engineering failures.

## Closure response

| Case | Battery MJ | Heat buffer MJ | Receiver fill error Pa | Reserve mass error kg | Reserve energy MJ | Max rack enthalpy error J/kg |
|---|---:|---:|---:|---:|---:|---:|
| baseline | -0.0000 | 0.6874 | 44.9492 | -0.010006 | 0.124474 | 0.067 |
| rack_minus_1pct | -0.0000 | 0.6874 | 49.6319 | 0.108818 | 0.935484 | 0.129 |
| rack_plus_1pct | -0.0000 | 0.6874 | 40.4205 | -0.100554 | -0.665209 | 0.131 |

## Full constraint and provenance records

- [baseline summary](../../results/transient/reduced_coordinates/baseline_summary.json), [exact inputs](../../results/transient/reduced_coordinates/baseline_config.json).
  Materially negative normalized constraints: none.
- [rack_minus_1pct summary](../../results/transient/reduced_coordinates/rack_minus_1pct_summary.json), [exact inputs](../../results/transient/reduced_coordinates/rack_minus_1pct_config.json).
  Materially negative normalized constraints: none.
- [rack_plus_1pct summary](../../results/transient/reduced_coordinates/rack_plus_1pct_summary.json), [exact inputs](../../results/transient/reduced_coordinates/rack_plus_1pct_config.json).
  Materially negative normalized constraints: none.

## Interpretation

The ±1% response is smooth at this tested scale: less total rack mass reduces dry mass and payoff slightly, while useful liquid changes by only about 0.12 kg/orbit. All three full integrations completed in 71–79 seconds. This is local evidence, not a guarantee across a broad design search.

The −1% case has receiver fill error +49.632 Pa against a ±50 Pa requirement and reserve energy residual +0.935 MJ against a ±1 MJ requirement. Its summed reserve mass discrepancy is 0.109 kg; the implemented closure criterion applies separately to each species (0.1 kg each), which is why it passes. Do not interpret this as an exactly periodic solution or a comfortable engineering margin.

A sensible next small outer solve can retain fixed rack fractions and add the already-existing fill/reserve closure coordinates (perigee, initial reserve mass and temperature), with explicit numerical reserve inside the original tolerances. This is a proposed experiment, not implemented here. Keep independent rack temperatures, geometry and hardware capacities fixed until measured residuals require otherwise. Thermal rack enthalpy residuals stayed below 0.14 J/kg versus the 500 J/kg criterion; battery and heat-buffer closure did not drive this local response.

No forward-cycle equations or tolerances were changed. Existing original inputs, solver and publication figures remain untouched.
