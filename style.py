import streamlit as st

def apply_industrial_sci_fi_style():
    industrial_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');

    /* Global Aesthetic */
    .stApp {
        background-color: #121417;
        color: #D1D1D1;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Remove Streamlit's default top bar and padding */
    header[data-testid="stHeader"] { visibility: hidden; }
    .block-container { padding-top: 2rem !important; }

    /* Modular Containers (Upper Deck Style) */
    [data-testid="stMetric"], .stExpander, .stChatMessage {
        background-color: #1A1D21;
        border: 1px solid #2D3239;
        border-radius: 2px !important;
        padding: 20px !important;
    }

    /* Metrics - Functional and Muted */
    [data-testid="stMetricValue"] {
        color: #E0E0E0 !important;
        font-weight: 300 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #6B7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Sidebar - Deep Slate and Minimal */
    [data-testid="stSidebar"] {
        background-color: #0F1113;
        border-right: 1px solid #2D3239;
        width: 300px !important;
    }

    /* Buttons - Industrial Tooling */
    .stButton>button {
        background-color: #2D3239;
        color: #D1D1D1;
        border: 1px solid #3F444D;
        border-radius: 2px;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        width: 100%;
        transition: 0.2s;
    }

    .stButton>button:hover {
        background-color: #E0E0E0;
        color: #121417;
        border-color: #E0E0E0;
    }

    /* Typography */
    h1, h2, h3 {
        color: #F0F0F0 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: -0.02em;
        border-bottom: 1px solid #2D3239;
        padding-bottom: 10px;
    }

    /* Custom Data Tag */
    .data-tag {
        background: #2D3239;
        padding: 2px 6px;
        font-size: 10px;
        color: #9CA3AF;
        border-radius: 2px;
        margin-right: 5px;
    }

    /* Target the Download Button specifically */
    /* Overwrite the Download Button for maximum impact */
    .stDownloadButton {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        padding-top: 2rem;
    }

    .stDownloadButton > button {
        background-color: #F0F0F0 !important;
        color: #121417 !important;
        border-radius: 0px !important;
        /* Make it larger */
        width: 400px !important; 
        height: 60px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        border: 2px solid #F0F0F0 !important;
    }

    .stDownloadButton > button:hover {
        background-color: #D1D1D1 !important; /* Slightly darker on hover */
        border-color: #D1D1D1 !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(240, 240, 240, 0.4) !important;
    }

    .stDownloadButton > button:active {
        transform: translateY(2px) !important;
    }

    /* Custom Industrial Status Boxes */
    .status-box {
        background-color: #F0F0F0;
        color: #121417;
        padding: 15px;
        border-radius: 0px;
        border: 1px solid #F0F0F0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }

    /* A version for warnings/idle states if you want it slightly different */
    .status-box-dim {
        background-color: #1A1D21;
        color: #F0F0F0;
        padding: 15px;
        border: 1px solid #2D3239;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    /* Stylize Number Input to look like an LCD readout */
    div[data-testid="stNumberInput"] {
        background-color: #0F1113 !important;
        border: 1px solid #2D3239 !important;
        padding: 5px !important;
    }

    div[data-testid="stNumberInput"] label {
        color: #6B7280 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #0F1113 !important;
        color: #F0F0F0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: none !important;
        font-size: 18px !important;
    }

    /* Target the +/- buttons */
    div[data-testid="stNumberInput"] button {
        background-color: #1A1D21 !important;
        color: #F0F0F0 !important;
        border: 1px solid #2D3239 !important;
    }
    </style>
    """
    st.markdown(industrial_css, unsafe_allow_html=True)