# Modeling and analysis

Research dossiers develop evidence-backed replacement models before code updates. The [design](../docs/DESIGN.md) gives the brief physical architecture; [investigations](../investigations/README.md) holds comparative decision evidence; [modeling/primary](../modeling/primary/MODEL.md) describes the currently implemented numerical package. These are distinct roles.

## Numerical model and studies

- [Mass allowance boundaries](primary/MASS_ALLOWANCES.md) and [ordered refinement plan](../docs/NEXT_REFINEMENTS.md).

- [Coupled forward-cycle implementation](primary/TRANSIENT_IMPLEMENTATION.md): installed hardware, state-resolved compression/cooling, finite power and plant, closure checks; [initial results](../investigations/transient/RESULTS.md).

- [Scalar coupled-search scope](primary/SCALAR_SEARCH_SCOPE.md): fixed diameter/L/D, recommended temporary locks, and individual optimizer inputs with reference seeds.

- [Primary model](primary/MODEL.md) and [input parameters](primary/PARAMETERS.md).
- [Periodic optimization specification](primary/TRANSIENT_OPTIMIZATION_SPEC.md): independent design/control/initial-state coordinates, net-liquid payoff, closure equations and path constraints.
- [Coupled transient primary-model plan](primary/TRANSIENT_MODEL_PLAN.md): one forward cycle per candidate, installed capacities as design inputs, and external optimization; first implementation now available.
- [Altitude sensitivity](../investigations/altitude_sensitivity/ANALYSIS.md): 50–150 km before finite racks and packaging constraints.
- [Optimization](optimization/RESULTS.md).
- [Detailed fluid studies](fluid/README.md), outside the optimizer.
- [Flight stability study](stability/FLIGHT_STUDY.md) and [stability research](stability/README.md).

## Finite racks and close-pass packing

The primary model now implements [finite rack heat transfer](metal_coolers/FINITE_RACK_MODEL.md)
with [optional PCM cores](metal_coolers/PCM_MODEL.md),
and [volume/deployment accounting](deployment/IMPLEMENTED_VOLUME.md). The
[updated constrained cases](../investigations/altitude_sensitivity/FINITE_RACK_LIMITS.md)
replace the old fixed-bay interpretation.

Research background: the [allocation specification](deployment/CLOSE_PASS_VOLUME.md) and
[reference-based packing screen](deployment/PACKING_SCREEN.md). Solar, radiator,
battery and compressor dossiers now separate material volume, package envelope
and installed clearance. The earlier fixed-length limit case is not a packed
vehicle reference.

## Subsystem research

**Priority:** compressor hardware mass and real-gas isentropic efficiency, then finite gas-to-metal heat transfer and their coupled chamber schedules. No new model coefficients or payoff claims are approved merely by filing a reference.

| Subsystem | Research entry point | Status |
|---|---|---|
| Compressor train | [Dossier](compressor/README.md), [requirements](compressor/RESEARCH_REQUIREMENTS.md), [hardware evidence](compressor/COMPARABLE_SYSTEMS.md) | Real-fluid state solution and conditional geometry mass implemented; low-Re maps unvalidated |
| Metal coolers | [Heat-transfer dossier](metal_coolers/README.md) | Finite convection/capacity and geometric volume implemented; correlation validation pending |
| Gas composition and real-fluid properties | [Dossier](gas_properties/README.md) | Research stub |
| Inlet, shock, diffuser and leakage | [Dossier](inlet/README.md) | Research stub |
| Pressure chambers, hull and stability structure | [Dossier](structure/README.md) | Research stub |
| Rack deployment, hatches and mechanisms | [Dossier](deployment/README.md) | Package-volume and motion-time screen implemented; installed-layout/lifetime validation pending |
| Coast refrigeration and liquefaction | [Dossier](liquefaction/README.md) | Research stub |
| Separation, cleanup and product accounting | [Dossier](separation/README.md) | Research stub |
| Cryogenic product storage and transfer | [Dossier](liquid_storage/README.md) | Research stub |
| Warm heat exchangers, fluid loops and radiators | [Dossier](warm_loop/README.md) | Package-volume and motion-time screen implemented; installed-layout/lifetime validation pending |
| Solar generation and repeatable deployment | [Dossier](solar/README.md) | Package-volume and motion-time screen implemented; installed-layout/lifetime validation pending |
| Batteries, motors and power distribution | [Dossier](electrical/README.md) | Package-volume and motion-time screen implemented; installed-layout/lifetime validation pending |
| Oxygen propulsion and orbital restoration | [Dossier](propulsion/README.md) | Research stub |
| Leading edge, hull heating and reusable materials | [Dossier](aerothermal/README.md) | Research stub |
| Nitrogen mixing and film cooling | [Dossier](mixing/README.md) | Research stub |
| Stability, attitude and flexible-body dynamics | [Dossier](stability/README.md) | Research stub |
| Orbit, atmosphere, export and lifetime | [Dossier](mission/README.md) | Research stub |

Each dossier follows the [review workflow](WORKFLOW.md): source evidence → state/geometry model → validation and uncertainty → explicit numerical handoff. Stubs are real files so every subsystem has a research home. The compressor dossier now includes the first implemented replacement and paired cycle results; other dossiers retain their stated research status.

- [Once-through liquid cooling](liquid_cooling/README.md): standalone sizing plus the [integrated ammonia option](liquid_cooling/INTEGRATED_MODEL.md) and its gas/compressor/regeneration coupling.

- [Transient chamber laboratory](chambers/README.md): separate mass/energy states, independently allocated rack and empty volumes, and coast withdrawal; outside the primary optimizer.
- [Per-rack material properties](chambers/MATERIALS.md): sourced caloric data, surface assumptions and thermal-reset screening in the isolated transient model.
