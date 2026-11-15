# Design conclusions

These documents record decision evidence separately from the single current
[design description](../docs/DESIGN.md). Each preserves numerical scope,
assumptions and reproduction inputs; a conclusion is not a chronological log.

- [Mouth closure](mouth_closure/ANALYSIS.md): omit it. The freely sized cases gain
  no useful recovery benefit, so its mass worsens payoff. The conditional
  exception and limits remain documented with the complete frozen experiment.
- [Incremental nitrogen mixing](incremental_mixing/ANALYSIS.md): thermal and
  compressor trade, coolant restoration and conditional payoff comparison. Mixing
  remains supported pending improved compressor physics.

- [Rear storage depth](rear_storage_depth/INVESTIGATION.md): block power fractions,
  reduced storage pressure, vessel mass, coast work and conditional payoff;
  includes fixed-hull space reallocation and a 10:1 layout diagnostic.

General component calculations and annotated references live in
[model_calculations](../modeling/README.md).
