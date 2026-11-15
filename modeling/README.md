# Subsystem modeling research

Research dossiers develop evidence-backed replacement models before code updates. The [design](../docs/DESIGN.md) gives the brief physical architecture; [conclusions](../conclusions/README.md) holds comparative decision evidence; [analysis/primary](../analysis/primary/MODEL.md) describes the currently implemented numerical package. These are distinct roles.

**Priority:** compressor hardware mass and real-gas isentropic efficiency, then finite gas-to-metal heat transfer and their coupled chamber schedules. No new model coefficients or payoff claims are approved merely by filing a reference.

| Subsystem | Research entry point | Status |
|---|---|---|
| Compressor train | [Dossier](compressor/README.md), [requirements](compressor/RESEARCH_REQUIREMENTS.md), [hardware evidence](compressor/COMPARABLE_SYSTEMS.md) | Initial sources and screening arithmetic; mass model unvalidated |
| Metal coolers | [Heat-transfer dossier](metal_coolers/README.md) | Detailed research specification; correlation selection pending |
| Gas composition and real-fluid properties | [Dossier](gas_properties/README.md) | Research stub |
| Inlet, shock, diffuser and leakage | [Dossier](inlet/README.md) | Research stub |
| Pressure chambers, hull and stability structure | [Dossier](structure/README.md) | Research stub |
| Rack deployment, hatches and mechanisms | [Dossier](deployment/README.md) | Research stub |
| Coast refrigeration and liquefaction | [Dossier](liquefaction/README.md) | Research stub |
| Separation, cleanup and product accounting | [Dossier](separation/README.md) | Research stub |
| Cryogenic product storage and transfer | [Dossier](liquid_storage/README.md) | Research stub |
| Warm heat exchangers, fluid loops and radiators | [Dossier](warm_loop/README.md) | Research stub |
| Solar generation and repeatable deployment | [Dossier](solar/README.md) | Research stub |
| Batteries, motors and power distribution | [Dossier](electrical/README.md) | Research stub |
| Oxygen propulsion and orbital restoration | [Dossier](propulsion/README.md) | Research stub |
| Leading edge, hull heating and reusable materials | [Dossier](aerothermal/README.md) | Research stub |
| Nitrogen mixing and film cooling | [Dossier](mixing/README.md) | Research stub |
| Stability, attitude and flexible-body dynamics | [Dossier](stability/README.md) | Research stub |
| Orbit, atmosphere, export and lifetime | [Dossier](mission/README.md) | Research stub |

Each dossier follows the [review workflow](WORKFLOW.md): source evidence → state/geometry model → validation and uncertainty → explicit numerical handoff. Stubs are real files so every subsystem has a research home. The existing program remains unchanged.
