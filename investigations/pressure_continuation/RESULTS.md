# Pressure continuation: numerical results

This is an exploratory v1.0.2 study, not a new version release. See [input groups and method](README.md). v1.0.1 remains the accepted 306.398724-day reference.

| Case | Perigee km | Target kPa | Rack mass t | Dry mass t | Liquid kg/orbit | Diagnostic days | Feasible |
|---|---:|---:|---:|---:|---:|---:|---|
| p105 seed | 85.521907 | 5.005174 | 475.852 | 13410.510 | 3209.6469 | 307.659257 | False |
| p105 selected | 85.653797 | 5.005174 | 475.852 | 13351.926 | 3167.1662 | 310.427929 | True |
| p110 seed | 85.252811 | 5.243516 | 498.511 | 13982.227 | 3329.8690 | 309.185639 | False |

The seed hardware scales with the intended larger atmospheric batch. During restoration, hardware scale stays fixed while perigee and initial reserve state vary; actual admitted mass need not retain the exact seed scaling. These points are **not payoff-optimized**, and a failed seed does not disprove a pressure target. Structural ratings scale too, so higher pressure is not free tank capacity.

## Collection and closure

| Case | Capture % | Fill error Pa | Reserve mass error kg | Reserve energy error MJ | Battery error MJ |
|---|---:|---:|---:|---:|---:|
| p105 seed | 99.980063 | 96.974049 | 30.458996 | -0.279108 | -0.000024 |
| p105 selected | 99.979749 | 0.005459 | 0.006027 | -0.000752 | -0.000002 |
| p110 seed | 99.980804 | 154.749640 | 64.422346 | -0.725680 | -0.000030 |

Original constraints remain: 99.9% collection minimum, ±50 Pa fill error, 0.1 kg per reserve species, ±1 MJ reserve energy, plus all thermal, electrical, structural and conservation checks. Collection fraction is admission from the modeled incident supply, not delivered-liquid yield.

## Local coupling diagnostic

Initial finite-difference Jacobian for the +5% seed:

| Scaled residual | Perigee / 1 km | Reserve mass / 1,000 kg | Reserve temperature / 100 K |
|---|---:|---:|---:|
| Fill error / 100 Pa | -6.62306 | 5.23098 | 1.93847 |
| Reserve mass error / 100 kg | -2.97691 | -4.29547 | -1.66731 |
| Reserve energy error / 10 MJ | -1.33928 | 0.16800 | -18.45726 |

The two-norm condition number is **3.647 under these explicitly chosen scales**. This indicates a locally distinguishable three-coordinate restoration direction, not universal numerical robustness; different units/scales change the condition number.

## Restoration termination

Least-squares success flag: **False**. Message: The maximum number of function evaluations is exceeded.. Outer function evaluations: **4**; total recorded forward configurations including derivative probes: **16**. Feasibility of the selected point: **True**. This is a closure restoration, not constrained payoff optimization.

## Independent tighter replay

Halving relative tolerance and maximum integration step gives **310.428510 days**, a difference of **+0.000581 days**. Feasible: **True**. [Replay summary](../../results/transient/pressure_continuation/p105/replay_summary.json) and [inputs](../../results/transient/pressure_continuation/p105/replay_config.json).

## Scope and numerical evidence

The initial process-pool launcher failed because the sandbox disallowed its forkserver socket. No derivative cycle was run by that launcher. The replacement uses subprocess workers; this infrastructure failure is not a numerical instability or rejected physical design. Each completed cycle and input is logged.

The seed trials isolate a practical partition: rack/material allocation can remain fixed while total thermal inventory scales; fill and reserve restoration use three dedicated outer coordinates. Compressor-chain and power/thermal groups are promising independent sizing subproblems, but still exchange boundary histories and physical package volume. No claim of independent subsystem optima is made.

### Artifacts

- [p105 seed summary](../../results/transient/pressure_continuation/p105/seed_summary.json).
- [p105 selected summary](../../results/transient/pressure_continuation/p105/selected_summary.json).
- [p110 seed summary](../../results/transient/pressure_continuation/p110/seed_summary.json).
- [Restoration evaluations](../../results/transient/pressure_continuation/p105/evaluations.json).
