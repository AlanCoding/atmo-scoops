# One-off plate thickness / clearance sensitivity — planned, not run

Freeze the verified plate reference (`configs/transient_plates_reference.json`,
COBYLA-history point 72) as the geometry anchor. Run three matched cases:

| Case | Every stage's full thickness | Every stage's clear gap |
|---|---|---|
| 1× control | reference | reference |
| 2× | twice reference | twice reference |
| 4× | four times reference | four times reference |

“Bigger sheets” here means thickness, not changing each deployed panel's lateral
dimensions. Keep the common scaling across all five stages, but preserve their
existing differences. Both dimensions are **fixed within each search**; optimize
the other 23 current coordinates, including inventories, initial temperatures,
compressor motor ratings, power/thermal capacities, Isp and burn duration. Do not
let the optimizer undo the experiment by shrinking gap or thickness.

Use a small investigation-local driver calling the existing model/COBYLA
interfaces. No new production-model parameter or default geometry. The 4× front
plate is about 5.74 mm, above the earlier 5 mm *search bound*: explicitly allow
that fixed study input rather than silently clipping it. Preserve all actual
material, thermal, volume and Reynolds constraints.

Use the same physical bounds for all remaining coordinates, same solver settings
and capability assumptions, and the same 20 MJ nominal reserve within the 100 MJ
battery closure tolerance. Include that reserve in the constraints for **all
three cases**, rather than selecting it after optimization. Use the same input
seed inventories; scaling thickness and gap together preserves porosity, so
unchanged depth initially preserves metal mass. Let inventories/depths then move.
Hold hull, orbit, schedule and other currently fixed capabilities fixed.

Report raw solver status, complete/failed evaluations, feasibility and binding
constraints. A budget stop is not convergence; a numerical failure is not physical
infeasibility. Verify each selected result at three resolutions and retain the
exact inputs and termination records. Compare payoff, dry mass, gas/product,
metal mass/envelope, deployment area/time, compressor and friction electricity,
peak ratings, battery, solar, warm-loop mass and stage P/T/Re/Kn/Bi diagnostics.

At fixed inventory and flow state, scaling both dimensions by s leaves porosity
unchanged, reduces surface area by 1/s and plane-Poiseuille pressure drop by
1/s². The continuum conductance also falls roughly as 1/s² (h ~ 1/g and area ~
1/t), while radiation area falls as 1/s. These are starting sensitivities, not
predictions of the reoptimized outcome. Real-gas states, inventory allocation,
molecular heat-transfer resistance and closure will change the result.

Do not update the working reference automatically. Publish this as a one-off
comparison and decide whether a different geometry deserves adoption afterward.
