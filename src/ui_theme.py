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
    --radius-sm: 8px;
    --radius-md: 12px;
}

*, *::before, *::after { box-sizing: border-box; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* ─── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%) !important;
    border-right: 2px solid rgba(220,50,100,0.5) !important;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5) !important;
}

[data-testid="stSidebarNav"] {
    padding: 0.75rem !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin: 3px 4px !important;
    padding: 10px 16px !important;
    transition: all 0.2s ease !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border: 1px solid transparent !important;
    background: transparent !important;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(220,50,100,0.12) !important;
    color: white !important;
    border-color: rgba(220,50,100,0.35) !important;
    transform: translateX(3px) !important;
}

[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(220,50,100,0.25), rgba(180,30,80,0.15)) !important;
    color: white !important;
    border-color: rgba(220,50,100,0.5) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(220,50,100,0.2) !important;
}

/* ─── Default buttons — ghost 3D ──────────────────────────── */
.stButton > button {
    background: rgba(255,255,255,0.03) !important;
    color: var(--text-primary) !important;
    border: 1px solid rgba(128,128,128,0.12) !important;
    border-bottom: 2px solid rgba(0,0,0,0.18) !important;
    border-radius: 7px !important;
    font-family: Inter, sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.12s ease !important;
    box-shadow:
        0 1px 2px rgba(0,0,0,0.12),
        inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

.stButton > button:hover {
    background: rgba(128,128,128,0.08) !important;
    border-color: rgba(128,128,128,0.20) !important;
    border-bottom-color: rgba(0,0,0,0.22) !important;
    transform: translateY(-1px) !important;
    box-shadow:
        0 3px 8px rgba(0,0,0,0.18),
        inset 0 1px 0 rgba(255,255,255,0.07) !important;
}

.stButton > button:active {
    transform: translateY(1px) !important;
    box-shadow: none !important;
    border-bottom-width: 1px !important;
}

/* ─── Primary buttons ─────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    border: 1px solid rgba(128,128,128,0.16) !important;
    border-bottom: 2px solid rgba(0,0,0,0.22) !important;
    box-shadow:
        0 2px 5px rgba(0,0,0,0.15),
        inset 0 1px 0 rgba(255,255,255,0.07) !important;
}

.stButton > button[kind="primary"]:hover {
    background: rgba(128,128,128,0.09) !important;
    border-bottom-color: rgba(0,0,0,0.28) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2) !important;
}

.stButton > button[kind="primary"]:active {
    transform: translateY(1px) !important;
    border-bottom-width: 1px !important;
    box-shadow: none !important;
}

/* ─── Cards ───────────────────────────────────────────────── */
.qa-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    transition: all 0.2s ease;
}
.qa-card:hover {
    border-color: var(--border-bright);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* ─── Page header ─────────────────────────────────────────── */
.qa-page-header {
    padding: 0.5rem 0 1.75rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

/* ─── Badges ──────────────────────────────────────────────── */
.qa-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
}
.qa-badge-blue  { background: rgba(79,142,247,0.12);  color: #7eb3fa; }
.qa-badge-green { background: rgba(34,197,94,0.12);   color: #4ade80; }
.qa-badge-teal  { background: rgba(20,184,166,0.12);  color: #2dd4bf; }
.qa-badge-red   { background: rgba(220,50,100,0.12);  color: #f472b6; }
.qa-badge-amber { background: rgba(245,158,11,0.12);  color: #fbbf24; }
</style>
"""


def inject_theme():
    """Call once at the top of every page to apply global styles."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Renders a styled page header with optional icon and subtitle."""
    import streamlit as st
    st.markdown(f"""
    <div class="qa-page-header">
        <h1 style="margin:0; color:var(--text-primary); font-family:Inter,sans-serif; font-size:1.6rem; font-weight:700;">
            {icon} {title}
        </h1>
        {f'<p style="color:var(--text-muted);margin-top:6px;font-size:0.875rem;font-family:Inter,sans-serif;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def status_badge(text: str, color: str = "blue") -> str:
    """Returns an HTML badge string. Use inside st.markdown(..., unsafe_allow_html=True)."""
    return f'<span class="qa-badge qa-badge-{color}">{text}</span>'


def active_button(label: str, key: str = None, use_container_width: bool = False) -> bool:
    """
    Renders a green 'active' styled button.

    Works by injecting an invisible sibling div directly before the button,
    then using CSS adjacent-sibling selector (+) to style it — the most
    reliable way to target a specific Streamlit button without custom class support.

    Usage:
        if active_button("✓ Run Tests", key="run_tests"):
            st.success("Running!")
    """
    import streamlit as st
    import hashlib

    btn_key = key or label.lower().replace(" ", "_").replace("✓", "check")
    uid = hashlib.md5(btn_key.encode()).hexdigest()[:8]

    st.markdown(f"""
    <style>
    .abtn-anchor-{uid} + div button,
    .abtn-anchor-{uid} + div + div button {{
        background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: Inter, sans-serif !important;
        font-size: 0.875rem !important;
        border: 1px solid rgba(22,163,74,0.5) !important;
        border-bottom: 2px solid rgba(10,90,40,0.45) !important;
        border-radius: 7px !important;
        transition: all 0.12s ease !important;
        box-shadow:
            0 2px 8px rgba(22,163,74,0.25),
            inset 0 1px 0 rgba(255,255,255,0.18) !important;
    }}
    .abtn-anchor-{uid} + div button:hover,
    .abtn-anchor-{uid} + div + div button:hover {{
        background: linear-gradient(180deg, #4ade80 0%, #22c55e 100%) !important;
        border-bottom-color: rgba(10,90,40,0.55) !important;
        transform: translateY(-1px) !important;
        box-shadow:
            0 4px 14px rgba(22,163,74,0.35),
            inset 0 1px 0 rgba(255,255,255,0.22) !important;
        color: #ffffff !important;
    }}
    .abtn-anchor-{uid} + div button:active,
    .abtn-anchor-{uid} + div + div button:active {{
        background: linear-gradient(180deg, #16a34a 0%, #15803d 100%) !important;
        transform: translateY(1px) !important;
        border-bottom-width: 1px !important;
        box-shadow: 0 1px 3px rgba(22,163,74,0.2) !important;
    }}
    </style>
    <div class="abtn-anchor-{uid}" style="display:none;"></div>
    """, unsafe_allow_html=True)

    return st.button(label, key=btn_key, use_container_width=use_container_width)


def card(content_fn, extra_class: str = ""):
    """
    Wraps a content function in a styled .qa-card div.

    Usage:
        def my_content():
            st.write("Hello inside card")
        card(my_content)
    """
    import streamlit as st
    st.markdown(f'<div class="qa-card {extra_class}">', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)