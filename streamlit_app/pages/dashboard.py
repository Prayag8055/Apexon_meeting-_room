"""Dashboard page — KPI overview and recent activity."""
from __future__ import annotations
import datetime
import streamlit as st
from api_client import get_rooms, get_bookings, get_users
from theme import COLORS, badge_html
from components.cards import stat_card, booking_card


def render_dashboard() -> None:
    st.markdown('<div class="rb-page">', unsafe_allow_html=True)

    # ── Page header ───────────────────────────────────────────────────────────
    today = datetime.date.today()
    day_name = today.strftime("%A, %B %d")
    st.markdown(
        f"""
        <div style="margin-bottom:1.75rem">
            <div class="rb-page-title">Good day 👋</div>
            <div class="rb-page-subtitle">{day_name} · Here's what's happening in your workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch data ────────────────────────────────────────────────────────────
    with st.spinner(""):
        rooms = get_rooms()
        bookings = get_bookings()
        users = get_users()

    today_str = today.isoformat()
    active_rooms = sum(1 for r in rooms if r.get("status") == "active")
    total_bookings = len(bookings)
    confirmed_today = sum(
        1 for b in bookings
        if b.get("status") == "confirmed" and b.get("start_time", "")[:10] == today_str
    )
    total_users = len(users)
    cancelled = sum(1 for b in bookings if b.get("status") == "cancelled")

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Active Rooms", active_rooms, "🏢", color="#818cf8", bg_color="#6366f1")
    with c2:
        stat_card("Total Bookings", total_bookings, "📅", color="#34d399", bg_color="#10b981")
    with c3:
        stat_card("Today's Meetings", confirmed_today, "✅", color="#fbbf24", bg_color="#f59e0b")
    with c4:
        stat_card("Team Members", total_users, "👥", color="#67e8f9", bg_color="#06b6d4")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Main content ──────────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown(
            '<div class="rb-section-header">'
            '<div class="rb-section-title">📋 Recent Bookings</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        recent = sorted(bookings, key=lambda b: b.get("created_at", ""), reverse=True)[:6]
        if recent:
            room_map = {r["room_id"]: r["name"] for r in rooms}
            user_map = {u["user_id"]: u["name"] for u in users}
            for b in recent:
                booking_card(
                    b,
                    room_name=room_map.get(b.get("room_id", ""), ""),
                    user_name=user_map.get(b.get("user_id", ""), ""),
                )
        else:
            st.markdown(
                '<div class="rb-empty"><div class="rb-empty-icon">📭</div>'
                '<div class="rb-empty-text">No bookings yet. Create your first booking!</div></div>',
                unsafe_allow_html=True,
            )

    with right:
        # Room status panel
        st.markdown(
            '<div class="rb-section-header">'
            '<div class="rb-section-title">🏢 Room Status</div>'
            f'<span style="font-size:0.75rem;color:#4a5568">{active_rooms} active</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        for room in rooms[:8]:
            status = room.get("status", "active")
            cap = room.get("capacity", 0)
            color = "#818cf8" if status == "active" else "#4a5568"
            dot_color = "#10b981" if status == "active" else "#4a5568"
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.75rem;
                            padding:0.65rem 0.875rem;margin-bottom:0.4rem;
                            background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem;
                            transition:all 0.2s ease">
                    <div style="width:8px;height:8px;border-radius:50%;background:{dot_color};flex-shrink:0"></div>
                    <div style="flex:1;min-width:0">
                        <div style="font-size:0.85rem;font-weight:600;color:#f0f4ff;
                                    overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{room.get('name','')}</div>
                        <div style="font-size:0.7rem;color:#4a5568">{cap} seats</div>
                    </div>
                    <div style="font-size:0.7rem;font-weight:700;color:{color};text-transform:uppercase;
                                letter-spacing:0.05em;flex-shrink:0">{status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Quick stats
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="rb-section-header">'
            '<div class="rb-section-title">📊 Quick Stats</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        utilization = int(active_rooms / len(rooms) * 100) if rooms else 0
        cancel_rate = int(cancelled / total_bookings * 100) if total_bookings else 0

        for label, value, pct, color in [
            ("Room Utilization", f"{utilization}%", utilization, "#6366f1"),
            ("Booking Success Rate", f"{100 - cancel_rate}%", 100 - cancel_rate, "#10b981"),
        ]:
            st.markdown(
                f"""
                <div style="padding:0.75rem 0.875rem;background:#0f1420;border:1px solid #1e2a45;
                            border-radius:0.75rem;margin-bottom:0.5rem">
                    <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem">
                        <span style="font-size:0.78rem;color:#8892b0">{label}</span>
                        <span style="font-size:0.85rem;font-weight:700;color:{color}">{value}</span>
                    </div>
                    <div style="height:4px;background:#1e2a45;border-radius:2px;overflow:hidden">
                        <div style="height:100%;width:{pct}%;background:{color};border-radius:2px"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
