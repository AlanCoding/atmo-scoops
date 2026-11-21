# Numerical controls and checkpoint evidence

The corrected thermal-spacing search uses actual SciPy COBYLA with 33 continuous
coordinates, individual signed nonlinear constraints, and one forward cycle per
requested candidate. Numerical failures stop the search; they are not assigned a
large objective or relabeled as infeasible designs. The search manifest records
the source hash, bounds, tolerances and seed. `termination.json` is the authority
for convergence. `select_terminal.py` selects the returned solver point rather
than an unused cached initialization probe.

## Initial conditions and pump-down accuracy

The corrected seed begins with evacuated gas chambers, consistent with the
end-of-cycle purge. The existing vacuum temperature regularization is a separate
property-decoding device, not initial physical gas inventory. Absolute tolerance
is 1e-10 instead of the earlier 1e-7. This resolves the small-inventory pump-down
regime without changing real-gas properties or weakening conservation/closure
criteria. The fixed seed passes a two-resolution gate including atol=1e-11.

## Burn-start step selection

The provisional best search point (evaluation 61) completed at search resolution,
but default first-step selection failed at refined resolution at exactly
`t = -617.1388525583765 s`, the burn-start boundary. No atmospheric gas had yet
been collected. Repeating with SciPy's automatic Jacobian also failed there;
this was not a rack heat-transfer or compressor-property failure.

At this event the initially zero thrust-impulse ledger begins accumulating at
approximately 51,313 N. With scalar atol=1e-11, SciPy's initial-step heuristic
selects approximately 7.29e-11 s. The solver reports that its required step has
fallen below floating-point time spacing. One-sided event evaluation was already
present and was retained.

Starting each integration segment with an explicit **0.001 s attempted step**
allows the tight-tolerance cycle to finish. BDF still controls/rejects steps with
the original tolerances; this is not a fixed time step, relaxed error criterion,
state reset or extra closure iteration. `validate_start_step.py` records the
override in the saved trajectory. The provisional result is feasible at
275.721009 days, versus 275.725916 days at search resolution, with species error
4.3e-11 kg and energy error 6.7e-9 MJ.

A second refined run with a 0.0001 s attempted initial step is also feasible at
275.730333 days. The three completed resolutions/initializations agree within
0.004%; the selected verification trajectory uses this recorded 0.1 ms override.

The main forward model's default initialization remains unchanged for exact
search reproduction. Explicit event-start step selection (or physically scaled
per-state absolute tolerances, especially for impulse/energy ledgers) is a
follow-up numerical improvement. Do not silently infer that every future
candidate is robust merely because this checkpoint passes.

Archived unsuccessful checks remain under
`results/transient/staggered/thermal_equivalence/provisional_validation_61/`
and `integrator_check_61/`. The attempted Radau configuration was rejected by
input validation (unsupported integrator); it is not an independent Radau
solution. The final selected-point verification is identified by the checkpoint
README and gate record.
