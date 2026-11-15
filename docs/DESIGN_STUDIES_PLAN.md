# Incremental mixing: remaining engineering work

The [numerical study](../conclusions/incremental_mixing/ANALYSIS.md) compares
incremental LN2 injection against the unmixed cycle using the same continuous
inlet, compressor envelope and downstream plant. This document tracks what
would turn that conditional trade into a physical design selection.

## Implemented scope

- Ratio r is injected nitrogen / newly admitted air. The zero-ratio limit exactly
  recovers the unmixed model, including no injector/tank hardware addition.
- `fixed_rack` holds the dry stream endpoint and solves the mixed temperature
  from enthalpy; `fixed_inlet` holds mixed temperature and reduces metal heat.
- Both routes include added compressor throughput, startup LN2, storage/injection
  hardware and work, reverse leakage, coast reliquefaction and replacement.
- Atmospheric oxygen and momentum are charged only to new incoming air.
  Recycled coolant is not new product. Pumping capacity/cutoff have equal search
  freedom across ratios; a second family also varies the thermal endpoint.
- Inlet coefficients and pump mass/efficiency are capability scenarios. The
  reduced model does not establish real film cooling, gas-solid conductance or
  a temperature-dependent compressor map.

## Next physical interfaces

1. Resolve metal passage heat transfer and pressure loss. Couple injection
   location and finite-rate vaporization to available throat volume, gas state,
   rack utilization and inlet pressure recovery. Export bounded coefficient
   maps from offline flow studies; keep CFD outside the optimizer loop.
2. Establish compressor inlet-temperature, pressure and composition envelopes.
   Include real suction/power curves, backing stages, internal backflow, thermal
   clearances, startup and installed mass. A lower temperature is not by itself
   proof of a lighter or more efficient complete compressor train.
3. Resolve film-cooling requirements from edge/wall heat flux, oxidation and
   repeated life. Distinguish mandatory local film flow from optional bulk
   cooling; separate film loss from fully mixed leakage.
4. Engineer the LN2 inventory, injection pressure, valves/pumps, tank heat leak
   and reserve. Confirm replacement can come from retained atmospheric nitrogen.
5. Replace nitrogen-equivalent product processing with species-resolved
   separation/phase behavior and account for finite-thrust delivery and return.

## Decision criteria

Preserve mass, species, energy and momentum, recover r=0 exactly, and compare
reoptimized controls under equal technology assumptions. Report net new product,
coolant turnover/replacement, component masses/areas and payoff. A claimed
benefit must exceed both numerical search uncertainty and the applicable
inlet/pump/thermal uncertainty. Report break-even capability improvements when
the existing map cannot support a categorical engineering decision.

Cold gaseous injection and liquid injection are distinct. For ideal equal-Cp
gases at common pressure, `(1+r) T_mix = T_hot + r T_cold`, so cold gas alone
cannot reduce total suction volume despite lowering temperature. LN2 adds a
latent-heat route; it also requires a complete restoration cycle. Do not use
this limiting gas result to reject liquid injection or required film protection.
