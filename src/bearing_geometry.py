import numpy as np

def calculate_defect_frequencies(n_rolling_elements, ball_diameter_mm, pitch_diameter_mm,
                                    contact_angle_deg, shaft_rpm):
    """
    Calculates standard bearing defect frequencies from physical geometry.
    These are the frequencies our feature_extraction.py should search for,
    depending on which part of the bearing is actually damaged.
    """
    fr = shaft_rpm / 60.0  # shaft rotation frequency in Hz
    ratio = (ball_diameter_mm / pitch_diameter_mm) * np.cos(np.radians(contact_angle_deg))
    N = n_rolling_elements

    bpfo = (N / 2) * fr * (1 - ratio)   # Outer race defect frequency
    bpfi = (N / 2) * fr * (1 + ratio)   # Inner race defect frequency
    bsf = (pitch_diameter_mm / (2 * ball_diameter_mm)) * fr * (1 - ratio ** 2)  # Ball/roller defect
    ftf = 0.5 * fr * (1 - ratio)         # Cage defect frequency

    return {"BPFO": bpfo, "BPFI": bpfi, "BSF": bsf, "FTF": ftf}