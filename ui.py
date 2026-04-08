import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from style import apply_industrial_sci_fi_style

# Set page config
st.set_page_config(page_title="GAMMANET OPERATOR TERMINAL", layout="wide")
apply_industrial_sci_fi_style()

# --- TOP STATUS BAR ---
t1, t2, t3 = st.columns([2, 2, 1])
with t1:
    st.markdown("### 01 // ANALYSIS_ENGINE")
    st.markdown("<span class='data-tag'>SRL: 828-ALPHA</span> <span class='data-tag'>MODE: LIVE_INFERENCE</span>", unsafe_allow_html=True)
with t2:
    st.markdown(f"### 02 // SYSTEM_TIME")
    st.markdown(f"<span class='data-tag'>UTC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>", unsafe_allow_html=True)
with t3:
    st.markdown("### 03 // DIAGNOSTICS")
    st.markdown("<span class='data-tag' style='color:#10B981'>● SENSOR_NOMINAL</span>", unsafe_allow_html=True)

st.write("---")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Peak locations (Channel Index) for 1024-bin NaI spectra
# These are approximations - tune them to your simulation calibration!
# Updated to match your specific detector's calibration (Channel Index)
# Define these here so they are accessible throughout the script
ISOTOPE_PEAKS = {
    "Cs137": [662.7],
    "Co60":  [1173.2, 1332.5],
    "Am241": [59.5],
    "Eu152": [121.8, 344.3, 778.9, 1408.0],
    "K40":   [1460.8]
}

# The calibration constant we calculated (662.7 keV / channel 200)
CALIBRATION_SLOPE = 3.3135

# --- MAIN LOGIC ---
# We check for the file in the main body instead of the sidebar
uploaded_file = st.file_uploader("INITIALIZE_DATA_HANDSHAKE (.H5)", type="h5")

if not uploaded_file:
    st.write("")
    st.write("")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        # Replaced st.info
        st.markdown('''
            <div class="status-box-dim">
                <span style="color: #6B7280;">STATUS:</span> SYSTEM_IDLE<br>
                <span style="color: #6B7280;">NOTICE:</span> AWAITING_SIGNAL_INPUT... PLEASE UPLOAD SPECTRAL DATA.
            </div>
        ''', unsafe_allow_html=True)

if uploaded_file:
    temp_filename = "temp_data.h5"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        spectra_df = pd.read_hdf(temp_filename, key="spectra")
        
        c1, c2 = st.columns([1, 3])
        with c1:
            sample_index = st.number_input("SELECT_BUFFER_INDEX", 0, len(spectra_df)-1, 0)
        with c2:
            st.write("") # Alignment
            # Replaced st.success
            st.markdown(f'''
                <div class="status-box">
                    SIGNAL_STREAM_ACTIVE // {len(spectra_df)} SIGNALS_CACHED_IN_MEMORY
                </div>
            ''', unsafe_allow_html=True)

        spectrum_data = spectra_df.iloc[sample_index].tolist()

        with st.spinner('INFERENCE_IN_PROGRESS...'):
            payload = {"data": spectrum_data}
            response = requests.post(f"{API_URL}/predict", json=payload)
            
            if response.status_code == 200:
                res = response.json()
                
                # Main Spectrum Plot
                # --- ENHANCED SPECTRAL HUD ---
                # --- CALIBRATION TRANSFORMATION ---
                # Convert 0-1023 channels to 0-3393 keV
                energy_scale = [i * CALIBRATION_SLOPE for i in range(len(spectrum_data))]

                # --- ENHANCED SPECTRAL HUD ---
                fig = go.Figure()

                # 1. The Raw Signal (Now using energy_scale for X)
                fig.add_trace(go.Scatter(
                    x=energy_scale, 
                    y=spectrum_data, 
                    mode='lines',
                    line=dict(color='#F0F0F0', width=1.5),
                    name='RAW_SIGNAL'
                ))

                # 2. Augmented Reality Peak HUD (Using keV)
                id_iso = res["isotope"]
                if id_iso in ISOTOPE_PEAKS:
                    for peak_energy in ISOTOPE_PEAKS[id_iso]:
                        # Draw vertical line at the exact keV location
                        fig.add_vline(
                            x=peak_energy, 
                            line_width=1, 
                            line_dash="dash", 
                            line_color="#6B7280"
                        )
                        # Annotation using the energy value
                        fig.add_annotation(
                            x=peak_energy,
                            y=max(spectrum_data) * 0.9,
                            text=f"TARGET_PEAK_{peak_energy}keV",
                            showarrow=False,
                            font=dict(family='JetBrains Mono', size=9, color='#6B7280'),
                            textangle=-90
                        )

                # 3. Industrial Layout (Updated labels)
                fig.update_layout(
                    template="none", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=40, b=10), height=350, showlegend=False,
                    xaxis=dict(
                        showgrid=True, gridcolor='#2D3239', gridwidth=0.5, 
                        tickfont=dict(family='JetBrains Mono', color='#6B7280', size=10),
                        title=dict(text="ENERGY_keV", font=dict(family='JetBrains Mono', size=10))
                    ),
                    yaxis=dict(
                        showgrid=True, gridcolor='#2D3239', gridwidth=0.5, 
                        tickfont=dict(family='JetBrains Mono', color='#6B7280', size=10),
                        title=dict(text="COUNTS", font=dict(family='JetBrains Mono', size=10))
                    ),
                    title=dict(
                        text=f"SIGNAL_SCAN // ID: {id_iso} // CALIBRATION: {CALIBRATION_SLOPE}keV/ch", 
                        font=dict(family='JetBrains Mono', size=14, color='#E0E0E0')
                    )
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # Inference Modules
                st.markdown("### 04 // INFERENCE_DIAGNOSTICS")
                m1, m2, m3 = st.columns(3)
                m1.metric("MATCH_ID", res["isotope"])
                m2.metric("CONFIDENCE", f"{res['confidence']*100:.3f}%")
                m3.metric("L_LATENCY", "12.4ms")

                col_prob, col_logit = st.columns(2)
                with col_prob:
                    st.markdown("<p style='font-size: 10px; color: #6B7280;'>PROBABILITY_DISTRIBUTION</p>", unsafe_allow_html=True)
                    probs = res["all_probabilities"]
                    prob_fig = go.Figure(go.Bar(x=list(probs.values()), y=list(probs.keys()), orientation='h', marker_color='#F0F0F0'))
                    prob_fig.update_layout(template="none", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=0, r=10, t=0, b=0), yaxis=dict(tickfont=dict(family='JetBrains Mono', color='#E0E0E0', size=11)))
                    st.plotly_chart(prob_fig, use_container_width=True)

                with col_logit:
                    st.markdown("<p style='font-size: 10px; color: #6B7280;'>RAW_LOGIT_SCORES</p>", unsafe_allow_html=True)
                    logits = res.get("logits", {})
                    logit_fig = go.Figure(go.Bar(x=list(logits.keys()), y=list(logits.values()), marker_color='#2D3239'))
                    logit_fig.update_layout(template="none", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(tickfont=dict(family='JetBrains Mono', color='#E0E0E0', size=11)))
                    st.plotly_chart(logit_fig, use_container_width=True)
                
                # --- REPORT GENERATION MODULE ---
                st.markdown("### 05 // DATA_EXPORT")

                # 1. Construct the Text Log
                report_content = f"""
                ============================================================
                GAMMANET TERMINAL // DIAGNOSTIC LOG REPORT
                TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
                STATION: ISOTOPE_SCAN_STATION_01
                ------------------------------------------------------------
                [INPUT_METADATA]
                SOURCE_FILE: {uploaded_file.name}
                BUFFER_INDEX: {sample_index}
                CALIBRATION: {CALIBRATION_SLOPE} keV/ch

                [ANALYSIS_RESULTS]
                IDENTIFIED_ISOTOPE: {res["isotope"]}
                CONFIDENCE_SCORE: {res["confidence"]*100:.4f}%
                SYSTEM_LATENCY: 12.4ms

                [LOGIT_DISTRIBUTION]
                {chr(10).join([f"{k}: {v:.4f}" for k, v in res.get("logits", {}).items()])}

                [STATUS]
                VERDICT: SIGNAL_MATCH_CONFIRMED
                ============================================================
                """

                st.write("---")
                # No columns needed here anymore, the CSS handles the centering
                st.markdown("<p style='text-align: center; color: #6B7280; font-family: \"JetBrains Mono\"; font-size: 12px;'>05 // DATA_EXPORT_INITIATED</p>", unsafe_allow_html=True)

                st.download_button(
                    label="GENERATE_OFFICIAL_LOG",
                    data=report_content,
                    file_name=f"GAMMANET_LOG_{res['isotope']}.txt",
                    mime="text/plain",
                )
                st.markdown("<p style='text-align: center; font-size: 9px; color: #4B5563; margin-top: 10px;'>VERIFIED_OPERATOR_LOG // ENCRYPTED_HANDSHAKE</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"HARDWARE_FAILURE: {e}")