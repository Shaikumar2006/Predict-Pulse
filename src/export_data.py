import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import numpy as np
from data_loader import load_ims_dataset
from feature_extraction import extract_features
from anomaly_model import AnomalySeverityModel, smooth_severity, estimate_time_to_critical
from energy_cost import estimate_weekly_cost
from bearing_geometry import calculate_defect_frequencies

FEATURE_KEYS = ["rms", "crest_factor", "kurtosis", "defect_band_energy", "harmonic_2x_energy", "harmonic_3x_energy"]
FEATURE_LABELS = {
    "rms": "Overall Vibration (RMS)",
    "crest_factor": "Crest Factor",
    "kurtosis": "Kurtosis (Impact Sharpness)",
    "defect_band_energy": "Defect Frequency Energy",
    "harmonic_2x_energy": "2nd Harmonic Energy",
    "harmonic_3x_energy": "3rd Harmonic Energy",
}

# Real bearing geometry for this test rig (Rexnord ZA-2115, validated earlier)
DEFECT_FREQS = calculate_defect_frequencies(
    n_rolling_elements=16, ball_diameter_mm=8.4, pitch_diameter_mm=71.5,
    contact_angle_deg=15.17, shaft_rpm=2000
)

MACHINES = [
    {
        "id": "bearing1",
        "name": "IMS Test Rig · Bearing 1",
        "faultType": "Outer race defect (BPFO)",
        "dataPath": "2nd_test/2nd_test",
        "channelIndex": 0,
        "defectFreqHz": DEFECT_FREQS["BPFO"],
        "recordingIntervalMinutes": 10,
    },
    {
        "id": "bearing3",
        "name": "IMS Test Rig · Bearing 3",
        "faultType": "Inner race defect (BPFI)",
        "dataPath": "1st_test/1st_test",
        "channelIndex": 4,  # Bearing 3, x-axis (Channel 5, 0-indexed)
        "defectFreqHz": DEFECT_FREQS["BPFI"],
        "recordingIntervalMinutes": 10,  # simplified; README notes first 43 files were every 5 min
    },
    {
        "id": "bearing4",
        "name": "IMS Test Rig · Bearing 4",
        "faultType": "Roller element defect (BSF)",
        "dataPath": "1st_test/1st_test",
        "channelIndex": 6,  # Bearing 4, x-axis (Channel 7, 0-indexed)
        "defectFreqHz": DEFECT_FREQS["BSF"],
        "recordingIntervalMinutes": 10,
    },
]


def process_machine(machine):
    snaps, sr = load_ims_dataset(machine["dataPath"], channel_index=machine["channelIndex"])
    feature_matrix = np.array([[extract_features(s["signal"], sr, machine["defectFreqHz"])[k] for k in FEATURE_KEYS] for s in snaps])

    model = AnomalySeverityModel()
    n_baseline = model.fit_on_healthy_baseline(feature_matrix)
    severity = model.score(feature_matrix)
    smoothed = smooth_severity(severity)

    baseline = feature_matrix[5:n_baseline]
    baseline_mean = baseline.mean(axis=0)

    # Per-bearing adaptive thresholds: derived from this bearing's OWN healthy-baseline
    # noise level, with a safety margin, rather than reusing Bearing 1's fixed numbers.
    # This addresses the real finding that different fault types (inner-race vs.
    # outer-race) show different baseline noise characteristics.
    grace_period = 7
    known_healthy_region_end = len(smoothed) // 2  # everything before this is confirmed pre-fault
    baseline_severity_max = float(smoothed[grace_period:known_healthy_region_end].max())
    moderate_threshold = 0.3
    critical_threshold = max(0.45, round(baseline_severity_max * 1.15, 3))


    records = []
    for i, s in enumerate(smoothed):
        cost = estimate_weekly_cost(s, rated_output_power_kw=15.0, tariff_rs_per_kwh=8.0)
        days_to_critical = estimate_time_to_critical(smoothed[:i + 1])

        contributions = []
        for j, key in enumerate(FEATURE_KEYS):
            pct_above_baseline = ((feature_matrix[i, j] - baseline_mean[j]) / abs(baseline_mean[j])) * 100
            contributions.append({"label": FEATURE_LABELS[key], "pctAboveBaseline": round(float(pct_above_baseline), 1)})

        records.append({
            "index": i,
            "severity": round(float(s), 4),
            "healthScore": round((1 - s) * 100, 1),
            "weeklyCostRs": round(cost["weekly_cost_rs"], 0),
            "efficiencyLossPct": round(cost["efficiency_loss_pct"], 2),
            "daysToCritical": days_to_critical,
            "contributions": contributions,
        })

    return {
        "id": machine["id"],
        "name": machine["name"],
        "faultType": machine["faultType"],
        "recordingIntervalMinutes": machine["recordingIntervalMinutes"],
        "gracePeriodSnapshots": 7,
        "moderateThreshold": moderate_threshold,
        "criticalThreshold": critical_threshold,
        "ratedPowerKw": 15.0,
        "tariffRsPerKwh": 8.0,
        "scheduledRepairCostRs": 8000,
        "records": records,
    }


def main():
    output = {"machines": []}
    for machine in MACHINES:
        print(f"Processing {machine['name']} ({machine['faultType']})...")
        output["machines"].append(process_machine(machine))
        print(f"  -> {len(output['machines'][-1]['records'])} records")

    out_path = "frontend/public/machine_data.json"
    with open(out_path, "w") as f:
        json.dump(output, f)
    print(f"\nExported {len(output['machines'])} machines to {out_path}")


if __name__ == "__main__":
    main()