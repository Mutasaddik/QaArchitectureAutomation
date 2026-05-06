# src/ui_theme.py

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary:    #0d1117;
    --bg-secondary:  #0a0f1a;
    --bg-card:       #161b27;
    --bg-hover:      #1c2333;
    --border:        rgba(255,255,255,0.06);
    --border-bright: rgba(255,255,255,0.12);
    --accent-blue:   #4f8ef7;
    --accent-cyan:   #38bdf8;
    --accent-green:  #22c55e;
    --accent-teal:   #14b8a6;
    --text-primary:  #f0ece3;
    --text-secondary:#a8a49c;
    --text-muted:    #5c5852;
    --gradient-1: linear-gradient(135deg, #4f8ef7 0%, #38bdf8 100%);
    --gradient-green: linear-gradient(135deg, #14b8a6, #22c55e);
    --shadow-glow: 0 0 24px rgba(79,142,247,0.12);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* ── Sidebar — no borders, floating clean nav ─── */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: none !important;
    box-shadow: none !important;
}

[data-testid="stSidebarNav"] {
    padding: 0.5rem 0.75rem !important;
}

[data-testid="stSidebarNav"] a {
    display: flex !important;
    align-items: center !important;
    border-radius: 8px !important;
    margin: 1px 0 !important;
    padding: 9px 14px !important;
    transition: all 0.15s ease !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border: none !important;
    background: transparent !important;
    letter-spacing: 0.01em !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(79,142,247,0.1) !important;
    color: var(--accent-cyan) !important;
    border-left: 2px solid var(--accent-blue) !important;
    font-weight: 600 !important;
}

/* ── Main content ────────────────────────────────── */
.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1280px !important;
}

/* ── Typography ──────────────────────────────────── */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    -webkit-text-fill-color: var(--text-primary) !important;
}

h2 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em !important;
}

h3 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

p, li { color: var(--text-secondary) !important; line-height: 1.65 !important; }

code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--accent-cyan) !important;
    padding: 2px 6px !important;
    font-size: 0.82em !important;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: var(--border-bright) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px) !important;
}

.stButton > button[kind="primary"] {
    background: var(--gradient-1) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(79,142,247,0.25) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79,142,247,0.35) !important;
    color: white !important;
}

/* ── Inputs ──────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.1) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── Select ──────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* ── Metrics ─────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.25rem 1.5rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="metric-container"]:hover {
    border-color: var(--border-bright) !important;
    box-shadow: var(--shadow-glow) !important;
    transform: translateY(-2px) !important;
}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
}

[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: var(--accent-green) !important;
    font-size: 0.78rem !important;
}

/* ── Expanders ───────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.15s ease !important;
}

.streamlit-expanderHeader:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-bright) !important;
}

.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    padding: 1rem !important;
}

/* ── Tabs ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 6px 16px !important;
    transition: all 0.15s ease !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255,255,255,0.05) !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(79,142,247,0.15) !important;
    color: var(--accent-cyan) !important;
    font-weight: 600 !important;
}

/* ── Alerts ──────────────────────────────────────── */
.stSuccess {
    background: rgba(20,184,166,0.08) !important;
    border: 1px solid rgba(20,184,166,0.2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--accent-teal) !important;
}

.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: var(--radius-sm) !important;
}

.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    border-radius: var(--radius-sm) !important;
}

.stInfo {
    background: rgba(79,142,247,0.06) !important;
    border: 1px solid rgba(79,142,247,0.15) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--accent-blue) !important;
}

/* ── Dataframe ───────────────────────────────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}

.stDataFrame thead th {
    background: var(--bg-hover) !important;
    color: var(--text-muted) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    border-bottom: 1px solid var(--border) !important;
}

.stDataFrame tbody tr { border-bottom: 1px solid var(--border) !important; }
.stDataFrame tbody tr:hover { background: var(--bg-hover) !important; }
.stDataFrame tbody td { color: var(--text-secondary) !important; font-size: 0.85rem !important; padding: 9px 16px !important; }

/* ── File uploader ───────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.5rem !important;
    transition: all 0.15s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-blue) !important;
    background: rgba(79,142,247,0.04) !important;
}

/* ── Chat messages ───────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.625rem !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(79,142,247,0.04) !important;
    border-color: rgba(79,142,247,0.15) !important;
}

[data-testid="stChatInput"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.08) !important;
}

/* ── Divider ─────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

.stCaption { color: var(--text-muted) !important; font-size: 0.78rem !important; }

/* ── Slider ──────────────────────────────────────── */
.stSlider > div > div > div > div { background: var(--gradient-1) !important; }

/* ── Radio ───────────────────────────────────────── */
.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-sm) !important;
    padding: 7px 14px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}
.stRadio > div > label:hover {
    border-color: var(--accent-blue) !important;
    color: var(--text-primary) !important;
}

/* ── Custom components ───────────────────────────── */
.qa-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    transition: all 0.2s ease;
    cursor: pointer;
}

.qa-card:hover {
    border-color: var(--border-bright);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.qa-page-header {
    padding: 0.5rem 0 1.75rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

.qa-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

.qa-badge-blue   { background: rgba(79,142,247,0.12); color: #7eb3fa; }
.qa-badge-green  { background: rgba(34,197,94,0.12);  color: #4ade80; }
.qa-badge-orange { background: rgba(245,158,11,0.12); color: #fbbf24; }
.qa-badge-teal   { background: rgba(20,184,166,0.12); color: #2dd4bf; }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    import streamlit as st
    st.markdown(f"""
    <div class="qa-page-header">
        <h1>{icon} {title}</h1>
        {f'<p style="color:var(--text-muted);margin-top:6px;font-size:0.875rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def status_badge(text: str, color: str = "blue") -> str:
    return f'<span class="qa-badge qa-badge-{color}">{text}</span>'