"""
energy_cost.py
==============
Owned by: You (Umar) -- the project's core differentiator.

Two things happen here:
1. Translates anomaly SEVERITY into estimated excess energy cost (Rs/week).
2. Estimates the avoided REPAIR cost premium if a fault is caught early
   enough to schedule the fix, rather than letting it fail unexpectedly.

LITERATURE BASIS for the energy-cost model:
- Bearing faults cause a documented 1.5% motor efficiency reduction at full
  load, rising to ~4% at light load (Analog Devices Analog Dialogue,
  summarizing peer-reviewed motor-fault studies).
- A real industrial case: a 400 kW compressor motor running continuously
  showed a 1.5% efficiency reduction from bearing wear prior to overhaul.
- Efficiency loss increases progressively with fault severity (ScienceDirect,
  "Efficiency monitoring as a strategy for cost-effective maintenance of
  induction motors").
- Healthy baseline efficiency (91.7%) is the IEC 60034-30-1 nominal
  efficiency for a 15 kW, 4-pole, IE3-class motor -- India's BEE-mandated
  minimum efficiency class for motors 0.75-375 kW, effective 2024.
- Electricity tariff (default Rs 8/kWh) sits within the typical Rs 6-9/kWh
  range reported for Indian industrial/commercial consumers.

LITERATURE BASIS for the avoided-repair-cost model:
- Emergency/reactive repairs are documented to cost 3-5x more than the same
  repair performed on a planned schedule -- consistently reported across
  multiple independent industry sources (Tractian; Oxmaint, two separate
  analyses; Strainlabs), driven by overtime labor, expedited parts freight,
  and production disruption. We use this RELATIVE multiplier rather than an
  absolute downtime-cost figure, since published per-hour downtime costs
  (often $10,000-$260,000+/hour) are typically reported for large enterprise
  lines and would not transfer honestly to an SME context.

HONEST FRAMING FOR JUDGES: both models are literature-grounded
approximations for a representative case, not precision figures for any
specific machine. This is stated plainly, not hidden.
"""

import numpy as np


def estimate_efficiency_loss_pct(severity: float, max_efficiency_loss_pct: float = 4.0) -> float:
    severity = np.clip(severity, 0.0, 1.0)
    return max_efficiency_loss_pct * (severity ** 1.5)


def estimate_weekly_cost(
    severity: float,
    rated_output_power_kw: float,
    healthy_efficiency: float = 0.917,  # IEC 60034-30-1 IE3 nominal efficiency for a 15kW motor
    operating_hours_per_week: float = 112,
    tariff_rs_per_kwh: float = 8.0,
    max_efficiency_loss_pct: float = 4.0,
) -> dict:
    eta_loss_pct = estimate_efficiency_loss_pct(severity, max_efficiency_loss_pct)
    eta_healthy = healthy_efficiency
    eta_degraded = max(0.05, eta_healthy - (eta_loss_pct / 100.0))

    input_power_healthy_kw = rated_output_power_kw / eta_healthy
    input_power_degraded_kw = rated_output_power_kw / eta_degraded
    excess_power_kw = input_power_degraded_kw - input_power_healthy_kw

    weekly_extra_kwh = excess_power_kw * operating_hours_per_week
    weekly_cost_rs = weekly_extra_kwh * tariff_rs_per_kwh

    return {
        "severity": severity,
        "efficiency_loss_pct": eta_loss_pct,
        "efficiency_healthy": eta_healthy,
        "efficiency_degraded": eta_degraded,
        "excess_power_kw": excess_power_kw,
        "weekly_extra_kwh": weekly_extra_kwh,
        "weekly_cost_rs": weekly_cost_rs,
    }


def estimate_cost_timeseries(severity_scores: np.ndarray, **kwargs) -> np.ndarray:
    return np.array([estimate_weekly_cost(s, **kwargs)["weekly_cost_rs"] for s in severity_scores])


def estimate_avoided_repair_premium(scheduled_repair_cost_rs: float, low_multiplier: float = 3, high_multiplier: float = 5):
    """
    Estimates the AVOIDED cost premium if a fault is caught early enough to
    schedule the repair, versus letting it fail and become an emergency
    repair. Uses the literature-documented 3-5x emergency-repair multiplier.
    Returns (avoided_low_rs, avoided_high_rs).
    """
    avoided_low = scheduled_repair_cost_rs * (low_multiplier - 1)
    avoided_high = scheduled_repair_cost_rs * (high_multiplier - 1)
    return avoided_low, avoided_high