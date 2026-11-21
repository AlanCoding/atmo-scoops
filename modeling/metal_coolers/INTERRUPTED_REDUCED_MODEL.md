# Offset plates: separate hydraulic and thermal spacing

The accepted approximation is **wide physical channels with a smaller effective
thermal spacing**, paid for with additional rack length and chamber volume.
This is an adopted reduced-model assumption, not a validated offset-fin
correlation. It replaces the earlier wide-channel thermal coefficient plus a
small entrance correction for this investigation.

## Geometry and inventory

Let t be plate thickness, n the number of serial rows, g_T the effective thermal
clearance, and p_H the physical pitch in each row:

```
p_H = n (t + g_T)
g_H = p_H - t
g_T = p_H / n - t
V_metal = A L t / p_H
A_wetted = 2 V_metal / t
```

At fixed metal inventory and thickness, increasing pitch by n requires n times
the plate-bearing length L. Each row then has the original panel length and
1/n as many plates across the section. Successive rows have transverse offsets
`j p_H/n`, j=0…n−1: all n phases are represented. Simply alternating two offsets
is not the geometrical basis for n-way thermal equivalence.

The model charges the complete longer core plus explicit inter-row clearances
to its gas chamber and subtracts this occupied length from the aft receiver.
It does not multiply metal mass, heat capacity, wetted area or radiating area.
The compiled geometry exports physical gap, effective thermal gap and row offsets.

## Heat transfer and friction

With `plate_thermal_model="offset_equivalent"`, the continuum coefficient is
`h_c = 7.54 k/(2 g_T)`. The existing molecular-accommodation resistance remains in
series, and Biot number uses the resulting coefficient. No developing-entry
heat enhancement is added on top of the thermal-equivalence credit. The existing
five lumped gas/solid inventories and coast cooling treatment remain in place;
spatial mixing, individual row temperatures and stagnant-gas diffusion are not
resolved by this approximation.

Flow area, velocity, hydraulic Reynolds/Knudsen numbers and shear friction use
**g_H**, never g_T. The pressure-loss surrogate retains the full physical length:

```
delta_p = 12 mu L u / g_H² + (n−1) K_restart rho u²/2
```

The retained K_restart=0.674 is a provisional entry-loss scale, not a calibrated
offset-edge coefficient. As previously agreed, pressure loss is charged to
compressor electricity/heat and finite power limits; it does not solve the actual
hydraulic pressure field. Report large delta_p/absolute-pressure ratios explicitly.

The [parallel-channel entry analysis by Muzychka and Yovanovich (2009)](https://www.researchgate.net/publication/224399646_Pressure_Drop_for_Laminar_Flow_in_Microchannels_of_Arbitrary_Cross-Sections)
provides an entry-loss reference scale. It does **not** establish this assumed
thermal equivalence. Detailed flow studies must test the equivalent thermal
spacing and the actual turning losses together.

## Optimization coordinates and constraints

For this mode, the five gap coordinates are **effective thermal clearances**.
The optimizer still chooses five sheet thicknesses and five metal inventories;
physical gaps and complete rack lengths are derived from them and the fixed row
count. This avoids an independent, cost-free thermal-spacing knob and prevents
negative equivalent clearance when thickness changes. There are still 33 search
coordinates. Four rows are fixed for the first comparison, not optimized.

Old `developing` mode remains available solely for reproduction. Its model used
physical gap for heat transfer with a small repeated-entry correction, based on
[Martin and Rhea (2002)](https://www.sciencedirect.com/science/article/pii/S0017931002000285).
The earlier ~423-day wide-pitch comparison and ~278-day compact warm-start search
used that different thermal assumption and do not answer the corrected question.

## Checkpoint packing and numerical controls

Use `configs/transient_staggered_thermal_seed.json`: fourfold pitch and core
length preserve the frozen reference's thermal clearances, mass and area. The
10 m front clear space, actual compressor lengths, and 1 m hatch buffers remain.
Other equipment remains charged to aft displacement pending the separate
125 m reserve/packaging checkpoint. No equipment mass disappears.

The seed starts evacuated, consistent with the end-of-cycle purge, and uses
absolute integration tolerance 1e-10. Vacuum temperature regularization remains
separate from physical gas inventory. Validate at finer resolution before any
optimization result is accepted. The frozen v1.0 reference is unchanged.
