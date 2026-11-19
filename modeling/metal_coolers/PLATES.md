# Parallel-plate coolers: power-only friction model

The working transient reference uses broad plates **parallel to gas flow**
in place of transverse rods. Earlier rod configurations remain reproducible. Choose
`rack_flow_layout="parallel_plates"`, `rack_pressure_model="layout"`, and
`rack_loss_mode="power_only"`. The existing SiC front / aluminum downstream
materials, finite gas and metal inventories, deployed radiation, and gas-feed
bypass remain in use.

## Independent dimensions and inventory

For each of five volumes, specify full plate thickness `plate_thickness_m`,
clear channel gap `plate_gap_m`, and axial rack depth `rack_depth_m`. Center pitch
is thickness plus gap. The optimizer instead uses solid volume divided by bore
area as its inventory coordinate and derives depth before each simulation.

For bore area A, axial length L, thickness t and gap g:

- Metal fraction is t/(t+g); open frontal fraction is g/(t+g).
- Metal volume is A L t/(t+g); this is subtracted from chamber gas volume.
- Gas-contact area is twice metal volume divided by thickness.
- Unfurled physical plate area is metal volume divided by thickness; two faces
  radiate, with the existing view factor and deployment-speed penalty.
- Thermal mass uses the actual material's temperature-dependent enthalpy.

This is a homogenized stack with negligible perimeter corrections and plate
edge area. There is **no integer axial row count**. It retains the existing
mechanism mass per deployed square metre and packing/accounting. It does not
supply a qualified support structure or minimum manufacturable thickness.
The study bounds thickness at 0.2–5 mm and clear gap at 0.5–30 mm. The former is
full plate thickness, not the old rod radius. Bounds are declared assumptions.

## Friction and added electricity

With mean channel velocity u = mdot/(rho A open_fraction), hydraulic diameter
Dh = 2g and dynamic viscosity mu:

```
Re = rho u Dh / mu
Darcy f = 96 / Re
delta_p = f (L / Dh) rho u^2 / 2 = 12 mu L u / g^2
P_extra = multiplier delta_p (mdot/rho) / (eta_compressor eta_motor)
```

The implementation uses the final expression directly, avoiding a division by
Re at zero flow. At fixed state and geometry the electric charge is quadratic
in mass flow and vanishes continuously at zero flow. Full resistance uses
multiplier 1. It deliberately does not feed delta_p into suction pressure or
the EOS. The existing power-only finite-motor reduction, shared bus limit and
warm-loop dissipation treatment still apply; see [POWER_ONLY.md](POWER_ONLY.md).
No additional form-loss coefficient or tube-bank formula is used.

A laminar-regime constraint keeps maximum recorded channel Re below 1000.
This is a conservative study boundary, not a sharp transition criterion.
Knudsen number uses the clear gap and is reported. The no-slip incompressible
local-state law is an energy surrogate when rarefaction, large fractional
pressure drop, entrance effects or high Mach number matter. These limits are
not proven away by solving the energy-budget optimization.

Thickness and gap are not completely decoupled. At fixed inventory, reducing
thickness increases required axial length and exposed/deployed area. That can
increase friction and mechanism mass even though local blockage falls. At
fixed geometry length, increasing thickness adds thermal mass but reduces flow
area. Thin plates may still be favored by heat transfer and radiation; a thick
optimum must be found, not imposed or promised.

## Gas-to-metal heat transfer

Use fully developed, laminar, constant-wall-temperature parallel-channel
Nu_Dh = 7.54, k = mu cp / 0.71, and h_continuum = Nu k / Dh. Both walls of a
channel have the same lumped stage temperature, which evolves with time.
The existing molecular-accommodation resistance is retained in series:

```
1/h = 1/h_continuum + 1/h_molecular
UA = h * gas_contact_area
Q_gas_to_metal = UA * (T_gas - T_metal)
Bi = h * (thickness/2) / metal_conductivity
```

The heat is debited from gas enthalpy and credited to the finite metal inventory.
The existing Bi < 0.1 constraint remains. Radiation integrates T_metal^4 during
coast; it is not a constant-temperature cooling credit. No PCM or film injection
is added by this geometry change.

Nu=7.54 is the fully developed limit, not a developing-channel enhancement.
The present model retains well-mixed chamber temperatures rather than resolving
an axial gas/plate temperature profile. Zero-flow thermal conduction and the
molecular bridge are reduced approximations; manifolds, thermal entrance effects,
plate warping, supports and deployment durability remain component research.

## References and what they establish

- [MIT, Couette and Poiseuille flows](https://ocw.mit.edu/courses/2-25-advanced-fluid-mechanics-fall-2013/1a114d602956fa0dd328155f9b45f93d_MIT2_25F13_Couet_and_Pois.pdf): exact fully developed plane pressure-driven velocity/flux solution; integrating its parabola gives the factor 12 in mean-velocity pressure drop.
- [US DOE NETL MFiX, plane Poiseuille verification](https://mfix.netl.doe.gov/doc/vvuq-manual/main/html/fluid/fld-01.html): independently documents the analytic laminar parallel-wall benchmark and numerical verification. It does not validate this spacecraft's rarefied or transient flow.
- [University of Illinois, Internal Flow Convection, Table 8.1](https://etrl.mechanical.illinois.edu/pdf/ME320/Lecture%2025%20-%20Internal%20Flow%20Convection.pdf): parallel plates have fully developed Nu=7.54 for uniform wall temperature and Darcy f Re=96. The alternative Nu=8.23 applies to uniform heat flux and is not used here.

## Optimization contract

`python -m atmo_scoops.transient.plate_optimize` calls SciPy's actual
[COBYLA constrained optimizer](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyla.html).
Its objective is dry mass / net new liquid per orbit * orbit period / 86400.
The constraints are individual forward-cycle path margins, paired signed
periodic residual bounds, conservation checks and validity guards. Objective
and constraints reuse one trajectory at exactly identical coordinates.
There is no inner cycle-closing loop and no hardware resized from results.
Numerically failed trajectories stop optimization; they are not assigned an
arbitrary penalty. Exact inputs, every evaluation, solver termination, and best
feasible trajectory are saved. A solver success flag is local termination at
the stated trust-region tolerance, not a global optimum or physical validation.

## Numerical finding: dilute HEOS pressure flashes

The first COBYLA attempt completed thirteen cycles, then failed during a property
call at approximately 872.028 K and 0.00798698 Pa. The exact candidate is saved
in `configs/transient_plates_failed_probe.json`; this is not a hydraulic rejection.

`atmo_scoops.low_density.gas_update` now avoids the library's pressure-to-density
flash below 100 Pa. It initializes rho=p/(R T), updates HEOS with density and
 temperature, and Newton-corrects rho using HEOS pressure and its analytic
constant-temperature derivative. It requires relative pressure residual below
1e-11 within six corrections, otherwise it raises an error. Enthalpy, entropy,
heat capacity and pressure remain the full HEOS values. Above 100 Pa the original
PT update remains. This changes the numerical route, not the equation of state,
and is continuous at the boundary to the solver tolerance.

The same update is used in the independent bracketed compressor-work audit.
Separate tests compare it against direct PT flashes over valid states, including
both sides of the 100 Pa boundary. The failed candidate receives two full-cycle
resolution checks before a fresh optimizer run; old/new numerical evaluations
are not mixed in a search cache.

[CoolProp's Helmholtz formulation](https://coolprop.org/fluid_properties/Mixtures.html)
provides the real mixture EOS; the density/temperature evaluation avoids its
failed pressure flash. [CoolProp's ideal-gas discussion](https://coolprop.org/coolprop/IdealGas.html)
explains the dilute density estimate, which is used only to initialize this
corrected HEOS calculation, not to replace caloric properties.

A subsequent trial exposed an independent HEOS edge case: provisional implicit-solver states near an empty chamber can have only one positive species after the existing nonnegative-inventory clamp. The three-component backend received [1, 0, 0] and failed even under a density update. `gas_update` now removes exactly absent species and returns the matching pure or reduced-mixture HEOS backend. No trace species are injected and no arbitrary composition floor is used. Callers must use the returned backend. Regression tests include pure N2/O2/Ar and a binary mixture, and compare compressor work against a bracketed entropy solve. The exact second failed candidate is `configs/transient_plates_failed_probe2.json`. It now completes at both resolutions with matching physical infeasibility; the numerical-only gate is distinct from its failed feasibility gate.
