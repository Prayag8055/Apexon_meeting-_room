"""Theme constants and CSS injection for Apexon Room Booking UI."""
from __future__ import annotations
import streamlit as st

COLORS = {
    "bg_primary":     "#080b14",
    "bg_surface":     "#0f1420",
    "bg_surface2":    "#161c2e",
    "bg_surface3":    "#1d2540",
    "accent":         "#6366f1",
    "accent2":        "#8b5cf6",
    "accent_hover":   "#4f46e5",
    "accent_muted":   "#1e1b4b",
    "text_primary":   "#f0f4ff",
    "text_secondary": "#8892b0",
    "text_muted":     "#4a5568",
    "success":        "#10b981",
    "warning":        "#f59e0b",
    "danger":         "#f43f5e",
    "info":           "#06b6d4",
    "border":         "#1e2a45",
    "border_bright":  "#2d3f6b",
}

RADIUS = "1rem"
TRANSITION = "all 0.25s cubic-bezier(0.4,0,0.2,1)"
SHADOW = "0 8px 32px rgba(0,0,0,0.6)"
SHADOW_GLOW = "0 0 40px rgba(99,102,241,0.15)"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Global background ── */
.stApp {
    background: linear-gradient(135deg, #080b14 0%, #0a0f1e 50%, #080b14 100%) !important;
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #080b14 100%) !important;
    border-right: 1px solid #1e2a45 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }
</style>
"""

_CSS2 = """
<style>
/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,0.2); }
    50%       { box-shadow: 0 0 40px rgba(99,102,241,0.4); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}
.rb-page { animation: fadeUp 0.4s cubic-bezier(0.4,0,0.2,1) forwards; }

/* ── Stat cards ── */
.rb-stat-card {
    background: linear-gradient(135deg, #0f1420 0%, #161c2e 100%);
    border: 1px solid #1e2a45;
    border-radius: 1.25rem;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    cursor: default;
}
.rb-stat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    opacity: 0; transition: opacity 0.3s ease;
}
.rb-stat-card:hover {
    border-color: #2d3f6b; transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(99,102,241,0.1);
}
.rb-stat-card:hover::before { opacity: 1; }
.rb-stat-glow {
    position: absolute; top: -20px; right: -20px;
    width: 80px; height: 80px; border-radius: 50%;
    opacity: 0.08; filter: blur(20px);
}
.rb-stat-icon-wrap {
    width: 48px; height: 48px; border-radius: 0.75rem;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; margin-bottom: 1rem;
}
.rb-stat-value {
    font-size: 2.25rem; font-weight: 800; line-height: 1;
    letter-spacing: -0.02em; margin-bottom: 0.35rem;
    background: linear-gradient(135deg, #f0f4ff, #a5b4fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.rb-stat-label {
    font-size: 0.8rem; color: #8892b0; text-transform: uppercase;
    letter-spacing: 0.08em; font-weight: 500;
}
.rb-stat-delta {
    font-size: 0.75rem; font-weight: 600; margin-top: 0.5rem;
    display: inline-flex; align-items: center; gap: 0.2rem;
}
</style>
"""

_CSS3 = """
<style>
/* ── Room card ── */
.rb-room-card {
    background: linear-gradient(135deg, #0f1420 0%, #161c2e 100%);
    border: 1px solid #1e2a45; border-radius: 1.25rem;
    padding: 1.5rem; transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden; height: 100%;
}
.rb-room-card:hover {
    border-color: #6366f1; transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(99,102,241,0.12);
}
.rb-room-name { font-size: 1.05rem; font-weight: 700; color: #f0f4ff; margin-bottom: 0.3rem; letter-spacing: -0.01em; }
.rb-room-meta { font-size: 0.8rem; color: #8892b0; display: flex; gap: 0.75rem; margin-bottom: 0.75rem; align-items: center; }
.rb-room-meta span { display: flex; align-items: center; gap: 0.25rem; }

/* ── Booking card ── */
.rb-booking-card {
    background: linear-gradient(135deg, #0f1420 0%, #161c2e 100%);
    border: 1px solid #1e2a45; border-radius: 1.25rem;
    padding: 1.25rem 1.5rem; transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden; margin-bottom: 0.6rem;
    display: flex; align-items: center; gap: 1rem;
}
.rb-booking-card:hover { border-color: #2d3f6b; transform: translateX(4px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.rb-booking-accent { width: 4px; border-radius: 4px; align-self: stretch; flex-shrink: 0; }
.rb-booking-title { font-size: 0.95rem; font-weight: 600; color: #f0f4ff; margin-bottom: 0.25rem; }
.rb-booking-meta { font-size: 0.78rem; color: #8892b0; display: flex; flex-wrap: wrap; gap: 0.6rem; align-items: center; }
.rb-booking-meta-item { display: flex; align-items: center; gap: 0.25rem; }

/* ── User card ── */
.rb-user-card {
    background: linear-gradient(135deg, #0f1420 0%, #161c2e 100%);
    border: 1px solid #1e2a45; border-radius: 1.25rem;
    padding: 1.5rem; transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    text-align: center; position: relative; overflow: hidden;
}
.rb-user-card:hover { border-color: #2d3f6b; transform: translateY(-4px); box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
.rb-avatar {
    width: 56px; height: 56px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; font-weight: 700; margin: 0 auto 0.75rem;
    background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white;
}
.rb-user-name { font-size: 0.95rem; font-weight: 700; color: #f0f4ff; margin-bottom: 0.2rem; }
.rb-user-email { font-size: 0.78rem; color: #8892b0; margin-bottom: 0.2rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rb-user-dept { font-size: 0.75rem; color: #6366f1; font-weight: 500; margin-bottom: 0.5rem; }
</style>
"""

_CSS4 = """
<style>
/* ── Badges ── */
.rb-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.25rem 0.7rem; border-radius: 9999px;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; white-space: nowrap;
}
.rb-badge-confirmed  { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
.rb-badge-cancelled  { background: rgba(244,63,94,0.12);  color: #f43f5e; border: 1px solid rgba(244,63,94,0.25); }
.rb-badge-active     { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }
.rb-badge-inactive   { background: rgba(100,116,139,0.12);color: #64748b; border: 1px solid rgba(100,116,139,0.25); }
.rb-badge-warning    { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }

/* ── Amenity pill ── */
.rb-pill {
    display: inline-flex; align-items: center; gap: 0.2rem;
    background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2);
    border-radius: 9999px; padding: 0.15rem 0.55rem;
    font-size: 0.68rem; color: #a5b4fc; font-weight: 500; margin: 0.1rem;
}

/* ── Availability grid ── */
.rb-avail-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.5rem; margin-top: 0.75rem;
}
.rb-slot { border-radius: 0.6rem; padding: 0.5rem 0.4rem; font-size: 0.72rem; font-weight: 600; text-align: center; transition: all 0.2s ease; cursor: default; }
.rb-slot-free { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.25); color: #10b981; }
.rb-slot-free:hover { background: rgba(16,185,129,0.15); }
.rb-slot-booked { background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.2); color: #f43f5e; }
.rb-slot-time { font-size: 0.7rem; font-weight: 700; }
.rb-slot-label { font-size: 0.62rem; opacity: 0.8; margin-top: 0.1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Section header ── */
.rb-section-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.25rem; padding-bottom: 0.75rem; border-bottom: 1px solid #1e2a45;
}
.rb-section-title { font-size: 1.1rem; font-weight: 700; color: #f0f4ff; display: flex; align-items: center; gap: 0.5rem; }

/* ── Page title ── */
.rb-page-title { font-size: 1.75rem; font-weight: 800; color: #f0f4ff; letter-spacing: -0.03em; line-height: 1.2; }
.rb-page-subtitle { font-size: 0.875rem; color: #8892b0; margin-top: 0.25rem; }

/* ── Empty state ── */
.rb-empty { text-align: center; padding: 3rem 1rem; color: #8892b0; }
.rb-empty-icon { font-size: 3rem; margin-bottom: 0.75rem; opacity: 0.5; }
.rb-empty-text { font-size: 0.9rem; }
</style>
"""

_CSS5 = """
<style>
/* ── Sidebar nav ── */
.rb-sidebar-logo { padding: 1.5rem 1.25rem 1rem; border-bottom: 1px solid #1e2a45; margin-bottom: 0.5rem; }
.rb-sidebar-logo-text {
    font-size: 1.1rem; font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.rb-sidebar-logo-sub { font-size: 0.7rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.1rem; }
.rb-nav-section { padding: 0 0.75rem; margin-bottom: 0.25rem; }
.rb-nav-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #4a5568; font-weight: 600; padding: 0.5rem 0.5rem 0.25rem; }
.rb-nav-btn {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 0.875rem; border-radius: 0.75rem;
    cursor: pointer; transition: all 0.2s ease;
    color: #8892b0; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.15rem;
}
.rb-nav-btn:hover { background: rgba(99,102,241,0.08); color: #a5b4fc; }
.rb-nav-btn.active {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
    color: #818cf8; border: 1px solid rgba(99,102,241,0.2);
}
.rb-nav-icon { font-size: 1rem; width: 20px; text-align: center; }
.rb-nav-dot { width: 6px; height: 6px; border-radius: 50%; background: #6366f1; margin-left: auto; }

/* ── Health indicator ── */
.rb-health { display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.875rem; border-radius: 0.75rem; font-size: 0.78rem; font-weight: 500; }
.rb-health-ok { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); color: #10b981; }
.rb-health-err { background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.2); color: #f43f5e; }
.rb-health-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.rb-health-dot-ok  { background: #10b981; animation: blink 2s infinite; }
.rb-health-dot-err { background: #f43f5e; }

/* ── Form panel ── */
.rb-form-panel {
    background: linear-gradient(135deg, #0f1420, #161c2e);
    border: 1px solid #1e2a45; border-radius: 1.25rem;
    padding: 1.5rem; margin-bottom: 1.25rem; position: relative;
}
.rb-form-panel::before {
    content: ''; position: absolute; top: 0; left: 1.5rem; right: 1.5rem; height: 1px;
    background: linear-gradient(90deg, transparent, #6366f1, transparent);
}
.rb-form-title { font-size: 1rem; font-weight: 700; color: #f0f4ff; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }

/* ── Confirm dialog ── */
.rb-confirm {
    background: rgba(244,63,94,0.06); border: 1px solid rgba(244,63,94,0.2);
    border-radius: 1rem; padding: 1rem 1.25rem; margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.75rem;
}
.rb-confirm-text { font-size: 0.875rem; color: #fda4af; flex: 1; }
</style>
"""

_CSS6 = """
<style>
/* ── Streamlit widget overrides ── */
.stTextInput > label, .stNumberInput > label,
.stSelectbox > label, .stMultiSelect > label,
.stTextArea > label, .stDateInput > label,
.stTimeInput > label {
    font-size: 0.78rem !important; font-weight: 600 !important;
    color: #8892b0 !important; text-transform: uppercase !important;
    letter-spacing: 0.06em !important; margin-bottom: 0.3rem !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0a0f1e !important; border: 1px solid #1e2a45 !important;
    border-radius: 0.75rem !important; color: #f0f4ff !important;
    font-size: 0.9rem !important; padding: 0.6rem 0.875rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #0a0f1e !important; border: 1px solid #1e2a45 !important;
    border-radius: 0.75rem !important; color: #f0f4ff !important;
}
.stDateInput > div > div > input, .stTimeInput > div > div > input {
    background: #0a0f1e !important; border: 1px solid #1e2a45 !important;
    border-radius: 0.75rem !important; color: #f0f4ff !important;
}
div[data-testid="stExpander"] {
    background: #0f1420 !important; border: 1px solid #1e2a45 !important; border-radius: 1rem !important;
}
div[data-testid="stExpander"] summary { color: #8892b0 !important; font-size: 0.85rem !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important; border: none !important; border-radius: 0.75rem !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button[kind="secondary"] {
    background: transparent !important; border: 1px solid #1e2a45 !important;
    color: #8892b0 !important; box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6366f1 !important; color: #a5b4fc !important;
    background: rgba(99,102,241,0.06) !important; box-shadow: none !important;
    transform: translateY(-1px) !important;
}
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important; border: none !important; border-radius: 0.75rem !important;
    font-weight: 700 !important; font-size: 0.9rem !important;
    padding: 0.65rem 1.5rem !important; width: 100% !important;
}
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

/* ── Alerts ── */
.stSuccess > div { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.25) !important; border-radius: 0.75rem !important; color: #6ee7b7 !important; }
.stError > div { background: rgba(244,63,94,0.08) !important; border: 1px solid rgba(244,63,94,0.25) !important; border-radius: 0.75rem !important; color: #fda4af !important; }
.stWarning > div { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.25) !important; border-radius: 0.75rem !important; color: #fcd34d !important; }
.stInfo > div { background: rgba(6,182,212,0.08) !important; border: 1px solid rgba(6,182,212,0.25) !important; border-radius: 0.75rem !important; color: #67e8f9 !important; }

/* ── Spinner & Scrollbar ── */
.stSpinner > div { border-top-color: #6366f1 !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080b14; }
::-webkit-scrollbar-thumb { background: #1e2a45; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2d3f6b; }

/* ── Quick book card ── */
.rb-quick-book {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05));
    border: 1px solid rgba(99,102,241,0.2); border-radius: 1.25rem;
    padding: 1.5rem; margin-bottom: 1.25rem;
}

/* ── Upcoming timeline ── */
.rb-timeline-item {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 0.875rem 1rem; margin-bottom: 0.4rem;
    background: #0f1420; border: 1px solid #1e2a45; border-radius: 0.75rem;
    transition: all 0.2s ease;
}
.rb-timeline-item:hover { border-color: #2d3f6b; transform: translateX(4px); }
.rb-timeline-time {
    font-size: 0.75rem; font-weight: 700; color: #818cf8;
    min-width: 50px; text-align: center; padding-top: 0.1rem;
}
.rb-timeline-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    flex-shrink: 0; margin-top: 0.3rem;
}
.rb-timeline-content { flex: 1; min-width: 0; }
.rb-timeline-title { font-size: 0.85rem; font-weight: 600; color: #f0f4ff; }
.rb-timeline-meta { font-size: 0.72rem; color: #4a5568; margin-top: 0.15rem; }

/* ── Tabs override ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid #1e2a45; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #8892b0 !important;
    border-radius: 0.5rem 0.5rem 0 0 !important; font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.1) !important; color: #818cf8 !important;
    border-bottom: 2px solid #6366f1 !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_CSS2, unsafe_allow_html=True)
    st.markdown(_CSS3, unsafe_allow_html=True)
    st.markdown(_CSS4, unsafe_allow_html=True)
    st.markdown(_CSS5, unsafe_allow_html=True)
    st.markdown(_CSS6, unsafe_allow_html=True)


def badge_html(label: str, variant: str) -> str:
    safe = variant.lower().strip()
    dots = {"confirmed": "●", "active": "●", "cancelled": "●", "inactive": "●"}
    dot = dots.get(safe, "")
    return f'<span class="rb-badge rb-badge-{safe}">{dot} {label}</span>'


def card_html(content: str, extra_class: str = "") -> str:
    cls = f"rb-card {extra_class}".strip()
    return f'<div class="{cls}">{content}</div>'


def pill_html(label: str) -> str:
    return f'<span class="rb-pill">{label}</span>'
