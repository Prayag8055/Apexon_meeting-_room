"""Room Booking UI — Streamlit entry point."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import streamlit as st
from theme import inject_css
from api_client import health_check
from pages.dashboard import render_dashboard
from pages.rooms import render_rooms
from pages.bookings import render_bookings
from pages.users import render_users

NAV_ITEMS = [
    ("📊", "Dashboard",  "dashboard",  "Overview & stats"),
    ("🏢", "Rooms",      "rooms",      "Manage spaces"),
    ("📅", "Bookings",   "bookings",   "Schedule & reserve"),
    ("👥", "Users",      "users",      "Team members"),
]

_CLEAR_KEYS = [
    "show_room_form", "show_booking_form", "show_user_form",
    "edit_room", "deactivate_room", "cancel_booking_obj",
    "reschedule_booking", "selected_user",
]


def _nav_item(icon: str, label: str, key: str, subtitle: str, active: bool) -> bool:
    active_cls = "active" if active else ""
    dot = '<span class="rb-nav-dot"></span>' if active else ""
    st.markdown(
        f"""
        <div class="rb-nav-btn {active_cls}" id="nav-{key}">
            <span class="rb-nav-icon">{icon}</span>
            <span style="flex:1">
                <div style="line-height:1.2">{label}</div>
                <div style="font-size:0.65rem;opacity:0.6;font-weight:400">{subtitle}</div>
            </span>
            {dot}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if active else "secondary")


def main() -> None:
    st.set_page_config(
        page_title="Room Booking",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Logo
        st.markdown(
            """
            <div class="rb-sidebar-logo">
                <div style="display:flex;align-items:center;gap:0.6rem">
                    <div style="width:36px;height:36px;border-radius:0.6rem;
                                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                                display:flex;align-items:center;justify-content:center;
                                font-size:1.1rem">🏢</div>
                    <div>
                        <div class="rb-sidebar-logo-text">RoomBook</div>
                        <div class="rb-sidebar-logo-sub">Workspace Manager</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Nav
        st.markdown('<div class="rb-nav-section"><div class="rb-nav-label">Navigation</div></div>',
                    unsafe_allow_html=True)

        for icon, label, key, subtitle in NAV_ITEMS:
            is_active = st.session_state.page == key
            # Invisible button layered over the styled div
            col = st.container()
            with col:
                active_cls = "active" if is_active else ""
                dot = '<span class="rb-nav-dot"></span>' if is_active else ""
                st.markdown(
                    f"""
                    <div class="rb-nav-btn {active_cls}" style="margin:0 0.75rem 0.1rem">
                        <span class="rb-nav-icon">{icon}</span>
                        <span style="flex:1">
                            <div style="line-height:1.3">{label}</div>
                            <div style="font-size:0.62rem;opacity:0.55;font-weight:400">{subtitle}</div>
                        </span>
                        {dot}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Transparent overlay button
                st.markdown(
                    f'<style>div[data-testid="stButton"] button[kind="{"primary" if is_active else "secondary"}"]'
                    f'[id="nav_{key}"]{{opacity:0;position:absolute;top:0;left:0;width:100%;height:100%}}</style>',
                    unsafe_allow_html=True,
                )
                if st.button(" ", key=f"nav_{key}", use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    st.session_state.page = key
                    for k in _CLEAR_KEYS:
                        st.session_state.pop(k, None)
                    st.rerun()

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="padding:0 0.75rem"><div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a45,transparent)"></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Health
        health = health_check()
        ok = health.get("status") == "ok"
        dot_cls = "rb-health-dot-ok" if ok else "rb-health-dot-err"
        health_cls = "rb-health-ok" if ok else "rb-health-err"
        health_text = "API Connected" if ok else "API Unreachable"
        st.markdown(
            f"""
            <div style="padding:0 0.75rem">
                <div class="rb-health {health_cls}">
                    <div class="rb-health-dot {dot_cls}"></div>
                    <span>{health_text}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="padding:0 1.25rem;font-size:0.65rem;color:#2d3f6b">v1.0 · Room Booking System</div>',
            unsafe_allow_html=True,
        )

    # ── Page routing ──────────────────────────────────────────────────────────
    try:
        page = st.session_state.page
        if page == "dashboard":
            render_dashboard()
        elif page == "rooms":
            render_rooms()
        elif page == "bookings":
            render_bookings()
        elif page == "users":
            render_users()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running on http://localhost:8000")
    except requests.exceptions.Timeout:
        st.error("Request timed out. The API may be slow or unreachable.")


if __name__ == "__main__":
    main()
