# Electrical bus, rack mechanisms and mass contingency

Values below refer to the 285-day, zero-external-skin-friction comparison case
in `results/transient/best.json`. These are **allowances**, not completed hardware
bills of materials. `transient/hardware.py` contains their definitions.

| Budget entry | Calculation | Mass | Intended scope and current limit |
|---|---|---:|---|
| `bus` | 900 MW × 1 kg/kW | 900 t | Electrical conditioning/distribution allowance: power converters, switching, protection, cabling and controls. This is not the entire spacecraft platform. No voltage, cable routing, conductor sizing or itemized converter design has established this coefficient. |
| `rack_mechanisms` | 460,872 m² deployment footprint × 1 kg/m² | 460.9 t | Deployment/retraction support and mechanisms, distinct from the 452.3 t of thermally active rods. Intended to cover supports, guides, attachments, actuators and associated deployable structure. It does not establish that pressure hatches, seals and repeated-cycle mechanisms have been structurally sized. |
| `margin` | 25% × 11,213.9 t pre-margin subtotal | 2,803.5 t | Unallocated mass contingency. It is 20% of the final 14,017.4 t total, because it is applied to the subtotal. It is not a physical component and not an uncertainty confidence interval. |

The mechanisms use **deployment footprint**, not rod wetted/emitting area.
For the current rod representation the footprint is derived from solid volume,
rod radius and pitch; it is not an independently invented area.

## Boundaries that need refinement

- The compressor bank separately includes motor mass; the thruster has a separate
  2 kg/kW allowance. Neither currently has a sufficiently detailed BOM to prove
  that motor drives or thruster PPUs are disjoint from the electrical bus.
  A proposed accounting boundary is: bus = common distribution/conditioning;
  compressor = motor plus dedicated drive; thruster = discharge hardware plus
  dedicated PPU. Refit coefficients to that boundary instead of counting both.
- Bus conversion/resistive losses are not independently modeled. Battery and
  compressor motor losses are; these do not stand in for bus losses. Add the
  missing electrical heat and recharge demand, not just more electrical mass.
- Mechanism mass is not a resolved torque, tension, acceleration or lifetime
  calculation. Resolve panel/rack supports and pressure hatches, then replace
  the area coefficient with named items. Existing vessel/head and auxiliary
  allowances must not be counted again without checking their intended scope.
- Margin adds dry mass but does **not** reserve additional folded package volume.
  Add geometric/layout reserve before claiming a fully packed manufacturing
  design. A mass contingency cannot cover an omitted drag force or heat load:
  those must enter their governing balances explicitly.

For Blender, show actual candidate components and labeled clearance/envelope
reservations. Do not render a 2,803 t 'margin component', or draw 900 t of cable
as though the electrical design had already selected that material quantity.
