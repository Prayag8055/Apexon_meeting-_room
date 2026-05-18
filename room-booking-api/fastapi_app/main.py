from __future__ import annotations

import dataclasses
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from ..core.models import BookingError
    from ..core import rooms as rooms_core
    from ..core import bookings as bookings_core
    from ..core import users as users_core
    from ..db.sqlite_adapter import SQLiteRoomRepo, SQLiteBookingRepo, SQLiteUserRepo
    from ..db.base import RoomRepository, BookingRepository, UserRepository
    from ..shared.config import get_db_path
except ImportError:
    from core.models import BookingError  # type: ignore
    from core import rooms as rooms_core  # type: ignore
    from core import bookings as bookings_core  # type: ignore
    from core import users as users_core  # type: ignore
    from db.sqlite_adapter import SQLiteRoomRepo, SQLiteBookingRepo, SQLiteUserRepo  # type: ignore
    from db.base import RoomRepository, BookingRepository, UserRepository  # type: ignore
    from shared.config import get_db_path  # type: ignore

logger = logging.getLogger("room_booking")


def _to_dict(obj) -> dict:
    return dataclasses.asdict(obj)


def _user_safe(user) -> dict:
    """Return user dict without password_hash."""
    d = _to_dict(user)
    d.pop("password_hash", None)
    return d


def create_app(
    room_repo: RoomRepository,
    booking_repo: BookingRepository,
    user_repo: UserRepository,
) -> FastAPI:
    app = FastAPI(title="Apexon Room Booking API", version="3.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    @app.exception_handler(BookingError)
    async def booking_error_handler(request: Request, exc: BookingError):
        return JSONResponse(status_code=exc.http_status, content={"error": exc.message, "detail": exc.detail})

    # ── Health & Stats ────────────────────────────────────────────────────
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/stats")
    async def stats():
        rooms = rooms_core.list_rooms(room_repo)
        bookings = bookings_core.list_bookings(booking_repo)
        users = users_core.list_users(user_repo)
        from datetime import date as _date
        today = _date.today().isoformat()
        active_rooms = sum(1 for r in rooms if r.status == "active")
        confirmed = [b for b in bookings if b.status == "confirmed"]
        cancelled = [b for b in bookings if b.status == "cancelled"]
        today_bookings = [b for b in confirmed if b.start_time[:10] == today]
        total = len(bookings)
        return {
            "total_rooms": len(rooms), "active_rooms": active_rooms,
            "total_bookings": total, "confirmed_bookings": len(confirmed),
            "cancelled_bookings": len(cancelled), "today_bookings": len(today_bookings),
            "total_users": len(users),
            "cancel_rate": round(len(cancelled) / total * 100, 1) if total else 0,
        }

    # ── Auth ──────────────────────────────────────────────────────────────
    @app.post("/auth/register", status_code=201)
    async def register(request: Request):
        data = await request.json()
        user = users_core.register_user(user_repo, data)
        return _user_safe(user)

    @app.post("/auth/login")
    async def login(request: Request):
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        user = users_core.login_user(user_repo, email, password)
        return _user_safe(user)


    # ── Rooms ─────────────────────────────────────────────────────────────
    @app.get("/rooms")
    async def list_rooms_route(capacity: Optional[int] = Query(None), floor: Optional[int] = Query(None), amenities: Optional[str] = Query(None)):
        amenities_list = [a.strip() for a in amenities.split(",")] if amenities else None
        return [_to_dict(r) for r in rooms_core.list_rooms(room_repo, capacity=capacity, amenities=amenities_list, floor=floor)]

    @app.post("/rooms", status_code=201)
    async def create_room_route(request: Request):
        return _to_dict(rooms_core.create_room(room_repo, await request.json()))

    @app.get("/rooms/{room_id}")
    async def get_room_route(room_id: str):
        return _to_dict(rooms_core.get_room(room_repo, room_id))

    @app.put("/rooms/{room_id}")
    async def update_room_route(room_id: str, request: Request):
        return _to_dict(rooms_core.update_room(room_repo, room_id, await request.json()))

    @app.delete("/rooms/{room_id}", status_code=204)
    async def deactivate_room_route(room_id: str):
        rooms_core.deactivate_room(room_repo, room_id)

    @app.get("/rooms/{room_id}/availability")
    async def room_availability_route(room_id: str, date: str = Query(...)):
        result = bookings_core.get_room_availability(booking_repo, room_repo, room_id, date)
        data = _to_dict(result)
        from shared.config import get_business_hours_start, get_business_hours_end
        from datetime import datetime as _dt, timedelta as _td
        sh, sm = map(int, get_business_hours_start().split(":"))
        eh, em = map(int, get_business_hours_end().split(":"))
        d = _dt.strptime(date, "%Y-%m-%d").date() if "T" not in date else _dt.fromisoformat(date).date()
        cursor = _dt(d.year, d.month, d.day, sh, sm)
        end = _dt(d.year, d.month, d.day, eh, em)
        booked = sorted(data.get("booked_slots", []), key=lambda x: x["start_time"])
        ranges = [(_dt.fromisoformat(b["start_time"]), _dt.fromisoformat(b["end_time"]), b) for b in booked]
        slots = []
        while cursor < end:
            slot_end = cursor + _td(minutes=30)
            if slot_end > end:
                break
            is_booked = any(cursor < be and slot_end > bs for bs, be, _ in ranges)
            title = next((bi.get("title", "Booked") for bs, be, bi in ranges if cursor < be and slot_end > bs), "")
            slots.append({"start_time": cursor.isoformat(), "end_time": slot_end.isoformat(), "is_available": not is_booked, "booking_title": title})
            cursor = slot_end
        data["slots"] = slots
        return data


    # ── Bookings ──────────────────────────────────────────────────────────
    @app.get("/bookings")
    async def list_bookings_route(user_id: Optional[str] = Query(None), room_id: Optional[str] = Query(None), date: Optional[str] = Query(None), status: Optional[str] = Query(None)):
        return [_to_dict(b) for b in bookings_core.list_bookings(booking_repo, user_id=user_id, room_id=room_id, date=date, status=status)]

    @app.post("/bookings", status_code=201)
    async def create_booking_route(request: Request):
        return _to_dict(bookings_core.create_booking(booking_repo, room_repo, user_repo, await request.json()))

    @app.get("/bookings/{booking_id}")
    async def get_booking_route(booking_id: str):
        return _to_dict(bookings_core.get_booking(booking_repo, booking_id))

    @app.put("/bookings/{booking_id}")
    async def update_booking_route(booking_id: str, request: Request):
        return _to_dict(bookings_core.update_booking(booking_repo, room_repo, user_repo, booking_id, await request.json()))

    @app.delete("/bookings/{booking_id}")
    async def cancel_booking_route(booking_id: str):
        return _to_dict(bookings_core.cancel_booking(booking_repo, booking_id))

    # ── Users ─────────────────────────────────────────────────────────────
    @app.get("/users")
    async def list_users_route():
        return [_user_safe(u) for u in users_core.list_users(user_repo)]

    @app.post("/users", status_code=201)
    async def create_user_route(request: Request):
        return _user_safe(users_core.create_user(user_repo, await request.json()))

    @app.get("/users/{user_id}")
    async def get_user_route(user_id: str):
        return _user_safe(users_core.get_user(user_repo, user_id))

    @app.get("/users/{user_id}/bookings")
    async def get_user_bookings_route(user_id: str):
        return [_to_dict(b) for b in users_core.get_user_bookings(booking_repo, user_id)]

    @app.post("/bookings/{booking_id}/checkin")
    async def checkin_booking_route(booking_id: str):
        # Set actual_check_in to now if not already set
        import datetime
        booking = bookings_core.get_booking(booking_repo, booking_id)
        if booking.actual_check_in:
            return JSONResponse(status_code=409, content={"error": "Already checked in"})
        booking.actual_check_in = datetime.datetime.utcnow().isoformat()
        bookings_core.save_booking(booking_repo, booking)
        return _to_dict(booking)

    @app.post("/bookings/{booking_id}/checkout")
    async def checkout_booking_route(booking_id: str):
        # Set actual_check_out to now if not already set
        import datetime
        booking = bookings_core.get_booking(booking_repo, booking_id)
        if booking.actual_check_out:
            return JSONResponse(status_code=409, content={"error": "Already checked out"})
        booking.actual_check_out = datetime.datetime.utcnow().isoformat()
        # If checking out early, update end_time for availability
        if booking.actual_check_out < booking.end_time:
            booking.end_time = booking.actual_check_out
        bookings_core.save_booking(booking_repo, booking)
        return _to_dict(booking)

    return app


def _make_default_app() -> FastAPI:
    db_path = get_db_path()
    return create_app(
        room_repo=SQLiteRoomRepo(db_path),
        booking_repo=SQLiteBookingRepo(db_path),
        user_repo=SQLiteUserRepo(db_path),
    )


app = _make_default_app()
