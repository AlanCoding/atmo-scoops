# Detailed fluid analysis

Purpose: resolve flow for a selected spacecraft configuration, including the
mouth/shock/throat, solid cooler, compressor boundary and external body. This is
an offline analysis area. The detailed solver has not been integrated here;
the primary model's `open_mouth.py` is only a reduced boundary approximation.

## Inputs and studies

Use a frozen public-API input JSON and a named geometry revision. Add edge radius,
throat area/distribution, diffuser shape, rack channels, walls, fin/aft geometry,
wall thermal/cooling conditions and compressor flow/pressure boundary. Supply
the atmospheric trajectory and gas composition from the primary encounter code.

Run selected times and transient sequences for inlet startup, sustained pumping,
outbound pressure decay, reverse flow and compressor cutoff. Map
pressure, temperature, species, velocity, wall heat/shear and net mass flux on
signed control surfaces. Resolve the location and direction of leakage directly.
Check continuum/rarefied and chemical-relaxation validity rather than choosing a
solver solely because it is available.

For exterior flow, include angle of attack/sideslip and rotational-rate cases
requested by [stability](../stability/README.md). Integrated force and moment,
not only attractive flow images, are required outputs.

## Interface back to the primary model

The dependency is:

`primary candidate → frozen fluid case → verified coefficient table → explicit
primary-model calibration → optimization`.

The optimizer never starts the fluid solver. It consumes only small reviewed
maps/correlations with: geometry/configuration identifiers; units and reference
areas; flow/thermal regime; independent coordinates and valid bounds; uncertainty;
conservation and grid/time-convergence evidence; interpolation rules; and source
case IDs. Extrapolation must be rejected or explicitly flagged.

Candidate outputs include capture efficiency, support pressure relative to
`rho*u²`, pressure-loss/conductance maps, leakage conductance, start/unstart
limits, heat-flux distributions and body force/moment coefficients. A single
coefficient is acceptable only if the study establishes its applicable range.
Keep each fluid case's inputs, mesh, raw fields and validation separate from
primary-model results. Do not restore obsolete spacecraft assumptions when
reusing numerical solver infrastructure.
