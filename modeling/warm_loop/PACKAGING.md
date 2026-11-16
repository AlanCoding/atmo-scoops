# Warm radiator and fluid-loop packing

**Status: sourced architectural evidence; full folded-package coefficient unresolved.**
A panel thickness, material volume and stowed stack envelope are different
quantities. No reviewed source here supports assigning a universal m³/kW.

## Reference hardware

- [NASA DSH configurations based on ISS systems](https://ntrs.nasa.gov/api/citations/20120014530/downloads/20120014530.pdf), PDF/slide 135 and 139 (zero-based PDF indices): EEATCS/PVR radiator ORU is listed at 741 kg and 7–14 kW, with rejection dependent on environment. The same component slide lists a 41 kg interface exchanger at 63 × 53 × 20 cm, a 0.0668 m³ bounding box. These anchor radiator/loop system boundaries; they do not disclose a complete stowed radiator box in the extracted data. PVR and HRS are distinct variants.
- [NASA ISS radiator qualification-test paper](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20010059377.pdf): qualification hardware and thermal-vacuum testing establish a real deployable HRS architecture. Qualification of flight thermal hardware does not establish high-cycle folding in our environment.
- [NASA lightweight deployable radiator concept](https://ntrs.nasa.gov/citations/20110016452): composite fin/liner construction, compact stowage and deployment without disconnecting fluid paths. This is a proposed concept/Tech Brief, not measured packaging or lifetime data.
- [NASA Shuttle-payload radiator development](https://ntrs.nasa.gov/citations/19760059385): rigid honeycomb/scissor and flexible roll/extension architectures were investigated. Treat these as separate package models, not one thin-sheet coefficient.

A public indexed HRS face-sheet report quotes 0.010-inch skins, but skins are
not the complete panel thickness and that number is **not** used as stack pitch.
A complete mechanism drawing, panel section and folded envelope remain required.
No numerical stowed-volume coefficient is promoted from a diagram without all
three dimensions and a clear equipment boundary.

## Area-to-volume relation to implement

Compute physical area from the heat balance, e.g.
`A_phys = Q_dot / [n_faces * (epsilon sigma T_skin^4 - absorbed_flux)]` only
when both sides have the stated view factors. Prefer face-specific radiation
when they differ. The existing output distinguishes panel area from emitting
area; keep that distinction in the packing calculation.

For rigid folding panels, choose module dimensions `w,l`, panel count
`N=ceil(A_phys/(w*l))`, actual panel thickness `t_panel`, fold gap `g`, and hinge,
header, drive and boom bounding geometry. A first stack height is
`H = N*t_panel + (N-1)*g + end_hardware_height`; stack footprint must include
headers protruding beyond panel edges. Preserve discrete module count and tube
bend radius. Multiple stacks consume bays and deployment openings.

For a rollable panel, include tubes/arteries, minimum roll radius, crush/bend
limits and fluid-joint accommodation in effective pitch. A skin that rolls is
not evidence that its pressurized coolant network does. Track drained versus
filled state: drain tanks, purge gas and refill time cost mass/volume/energy.
No additional coolant tank is needed for fluid already counted inside tubes,
unless a distinct drained configuration requires it.

Supply/return piping needs `V_fluid=sum(pi*d_inner²*l/4)` and external routing
volume including insulation, bend radii and clearance. Pump/HX/accumulator
packages need operating-point-specific dimensions. Fluid-compatible rotary or
flexible connections must survive the mission's cyclic pressure and temperature.
ISS ammonia heritage is not validation at every temperature in the present model.

## Handoff and tests

Provide named rigid and rollable module options with measured dimensions,
physical/emitting area, thermal duty, fluid pressure, mass and deployment state.
Check that summing tube, face-sheet and honeycomb material volume does not replace
the external envelope. Publish heat rejection at the actual skin temperature,
then derive area, discrete package count and stowed dimensions. Until a complete
stack reference is obtained, keep package pitch an explicitly uncalibrated
engineering variable, not a hidden allowance or a fixed bay length.
