"""Rooms page — list, create, edit, deactivate, availability."""
from __future__ import annotations
import datetime
import streamlit as st
from api_client import get_rooms, create_room, update_room, deactivate_room, get_room_availability, APIError
from components.cards import room_card, availability_grid
from components.forms import room_form, confirm_dialog, AMENITY_OPTIONS


def render_rooms() -> None:
    st.markdown('<div class="rb-page">', unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    h_col, btn_col = st.columns([3, 1])
    with h_col:
        st.markdown(
            '<div class="rb-page-title">🏢 Meeting Rooms</div>'
            '<div class="rb-page-subtitle">Manage your workspace rooms, amenities, and availability</div>',
            unsafe_allow_html=True,
        )
    with btn_col:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        if st.button("＋ New Room", key="new_room_btn", use_container_width=True):
            st.session_state["show_room_form"] = not st.session_state.get("show_room_form", False)
            st.session_state.pop("edit_room", None)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Create form ───────────────────────────────────────────────────────────
    if st.session_state.get("show_room_form"):
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = room_form()
        if payload:
            with st.spinner("Creating room..."):
                try:
                    create_room(payload)
                    st.success("✅ Room created successfully.")
                    st.session_state["show_room_form"] = False
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Close", key="close_create_room", type="secondary"):
                st.session_state["show_room_form"] = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Edit form ─────────────────────────────────────────────────────────────
    if st.session_state.get("edit_room"):
        room = st.session_state["edit_room"]
        st.markdown('<div class="rb-form-panel">', unsafe_allow_html=True)
        payload = room_form(existing=room)
        if payload:
            with st.spinner("Updating room..."):
                try:
                    update_room(room["room_id"], payload)
                    st.success("✅ Room updated.")
                    st.session_state["edit_room"] = None
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")
        c1, _ = st.columns([1, 3])
        with c1:
            if st.button("✖ Cancel Edit", key="cancel_edit_room", type="secondary"):
                st.session_state["edit_room"] = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Deactivate confirm ────────────────────────────────────────────────────
    if st.session_state.get("deactivate_room"):
        room = st.session_state["deactivate_room"]
        if confirm_dialog(
            f"Deactivate '{room.get('name')}'? This will prevent new bookings.",
            key=f"deact_{room['room_id']}",
        ):
            with st.spinner("Deactivating..."):
                try:
                    deactivate_room(room["room_id"])
                    st.success("Room deactivated.")
                    st.session_state["deactivate_room"] = None
                    st.rerun()
                except APIError as e:
                    st.error(f"❌ {e}")

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filter Rooms", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        min_cap = fc1.number_input("Min Capacity", min_value=0, value=0, help="Minimum number of seats")
        amenity_f = fc2.multiselect("Required Amenities", options=AMENITY_OPTIONS)
        status_filter = fc3.selectbox("Status", options=["All", "Active", "Inactive"], key="room_status_filter")

    with st.spinner(""):
        rooms = get_rooms(
            capacity=int(min_cap) if min_cap > 0 else None,
            amenities=amenity_f if amenity_f else None,
        )

    # Apply status filter client-side
    if status_filter != "All":
        rooms = [r for r in rooms if r.get("status") == status_filter.lower()]

    if not rooms:
        st.markdown(
            '<div class="rb-empty"><div class="rb-empty-icon">🏗️</div>'
            '<div class="rb-empty-text">No rooms found. Try adjusting your filters or create a new room.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Summary bar ───────────────────────────────────────────────────────────
    active_count = sum(1 for r in rooms if r.get("status") == "active")
    total_capacity = sum(r.get("capacity", 0) for r in rooms)
    st.markdown(
        f"""
        <div style="display:flex;gap:1.5rem;margin-bottom:1.25rem;
                    padding:0.75rem 1rem;background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#f0f4ff;font-weight:700">{len(rooms)}</span> rooms
            </span>
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#10b981;font-weight:700">{active_count}</span> active
            </span>
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#f43f5e;font-weight:700">{len(rooms)-active_count}</span> inactive
            </span>
            <span style="font-size:0.8rem;color:#8892b0">
                <span style="color:#818cf8;font-weight:700">{total_capacity}</span> total seats
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Room grid ─────────────────────────────────────────────────────────────
    for i in range(0, len(rooms), 3):
        cols = st.columns(3, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(rooms):
                with col:
                    room_card(
                        rooms[i + j],
                        on_edit=lambda r: st.session_state.update({"edit_room": r, "show_room_form": False}),
                        on_deactivate=lambda r: st.session_state.update({"deactivate_room": r}),
                    )

    # ── Availability viewer ───────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,#1e2a45,transparent);margin-bottom:1.5rem"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="rb-section-header">'
        '<div class="rb-section-title">📅 Room Availability</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    ac1, ac2 = st.columns(2)
    active_rooms = [r for r in rooms if r.get("status") == "active"]
    room_names = [r["name"] for r in active_rooms]
    sel_name = ac1.selectbox("Select Room", options=room_names, key="avail_room_select")
    sel_date = ac2.date_input("Date", value=datetime.date.today(), key="avail_date")

    if sel_name and sel_date:
        room_id = next((r["room_id"] for r in active_rooms if r["name"] == sel_name), None)
        if room_id:
            with st.spinner("Fetching availability..."):
                try:
                    avail = get_room_availability(room_id, str(sel_date))
                    availability_grid(avail)
                except APIError as e:
                    st.error(f"❌ {e}")

    st.markdown("</div>", unsafe_allow_html=True)
