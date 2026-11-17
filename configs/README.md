# Configuration status

These are reproducible numerical inputs, not approved physical layouts.

`transient_reference.json` is the new coupled-cycle reference. Run it with `python -m atmo_scoops.transient`; edit installed capacities, stages, schedules and initial states independently. The best tested inputs are in `results/transient/best_config.json`. See [the coupled model](../modeling/primary/TRANSIENT_IMPLEMENTATION.md). Other files below reproduce older scalar/isolated studies.
`limit_case_reference.json` preserves the fixed-allocation investigation. Its
25 m front and 100 m machinery allowance do not establish a packed spacecraft.
See [volume accounting](../modeling/deployment/CLOSE_PASS_VOLUME.md). Do not
present its pressure/altitude boundary as a geometry-feasible design.

`finite_rack_reference.json` is the earlier scalar conditional 30 m-bore reference, with finite wire-rack cooling, explicit folded envelopes and 10 m/s deployment. It is a reduced-model candidate, not an approved hardware layout; see the [investigation](../investigations/altitude_sensitivity/FINITE_RACK_LIMITS.md).

`pcm_melting_reference.json` demonstrates active melting with 5 mm salt-core cells. `pcm_10mm_reference.json` uses a 1 cm outer radius in front and 5 mm interstage cells. These are fixed-orbit sensitivity examples, not replacement reference designs; see the [comparison](../investigations/pcm_racks/ANALYSIS.md).

`liquid_cooling_reference.json` belongs to the standalone `atmo_scoops.liquid_cooling` component model, not `system.simulate`. It contains explicit chamber duties and coolant/hardware inputs; it does not generate payoff.

`ammonia_cold200_reference.json`, `ammonia_cold200_small_reference.json` and `ammonia_warm280_reference.json` are complete primary-model configurations. Their inventories include 10% reserve over the screening trajectories. See the [integrated investigation](../investigations/liquid_cooling/INTEGRATED.md); these are conditional initial comparisons, not global optima.

`reboost_{solid,ammonia,warm_ammonia}_isp_optimum.json` reproduce fixed-orbit Isp minima with nitrogen propellant allowed. They retain the 300 s battery-fed burst; direct-solar arcs are a separate [investigation](../investigations/reboost/README.md).

`chamber_transient_reference.json` is for `python -m atmo_scoops.chambers`, not the primary CLI. It specifies an isolated five-volume transient experiment, including a receiver rack and gas withdrawal. See the [histories](../investigations/chamber_transient/README.md).

`chamber_transient_optimized.json` is the best sampled transient allocation under a declared mass proxy and fixed compressor controls, not a primary-model optimum. It starts at -600 s and uses 2 kg/s coast withdrawal; compare it with the matched baseline in `results/chamber_optimization/`.

`transient_skin_reference.json` is the explicit Cf=0.002 skin-friction scenario with power/thermal capacities proposed before integration. It is an illustrative penalty case, not a calibrated drag estimate or a new all-variable optimum.
