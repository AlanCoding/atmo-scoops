"""Regenerate the frozen-history hydraulic-power comparison."""
import json
from pathlib import Path

def main():
    root=Path('results/transient')
    ref=json.loads((root/'loss_power_screen.json').read_text())
    current=json.loads((root/'loss_power_screen_current.json').read_text())
    coarse=json.loads((root/'loss_power_screen_coarse.json').read_text())
    text=['# Rack resistance as an additive power charge','',
          'This is post-processing of saved trajectories, not a new cycle simulation or optimization. No gas state, flow, temperature, property model, closure condition or hardware rating changes. No hydraulic root solve is performed. The active coupled model is unchanged.','',
          '## Definition','',
          'At each saved time and rack, use the existing laminar-bank coefficient and exit term:', '',
          '`K = (rows × zeta_laminar(Re, pitch/diameter) + (1 − beta)²) / beta²`',
          '`delta_p_linear = alpha K (mass_flow / frontal_area)² / (2 rho)`',
          '`added_electric_power = delta_p_linear × (mass_flow / rho) / (eta_compressor eta_motor)`','',
          'Density is saved species inventory divided by gas volume. Temperature and mass flow are read directly from the saved histories. Only the existing algebraic viscosity relation is evaluated; there is no new fluid-property flash. Efficiencies are 75% compressor and 95% motor. Integrate added power over the saved adaptive time samples, including the low-pressure evacuation tail and coast withdrawal. The front four racks use their compressor outflows; the fifth uses combined receiver withdrawal into the coast train. This charges the same outlet paths as the hydraulic model, not every possible recirculating motion in a chamber.','',
          'This is the small-loss expansion of the pressure-squared relation. It is a prescribed engineering power surcharge, not the exact difference between two real-gas compressor calculations. At large fractional pressure loss, the linear estimate is not a validated compressible-flow result. The 1%, 10% and 100% energy charges scale exactly by construction.','',
          '## Clean comparison: saved zero-loss reference','',
          f'Source: `{ref["source"]}`. Existing gas compression electricity is **{ref["baseline_compression_electric_MWh"]:.4f} MWh/orbit**, inferred from the shaft-work ledger divided by motor efficiency. It includes dive, coast and propellant-fill compression, but excludes spin-up, idle draw and refrigeration. The separately integrated total vehicle electrical load is **{ref["baseline_total_load_MWh"]:.2f} MWh/orbit**.','',
          '| Resistance factor | Added electricity, MWh/orbit | Increase in compression electricity | Total compression electricity, MWh/orbit | Peak added power, MW |',
          '|---|---:|---:|---:|---:|']
    for a in ref['cases']:
        text.append(f'| {a["multiplier"]:.0%} | {a["added_MWh"]:.5f} | {a["percent_of_baseline"]:.2f}% | {ref["baseline_compression_electric_MWh"]+a["added_MWh"]:.5f} | {a["peak_added_MW"]:.3f} |')
    text+=['','The peak is the maximum of the simultaneous sum across racks, not the sum of unrelated stage peaks.','',
           '| Rack / downstream train | Full-strength added electricity, kWh/orbit |','|---|---:|']
    for label,value in zip(['Front → compressor 1','Intermediate → compressor 2','Intermediate → compressor 3','Intermediate → compressor 4','Receiver → coast train'],ref['cases'][-1]['stage_added_MWh']):text.append(f'| {label} | {value*1000:.4f} |')
    relative=abs(coarse['cases'][-1]['added_MWh']/ref['cases'][-1]['added_MWh']-1)
    text+=['',f'The front rack accounts for **{100*ref["cases"][-1]["stage_added_MWh"][0]/ref["cases"][-1]["added_MWh"]:.2f}%** of the surcharge. Coarse versus refined saved trajectories change the integrated surcharge by **{100*relative:.4f}%**.','',
           '## Check using the latest 1%-loss reference','',
           f'Source: `{current["source"]}`. Its existing compression electricity is {current["baseline_compression_electric_MWh"]:.4f} MWh/orbit. Applying the same diagnostic to its frozen states gives:', '',
           '| Resistance factor | Nominal charge, MWh/orbit | Peak, MW |','|---|---:|---:|']
    for a in current['cases']:text.append(f'| {a["multiplier"]:.0%} | {a["added_MWh"]:.5f} | {a["peak_added_MW"]:.3f} |')
    text+=['',
           'Do not add these charges blindly to that reference: its existing compression already includes coupled 1% resistance. This second calculation shows sensitivity to the chosen frozen trajectory; the zero-loss reference above provides the clean additive comparison. Differences arise especially in the front low-pressure tail.','',
           '## Meaning and limits','',
           'For the clean reference, approximately 0.79%, 11.86% and 100% of front-compressor transported mass lies at points where the original pressure-squared equation cannot support that unchanged flow at 1%, 10% and 100% resistance, respectively. This does not prevent calculating the requested power surcharge, but it does prevent claiming that full-strength loss can physically be handled by adding electricity alone. The figures are a bearing on energy scale, not demonstrated capture performance. The comparison leaves electrical limits, batteries, heat rejection, hardware mass and payoff unchanged; accommodating the surcharge is a separate design calculation.','',
           '## Reproduction','', '```sh',
           '.venv/bin/python -m atmo_scoops.transient.loss_power_screen',
           '.venv/bin/python -m atmo_scoops.transient.loss_power_screen --input results/transient/staged/bypass_verify/check.json.gz --output results/transient/loss_power_screen_coarse.json',
           '.venv/bin/python -m atmo_scoops.transient.loss_power_screen --input results/transient/loss_continuation/refined_best/loss_0.01.json.gz --output results/transient/loss_power_screen_current.json',
           '.venv/bin/python -m atmo_scoops.transient.loss_power_report', '```','']
    Path('investigations/staged_refinement/POWER_ONLY.md').write_text('\n'.join(text))

if __name__=='__main__':main()
