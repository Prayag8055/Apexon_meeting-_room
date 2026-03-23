"""Reusable card components for Apexon Room Booking UI."""
from __future__ import annotations
from typing import Callable, Optional
import streamlit as st
from theme import COLORS, badge_html, pill_html

# Amenity icons
_AMENITY_ICONS = {
    "projector": "📽️", "whiteboard": "📋", "video conferencing": "📹",
    "tv screen": "📺", "phone": "📞", "standing desk": "🪑",
    "natural light": "☀️", "air conditioning": "❄️",
}


def _amenity_icon(name: str) -> str:
    return _AMENITY_ICONS.get(name.lower(), "✦")


def stat_card(
    label: str,
    value: int | str,
    icon: str,
    color: str = "#6366f1",
    bg_color: str = "#6366f1",
    delta: str = "",
) -> None:
    delta_html = ""
    if delta:
        delta_html = f'<div class="rb-stat-delta" style="color:{color}">{delta}</div>'
    st.markdown(
        f"""
        <div class="rb-stat-card">
            <div class="rb-stat-glow" style="background:{bg_color}"></div>
            <div class="rb-stat-icon-wrap" style="background:linear-gradient(135deg,{bg_color}22,{bg_color}11);border:1px solid {bg_color}33">
                <span>{icon}</span>
            </div>
            <div class="rb-stat-value">{value}</div>
            <div class="rb-stat-label">{label}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def room_card(
    room: dict,
    on_edit: Optional[Callable] = None,
    on_deactivate: Optional[Callable] = None,
) -> None:
    status = room.get("status", "active")
    amenities = room.get("amenities") or []
    pills = "".join(
        f'<span class="rb-pill">{_amenity_icon(a)} {a}</span>' for a in amenities[:4]
    )
    extra = f'<span class="rb-pill" style="color:#4a5568">+{len(amenities)-4} more</span>' if len(amenities) > 4 else ""
    cap = room.get("capacity", 0)
    floor = room.get("floor", 1)
    cap_pct = min(int(cap) / 50 * 100, 100) if cap else 0

    st.markdown(
        f"""
        <div class="rb-room-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem">
                <div style="flex:1;min-width:0">
                    <div class="rb-room-name">{room.get('name','')}</div>
                    <div class="rb-room-meta">
                        <span>👥 {cap} seats</span>
                        <span>🏢 Floor {floor}</span>
                    </div>
                </div>
                <div style="margin-left:0.75rem;flex-shrink:0">{badge_html(status, status)}</div>
            </div>
            <div style="margin-bottom:0.75rem;flex-wrap:wrap;display:flex">{pills}{extra}</div>
            <div style="margin-top:auto">
                <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#4a5568;margin-bottom:0.3rem">
                    <span>Capacity</span><span style="color:#8892b0">{cap} people</span>
                </div>
                <div style="height:4px;background:#1e2a45;border-radius:2px;overflow:hidden">
                    <div style="height:100%;width:{cap_pct}%;background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:2px;transition:width 0.5s ease"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if on_edit or on_deactivate:
        c1, c2 = st.columns(2)
        if on_edit:
            with c1:
                if st.button("✏️ Edit", key=f"edit_room_{room.get('room_id')}", use_container_width=True, type="secondary"):
                    on_edit(room)
        if on_deactivate and status == "active":
            with c2:
                if st.button("🗑️ Deactivate", key=f"deact_room_{room.get('room_id')}", use_container_width=True, type="secondary"):
                    on_deactivate(room)


def booking_card(
    booking: dict,
    room_name: str = "",
    user_name: str = "",
    on_cancel: Optional[Callable] = None,
    on_reschedule: Optional[Callable] = None,
) -> None:
    status = booking.get("status", "confirmed")
    start_raw = booking.get("start_time", "")
    end_raw = booking.get("end_time", "")
    date_str = start_raw[:10] if start_raw else ""
    start_t = start_raw[11:16] if len(start_raw) > 11 else ""
    end_t = end_raw[11:16] if len(end_raw) > 11 else ""

    # Calculate duration
    duration = ""
    try:
        from datetime import datetime as _dt
        s = _dt.fromisoformat(start_raw)
        e = _dt.fromisoformat(end_raw)
        mins = int((e - s).total_seconds() / 60)
        if mins >= 60:
            h, m = divmod(mins, 60)
            duration = f"{h}h{m}m" if m else f"{h}h"
        else:
            duration = f"{mins}m"
    except Exception:
        pass

    accent_colors = {"confirmed": "#10b981", "cancelled": "#f43f5e"}
    accent = accent_colors.get(status, "#6366f1")

    notes = booking.get("notes", "")
    notes_html = (
        f'<div style="font-size:0.75rem;color:#4a5568;margin-top:0.4rem;font-style:italic">'
        f'"{notes[:80]}{"…" if len(notes)>80 else ""}"</div>'
        if notes else ""
    )

    duration_html = f'<span class="rb-booking-meta-item">⏱️ {duration}</span>' if duration else ""

    st.markdown(
        f"""
        <div class="rb-booking-card">
            <div class="rb-booking-accent" style="background:{accent}"></div>
            <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:0.5rem">
                    <div class="rb-booking-title">{booking.get('title','Booking')}</div>
                    {badge_html(status, status)}
                </div>
                <div class="rb-booking-meta">
                    <span class="rb-booking-meta-item">🏢 {room_name or booking.get('room_id','')[:8]}</span>
                    <span class="rb-booking-meta-item">👤 {user_name or booking.get('user_id','')[:8]}</span>
                    <span class="rb-booking-meta-item">📅 {date_str}</span>
                    <span class="rb-booking-meta-item">🕐 {start_t} – {end_t}</span>
                    {duration_html}
                </div>
                {notes_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if status == "confirmed" and (on_cancel or on_reschedule):
        c1, c2, c3 = st.columns([1, 1, 2])
        if on_reschedule:
            with c1:
                if st.button("🔄 Reschedule", key=f"reschedule_{booking.get('booking_id')}", use_container_width=True, type="secondary"):
                    on_reschedule(booking)
        if on_cancel:
            with c2:
                if st.button("✖ Cancel", key=f"cancel_{booking.get('booking_id')}", use_container_width=True, type="secondary"):
                    on_cancel(booking)


def user_card(
    user: dict,
    booking_count: int = 0,
    on_view: Optional[Callable] = None,
) -> None:
    name = user.get("name", "")
    initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "?"
    dept = user.get("department", "")
    email = user.get("email", "")
    role = user.get("role", "employee")

    # Generate a consistent gradient based on name
    colors = [
        ("6366f1", "8b5cf6"), ("10b981", "34d399"), ("f59e0b", "fbbf24"),
        ("06b6d4", "22d3ee"), ("f43f5e", "fb7185"), ("8b5cf6", "c084fc"),
    ]
    idx = sum(ord(c) for c in name) % len(colors) if name else 0
    c1, c2 = colors[idx]

    st.markdown(
        f"""
        <div class="rb-user-card">
            <div class="rb-avatar" style="background:linear-gradient(135deg,#{c1},#{c2})">{initials}</div>
            <div class="rb-user-name">{name}</div>
            <div class="rb-user-email" title="{email}">{email}</div>
            <div style="font-size:0.68rem;font-weight:700;color:{'#818cf8' if role == 'admin' else '#8892b0'};text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.15rem">{'🛡️ ' + role if role == 'admin' else '👤 ' + role}</div>
            <div class="rb-user-dept">{dept or "No department"}</div>
            <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.5rem">
                <div style="text-align:center">
                    <div style="font-size:1.1rem;font-weight:700;color:#818cf8">{booking_count}</div>
                    <div style="font-size:0.65rem;color:#4a5568;text-transform:uppercase;letter-spacing:0.06em">Bookings</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if on_view:
        if st.button("View Bookings →", key=f"view_{user.get('user_id')}", use_container_width=True, type="secondary"):
            on_view(user)


def availability_grid(availability: dict) -> None:
    slots = availability.get("slots", [])
    if not slots:
        st.markdown(
            '<div class="rb-empty"><div class="rb-empty-icon">📭</div>'
            '<div class="rb-empty-text">No availability data for this date.</div></div>',
            unsafe_allow_html=True,
        )
        return

    free = sum(1 for s in slots if s.get("is_available", True))
    total = len(slots)
    pct = int(free / total * 100) if total else 0

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;
                    background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem;padding:0.75rem 1rem">
            <div style="flex:1">
                <div style="font-size:0.75rem;color:#8892b0;margin-bottom:0.3rem">Availability — {free} of {total} slots free</div>
                <div style="height:6px;background:#1e2a45;border-radius:3px;overflow:hidden">
                    <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#10b981,#34d399);border-radius:3px"></div>
                </div>
            </div>
            <div style="text-align:right;flex-shrink:0">
                <div style="font-size:1.1rem;font-weight:700;color:#10b981">{pct}%</div>
                <div style="font-size:0.65rem;color:#4a5568">available</div>
            </div>
        </div>
        <div class="rb-avail-grid">
        """,
        unsafe_allow_html=True,
    )

    slot_htmls = []
    for slot in slots:
        start = slot.get("start_time", "")
        end = slot.get("end_time", "")
        s_t = start[11:16] if len(start) > 11 else start[-5:]
        e_t = end[11:16] if len(end) > 11 else end[-5:]
        if slot.get("is_available", True):
            slot_htmls.append(
                f'<div class="rb-slot rb-slot-free">'
                f'<div class="rb-slot-time">{s_t}</div>'
                f'<div class="rb-slot-label">Available</div>'
                f'</div>'
            )
        else:
            title = (slot.get("booking_title") or "Booked")[:12]
            slot_htmls.append(
                f'<div class="rb-slot rb-slot-booked">'
                f'<div class="rb-slot-time">{s_t}</div>'
                f'<div class="rb-slot-label">{title}</div>'
                f'</div>'
            )

    st.markdown("".join(slot_htmls) + "</div>", unsafe_allow_html=True)
