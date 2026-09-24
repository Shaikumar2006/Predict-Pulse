import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from data_loader import generate_synthetic_run_to_failure, load_ims_dataset
from feature_extraction import extract_features
from anomaly_model import AnomalySeverityModel, smooth_severity, estimate_time_to_critical
from energy_cost import estimate_weekly_cost, estimate_avoided_repair_premium
from bearing_geometry import calculate_defect_frequencies

st.set_page_config(page_title="Predictive Maintenance Advisor", layout="wide")
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #F0F4F4;
        border-radius: 10px;
        padding: 15px 10px;
        border: 1px solid #E0E6E6;
    }
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
    .stSlider [data-baseweb="slider"] {
        padding-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)
st.title("🔧 Predictive Maintenance & Energy-Cost Advisor")
st.caption(
    "Detects early-stage bearing degradation from vibration data and translates it "
    "into an estimated energy cost — built for SME manufacturers who can't afford "
    "enterprise-grade condition monitoring."
)

# --- Sidebar: Machine Parameters ---
st.sidebar.header("Machine Parameters")
rated_power_kw = st.sidebar.number_input("Motor rated power (kW)", value=15.0)
tariff = st.sidebar.number_input("Electricity tariff (Rs/kWh)", value=8.0)
scheduled_repair_cost = st.sidebar.number_input(
    "Estimated cost of a SCHEDULED repair (Rs)", value=8000,
    help="What you'd expect to pay for a planned bearing replacement, including labor and parts."
)

# --- Sidebar: Bearing Specifications (generalizes beyond this one test rig) ---
st.sidebar.divider()
with st.sidebar.expander("⚙️ Bearing Specifications (advanced)", expanded=False):
    st.caption("Defaults match the IMS test rig (Rexnord ZA-2115) used to validate this model.")
    n_rolling_elements = st.number_input("Number of rolling elements", value=16, min_value=2)
    ball_diameter_mm = st.number_input("Ball/roller diameter (mm)", value=8.4)
    pitch_diameter_mm = st.number_input("Pitch diameter (mm)", value=71.5)
    contact_angle_deg = st.number_input("Contact angle (degrees)", value=15.17)
    shaft_rpm = st.number_input("Shaft speed (RPM)", value=2000)
    fault_type = st.selectbox("Which fault type to monitor for?", ["BPFO (Outer race)", "BPFI (Inner race)", "BSF (Ball/roller)"])

defect_freqs = calculate_defect_frequencies(n_rolling_elements, ball_diameter_mm, pitch_diameter_mm, contact_angle_deg, shaft_rpm)
fault_key_map = {"BPFO (Outer race)": "BPFO", "BPFI (Inner race)": "BPFI", "BSF (Ball/roller)": "BSF"}
defect_freq_hz = defect_freqs[fault_key_map[fault_type]]
st.sidebar.caption(f"Calculated defect frequency: {defect_freq_hz:.1f} Hz")

st.sidebar.divider()
# --- Sidebar: Data Source ---
st.sidebar.header("Data Source")
data_mode = st.sidebar.radio("Choose dataset", ["Synthetic demo", "Real IMS data (2nd_test)"])

GRACE_PERIOD_SNAPSHOTS = 7
FEATURE_KEYS = ["rms", "crest_factor", "kurtosis", "defect_band_energy", "harmonic_2x_energy", "harmonic_3x_energy"]

# --- Run the pipeline once per (data source, defect frequency) combo, cached ---
@st.cache_data
def run_pipeline(mode, defect_freq_hz):
    if mode == "Real IMS data (2nd_test)":
        snaps, sr = load_ims_dataset("2nd_test/2nd_test")
        recording_interval_minutes = 10  # per official IMS README
    else:
        snaps, sr = generate_synthetic_run_to_failure()
        recording_interval_minutes = None

    feature_matrix = np.array([
        [extract_features(s["signal"], sr, defect_freq_hz)[k] for k in FEATURE_KEYS]
        for s in snaps
    ])
    model = AnomalySeverityModel()
    model.fit_on_healthy_baseline(feature_matrix)  # tuned defaults: healthy_fraction=0.4, skip_startup=5
    severity = model.score(feature_matrix)
    smoothed = smooth_severity(severity)  # tuned default: window=5
    return smoothed, recording_interval_minutes

severity, recording_interval_minutes = run_pipeline(data_mode, defect_freq_hz)

# --- Replay slider ---
st.subheader("Live Monitoring Replay")
if recording_interval_minutes:
    st.caption(f"Drag to simulate time passing. Each step here = {recording_interval_minutes} minutes of real recorded data.")
else:
    st.caption("Drag to simulate time passing over this machine's operating life (synthetic demo).")

time_index = st.slider("Simulated time (snapshot #)", 0, len(severity) - 1, len(severity) - 1)
current_severity = severity[time_index]
cost = estimate_weekly_cost(current_severity, rated_output_power_kw=rated_power_kw, tariff_rs_per_kwh=tariff)

# --- Metrics row ---
col1, col2 = st.columns(2)
col1.metric("Health Score", f"{(1 - current_severity) * 100:.0f}/100")
col2.metric("Estimated Excess Cost", f"₹{cost['weekly_cost_rs']:.0f}/week")

# --- Days-to-failure projection ---
if current_severity > 0.3:
    days_projection = estimate_time_to_critical(severity[:time_index + 1])
    if days_projection == 0.0:
        st.caption("📉 Already at or above the critical threshold based on current readings.")
    elif days_projection is not None and days_projection > 0:
        st.caption(
            f"📉 Rough trend-based estimate: **~{days_projection:.1f} days** to critical threshold "
            f"if current trend continues. Note: sudden-onset faults can shorten this significantly — "
            f"treat as directional, not precise."
        )

# --- Three-tier alert, with a startup grace period ---
st.subheader("Machine Status")
if time_index < GRACE_PERIOD_SNAPSHOTS:
    st.info(
        f"🔵 **Warming up.** Startup vibration transients are expected in the first few "
        f"readings after a machine starts — monitoring will begin evaluating for real "
        f"anomalies after this initial period."
    )
elif current_severity > 0.45:
    avoided_low, avoided_high = estimate_avoided_repair_premium(scheduled_repair_cost)
    st.error(
        f"⚠️ **High-severity anomaly detected.** Estimated efficiency loss: "
        f"{cost['efficiency_loss_pct']:.2f}%, costing an estimated ₹{cost['weekly_cost_rs']:.0f}/week "
        f"in excess energy alone. **Recommend scheduling an inspection within the next few days.**\n\n"
        f"💰 Catching this now, rather than waiting for it to fail, could also avoid an estimated "
        f"**₹{avoided_low:.0f}–₹{avoided_high:.0f}** in emergency repair premium — reactive repairs "
        f"are documented to cost 3–5x more than the same job done on a planned schedule."
    )
elif current_severity > 0.3:
    st.warning(
        f"🟡 **Moderate anomaly detected.** Estimated efficiency loss: {cost['efficiency_loss_pct']:.2f}%. "
        f"Not urgent yet — recommend monitoring closely and planning inspection during the next scheduled downtime."
    )
else:
    st.success("✅ Machine operating within normal parameters. No action needed.")

# --- Trend chart ---
health_scores = (1 - severity[:time_index + 1]) * 100
x_vals = list(range(len(health_scores)))

fig = go.Figure()

# Shaded zones (drawn first, so the line sits on top)
fig.add_hrect(y0=70, y1=100, fillcolor="rgba(16, 163, 74, 0.08)", line_width=0)   # green: healthy
fig.add_hrect(y0=55, y1=70, fillcolor="rgba(234, 179, 8, 0.10)", line_width=0)    # yellow: moderate
fig.add_hrect(y0=0, y1=55, fillcolor="rgba(220, 38, 38, 0.08)", line_width=0)     # red: high severity

# The actual health score line
fig.add_trace(go.Scatter(x=x_vals, y=health_scores, mode="lines", name="Health Score",
                          line=dict(color="#0E7C7B", width=2)))

fig.update_layout(
    title="Machine Health Over Time",
    yaxis_title="Health Score",
    xaxis_title="Snapshot #",
    yaxis_range=[0, 100],
    height=350,
    margin=dict(l=10, r=10, t=40, b=10),
)

st.plotly_chart(fig, use_container_width=True)

# --- Transparency panel ---
with st.expander("How is this cost calculated? (full transparency)"):
    st.write(f"""
    - **Current severity score:** {current_severity:.3f} (0 = healthy, 1 = most anomalous observed)
    - **Estimated efficiency loss:** {cost['efficiency_loss_pct']:.2f}%, scaled within the literature-reported
      1.5–4% range for bearing faults, as a function of severity
    - **Healthy motor efficiency assumed:** 91.7% (IEC 60034-30-1 nominal for a 15 kW IE3-class motor —
      India's BEE-mandated minimum efficiency class)
    - **Excess power draw:** {cost['excess_power_kw']:.3f} kW
    - **Operating assumption:** {rated_power_kw:.0f} kW rated motor, ₹{tariff:.2f}/kWh tariff
    - **Bearing defect frequency:** {defect_freq_hz:.1f} Hz, calculated from your entered bearing geometry
      (not hardcoded — this is what makes the tool work for any bearing, not just this test rig)
    - **Result:** ₹{cost['weekly_cost_rs']:.0f}/week in estimated excess energy cost
    - **Avoided repair premium (if high severity):** based on a documented 3–5x emergency-vs-scheduled
      repair cost multiplier, applied to your entered scheduled-repair estimate of ₹{scheduled_repair_cost:.0f}

    *These are literature-grounded approximations for a representative case, not precision figures
    for this specific machine — exact costs depend on motor design, load profile, fault type, and
    local labor/parts markets.*
    """)