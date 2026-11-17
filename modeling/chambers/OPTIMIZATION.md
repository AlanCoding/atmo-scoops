# Transient allocation search and explicit proxy

This is an isolated search over `atmo_scoops.chambers`, not a replacement for
primary-system payoff. Results and atmospheric timing are in the
[allocation investigation](../../investigations/chamber_transient/OPTIMIZATION.md).

## Coordinates and fixed assumptions

Ten independent design coordinates: five rack-envelope depths and five additional
empty depths. Physical depth is their sum, so rack overfill is impossible by
construction. Bore stays 30 m, wire radius 1 mm, pitch 10 mm, initial rods 298 K.
Compressor capacities, head limits and controls remain fixed. No arbitrary
improvement of compressor efficiency or materials is a search coordinate.

The search starts integration at -600 s. The atmospheric forcing interval expands
to include that start rather than declaring the inbound part above 200 km empty.
Plots emphasize the 5–95% incident-column interval rather than compressing the
important pass into a 50-minute axis. Initial and final densities are still a
prescribed atmospheric profile, not a sharp physical atmosphere edge.

Bounds (metres) are deliberately exploratory, not certified material/layout limits:
front rack 2–7; interstage racks 0.015–0.8; receiver rack 0.015–1;
front/intermediate extra empty depths 0–12; receiver extra empty depth 2–100.
The empty-volume coordinate is independent of rod surface/metal mass. Rack gas
pores remain available as gas volume.

## Figure of merit

`proxy_days = proxy_dry_mass / useful_batch * orbit_period / 86400`.
Useful batch is gas already withdrawn plus gas remaining in the final receiver,
minus initial seed gas, a final receiver purge allowance, and propulsion mass.
Residual intermediate inventories receive no product credit. All cases pay the
same geometric intercepted-column impulse divided by the fixed optimized exhaust
speed; discarded air does not make the momentum bill disappear. Nitrogen can
supply propulsion along with oxygen. No circular-apogee delivery is represented.

Dry mass consists of:

1. Fixed hardware from the saved solid-rack/perigee-Isp reference, excluding its
   old metal, sheet-deployment mass, exterior shell, receiver vessel and margin.
   Compressor structures, propulsion and most electrical/thermal hardware remain
   installed; none gets resized optimistically merely because a chamber is smaller.
   Each stage motor is uprated when its measured peak electrical load exceeds the
   reference rating, using the existing motor W/kg and machinery packing density.
   The retained common reboost bus/battery power capability exceeds the selected
   total compressor peak; it is not deleted or downsized.
2. Actual metal from geometry and sheet-deployment allowance from wire footprint.
3. Exterior shell using total chamber length plus the reference's **accounted
   equipment-package depth**, not a newly invented machinery allowance.
4. All sealed chamber vessels: the greater of a thin-membrane pressure-volume
   lower bound and minimum-gauge surface mass, plus support/insulation allowances.
   Actual shared bulkheads, head geometry and bending have not been designed.
5. Signed change in compressor shaft energy from the transient baseline, converted
   to battery and average-sunlight array mass using the existing coefficients.
   It does not remove installed compressor structural mass or redesign peak buses.
6. An explicit **10 kg/MJ** surcharge for recovered feed enthalpy above 340 K,
   representing additional hot-gas handling, buffering and heat rejection. The
   retained baseline thermal hardware is not freed. This is intentionally a
   conservative extra capacity allowance, not a derived cryoplant design. Reports
   also score candidates at 0, 5 and 20 kg/MJ to expose dependence on this choice.
7. The existing 25% additive design margin, once.

Coast withdrawal is fixed at 2 kg/s for every search and matched baseline case.
A modular throughput allowance increases baseline refrigerator/feed/separator
hardware if 2 kg/s exceeds its implied processing rate. These choices give a
repeat-cycle timing allowance without adding a full plant simulation.

## Constraints and cycle completion

Impose rack fit, total L/D ≤ 10 including fixed equipment packing, peak gas
pressure ≤110 kPa, metal ≤1042 K, gas ≤2000 K when inventory exceeds 0.01 kg,
positive net product, caloric-domain validity and mass/energy audit limits.
Early near-vacuum temperatures are not interpreted as meaningful gas states.

Integration ends at +2400 s, not at a falsely declared completed cycle. The proxy
then estimates draining to twice the withdrawal-pressure-floor inventory evaluated
at 298 K. For `dm/dt = -F*(1-mf/m)`, the remaining time is
`[m0-m1 + mf*ln((m0-mf)/(m1-mf))]/F`. That final purge mass is deducted from product.
After draining and purging, estimate rack deployment, radiative reset to initial
298 K and retraction, using the existing iron/wire cooldown relation. Require all
of this before the next -600 s entry. This is a conservative scheduling screen,
not an integrated repeated-cycle solution; deployment and thermal recovery still
need physical engineering. The old 1.5 kg/s demonstration setting does not leave
enough time under this all-racks-wait-for-draining schedule.

## Search and numerical validation

A bounded coordinate pattern search compares two initial layouts and all positive/
negative coordinate moves at three shrinking step sizes. It is a limited search,
not proof of a global optimum. Each trial integrates the coupled dynamics. A
35-second screening timeout is recorded as a numerical failure, not a physical
constraint. Search records preserve all trial coordinates and reasons for rejection.

Screening uses 8 s maximum step and relative tolerance 1e-4; selected layouts and
the matched baseline are rerun at 2 s and 2e-6, with further refinement of the
selected layout. Recheck physical constraints at refined resolution. Keep
pressure, temperature and conservation tests separate from improvement of the
proxy. Variable allocation, startup thermal states, wire geometry, pumps, orbit,
withdrawal controls and actual plant sizing are not jointly optimized here.

## Hardware coupling audit

The [mixed-material mass audit](../../investigations/chamber_transient/MASS_AUDIT.md)
expands the fixed hardware ledger and identifies the outstanding absolute-cycle
coupling. In particular, processing capacity mass is scaled without corresponding
power/rejection/packing updates, inherited warm hardware can overlap the new rack
thermal path, and compressor energy is adjusted against a separate transient
baseline. Therefore the proxy is neither a fully recoupled spacecraft payoff nor
a demonstrated upper bound. Deployment travel now uses physical deployed area,
not mechanism mass; this dimensional correction leaves the saved reference cases
unchanged at their 1 kg/m² mechanism coefficient.
