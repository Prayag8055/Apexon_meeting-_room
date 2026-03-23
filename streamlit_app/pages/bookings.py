"""Bookings page — list, create, cancel, reschedule."""
from __future__ import annotations
import datetime
import streamlit as st
from api_client import get_rooms, get_users, get_bookings, create_booking, update_booking, cancel_booking, APIError
from components.cards import booking_card
from components.forms import booking_form, confirm_dialog


def render_bookings() -> None:
    st.markdown('<div class="rb-page">', unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            '<div class="rb-page-title">📅 Bookings</div>'
            '<div class="rb-page-subtitle">Schedule and manage room reservations</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("＋ New Booking", key="new_booking_btn", use_container_width=True):
            st.session_state["show_booking_form"] = not st.session_state.get("show_booking_form", False)
            st.session_state.pop("reschedule_booking", None)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    with st.spinner(""):
        rooms = get_rooms()
        users = get_users()

    # ── Create form ───────────────────────────────────────────────────────────
    if st.session_state.get("show_booking_form"):
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = booking_form(rooms, users)
        if payload:
            with st.spinner("Creating booking..."):
                try:
                    create_booking(payload)
                    st.success("✅ Booking confirmed.")
                    st.session_state["show_booking_form"] = False
                    st.rerun()
                except APIError as e:
                    if e.status_code == 409:
                        st.error(f"⚠️ Time slot unavailable: {e.detail or e.message}")
                    else:
                        st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Close", key="close_booking_form", type="secondary"):
                st.session_state["show_booking_form"] = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Reschedule form ───────────────────────────────────────────────────────
    if st.session_state.get("reschedule_booking"):
        booking = st.session_state["reschedule_booking"]
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = booking_form(rooms, users, existing=booking)
        if payload:
            with st.spinner("Rescheduling..."):
                try:
                    update_booking(booking["booking_id"], payload)
                    st.success("✅ Booking rescheduled.")
                    st.session_state["reschedule_booking"] = None
                    st.rerun()
                except APIError as e:
                    if e.status_code == 409:
                        st.error(f"⚠️ Time slot unavailable: {e.detail or e.message}")
                    else:
                        st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Cancel", key="cancel_reschedule", type="secondary"):
                st.session_state["reschedule_booking"] = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Cancel confirm ────────────────────────────────────────────────────────
    if st.session_state.get("cancel_booking_obj"):
        b = st.session_state["cancel_booking_obj"]
        if confirm_dialog(
            f"Cancel booking '{b.get('title')}'? This action cannot be undone.",
            key=f"cancel_{b['booking_id']}",
        ):
            with st.spinner("Cancelling..."):
                try:
                    cancel_booking(b["booking_id"])
                    st.success("Booking cancelled.")
                    st.session_state["cancel_booking_obj"] = None
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filter Bookings", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        date_f = fc1.date_input("Date", value=None, key="booking_date_filter")
        room_names_all = ["All"] + [r["name"] for r in rooms]
        user_names_all = ["All"] + [u["name"] for u in users]
        room_f = fc2.selectbox("Room", options=room_names_all, key="booking_room_filter")
        user_f = fc3.selectbox("User", options=user_names_all, key="booking_user_filter")
        status_f = fc4.selectbox("Status", options=["All", "confirmed", "cancelled"], key="booking_status_filter")

    room_id_f = next((r["room_id"] for r in rooms if r["name"] == room_f), None) if room_f != "All" else None
    user_id_f = next((u["user_id"] for u in users if u["name"] == user_f), None) if user_f != "All" else None

    with st.spinner(""):
        bookings = get_bookings(
            user_id=user_id_f,
            room_id=room_id_f,
            date=str(date_f) if date_f else None,
            status=status_f if status_f != "All" else None,
        )

    # ── Summary bar ───────────────────────────────────────────────────────────
    confirmed_n = sum(1 for b in bookings if b.get("status") == "confirmed")
    cancelled_n = sum(1 for b in bookings if b.get("status") == "cancelled")
    st.markdown(
        f"""
        <div style="display:flex;gap:1.5rem;margin-bottom:1rem;
                    padding:0.75rem 1rem;background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#f0f4ff;font-weight:700">{len(bookings)}</span> results
            </span>
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#10b981;font-weight:700">{confirmed_n}</span> confirmed
            </span>
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#f43f5e;font-weight:700">{cancelled_n}</span> cancelled
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not bookings:
        st.markdown(
            '<div class="rb-empty"><div class="rb-empty-icon">📭</div>'
            '<div class="rb-empty-text">No bookings match your filters.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    room_map = {r["room_id"]: r["name"] for r in rooms}
    user_map = {u["user_id"]: u["name"] for u in users}

    for b in bookings:
        booking_card(
            b,
            room_name=room_map.get(b.get("room_id", ""), ""),
            user_name=user_map.get(b.get("user_id", ""), ""),
            on_cancel=lambda bk: st.session_state.update({"cancel_booking_obj": bk}),
            on_reschedule=lambda bk: st.session_state.update({"reschedule_booking": bk, "show_booking_form": False}),
        )

    st.markdown("</div>", unsafe_allow_html=True)
