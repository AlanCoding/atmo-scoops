"""Loss/base compression comparisons with explicit instantaneous denominator floors."""
import numpy as np

def loss_metrics(r):
    t=np.asarray(r['time_s']);h=r['history'];loss=np.asarray(h['rack_loss_MW']);base=np.asarray(h['stage_compression_base_MW'])
    energy=np.array([r['ledger'][f'rack_loss_{i}_MJ'][-1] for i in range(5)])
    baseline=r['ledger']['shaft_MJ'][-1]/r['inputs']['capabilities']['eta_motor']
    per_stage=np.trapezoid(base,t,axis=0)
    # Exclude near-zero denominators from the instantaneous ratio statistic;
    # retain all energy, including zero-base-work phases, in the energy ratio.
    significant=base>.001
    ratios=np.divide(loss,base,out=np.zeros_like(loss),where=significant)
    return dict(loss_electric_MWh=float(energy.sum()/3600),base_compression_MWh=float(baseline/3600),
                energy_ratio=float(energy.sum()/max(baseline,1e-30)),stage_loss_MWh=(energy/3600).tolist(),
                stage_energy_ratios=(energy/np.maximum(per_stage,1e-30)).tolist(),
                peak_loss_MW=float(loss.sum(axis=1).max()),
                peak_stage_ratio_above_1kW=ratios.max(axis=0).tolist(),
                peak_total_ratio_above_1kW=float(np.divide(loss.sum(axis=1),base.sum(axis=1),out=np.zeros(len(t)),where=base.sum(axis=1)>.001).max()),
                loss_energy_at_base_below_1kW_MWh=(np.trapezoid(loss*(~significant),t,axis=0)/3600).tolist())
