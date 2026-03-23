"""Users page — list, register, view bookings."""
from __future__ import annotations
import streamlit as st
from api_client import get_users, create_user, get_user_bookings, APIError
from components.cards import user_card, booking_card
from components.forms import user_form


def render_users() -> None:
    st.markdown('<div class="rb-page">', unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            '<div class="rb-page-title">👥 Users</div>'
            '<div class="rb-page-subtitle">Manage team members and their bookings</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("＋ Register User", key="new_user_btn", use_container_width=True):
            st.session_state["show_user_form"] = not st.session_state.get("show_user_form", False)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Register form ─────────────────────────────────────────────────────────
    if st.session_state.get("show_user_form"):
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = user_form()
        if payload:
            with st.spinner("Registering..."):
                try:
                    create_user(payload)
                    st.success("✅ User registered successfully.")
                    st.session_state["show_user_form"] = False
                    st.rerun()
                except APIError as e:
                    if e.status_code == 409:
                        st.error(f"⚠️ Email already registered: {e.detail or e.message}")
                    else:
                        st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Close", key="close_user_form", type="secondary"):
                st.session_state["show_user_form"] = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with st.spinner(""):
        users = get_users()

    if not users:
        st.markdown(
            '<div class="rb-empty"><div class="rb-empty-icon">👤</div>'
            '<div class="rb-empty-text">No users registered yet. Add your first team member!</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Summary bar ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="display:flex;gap:1.5rem;margin-bottom:1.25rem;
                    padding:0.75rem 1rem;background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#f0f4ff;font-weight:700">{len(users)}</span> team members
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── User grid (3 columns) ─────────────────────────────────────────────────
    for i in range(0, len(users), 3):
        cols = st.columns(3, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(users):
                with col:
                    user_card(
                        users[i + j],
                        on_view=lambda u: st.session_state.update({"selected_user": u}),
                    )

    # ── User bookings drawer ──────────────────────────────────────────────────
    if st.session_state.get("selected_user"):
        user = st.session_state["selected_user"]
        st.markdown(
            '<div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a45,transparent);margin:1.5rem 0"></div>',
            unsafe_allow_html=True,
        )

        name = user.get("name", "")
        initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "?"

        hc1, hc2 = st.columns([3, 1])
        with hc1:
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.875rem;margin-bottom:1rem">
                    <div style="width:40px;height:40px;border-radius:50%;
                                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                                display:flex;align-items:center;justify-content:center;
                                font-size:1rem;font-weight:700;color:white;flex-shrink:0">{initials}</div>
                    <div>
                        <div style="font-size:1rem;font-weight:700;color:#f0f4ff">Bookings for {name}</div>
                        <div style="font-size:0.75rem;color:#8892b0">{user.get('email','')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with hc2:
            if st.button("✖ Close", key="close_user_bookings", type="secondary", use_container_width=True):
                st.session_state["selected_user"] = None
                st.rerun()

        with st.spinner(""):
            try:
                user_bookings = get_user_bookings(user["user_id"])
            except APIError as e:
                st.error(f"❌ {e}")
                user_bookings = []

        if user_bookings:
            confirmed = sum(1 for b in user_bookings if b.get("status") == "confirmed")
            st.markdown(
                f"""
                <div style="display:flex;gap:1.5rem;margin-bottom:1rem;
                            padding:0.65rem 1rem;background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">
                    <span style="font-size:0.8rem;color:#8892b0">
                        <span style="color:#f0f4ff;font-weight:700">{len(user_bookings)}</span> total
                    </span>
                    <span style="font-size:0.8rem;color:#8892b0">
                        <span style="color:#10b981;font-weight:700">{confirmed}</span> confirmed
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for b in user_bookings:
                booking_card(b)
        else:
            st.markdown(
                '<div class="rb-empty"><div class="rb-empty-icon">📭</div>'
                '<div class="rb-empty-text">No bookings for this user yet.</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
