# Power-only rack resistance in the forward cycle

`design.rack_loss_mode="power_only"` selects the owner's simplified energy
penalty. `"pressure"` retains the pressure-coupled model. The prescribed
`capabilities.rack_loss_multiplier` is not an optimizer coordinate.

At the current chamber state and provisional compressor flow, use the same
laminar-bank coefficient and finite-row exit term as the
[frozen-history calculation](../../investigations/staged_refinement/POWER_ONLY.md):

```
delta_p = alpha K (mdot / frontal_area)^2 / (2 rho)
P_loss = delta_p (mdot / rho) / (eta_compressor eta_motor)
```

There is no reduction of suction pressure, hydraulic root solve or new fluid
property flash. Existing gas properties, compression work, rack heat exchange,
deployment and radiation remain in use. This is an approximate electric-energy
charge, not an exact additional real-gas compression calculation. Large
delta-p/chamber-pressure ratios are permitted deliberately in this simplified
experiment; they do not establish hydraulic feasibility.

## Finite hardware and conservation

The existing compressor map first supplies provisional flow and ordinary power.
If ordinary power plus loss exceeds motor capacity remaining after spin-up,
multiply provisional flow and ordinary power by the available/required ratio.
Recompute the loss charge at that lower flow. At fixed state this loss scales as
a positive quadratic plus cubic in mass flow, so this explicit reduction fits
inside the motor allowance. It is conservative: it can leave spare motor power
compared with solving for maximum permissible flow. It avoids another nested
root solve and is not claimed as a calibrated compressor control law.

For the receiver, apply the same coast-motor reduction to both downstream
branches and divide its rack-loss charge in proportion to their flows. The
propellant booster retains its separate ordinary motor limit.

The shared bus/battery allocator sees the resulting **total** requested power.
If power remains unavailable, it scales flow and paid power proportionally, as
in the existing model; unmet demand is still a feasibility constraint. Within
that interval the paid loss scales proportionally rather than being solved
again, another conservative approximation. No unpaid charge is counted as
available work. Paid loss becomes warm-loop heat; it is not an external energy
sink or added gas enthalpy. This assumes that the added dissipation is rejected
through compressor/warm-loop cooling. Batteries, solar, warm stores, radiators,
volume accounting, reboost, species and periodic closure retain their existing
constraints. Hardware is always compiled before the single forward cycle.

## Geometry and metrics

Five rack pitches can change independently. The radius phase additionally
releases five radii, bounded below by **0.2 mm**, while keeping pitch free.
Search coordinates are radius and pitch/radius ratio; these independently
specify radius and physical pitch. Radius lies in 0.2–5 mm and pitch/radius in
4.01–40 for this bounded study. These are search bounds, not qualified materials
or correlation validity limits. The legacy cooling law is retained. Nominal
solid inventory is preserved by changing rack depth; actual integer-row
rounding, displaced volume, metal mass and deployed footprint are compiled and
charged. Hull diameter, L/D, materials and orbit remain fixed.

The blocked pattern search polls geometry, then propulsion/power/thermal/plant
capacities and five compressor motor ratings. It accepts only feasible complete
cycles. It tests combined favorable hardware directions in a separate cycle.
Its finite search budget is **not** a convergence certificate; unresolved cases
and final resolution gates are reported explicitly.

Five cumulative `rack_loss_i_MJ` ledgers record paid electrical losses.
`loss_power_audit` compares these with ordinary compression electricity, both
for the complete train and per stage. Energy ratios include the entire cycle.
Instantaneous ratios are reported only where ordinary compression exceeds
1 kW, with separate accounting of loss energy below that threshold. Even with
that screen, ratios near zero ordinary head can be enormous; report those
separately from cycle-energy ratios. A 200% loss ratio means loss electricity is
twice ordinary compression electricity, not twice the total including loss.

The pressure-coupled default reference is preserved until this distinct model
and its selected candidates have been reviewed.
