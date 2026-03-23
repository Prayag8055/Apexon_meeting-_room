"""Bookings page — room cards → pick slot → confirm. Plus booking history."""
from __future__ import annotations
import datetime
import streamlit as st
from api_client import (
    get_rooms, get_users, get_bookings, create_booking,
    update_booking, cancel_booking, get_room_availability, APIError,
)
from components.cards import booking_card
from components.forms import booking_form, confirm_dialog

_AMENITY_ICONS = {
    "projector": "📽️", "whiteboard": "📋", "video conferencing": "📹",
    "tv screen": "📺", "phone": "📞", "standing desk": "🪑",
    "natural light": "☀️", "air conditioning": "❄️",
}


def _amenity_icon(name: str) -> str:
    return _AMENITY_ICONS.get(name.lower(), "✦")


def render_bookings() -> None:
    user = st.session_state.get("user", {})
    is_admin = user.get("role") == "admin"
    today = datetime.date.today()

    st.markdown('<div class="rb-page">', unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="rb-page-title">📅 Book a Room</div>'
        '<div class="rb-page-subtitle">Select a room, pick a time slot, and confirm your booking</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.spinner(""):
        rooms = get_rooms()
        users = get_users() if is_admin else [user]

    active_rooms = [r for r in rooms if r.get("status") == "active"]

    # ── Room Cards Grid ───────────────────────────────────────────────────
    if not active_rooms:
        st.info("No active rooms available.")
    else:
        for i in range(0, len(active_rooms), 3):
            cols = st.columns(3, gap="medium")
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(active_rooms):
                    room = active_rooms[idx]
                    rid = room["room_id"]
                    amenities = room.get("amenities") or []
                    pills = "".join(
                        f'<span class="rb-pill">{_amenity_icon(a)} {a}</span>'
                        for a in amenities[:4]
                    )
                    extra = (
                        f'<span class="rb-pill" style="color:#4a5568">+{len(amenities)-4} more</span>'
                        if len(amenities) > 4 else ""
                    )
                    cap = room.get("capacity", 0)
                    floor = room.get("floor", 1)
                    cap_pct = min(int(cap) / 50 * 100, 100) if cap else 0

                    is_selected = st.session_state.get("book_room_id") == rid

                    with col:
                        # Card HTML
                        border_color = "#6366f1" if is_selected else "#1e2a45"
                        shadow = "0 0 20px rgba(99,102,241,0.2)" if is_selected else "none"
                        st.markdown(
                            f"""
                            <div class="rb-room-card" style="border-color:{border_color};box-shadow:{shadow}">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem">
                                    <div style="flex:1;min-width:0">
                                        <div class="rb-room-name">{room.get('name','')}</div>
                                        <div class="rb-room-meta">
                                            <span>👥 {cap} seats</span>
                                            <span>🏢 Floor {floor}</span>
                                        </div>
                                    </div>
                                </div>
                                <div style="margin-bottom:0.75rem;flex-wrap:wrap;display:flex">{pills}{extra}</div>
                                <div style="margin-top:auto">
                                    <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#4a5568;margin-bottom:0.3rem">
                                        <span>Capacity</span><span style="color:#8892b0">{cap} people</span>
                                    </div>
                                    <div style="height:4px;background:#1e2a45;border-radius:2px;overflow:hidden">
                                        <div style="height:100%;width:{cap_pct}%;background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:2px"></div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        btn_label = "✅ Selected" if is_selected else "📅 Book"
                        btn_type = "primary" if is_selected else "secondary"
                        if st.button(btn_label, key=f"book_room_{rid}", use_container_width=True, type=btn_type):
                            if is_selected:
                                # Deselect
                                st.session_state.pop("book_room_id", None)
                                st.session_state.pop("book_selected_slot", None)
                            else:
                                st.session_state["book_room_id"] = rid
                                st.session_state.pop("book_selected_slot", None)
                            st.rerun()

    # ── Slot Picker (shown when a room is selected) ───────────────────────
    selected_rid = st.session_state.get("book_room_id")
    if selected_rid:
        selected_room = next((r for r in active_rooms if r["room_id"] == selected_rid), None)
        if selected_room:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="height:1px;background:linear-gradient(90deg,transparent,#6366f1,transparent);margin-bottom:1.25rem"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="rb-section-header">'
                f'<div class="rb-section-title">⚡ Pick a Time Slot — {selected_room["name"]}</div></div>',
                unsafe_allow_html=True,
            )

            dc1, dc2 = st.columns([1, 3])
            book_date = dc1.date_input("Date", value=today, key="book_date_pick")

            try:
                avail = get_room_availability(selected_rid, str(book_date))
                free_slots = [s for s in avail.get("slots", []) if s.get("is_available")]

                # Filter past slots for today
                if str(book_date) == str(today):
                    now_str = datetime.datetime.now().strftime("%H:%M")
                    free_slots = [s for s in free_slots if s["start_time"][11:16] >= now_str]

                if free_slots:
                    st.markdown(
                        f'<div style="font-size:0.8rem;color:#8892b0;margin:0.25rem 0 0.75rem">'
                        f'🟢 {len(free_slots)} available slots — click one to book</div>',
                        unsafe_allow_html=True,
                    )
                    cols_per_row = 8
                    for si in range(0, len(free_slots), cols_per_row):
                        slot_cols = st.columns(cols_per_row)
                        for sj, scol in enumerate(slot_cols):
                            sidx = si + sj
                            if sidx < len(free_slots):
                                slot = free_slots[sidx]
                                s_t = slot["start_time"][11:16]
                                is_picked = (
                                    st.session_state.get("book_selected_slot")
                                    and st.session_state["book_selected_slot"]["start_time"] == slot["start_time"]
                                )
                                with scol:
                                    btype = "primary" if is_picked else "secondary"
                                    if st.button(s_t, key=f"bslot_{sidx}", use_container_width=True, type=btype):
                                        st.session_state["book_selected_slot"] = slot
                                        st.rerun()
                else:
                    st.info("No available slots for this date. Try another date.")
            except APIError as e:
                st.error(f"❌ {e}")

            # ── Confirm form (shown when slot is picked) ──────────────────
            if st.session_state.get("book_selected_slot"):
                slot = st.session_state["book_selected_slot"]
                s_t = slot["start_time"][11:16]
                e_t = slot["end_time"][11:16]
                st.markdown(
                    f'<div style="margin-top:0.75rem;padding:0.85rem 1.25rem;'
                    f'background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);'
                    f'border-radius:0.75rem">'
                    f'<div style="font-size:0.9rem;font-weight:600;color:#10b981">'
                    f'📅 {selected_room["name"]} · {book_date} · {s_t} – {e_t}</div></div>',
                    unsafe_allow_html=True,
                )
                with st.form("book_confirm_form", clear_on_submit=True):
                    bc1, bc2 = st.columns([3, 1])
                    title_val = bc1.text_input(
                        "Meeting Title", placeholder="e.g. Sprint Planning", key="book_title_input",
                    )
                    fc1, fc2 = st.columns(2)
                    confirmed = fc1.form_submit_button("✅ Confirm Booking", use_container_width=True)
                    if fc2.form_submit_button("✖ Cancel", use_container_width=True):
                        st.session_state.pop("book_selected_slot", None)
                        st.rerun()
                    if confirmed:
                        title_final = title_val.strip() if title_val else "Meeting"
                        try:
                            create_booking({
                                "title": title_final,
                                "room_id": selected_rid,
                                "user_id": user.get("user_id"),
                                "start_time": slot["start_time"],
                                "end_time": slot["end_time"],
                                "notes": "",
                            })
                            st.session_state.pop("book_selected_slot", None)
                            st.session_state.pop("book_room_id", None)
                            st.success(f"✅ Booked! {selected_room['name']} at {s_t}")
                            st.rerun()
                        except APIError as e:
                            if e.status_code == 409:
                                st.error("⚠️ Slot just got taken. Pick another.")
                            else:
                                st.error(f"❌ {e}")

    # ══════════════════════════════════════════════════════════════════════
    # ── My Bookings / All Bookings section ────────────────────────────────
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a45,transparent);margin-bottom:1.25rem"></div>',
        unsafe_allow_html=True,
    )

    section_title = "📋 All Bookings" if is_admin else "📋 My Bookings"
    section_sub = "Manage all reservations" if is_admin else "Your scheduled meetings"
    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            f'<div class="rb-section-header" style="border-bottom:none;margin-bottom:0.5rem">'
            f'<div class="rb-section-title">{section_title}</div></div>',
            unsafe_allow_html=True,
        )

    # ── Reschedule form ───────────────────────────────────────────────────
    if st.session_state.get("reschedule_booking"):
        bk = st.session_state["reschedule_booking"]
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = booking_form(rooms, users, existing=bk, current_user=user)
        if payload:
            with st.spinner("Rescheduling..."):
                try:
                    update_booking(bk["booking_id"], payload)
                    st.success("✅ Booking rescheduled.")
                    st.session_state["reschedule_booking"] = None
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Cancel", key="cancel_reschedule", type="secondary"):
                st.session_state["reschedule_booking"] = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Cancel confirm ────────────────────────────────────────────────────
    if st.session_state.get("cancel_booking_obj"):
        b = st.session_state["cancel_booking_obj"]
        if confirm_dialog(f"Cancel booking '{b.get('title')}'?", key=f"cancel_{b['booking_id']}"):
            with st.spinner("Cancelling..."):
                try:
                    cancel_booking(b["booking_id"])
                    st.success("Booking cancelled.")
                    st.session_state["cancel_booking_obj"] = None
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")

    # ── Filters ───────────────────────────────────────────────────────────
    with st.expander("🔍 Filter Bookings", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        date_f = fc1.date_input("Date", value=None, key="booking_date_filter")
        room_names_all = ["All"] + [r["name"] for r in rooms]
        room_f = fc2.selectbox("Room", options=room_names_all, key="booking_room_filter")
        status_f = fc3.selectbox("Status", options=["All", "confirmed", "cancelled"], key="booking_status_filter")

    room_id_f = next((r["room_id"] for r in rooms if r["name"] == room_f), None) if room_f != "All" else None
    user_id_f = None if is_admin else user.get("user_id")

    with st.spinner(""):
        bookings = get_bookings(
            user_id=user_id_f, room_id=room_id_f,
            date=str(date_f) if date_f else None,
            status=status_f if status_f != "All" else None,
        )

    confirmed_n = sum(1 for b in bookings if b.get("status") == "confirmed")
    cancelled_n = sum(1 for b in bookings if b.get("status") == "cancelled")
    st.markdown(
        f'<div style="display:flex;gap:1.5rem;margin-bottom:1rem;padding:0.75rem 1rem;'
        f'background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">'
        f'<span style="font-size:0.8rem;color:#8892b0"><span style="color:#f0f4ff;font-weight:700">{len(bookings)}</span> results</span>'
        f'<span style="font-size:0.8rem;color:#8892b0"><span style="color:#10b981;font-weight:700">{confirmed_n}</span> confirmed</span>'
        f'<span style="font-size:0.8rem;color:#8892b0"><span style="color:#f43f5e;font-weight:700">{cancelled_n}</span> cancelled</span></div>',
        unsafe_allow_html=True,
    )

    if not bookings:
        st.markdown(
            '<div class="rb-empty"><div class="rb-empty-icon">📭</div>'
            '<div class="rb-empty-text">No bookings found.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    room_map = {r["room_id"]: r["name"] for r in rooms}
    all_users = get_users() if is_admin else [user]
    user_map = {u["user_id"]: u["name"] for u in all_users}

    for b in bookings:
        can_modify = is_admin or b.get("user_id") == user.get("user_id")
        booking_card(
            b, room_name=room_map.get(b.get("room_id", ""), ""),
            user_name=user_map.get(b.get("user_id", ""), ""),
            on_cancel=(lambda bk: st.session_state.update({"cancel_booking_obj": bk})) if can_modify else None,
            on_reschedule=(lambda bk: st.session_state.update({"reschedule_booking": bk})) if can_modify else None,
        )

    st.markdown("</div>", unsafe_allow_html=True)
