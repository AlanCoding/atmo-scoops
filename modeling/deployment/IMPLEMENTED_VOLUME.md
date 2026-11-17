# Implemented close-pass volume and timing

The main `system.simulate` API now enables finite racks and packaging by default.
`racks.enabled=false` preserves the prescribed-temperature calculation for
historical regression. `packaging.enabled=false` disables the new packaging
screen; neither switch describes the current reference design.

There is no active fixed 100 m machinery bay. The hull length is built from:

1. Front depth, at least large enough for its working rack, with solid metal
   removed from available gas volume.
2. Independent intermediate working-rack envelopes, with gas in their pores.
3. Equipment package volumes divided by the declared installation fill fraction
   and inner cross-sectional area.
4. Rear physical depth including ellipsoidal heads.

Compressor package envelopes use module diameters, counts and computed row
lengths, plus separate motor volume. Smaller banks may share axial allocation
with other equipment; the code does not charge every bank a full-bore cylinder.
This is a volume allocation screen, not a collision-free CAD arrangement. Routing,
pressure bulkheads, hatches, structural load paths and inaccessible voids still
need an installed-layout design. Surface/TPS mass follows the derived total
length. The old `machinery_depth_m` input is ignored in this active path.

## Serialized packaging capabilities

| Item | Reference | Evidence/status |
|---|---:|---|
| Solar package | 40 kW/m³ | Approximate ROSA manufacturer figure; [dossier](../solar/PACKAGING.md) |
| Warm radiator | 0.02 m stack pitch per m² physical panel | Explicit engineering assumption; no qualified package coefficient found |
| Liquefaction, exchangers, motors, propulsion/distribution, deployment mechanisms | 250 kg/m³ installed package | Explicit bulk-envelope scenario; **not** solid material density or measured scoop hardware |
| Battery | 280 kWh/m³, with 1800 kg/m³ mass-envelope floor | Module figures bracket energy density; complete installation remains provisional |
| Warm heat buffer | 800 kg/m³ | Bulk-envelope assumption |
| Compressor module packing | 0.75 | Geometric installation assumption |
| Equipment bay fill fraction | 0.70 | Extra installation space; does not include chamber gas |
| Deployment/retraction speed | 10 m/s | Owner's reference capability |

All are inputs in `packaging`. A result controlled by the 250 kg/m³ scenario is
not a fundamental material or altitude limit. In particular, existing thrust
and distribution mass assumptions can produce very large package demands.
The study must report those contributions rather than hide them in a bay length.

Liquid storage is allocated for the batch, allowing ullage. Separate solar,
warm radiator and rack deployment footprints are reported. Rack deployment
hardware is included by mass and packaging; working metal envelopes are counted
once in their chambers. The separate equipment bay does not include rack pores.

## Deployment coupling

For each deployed system:

```
travel time = travel_over_sqrt_area * sqrt(physical area) / deployment_speed
```

The reference uses one simultaneous, conservative deployment schedule governed
by the slowest of the three systems. Processing and full sunlight/radiator credit
start only after it finishes, and stop before retraction. Optional fixed deployment
and retraction inputs act as minimum mechanism times; their defaults are zero.
The solar-area/coast-duration coupling is iterated to a fixed point. An orbit
without sufficient deployment/coast/retraction time is rejected. This does not
model progressive illumination or radiation during partial extension, tether
loads, acceleration or flexible dynamics. It charges finite travel time without
claiming an independently scalable number of deployment modules.

## Limits

Default screens enforce L/D ≤ 10 and warm rear-storage pressure ≤ 110,000 Pa.
That pressure is the retained **1 bar liquefaction-feed reference plus 10%**, not
a claim that every liquefaction process requires exactly 1 bar. Pure N2 and O2
phase boundaries and a complete air-separation train are distinct constraints.
Operating-orbit payoff remains separate from unimplemented circular-apogee export.
