import numpy as np
import os
import glob

def generate_synthetic_run_to_failure(n_snapshots=200, snapshot_length=4096,
                                        sample_rate_hz=20000, defect_freq_hz=236.4):
    """
    Simulates a bearing's vibration signal over its life, from healthy to failure.
    """
    rng = np.random.default_rng(42)
    t = np.arange(snapshot_length) / sample_rate_hz
    snapshots = []

    for i in range(n_snapshots):
        life_fraction = i / (n_snapshots - 1)

        # Baseline healthy vibration: shaft rotation tone + random noise
        signal = 0.3 * np.sin(2 * np.pi * 30 * t)
        signal += rng.normal(0, 0.15, size=snapshot_length)

        # Fault severity: stays at 0 for the first 55% of life, then ramps up
        # non-linearly (squared) so it accelerates near the end -- like a real fault.
        defect_severity = max(0.0, life_fraction - 0.55) / 0.45
        defect_severity = defect_severity ** 2.2

        if defect_severity > 0:
            # A real bearing fault creates a repeating "impulse" every time
            # the damaged spot rolls past -- that's what this loop simulates.
            impulse_train = np.zeros(snapshot_length)
            period_samples = int(sample_rate_hz / defect_freq_hz)
            for start in range(0, snapshot_length, period_samples):
                end = min(start + 3, snapshot_length)
                impulse_train[start:end] += 1.0
            signal += defect_severity * 1.8 * impulse_train

        snapshots.append({
            "index": i,
            "signal": signal,
            "true_life_fraction": life_fraction,
        })

    return snapshots, sample_rate_hz

def load_ims_dataset(folder_path, sample_rate_hz=20000, channel_index=0):
    """
    Loads real IMS bearing files from a folder. Each file is one timestamped
    vibration snapshot with one column per bearing channel. channel_index=0
    corresponds to Bearing 1 -- confirmed against the official README for
    Set 2, where Bearing 1 is Channel 1 (0-indexed here) and is the bearing
    that developed the outer-race fault.
    """
    files = sorted(glob.glob(os.path.join(folder_path, "*")))
    if not files:
        raise FileNotFoundError(f"No files found in {folder_path}.")

    snapshots = []
    for i, f in enumerate(files):
        data = np.loadtxt(f)
        signal = data[:, channel_index] if data.ndim > 1 else data
        snapshots.append({"index": i, "signal": signal, "true_life_fraction": None})

    return snapshots, sample_rate_hz