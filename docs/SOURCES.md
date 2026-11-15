# Evidence and property sources

These primary sources support material properties, equations and engineering
comparisons. They do not demonstrate the complete scoop spacecraft. The
configuration identifies capability targets separately from these measurements.

## Atmosphere and thermochemistry

- [Emmert et al., NRLMSIS 2.0](https://repository.library.noaa.gov/view/noaa/53074/noaa_53074_DS1.pdf),
  [NRLMSIS interface](https://kauai.ccmc.gsfc.nasa.gov/instantrun/nrlmsis/),
  [pymsis implementation](https://github.com/SWxTREC/pymsis).
  The model uses reproducible NRLMSIS 2.1 profiles, converts species number
  density into mass fractions, and records solar/geomagnetic drivers. Profiles
  are scenario atmospheres, not forecasts of individual passes.
- [NASA thermodynamic database](https://ntrs.nasa.gov/citations/20020085330),
  [Cantera equilibrium API](https://cantera.org/stable/python/thermo.html),
  [airNASA9 species data](https://github.com/Cantera/cantera/blob/v3.2.0/data/airNASA9.yaml).
  Atmospheric kinetic and chemical energy share a consistent enthalpy reference.
  Equilibrium endpoints do not establish finite-rate chemistry or inlet capture.
- [NIST nitrogen heat capacity](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Units=SI&Mask=1),
  [nitrogen phase properties](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Units=SI&Mask=4),
  [oxygen phase properties](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=4).
  Product cooling uses a nitrogen-equivalent thermal duty with explicit finite
  approaches. This does not resolve mixed-air phase equilibrium or separation.

## Solid absorber and thermal system

- [NIST alpha/delta iron calorimetry](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896&Mask=2&Units=SI),
  checked 12 November 2026. Integrating the solid Shomate Cp gives the thermal
  capacity between each selected cold/hot endpoint. The implemented range is
  298–1042 K. Iron is a calorimetry proxy, not a qualified flight alloy/coating.
- [NASA ISS thermal-control guide](https://www.nasa.gov/wp-content/uploads/2017/09/np-2015-05-022-jsc-iss-guide-2015-update-111015-508c.pdf),
  [ammonia pump performance record](https://ntrs.nasa.gov/citations/20110023292).
  Evidence for separate pumped ammonia heat rejection. Scoop radiator
  temperatures, areas, mass and cycling remain calculated requirements/targets.
- [NIST cryocooler overview](https://trc.nist.gov/cryogenics/cryocoolers.html),
  [NASA high-capacity cryocooler development](https://ntrs.nasa.gov/api/citations/20205010721/downloads/1676%20-%20ICC21%20Presentation.pdf).
  Supports separating product heat exchange, refrigerator work and warm heat
  rejection. The configured efficiency and cold-package specific mass are
  development targets, not fitted performance of a selected cryoplant.
- [NASA JIMO radiator study](https://ntrs.nasa.gov/api/citations/20050160234/downloads/20050160234.pdf?attachment=true).
  High-temperature spacecraft heat-rejection engineering context. It does not
  establish the mass or life of repeatedly deployed scoop absorber sheets.

## Compressors, inlet control and finite flow

- [Leybold RUVAC WH/WHU technical data](https://www.leybold.com/content/dam/brands/leybold/downloads/brochures/product-brochures-fore-vacuum/mechanical-booster-pumps/3611019802_RUVAC%20WH_web.pdf).
  WH 7000 lists 650 kg and nominal 9,800 m³/h at its highest listed frequency:
  about 239 kg/(m³/s) for that booster. Effective speed depends on backing
  equipment. It is not a hot-gas space pump. The complete-bank scoop targets
  of 10–300 kg/(m³/s) are explicit sensitivities, not measured scaled products.
- [NASA mass-flow choking relation](https://www.grc.nasa.gov/www/k-12/airplane/mflchk.html).
  Bounds passive cooled-plenum flow through compressor inlet openings. Local
  gas gamma and an explicit discharge factor enter the calculation; it is not
  a rotating-machine map or a shock stability proof.
- [NASA inlet/isolator unstart study](https://ntrs.nasa.gov/citations/20240016426),
  [inlet overview](https://www.grc.nasa.gov/www/k-12/airplane/inlet.html).
  Shock travel and unstart depend on backpressure, boundary layers and geometry.
  The studied Mach-4 inlet is not a validated operating envelope for the scoop.
- [NASA compressor work relations](https://www.grc.nasa.gov/www/k-12/BGP/compth.html).
  Thermodynamic duty must be separated from actual stage efficiency, machine
  mass and available flow/pressure map.

## Repeated deployment and electrical hardware

- [NASA ROSA flight-test presentation](https://ntrs.nasa.gov/api/citations/20220005587/downloads/Chamberlain%20-%20ASCE%20Earth%20and%20Space%20Final%20v2.pdf?attachment=true).
  The 5.4 × 1.67 m experiment deployed in 3.5 minutes. Retraction reached the
  latch but failed to latch. Deployment timing does not demonstrate repeated
  restow/reuse lifetime at scoop scale.
- [NASA iROSA deployment account](https://www.nasa.gov/blogs/spacestation/2021/06/25/second-of-the-new-solar-arrays-successfully-deployed/).
  Roughly ten-minute deployment for the approximately 60-foot wing. This does
  not specify retraction time or repeated atmospheric-dive cycling.
- [NASA 300 kW array study](https://ntrs.nasa.gov/api/citations/20140000360/downloads/20140000360.pdf?attachment=true),
  [transformational solar-array fact sheet](https://www1.grc.nasa.gov/wp-content/uploads/EESP_FS_FINAL_7-24-17-1.pdf).
  Array specific power/packing development context. The reference 150 W/kg,
  250 W/m² and five-minute mechanism timings are scenario targets.
- [NASA thermal technology survey](https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control/).
  Thermal-system architectures and engineering context, not a measured scoop
  thermal-buffer or deployment mass.

## Oxygen propulsion and momentum

- [NASA specific impulse definition](https://www.grc.nasa.gov/www/BGH/specimp.html).
  Effective exhaust velocity is Isp times standard gravity: 4,000 s corresponds
  to 39,226.6 m/s. This identity does not demonstrate efficiency or hardware mass.
- [Oxygen-propellant plasma thruster study](https://ntrs.nasa.gov/citations/20210004967).
  Oxygen electric propulsion has a research basis; configured peak-power
  specific mass, efficiency and lifetime remain requirements.
- [Crandall and Wirz, IEPC 2024](https://electricrocket.org/IEPC_2024/259.pdf).
  Small nitrogen/air gridded-ion experiments report efficiency and Isp at
  distinct operating points. They do not establish the configured oxygen
  system's 60% efficiency or 2 kg/kW installed mass.
- [NASA momentum effects](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/momentum-effects/).
  Distinguish momentum flux rho*u² from dynamic pressure rho*u²/2. Captured-air
  momentum enters the reboost ledger once; exterior drag remains separate.

## Reduced open-mouth port law

- [NASA Glenn compressible mass flow and choking](https://www.grc.nasa.gov/www/BGH/mflchk.html),
  [isentropic relations](https://www.grc.nasa.gov/WWW/k-12/airplane/isentrop.html).
  Support the ideal reservoir/port pressure-ratio relation and its sonic limit
  in `open_mouth.py`. These equations do **not** establish the scoop's recovered
  pressure, effective throat area, discharge coefficient, or shock stability.
  The inlet boundary's support/ram ratio and discharge factor are explicit
  sensitivity inputs pending offline fluid analysis.

## Atmospheric-column dimensional analysis

- [NASA dynamic pressure](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/),
  [ideal-gas equation of state](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/equation-of-state/),
  [normal-shock relations](https://www.grc.nasa.gov/WWW/BGH/normal.html).
  Support q=ρu²/2, p=ρRT and the distinction between shock compression and
  cooled-plenum density. The column derivation and numerical examples in
  `analysis/primary/ATMOSPHERIC_COLUMN.md` are this project's calculations.
  The pressure-recovery factor is an assumption, not a NASA-validated inlet
  coefficient. Density-amplitude cancellation is conditional on fixed trajectory,
  cooled gas state and pressure factor; it is not universal altitude invariance.

## Declining-pressure compressor envelope

- [Pfeiffer vacuum generation](https://www.pfeiffervacuum.com/no/en/knowledge/vacuum-technology/knowledge-book/4-vacuum-generation/).
  Throughput depends on inlet pressure and effective pumping speed; useful
  pumping vanishes at ultimate pressure. This supports treating a practical
  cutoff separately from a hardware ultimate pressure.
- [Leybold, Fundamentals of Vacuum Technology](https://www.leybold.com/content/dam/brands/leybold/downloads/brochures/general-brochures/Fundamentals_of_Vacuum_Technology_EN.pdf),
  [Roots pump operation](https://www.leybold.com/en-us/knowledge/vacuum-fundamentals/vacuum-generation/how-does-a-roots-pump-work).
  Net throughput differs from displacement throughput because of internal
  backflow; backing pressure and attainable compression affect useful speed.
  The active model uses the declared envelope `S_eff/S = max(1-p_ultimate/p,0)`
  and an independent idle-power allowance. Neither that curve's coefficients
  nor the scoop's temperature, specific mass, scale or efficiency are qualified
  by these sources. A real multistage compressor map remains necessary.

## Incremental LN2 mixing

- [NIST nitrogen phase data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=4&Units=SI)
  gives the 5.6 kJ/mol vaporization anchor at 77 K. Together with the listed NIST
  gas heat capacities and Cantera gas enthalpies, this anchors the liquid/gas
  mixing balance without extrapolating gas polynomials into the liquid phase.
- [Leybold Roots-pump operation](https://www.leybold.com/en-us/knowledge/vacuum-fundamentals/vacuum-generation/how-does-a-roots-pump-work)
  describes internal backflow, backing-pressure effects and gas cooling. This
  supports treating thermal behavior as part of a pump map, not assuming that
  cooler inlet gas guarantees a selected efficiency or specific mass. Its
  industrial machines do not qualify the scoop's high-temperature compressor.

The mixing study's tank/injector allowances, 1 MPa injection pressure, 806 kg/m³
LN2 density proxy, efficiency and pump specific power are declared inputs.
They do not select an off-the-shelf cryogenic injection system. Product duty
uses the entire retained mixture; restored coolant is subtracted from new yield.
