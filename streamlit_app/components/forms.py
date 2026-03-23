"""Form components for Room Booking UI."""
from __future__ import annotations
import datetime
from typing import Optional
import streamlit as st

AMENITY_OPTIONS = [
    "Projector", "Whiteboard", "Video Conferencing", "TV Screen",
    "Phone", "Standing Desk", "Natural Light", "Air Conditioning",
]


def _form_header(title: str, icon: str) -> None:
    st.markdown(
        f'<div class="rb-form-title">{icon} {title}</div>',
        unsafe_allow_html=True,
    )


def room_form(existing: Optional[dict] = None) -> Optional[dict]:
    is_edit = existing is not None
    fkey = f"room_form_{existing.get('room_id','new') if existing else 'new'}"
    _form_header("Edit Room" if is_edit else "New Room", "✏️" if is_edit else "🏢")

    with st.form(key=fkey, clear_on_submit=not is_edit):
        name = st.text_input(
            "Room Name",
            value=existing.get("name", "") if existing else "",
            placeholder="e.g. Horizon Suite",
        )
        capacity = st.number_input("Capacity (seats)", min_value=1, max_value=500,
                                   value=int(existing.get("capacity", 10)) if existing else 10)
        amenities = st.multiselect(
            "Amenities",
            options=AMENITY_OPTIONS,
            default=existing.get("amenities", []) if existing else [],
        )
        if is_edit:
            status = st.selectbox(
                "Status",
                options=["active", "inactive"],
                index=0 if existing.get("status") == "active" else 1,
            )
        else:
            status = "active"

        submitted = st.form_submit_button(
            "💾 Save Room" if is_edit else "✅ Create Room",
            use_container_width=True,
        )
        if submitted:
            if not name.strip():
                st.error("Room name is required.")
                return None
            return {
                "name": name.strip(),
                "capacity": int(capacity),
                "amenities": amenities,
                "status": status,
            }
    return None


def booking_form(
    rooms: list[dict],
    users: list[dict],
    existing: Optional[dict] = None,
) -> Optional[dict]:
    is_edit = existing is not None
    fkey = f"booking_form_{existing.get('booking_id','new') if existing else 'new'}"
    _form_header("Reschedule Booking" if is_edit else "New Booking", "🔄" if is_edit else "📅")

    with st.form(key=fkey, clear_on_submit=not is_edit):
        title = st.text_input(
            "Meeting Title",
            value=existing.get("title", "") if existing else "",
            placeholder="e.g. Q3 Planning Session",
        )

        c1, c2 = st.columns(2)
        room_options = {r["name"]: r["room_id"] for r in rooms}
        room_names = list(room_options.keys())
        default_room_idx = 0
        if existing:
            for i, r in enumerate(rooms):
                if r["room_id"] == existing.get("room_id"):
                    default_room_idx = i
                    break
        selected_room = c1.selectbox("Room", options=room_names, index=default_room_idx)

        user_options = {u["name"]: u["user_id"] for u in users}
        user_names = list(user_options.keys())
        default_user_idx = 0
        if existing:
            for i, u in enumerate(users):
                if u["user_id"] == existing.get("user_id"):
                    default_user_idx = i
                    break
        selected_user = c2.selectbox("Organizer", options=user_names, index=default_user_idx)

        default_date = datetime.date.today()
        if existing and existing.get("start_time"):
            try:
                default_date = datetime.date.fromisoformat(existing["start_time"][:10])
            except Exception:
                pass

        default_start = datetime.time(9, 0)
        default_end = datetime.time(10, 0)
        if existing:
            try:
                default_start = datetime.time.fromisoformat(existing["start_time"][11:16])
                default_end = datetime.time.fromisoformat(existing["end_time"][11:16])
            except Exception:
                pass

        dc, sc, ec = st.columns(3)
        date = dc.date_input("Date", value=default_date)
        start_time = sc.time_input("Start Time", value=default_start)
        end_time = ec.time_input("End Time", value=default_end)

        notes = st.text_area(
            "Notes (optional)",
            value=existing.get("notes", "") if existing else "",
            height=80,
            placeholder="Any special requirements or agenda...",
        )

        submitted = st.form_submit_button(
            "💾 Save Changes" if is_edit else "✅ Confirm Booking",
            use_container_width=True,
        )
        if submitted:
            if not title.strip():
                st.error("Meeting title is required.")
                return None
            if not room_names or not user_names:
                st.error("No rooms or users available.")
                return None
            if start_time >= end_time:
                st.error("End time must be after start time.")
                return None
            return {
                "title": title.strip(),
                "room_id": room_options[selected_room],
                "user_id": user_options[selected_user],
                "start_time": datetime.datetime.combine(date, start_time).isoformat(),
                "end_time": datetime.datetime.combine(date, end_time).isoformat(),
                "notes": notes.strip(),
            }
    return None


def user_form(existing: Optional[dict] = None) -> Optional[dict]:
    is_edit = existing is not None
    fkey = f"user_form_{existing.get('user_id','new') if existing else 'new'}"
    _form_header("Edit User" if is_edit else "Register User", "✏️" if is_edit else "👤")

    with st.form(key=fkey, clear_on_submit=not is_edit):
        name = st.text_input(
            "Full Name",
            value=existing.get("name", "") if existing else "",
            placeholder="e.g. Alex Johnson",
        )
        email = st.text_input(
            "Email Address",
            value=existing.get("email", "") if existing else "",
            placeholder="e.g. alex@company.com",
        )
        department = st.text_input(
            "Department",
            value=existing.get("department", "") if existing else "",
            placeholder="e.g. Engineering",
        )
        submitted = st.form_submit_button(
            "💾 Save User" if is_edit else "✅ Register",
            use_container_width=True,
        )
        if submitted:
            if not name.strip() or not email.strip():
                st.error("Name and email are required.")
                return None
            return {
                "name": name.strip(),
                "email": email.strip(),
                "department": department.strip(),
            }
    return None


def confirm_dialog(message: str, key: str) -> bool:
    state_key = f"confirm_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = False

    st.markdown(
        f'<div class="rb-confirm"><span style="font-size:1.1rem">⚠️</span>'
        f'<span class="rb-confirm-text">{message}</span></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes, confirm", key=f"{key}_yes", use_container_width=True):
        st.session_state[state_key] = True
    if c2.button("✖ Cancel", key=f"{key}_no", use_container_width=True, type="secondary"):
        st.session_state[state_key] = False

    result = st.session_state[state_key]
    if result:
        st.session_state[state_key] = False
    return result
