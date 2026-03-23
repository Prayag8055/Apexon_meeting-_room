"""Form components for Apexon Room Booking UI."""
from __future__ import annotations
import datetime
from typing import Optional
import streamlit as st

AMENITY_OPTIONS = [
    "Projector", "Whiteboard", "Video Conferencing", "TV Screen",
    "Phone", "Standing Desk", "Natural Light", "Air Conditioning",
]

DEPARTMENT_OPTIONS = [
    "Engineering", "Design", "Product", "Marketing", "Sales",
    "HR", "Finance", "Operations", "Legal", "Support", "Other",
]


def _form_header(title: str, icon: str) -> None:
    st.markdown(f'<div class="rb-form-title">{icon} {title}</div>', unsafe_allow_html=True)


def room_form(existing: Optional[dict] = None) -> Optional[dict]:
    is_edit = existing is not None
    fkey = f"room_form_{existing.get('room_id','new') if existing else 'new'}"
    _form_header("Edit Room" if is_edit else "New Room", "✏️" if is_edit else "🏢")

    with st.form(key=fkey, clear_on_submit=not is_edit):
        c1, c2 = st.columns(2)
        name = c1.text_input("Room Name", value=existing.get("name", "") if existing else "", placeholder="e.g. Horizon Suite")
        capacity = c2.number_input("Capacity (seats)", min_value=1, max_value=500, value=int(existing.get("capacity", 10)) if existing else 10)
        c3, c4 = st.columns(2)
        floor = c3.number_input("Floor", min_value=0, max_value=50, value=int(existing.get("floor", 1)) if existing else 1)
        if is_edit:
            status = c4.selectbox("Status", options=["active", "inactive"], index=0 if existing.get("status") == "active" else 1)
        else:
            status = "active"
        amenities = st.multiselect("Amenities", options=AMENITY_OPTIONS, default=existing.get("amenities", []) if existing else [])
        submitted = st.form_submit_button("💾 Save Room" if is_edit else "✅ Create Room", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Room name is required.")
                return None
            return {"name": name.strip(), "capacity": int(capacity), "floor": int(floor), "amenities": amenities, "status": status}
    return None


def booking_form(
    rooms: list[dict],
    users: list[dict],
    existing: Optional[dict] = None,
    current_user: Optional[dict] = None,
) -> Optional[dict]:
    """Booking form. For employees, user is auto-set. For admins, user is selectable."""
    is_edit = existing is not None
    is_admin = current_user and current_user.get("role") == "admin"
    fkey = f"booking_form_{existing.get('booking_id','new') if existing else 'new'}"
    _form_header("Reschedule Booking" if is_edit else "New Booking", "🔄" if is_edit else "📅")

    active_rooms = [r for r in rooms if r.get("status") == "active"]
    if not active_rooms:
        st.warning("No active rooms available.")
        return None

    with st.form(key=fkey, clear_on_submit=not is_edit):
        title = st.text_input("Meeting Title", value=existing.get("title", "") if existing else "", placeholder="e.g. Sprint Planning")

        c1, c2 = st.columns(2)
        room_options = {r["name"]: r["room_id"] for r in active_rooms}
        room_names = list(room_options.keys())
        default_room_idx = 0
        if existing:
            for i, r in enumerate(active_rooms):
                if r["room_id"] == existing.get("room_id"):
                    default_room_idx = i; break
        selected_room = c1.selectbox("Room", options=room_names, index=default_room_idx)

        # For employees, auto-set user. For admins, allow selection.
        if is_admin and len(users) > 1:
            user_options = {u["name"]: u["user_id"] for u in users}
            user_names = list(user_options.keys())
            default_user_idx = 0
            if existing:
                for i, u in enumerate(users):
                    if u["user_id"] == existing.get("user_id"):
                        default_user_idx = i; break
            selected_user_name = c2.selectbox("Organizer", options=user_names, index=default_user_idx)
            selected_user_id = user_options[selected_user_name]
        else:
            c2.text_input("Organizer", value=current_user.get("name", ""), disabled=True)
            selected_user_id = current_user.get("user_id")

        default_date = datetime.date.today()
        default_start = datetime.time(9, 0)
        default_end = datetime.time(10, 0)
        if existing:
            try:
                default_date = datetime.date.fromisoformat(existing["start_time"][:10])
                default_start = datetime.time.fromisoformat(existing["start_time"][11:16])
                default_end = datetime.time.fromisoformat(existing["end_time"][11:16])
            except Exception:
                pass

        dc, sc, ec = st.columns(3)
        date = dc.date_input("Date", value=default_date)
        start_time = sc.time_input("Start", value=default_start, step=datetime.timedelta(minutes=15))
        end_time = ec.time_input("End", value=default_end, step=datetime.timedelta(minutes=15))

        notes = st.text_area("Notes (optional)", value=existing.get("notes", "") if existing else "", height=68, placeholder="Agenda or requirements...")

        submitted = st.form_submit_button("💾 Save" if is_edit else "✅ Confirm Booking", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Meeting title is required."); return None
            if start_time >= end_time:
                st.error("End time must be after start time."); return None
            return {
                "title": title.strip(), "room_id": room_options[selected_room],
                "user_id": selected_user_id,
                "start_time": datetime.datetime.combine(date, start_time).isoformat(),
                "end_time": datetime.datetime.combine(date, end_time).isoformat(),
                "notes": notes.strip(),
            }
    return None


def user_form(existing: Optional[dict] = None) -> Optional[dict]:
    """Admin form to register a new user (with password)."""
    is_edit = existing is not None
    fkey = f"user_form_{existing.get('user_id', 'new') if existing else 'new'}"
    _form_header("Edit User" if is_edit else "Register New User", "✏️" if is_edit else "👤")

    with st.form(key=fkey, clear_on_submit=not is_edit):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name", value=existing.get("name", "") if existing else "", placeholder="e.g. Alex Johnson")
        email = c2.text_input("Email", value=existing.get("email", "") if existing else "", placeholder="user@apexon.com")
        c3, c4 = st.columns(2)
        password = c3.text_input("Password", type="password", placeholder="Min 4 characters", value="")
        dept_idx = 0
        if existing and existing.get("department") in DEPARTMENT_OPTIONS:
            dept_idx = DEPARTMENT_OPTIONS.index(existing["department"])
        department = c4.selectbox("Department", options=[""] + DEPARTMENT_OPTIONS, index=dept_idx,
                                  format_func=lambda x: x if x else "Select department...")
        c5, c6 = st.columns(2)
        role_options = ["employee", "admin"]
        role_idx = 0
        if existing and existing.get("role") in role_options:
            role_idx = role_options.index(existing["role"])
        role = c5.selectbox("Role", options=role_options, index=role_idx)

        submitted = st.form_submit_button("💾 Save" if is_edit else "✅ Register User", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Full name is required.")
                return None
            if not email.strip() or "@" not in email:
                st.error("A valid email is required.")
                return None
            if not is_edit and (not password or len(password) < 4):
                st.error("Password must be at least 4 characters.")
                return None
            payload = {
                "name": name.strip(),
                "email": email.strip(),
                "department": department or "",
                "role": role,
            }
            if password:
                payload["password"] = password
            return payload
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
