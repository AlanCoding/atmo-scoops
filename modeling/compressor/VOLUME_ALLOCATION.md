# Compressor blocks and independent chamber volumes

**Status: geometry requirements; not a completed transient multichamber model.**
The code currently computes four bank states and geometry-based masses but uses
only front and rear inventory states. Prescribed interstage cooling targets do
not create physical intermediate chambers. The 100 m machinery allowance has
no reference-design derivation and must not determine residual tank volume in a
claimed packed spacecraft.

Existing bank outputs supply module count, approximate diameter and blade-row
length. A first bank hardware envelope is the sum of module external cylinders,
plus separate motor, shaft/bearing, inlet/diffuser, casing and manifold ends.
The current diameter is flow-path sizing, not a verified outside diameter; do
not call its cylinder a complete installed volume. The NASA WATE-S source in
[the compressor dossier](COMPARABLE_SYSTEMS.md) supports a stagewise geometry
buildup, not a fixed full-bore ship compartment.

The saved 937 km-apogee limit case has row lengths totaling about 22 m across
four banks. This neither justifies 100 m nor establishes that 22 m completes the
train: intercoolers, gas buffers, pressure boundaries, drives and ducting still
need dimensions. Small later banks can share a longitudinal section with other
equipment where an actual layout proves fit. Many parallel modules do not all
occupy sequential length; each bank's footprint must fit its local cross-section.

Each cooling chamber has independent geometry, accessible gas volume, rack
solid/core mass, porosity, heat-transfer area, hydraulic diameter and pressure
loss. Track mass/energy/species over time with unequal upstream/downstream flows.
A front control-buffer volume is based on flow mismatch and allowed pressure
excursion over control delay, not an assumed 25 m length. The flow-field study
must bound shock/diffuser extent separately. Coolers impose conductance/storage
and passage geometry requirements independently of inventory buffering.

See [close-pass allocation](../deployment/CLOSE_PASS_VOLUME.md) for the ledger
and overlap rules. The numerical replacement must remove `machinery_depth_m` as
an unexplained volume reserve, derive bank and cooler envelopes, and expose
separate chamber design variables. Retain old inputs only for labeled historical
reproduction; do not silently reinterpret them as solved stage volumes.
