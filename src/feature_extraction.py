import numpy as np
from scipy.stats import kurtosis

def extract_features(signal, sample_rate_hz, defect_freq_hz, band_width_hz=15.0):
    signal = np.asarray(signal, dtype=float)
    signal = signal - np.mean(signal)

    rms = np.sqrt(np.mean(signal ** 2))
    peak = np.max(np.abs(signal))
    crest_factor = peak / rms if rms > 0 else 0.0
    kurt = kurtosis(signal, fisher=False)

    n = len(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
    spectrum = np.abs(np.fft.rfft(signal)) / n

    def band_energy(center_freq):
        mask = (freqs >= center_freq - band_width_hz) & (freqs <= center_freq + band_width_hz)
        return np.sum(spectrum[mask] ** 2)

    defect_band_energy = band_energy(defect_freq_hz)
    harmonic_2x_energy = band_energy(defect_freq_hz * 2)
    harmonic_3x_energy = band_energy(defect_freq_hz * 3)

    return {
        "rms": rms,
        "crest_factor": crest_factor,
        "kurtosis": kurt,
        "defect_band_energy": defect_band_energy,
        "harmonic_2x_energy": harmonic_2x_energy,
        "harmonic_3x_energy": harmonic_3x_energy,
    }