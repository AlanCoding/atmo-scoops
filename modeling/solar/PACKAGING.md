# Folded solar-array volume and repeatability

**Status: primary-source evidence and proposed sizing relations; not integrated.**
Retrieved 2026-11-15. Array packing belongs to the close-pass configuration,
including the active retraction system and protective accommodation.

## Reference systems and what they establish

| Reference | Published quantity | Applicability and exclusions |
|---|---|---|
| Redwire ROSA flysheet, revision v1_10-2-2025, p.1 | Approximately 40 kW/m³ stowed power density; optional retractable wings | Manufacturer design-level estimate. No repeated-cycle lifetime or full installed scoop-bay volume specified. |
| Same flysheet, SunStone / Phenacite | 28 / 37 kW BOL; 331 / 521 kg; deployed length 19.4 / 18.5 m; stowed width 3.1 / 4.94 m | Width alone is insufficient to reconstruct a package volume. Do not substitute deployed length for rolled diameter. |
| Orbital ATK IEPC-2017-293, section III.D, printed p.10 | UltraFlex/MegaFlex flexible fan-fold architecture: >40 kW/m³, up to 200 W/kg | Independent manufacturer architecture comparison, not a universal coefficient. Do not assume peak specific mass and packing describe the same configuration. |
| NASA/TM-2016-218921, printed p.4 | Nominal 20 kW ROSA and MegaFlex EDUs; vacuum deployment tests at ±60°C | Establishes hardware/environmental testing and distinct deployment mechanisms; not thousands of retract/deploy cycles. |
| Chamberlain et al., IAC-19-C3.4.1, pp.4–5 | Flight demonstrator deployment 3 min 21 s; three unsuccessful retraction/latching attempts, followed by redeployments | Demonstrated deployment timing for that article, not a universal timing law. Telescoping/misalignment prevented latch engagement. |

Sources:
- [Redwire flysheet](https://rdw.com/wp-content/uploads/2023/06/redwire-roll-out-solar-array-flysheet.pdf). Its specifications are explicitly approximate design information.
- [Orbital ATK system paper](https://electricrocket.org/IEPC/IEPC_2017_293.pdf). The fan-fold family provides a second architecture; module-level dimensional drawings are still needed for our layout.
- [NASA EDU assessment](https://ntrs.nasa.gov/api/citations/20160003683/downloads/20160003683.pdf).
- [ROSA flight test paper](https://ntrs.nasa.gov/api/citations/20205003936/downloads/Chamberlain_IAC2019_IAC19C341x49723_ActaRevised.docx.pdf).

## First conversion and its boundary

For the published packing quantity `q_V` in kW/m³,
`V_package = P_rated,kW / q_V`.
Specify BOL/EOL, solar distance, temperature, pointing and electrical interface.
If the cycle asks for bus power `P_bus`, use
`P_rated = P_bus / (f_temperature f_age f_pointing eta_electrical)` with each
factor supported by a selected cell/blanket model. Eclipse duration already
belongs in energy-per-orbit sizing; do not apply it again as a panel derating.
The hardware mass, area, power and packing must refer to the same design.

For a roll, length of blanket `l`, width `w`, packing pitch `t_pitch` and mandrel
radius `r0`, first geometry gives `r_roll² = r0² + l*t_pitch/pi`. The cylindrical
roll volume is `pi*r_roll²*w`; its rectangular bounding box is larger. Then add
side supports, drive and latch envelopes only where the quoted source package
does not already include them. The pitch includes cells, interconnects, layers,
protective spacers and required bend radius effects—not bare substrate thickness.
For fan-fold arrays, calculate panel count, fold pitch, spar/hinge bundle and
stack dimensions instead. Confirm the source power-density metric against the
selected module drawing before adding a blanket packing efficiency.

## Required repeat-cycle development

A reversible wing requires controlled rewinding, tension management, guiding,
thermal alignment, capture/latches and condition sensing. Stored-strain-energy
unfurling alone does not supply these. Qualify cells/interconnects, fold/roll
fatigue, coatings, booms and latches at the actual cycle count and temperature.
Timing includes depressurization/opening if housed behind a hatch, extension,
tensioning, electrical enable, and retraction/latch verification. Different
modules can operate in parallel, but their paths and electrical transients must
fit the design. No flight datum found here qualifies every-orbit long-life
retraction; that remains development work rather than a reason to abandon it.

The handoff needs module area, rated power, complete package dimensions/mass,
repeat-cycle mechanism additions, deployment path/time and a demonstrated test
condition. The 40 kW/m³ figure is suitable for a named comparison scenario today,
not an unqualified optimizer default.
