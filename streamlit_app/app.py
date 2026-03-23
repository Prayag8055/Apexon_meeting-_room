"""Apexon Room Booking — Streamlit entry point with auth."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import streamlit as st
from theme import inject_css
from api_client import health_check
from pages.auth import render_login
from pages.dashboard import render_dashboard
from pages.rooms import render_rooms
from pages.bookings import render_bookings
from pages.users import render_users

# Nav items: (icon, label, key, subtitle, admin_only)
NAV_ITEMS = [
    ("📊", "Dashboard",  "dashboard",  "Overview & stats",    False),
    ("🏢", "Rooms",      "rooms",      "Manage spaces",       True),
    ("📅", "Bookings",   "bookings",   "Schedule & reserve",  False),
    ("👥", "Users",      "users",      "Team members",        True),
]

_CLEAR_KEYS = [
    "show_room_form", "show_booking_form", "show_user_form",
    "edit_room", "deactivate_room", "cancel_booking_obj",
    "reschedule_booking", "selected_user",
    "book_room_id", "book_selected_slot",
]


def _get_user():
    return st.session_state.get("user")


def _is_admin():
    user = _get_user()
    return user and user.get("role") == "admin"


def main() -> None:
    st.set_page_config(
        page_title="Apexon Room Booking",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    # ── Auth gate ─────────────────────────────────────────────────────────
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is None:
        # Center the login form
        _, center, _ = st.columns([1, 2, 1])
        with center:
            render_login()
        return

    user = st.session_state["user"]
    is_admin = user.get("role") == "admin"

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    # If employee navigated to admin-only page, redirect
    if not is_admin and st.session_state.page in ("rooms", "users"):
        st.session_state.page = "dashboard"


    # ── Sidebar ───────────────────────────────────────────────────────────
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
                        <div class="rb-sidebar-logo-text">Apexon RoomBook</div>
                        <div class="rb-sidebar-logo-sub">Meeting Room Manager</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # User info
        name = user.get("name", "")
        initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "?"
        role_badge = "🛡️ Admin" if is_admin else "👤 Employee"
        st.markdown(
            f"""
            <div style="padding:0.75rem 1rem;margin:0 0.5rem 0.5rem;
                        background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
                        border-radius:0.75rem">
                <div style="display:flex;align-items:center;gap:0.6rem">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.8rem;font-weight:700;color:white">{initials}</div>
                    <div style="flex:1;min-width:0">
                        <div style="font-size:0.82rem;font-weight:600;color:#f0f4ff;
                                    overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{name}</div>
                        <div style="font-size:0.65rem;color:#8892b0">{role_badge}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Nav
        st.markdown('<div class="rb-nav-section"><div class="rb-nav-label">Navigation</div></div>', unsafe_allow_html=True)

        for icon, label, key, subtitle, admin_only in NAV_ITEMS:
            if admin_only and not is_admin:
                continue
            is_active = st.session_state.page == key
            active_cls = "active" if is_active else ""
            dot = '<span class="rb-nav-dot"></span>' if is_active else ""
            st.markdown(
                f"""<div class="rb-nav-btn {active_cls}" style="margin:0 0.75rem 0.1rem">
                    <span class="rb-nav-icon">{icon}</span>
                    <span style="flex:1"><div style="line-height:1.3">{label}</div>
                    <div style="font-size:0.62rem;opacity:0.55;font-weight:400">{subtitle}</div></span>{dot}
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(" ", key=f"nav_{key}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.page = key
                for k in _CLEAR_KEYS:
                    st.session_state.pop(k, None)
                st.rerun()


        # Divider
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown('<div style="padding:0 0.75rem"><div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a45,transparent)"></div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Health
        health = health_check()
        ok = health.get("status") == "ok"
        dot_cls = "rb-health-dot-ok" if ok else "rb-health-dot-err"
        health_cls = "rb-health-ok" if ok else "rb-health-err"
        health_text = "API Connected" if ok else "API Unreachable"
        st.markdown(
            f'<div style="padding:0 0.75rem"><div class="rb-health {health_cls}">'
            f'<div class="rb-health-dot {dot_cls}"></div><span>{health_text}</span></div></div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Logout button
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True, type="secondary"):
            st.session_state["user"] = None
            st.session_state.page = "dashboard"
            for k in _CLEAR_KEYS:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div style="padding:0 1.25rem;font-size:0.65rem;color:#2d3f6b">v3.0 · Apexon Room Booking</div>', unsafe_allow_html=True)

    # ── Page routing ──────────────────────────────────────────────────────
    try:
        page = st.session_state.page
        if page == "dashboard":
            render_dashboard()
        elif page == "rooms" and is_admin:
            render_rooms()
        elif page == "bookings":
            render_bookings()
        elif page == "users" and is_admin:
            render_users()
        else:
            render_dashboard()
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to API. Make sure the backend is running on http://localhost:8000")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out.")


if __name__ == "__main__":
    main()
