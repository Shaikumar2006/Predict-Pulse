import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalySeverityModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=0.01, random_state=42)

    def fit_on_healthy_baseline(self, feature_matrix, healthy_fraction=0.4, skip_startup=5):
        """
        skip_startup: number of initial snapshots to exclude from training,
        since real machines often show startup transients that aren't
        representative of steady-state healthy operation.
        """
        n_baseline = int(len(feature_matrix) * healthy_fraction)
        baseline = feature_matrix[skip_startup:n_baseline]
        baseline_scaled = self.scaler.fit_transform(baseline)
        self.model.fit(baseline_scaled)
        return n_baseline

    def score(self, feature_matrix):
        scaled = self.scaler.transform(feature_matrix)
        raw_scores = -self.model.decision_function(scaled)
        severity = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min() + 1e-9)
        return severity


def smooth_severity(severity, window=5):
    """Backward-looking rolling average -- only uses past and current values,
    never future ones. This is essential for live monitoring: at any real
    moment in time, future readings simply don't exist yet."""
    smoothed = np.zeros_like(severity, dtype=float)
    for i in range(len(severity)):
        start = max(0, i - window + 1)
        smoothed[i] = np.mean(severity[start:i + 1])
    return smoothed


def estimate_time_to_critical(severity_history, snapshot_interval_minutes=10, critical_threshold=0.45):
    """
    Fits a straight line through the most recent readings and projects forward
    to estimate when severity will cross the critical threshold. Only uses
    past/current data -- exactly like a real live system would have to.

    IMPORTANT: checks "already at/above critical" BEFORE checking the recent
    slope. A noisy plateau sitting above the threshold can have a flat or
    slightly negative slope even though it's already critical -- checking
    slope first would incorrectly return None in that case.

    Returns:
        0.0 if already at or above critical_threshold
        a positive number of days if a genuine rising trend is projected to cross it
        None if there's no rising trend and it's not already critical
    """
    recent_window = min(20, len(severity_history))
    if recent_window < 3:
        return None

    recent = severity_history[-recent_window:]
    current = recent[-1]

    if current >= critical_threshold:
        return 0.0

    x = np.arange(recent_window)
    slope, intercept = np.polyfit(x, recent, 1)

    if slope <= 1e-6:
        return None

    steps_needed = (critical_threshold - current) / slope
    minutes_needed = steps_needed * snapshot_interval_minutes
    return minutes_needed / (60 * 24)