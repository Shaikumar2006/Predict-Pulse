import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from data_loader import load_ims_dataset
from feature_extraction import extract_features


def smooth(severity, window):
    out = np.zeros_like(severity)
    for i in range(len(severity)):
        start = max(0, i - window + 1)
        out[i] = np.mean(severity[start:i + 1])
    return out


def main():
    snaps, sr = load_ims_dataset("2nd_test/2nd_test")
    keys = ["rms", "crest_factor", "kurtosis", "defect_band_energy", "harmonic_2x_energy", "harmonic_3x_energy"]
    feature_matrix = np.array([[extract_features(s["signal"], sr, 236.4)[k] for k in keys] for s in snaps])

    total = len(feature_matrix)
    print(f"{'healthy_frac':>13} {'window':>6} {'n_baseline':>10} {'worst_healthy':>14} {'crossing_idx':>13} {'lead_days':>10}")

    for healthy_fraction in [0.3, 0.4, 0.5]:
        n_baseline = int(total * healthy_fraction)
        scaler = StandardScaler()
        baseline = feature_matrix[5:n_baseline]  # still skip startup transient
        baseline_scaled = scaler.fit_transform(baseline)
        model = IsolationForest(contamination=0.05, random_state=42)  # confirmed not to matter, fixed value
        model.fit(baseline_scaled)

        scaled_all = scaler.transform(feature_matrix)
        raw = -model.decision_function(scaled_all)
        severity = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)

        for window in [5, 7]:  # excluding window=3, already proven unreliable
            smoothed = smooth(severity, window)
            # IMPORTANT: healthy-period check must stay within the region we
            # actually know is healthy (up to 520), regardless of n_baseline,
            # so larger training sizes don't sneak fault-affected data into
            # what we call "healthy" during evaluation.
            worst_healthy = smoothed[20:520].max()
            crossing = next((i for i, v in enumerate(smoothed) if i > 20 and v > 0.45), None)
            if crossing:
                lead_days = (total - 1 - crossing) * 10 / 60 / 24
                print(f"{healthy_fraction:>13} {window:>6} {n_baseline:>10} {worst_healthy:>14.3f} {crossing:>13} {lead_days:>10.2f}")
            else:
                print(f"{healthy_fraction:>13} {window:>6} {n_baseline:>10} {worst_healthy:>14.3f} {'never':>13} {'-':>10}")


if __name__ == "__main__":
    main()