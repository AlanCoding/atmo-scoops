# Modeling and analysis

Research dossiers develop evidence-backed replacement models before code updates. The [design](../docs/DESIGN.md) gives the brief physical architecture; [investigations](../investigations/README.md) holds comparative decision evidence; [modeling/primary](../modeling/primary/MODEL.md) describes the currently implemented numerical package. These are distinct roles.

## Numerical model and studies

- [Primary model](primary/MODEL.md) and [input parameters](primary/PARAMETERS.md).
- [Altitude sensitivity](../investigations/altitude_sensitivity/ANALYSIS.md): 50–150 km with the current compressor.
- [Optimization](optimization/RESULTS.md).
- [Detailed fluid studies](fluid/README.md), outside the optimizer.
- [Flight stability study](stability/FLIGHT_STUDY.md) and [stability research](stability/README.md).

## Close-pass packing research

Start with the [allocation specification](deployment/CLOSE_PASS_VOLUME.md) and
[reference-based packing screen](deployment/PACKING_SCREEN.md). Solar, radiator,
battery and compressor dossiers now separate material volume, package envelope
and installed clearance. The earlier fixed-length limit case is not a packed
vehicle reference.

## Subsystem research

**Priority:** compressor hardware mass and real-gas isentropic efficiency, then finite gas-to-metal heat transfer and their coupled chamber schedules. No new model coefficients or payoff claims are approved merely by filing a reference.

| Subsystem | Research entry point | Status |
|---|---|---|
| Compressor train | [Dossier](compressor/README.md), [requirements](compressor/RESEARCH_REQUIREMENTS.md), [hardware evidence](compressor/COMPARABLE_SYSTEMS.md) | Real-fluid state solution and conditional geometry mass implemented; low-Re maps unvalidated |
| Metal coolers | [Heat-transfer dossier](metal_coolers/README.md) | Detailed research specification; correlation selection pending |
| Gas composition and real-fluid properties | [Dossier](gas_properties/README.md) | Research stub |
| Inlet, shock, diffuser and leakage | [Dossier](inlet/README.md) | Research stub |
| Pressure chambers, hull and stability structure | [Dossier](structure/README.md) | Research stub |
| Rack deployment, hatches and mechanisms | [Dossier](deployment/README.md) | Packaging sources and allocation equations; integration pending |
| Coast refrigeration and liquefaction | [Dossier](liquefaction/README.md) | Research stub |
| Separation, cleanup and product accounting | [Dossier](separation/README.md) | Research stub |
| Cryogenic product storage and transfer | [Dossier](liquid_storage/README.md) | Research stub |
| Warm heat exchangers, fluid loops and radiators | [Dossier](warm_loop/README.md) | Packaging sources and allocation equations; integration pending |
| Solar generation and repeatable deployment | [Dossier](solar/README.md) | Packaging sources and allocation equations; integration pending |
| Batteries, motors and power distribution | [Dossier](electrical/README.md) | Packaging sources and allocation equations; integration pending |
| Oxygen propulsion and orbital restoration | [Dossier](propulsion/README.md) | Research stub |
| Leading edge, hull heating and reusable materials | [Dossier](aerothermal/README.md) | Research stub |
| Nitrogen mixing and film cooling | [Dossier](mixing/README.md) | Research stub |
| Stability, attitude and flexible-body dynamics | [Dossier](stability/README.md) | Research stub |
| Orbit, atmosphere, export and lifetime | [Dossier](mission/README.md) | Research stub |

Each dossier follows the [review workflow](WORKFLOW.md): source evidence → state/geometry model → validation and uncertainty → explicit numerical handoff. Stubs are real files so every subsystem has a research home. The compressor dossier now includes the first implemented replacement and paired cycle results; other dossiers retain their stated research status.
