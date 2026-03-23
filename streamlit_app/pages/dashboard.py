"""Dashboard — KPIs, instant booking, upcoming meetings."""
from __future__ import annotations
import datetime
import streamlit as st
from api_client import get_rooms, get_bookings, get_stats, create_booking, get_room_availability, APIError
from components.cards import stat_card, booking_card


def _greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12: return "Good morning"
    elif hour < 17: return "Good afternoon"
    return "Good evening"


def render_dashboard() -> None:
    user = st.session_state.get("user", {})
    is_admin = user.get("role") == "admin"
    user_name = user.get("name", "").split()[0] if user.get("name") else ""

    st.markdown('<div class="rb-page">', unsafe_allow_html=True)
    today = datetime.date.today()
    st.markdown(
        f'<div style="margin-bottom:1.5rem">'
        f'<div class="rb-page-title">{_greeting()}, {user_name} 👋</div>'
        f'<div class="rb-page-subtitle">{today.strftime("%A, %B %d, %Y")}</div></div>',
        unsafe_allow_html=True,
    )

    with st.spinner(""):
        stats = get_stats()
        rooms = get_rooms()
        bookings = get_bookings()


    # ── KPI row ───────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Active Rooms", stats.get("active_rooms", 0), "🏢", color="#818cf8", bg_color="#6366f1")
    with c2:
        stat_card("Total Bookings", stats.get("total_bookings", 0), "📅", color="#34d399", bg_color="#10b981")
    with c3:
        stat_card("Today's Meetings", stats.get("today_bookings", 0), "✅", color="#fbbf24", bg_color="#f59e0b")
    with c4:
        if is_admin:
            stat_card("Team Members", stats.get("total_users", 0), "👥", color="#67e8f9", bg_color="#06b6d4")
        else:
            my_bookings = sum(1 for b in bookings if b.get("user_id") == user.get("user_id") and b.get("status") == "confirmed")
            stat_card("My Bookings", my_bookings, "📋", color="#67e8f9", bg_color="#06b6d4")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Main layout ───────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        # ── INSTANT BOOK — the fast booking flow ──────────────────────────
        st.markdown(
            '<div class="rb-section-header"><div class="rb-section-title">⚡ Instant Book</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="rb-quick-book">', unsafe_allow_html=True)

        active_rooms = [r for r in rooms if r.get("status") == "active"]
        if active_rooms:
            # Step 1: Pick room and date
            qc1, qc2 = st.columns(2)
            room_opts = {r["name"]: r["room_id"] for r in active_rooms}
            q_room = qc1.selectbox("Room", options=list(room_opts.keys()), key="ib_room")
            q_date = qc2.date_input("Date", value=today, key="ib_date")

            # Step 2: Show available slots as clickable buttons
            room_id = room_opts.get(q_room)
            if room_id:
                try:
                    avail = get_room_availability(room_id, str(q_date))
                    free_slots = [s for s in avail.get("slots", []) if s.get("is_available")]

                    # Filter out past slots for today
                    if str(q_date) == str(today):
                        now_str = datetime.datetime.now().strftime("%H:%M")
                        free_slots = [s for s in free_slots if s["start_time"][11:16] >= now_str]

                    if free_slots:
                        st.markdown(
                            f'<div style="font-size:0.78rem;color:#8892b0;margin:0.5rem 0 0.4rem">'
                            f'🟢 {len(free_slots)} slots available — click to book instantly</div>',
                            unsafe_allow_html=True,
                        )
                        # Show slots in a grid
                        cols_per_row = 6
                        for i in range(0, min(len(free_slots), 18), cols_per_row):
                            slot_cols = st.columns(cols_per_row)
                            for j, col in enumerate(slot_cols):
                                idx = i + j
                                if idx < len(free_slots) and idx < 18:
                                    slot = free_slots[idx]
                                    s_t = slot["start_time"][11:16]
                                    e_t = slot["end_time"][11:16]
                                    with col:
                                        if st.button(f"{s_t}", key=f"ib_slot_{idx}", use_container_width=True, type="secondary"):
                                            st.session_state["ib_selected_slot"] = slot
                    else:
                        st.info("No available slots for this date. Try another room or date.")
                except APIError as e:
                    st.error(f"❌ {e}")


            # Step 3: If slot selected, show minimal confirm form
            if st.session_state.get("ib_selected_slot"):
                slot = st.session_state["ib_selected_slot"]
                s_t = slot["start_time"][11:16]
                e_t = slot["end_time"][11:16]
                st.markdown(
                    f'<div style="margin-top:0.75rem;padding:0.75rem 1rem;background:rgba(16,185,129,0.08);'
                    f'border:1px solid rgba(16,185,129,0.2);border-radius:0.75rem">'
                    f'<div style="font-size:0.85rem;font-weight:600;color:#10b981">'
                    f'📅 {q_room} · {q_date} · {s_t} – {e_t}</div></div>',
                    unsafe_allow_html=True,
                )
                with st.form("instant_book_confirm", clear_on_submit=True):
                    ib_title = st.text_input("Meeting Title", placeholder="e.g. Sprint Planning", key="ib_title")
                    fc1, fc2 = st.columns(2)
                    confirmed = fc1.form_submit_button("✅ Confirm Booking", use_container_width=True)
                    if fc2.form_submit_button("✖ Cancel", use_container_width=True):
                        st.session_state.pop("ib_selected_slot", None)
                        st.rerun()
                    if confirmed:
                        title = ib_title.strip() if ib_title else "Meeting"
                        try:
                            create_booking({
                                "title": title,
                                "room_id": room_id,
                                "user_id": user.get("user_id"),
                                "start_time": slot["start_time"],
                                "end_time": slot["end_time"],
                                "notes": "",
                            })
                            st.session_state.pop("ib_selected_slot", None)
                            st.success(f"✅ Booked! {q_room} at {s_t}")
                            st.rerun()
                        except APIError as e:
                            if e.status_code == 409:
                                st.error("⚠️ Slot just got taken. Please pick another.")
                            else:
                                st.error(f"❌ {e}")
        else:
            st.info("No active rooms available.")
        st.markdown('</div>', unsafe_allow_html=True)


        # ── My Recent Bookings ────────────────────────────────────────────
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="rb-section-header"><div class="rb-section-title">📋 My Recent Bookings</div></div>',
            unsafe_allow_html=True,
        )
        my_bookings_list = sorted(
            [b for b in bookings if b.get("user_id") == user.get("user_id")],
            key=lambda b: b.get("created_at", ""), reverse=True,
        )[:6]
        room_map = {r["room_id"]: r["name"] for r in rooms}
        if my_bookings_list:
            for b in my_bookings_list:
                booking_card(b, room_name=room_map.get(b.get("room_id", ""), ""), user_name=user.get("name", ""))
        else:
            st.markdown(
                '<div class="rb-empty" style="padding:2rem"><div class="rb-empty-icon">📭</div>'
                '<div class="rb-empty-text">No bookings yet. Use Instant Book above!</div></div>',
                unsafe_allow_html=True,
            )

    with right:
        # ── Upcoming Today ────────────────────────────────────────────────
        st.markdown(
            '<div class="rb-section-header"><div class="rb-section-title">🕐 Upcoming Today</div></div>',
            unsafe_allow_html=True,
        )
        today_str = today.isoformat()
        now_str = datetime.datetime.now().strftime("%H:%M")
        upcoming = sorted(
            [b for b in bookings
             if b.get("status") == "confirmed"
             and b.get("start_time", "")[:10] == today_str
             and b.get("start_time", "")[11:16] >= now_str],
            key=lambda b: b.get("start_time", ""),
        )[:8]

        if upcoming:
            for b in upcoming:
                s_t = b.get("start_time", "")[11:16]
                e_t = b.get("end_time", "")[11:16]
                rname = room_map.get(b.get("room_id", ""), "")
                is_mine = b.get("user_id") == user.get("user_id")
                mine_dot = ' style="border-left:3px solid #6366f1;padding-left:0.5rem"' if is_mine else ""
                st.markdown(
                    f'<div class="rb-timeline-item"{mine_dot}>'
                    f'<div class="rb-timeline-time">{s_t}</div>'
                    f'<div class="rb-timeline-dot"></div>'
                    f'<div class="rb-timeline-content">'
                    f'<div class="rb-timeline-title">{b.get("title","")}</div>'
                    f'<div class="rb-timeline-meta">🏢 {rname} · {s_t}–{e_t}'
                    f'{"  · 👤 You" if is_mine else ""}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="rb-empty" style="padding:2rem"><div class="rb-empty-icon">🎉</div>'
                '<div class="rb-empty-text">No more meetings today!</div></div>',
                unsafe_allow_html=True,
            )


        # ── Room Status ───────────────────────────────────────────────────
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="rb-section-header"><div class="rb-section-title">🏢 Rooms</div></div>',
            unsafe_allow_html=True,
        )
        for room in rooms[:10]:
            status = room.get("status", "active")
            cap = room.get("capacity", 0)
            dot_color = "#10b981" if status == "active" else "#4a5568"
            color = "#818cf8" if status == "active" else "#4a5568"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:0.75rem;'
                f'padding:0.55rem 0.875rem;margin-bottom:0.35rem;'
                f'background:#0f1420;border:1px solid #1e2a45;border-radius:0.75rem">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{dot_color}"></div>'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-size:0.82rem;font-weight:600;color:#f0f4ff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{room.get("name","")}</div>'
                f'<div style="font-size:0.68rem;color:#4a5568">👥 {cap} seats</div></div>'
                f'<div style="font-size:0.68rem;font-weight:700;color:{color};text-transform:uppercase">{status}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
