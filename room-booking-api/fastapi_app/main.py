from __future__ import annotations

import dataclasses
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
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
    # Absolute imports when room-booking-api/ is on sys.path directly
    from core.models import BookingError  # type: ignore
    from core import rooms as rooms_core  # type: ignore
    from core import bookings as bookings_core  # type: ignore
    from core import users as users_core  # type: ignore
    from db.sqlite_adapter import SQLiteRoomRepo, SQLiteBookingRepo, SQLiteUserRepo  # type: ignore
    from db.base import RoomRepository, BookingRepository, UserRepository  # type: ignore
    from shared.config import get_db_path  # type: ignore


def _to_dict(obj) -> dict:
    """Convert a dataclass instance to a plain dict."""
    return dataclasses.asdict(obj)


def create_app(
    room_repo: RoomRepository,
    booking_repo: BookingRepository,
    user_repo: UserRepository,
) -> FastAPI:
    app = FastAPI(title="Room Booking API")

    # ------------------------------------------------------------------
    # Global exception handler
    # ------------------------------------------------------------------

    @app.exception_handler(BookingError)
    async def booking_error_handler(request: Request, exc: BookingError):
        return JSONResponse(
            status_code=exc.http_status,
            content={"error": exc.message, "detail": exc.detail},
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # ------------------------------------------------------------------
    # Rooms
    # ------------------------------------------------------------------

    @app.get("/rooms", status_code=200)
    async def list_rooms_route(
        capacity: Optional[int] = Query(None),
        floor: Optional[int] = Query(None),
        amenities: Optional[str] = Query(None),
    ):
        amenities_list = [a.strip() for a in amenities.split(",")] if amenities else None
        result = rooms_core.list_rooms(room_repo, capacity=capacity, amenities=amenities_list, floor=floor)
        return [_to_dict(r) for r in result]

    @app.post("/rooms", status_code=201)
    async def create_room_route(request: Request):
        data = await request.json()
        room = rooms_core.create_room(room_repo, data)
        return _to_dict(room)

    @app.get("/rooms/{room_id}", status_code=200)
    async def get_room_route(room_id: str):
        room = rooms_core.get_room(room_repo, room_id)
        return _to_dict(room)

    @app.put("/rooms/{room_id}", status_code=200)
    async def update_room_route(room_id: str, request: Request):
        data = await request.json()
        room = rooms_core.update_room(room_repo, room_id, data)
        return _to_dict(room)

    @app.delete("/rooms/{room_id}", status_code=204)
    async def deactivate_room_route(room_id: str):
        rooms_core.deactivate_room(room_repo, room_id)

    @app.get("/rooms/{room_id}/availability", status_code=200)
    async def room_availability_route(room_id: str, date: str = Query(...)):
        result = bookings_core.get_room_availability(booking_repo, room_repo, room_id, date)
        return _to_dict(result)

    # ------------------------------------------------------------------
    # Bookings
    # ------------------------------------------------------------------

    @app.get("/bookings", status_code=200)
    async def list_bookings_route(
        user_id: Optional[str] = Query(None),
        room_id: Optional[str] = Query(None),
        date: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
    ):
        result = bookings_core.list_bookings(booking_repo, user_id=user_id, room_id=room_id, date=date, status=status)
        return [_to_dict(b) for b in result]

    @app.post("/bookings", status_code=201)
    async def create_booking_route(request: Request):
        data = await request.json()
        booking = bookings_core.create_booking(booking_repo, room_repo, user_repo, data)
        return _to_dict(booking)

    @app.get("/bookings/{booking_id}", status_code=200)
    async def get_booking_route(booking_id: str):
        booking = bookings_core.get_booking(booking_repo, booking_id)
        return _to_dict(booking)

    @app.put("/bookings/{booking_id}", status_code=200)
    async def update_booking_route(booking_id: str, request: Request):
        data = await request.json()
        booking = bookings_core.update_booking(booking_repo, room_repo, user_repo, booking_id, data)
        return _to_dict(booking)

    @app.delete("/bookings/{booking_id}", status_code=200)
    async def cancel_booking_route(booking_id: str):
        booking = bookings_core.cancel_booking(booking_repo, booking_id)
        return _to_dict(booking)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    @app.get("/users", status_code=200)
    async def list_users_route():
        result = users_core.list_users(user_repo)
        return [_to_dict(u) for u in result]

    @app.post("/users", status_code=201)
    async def create_user_route(request: Request):
        data = await request.json()
        user = users_core.create_user(user_repo, data)
        return _to_dict(user)

    @app.get("/users/{user_id}", status_code=200)
    async def get_user_route(user_id: str):
        user = users_core.get_user(user_repo, user_id)
        return _to_dict(user)

    @app.get("/users/{user_id}/bookings", status_code=200)
    async def get_user_bookings_route(user_id: str):
        result = users_core.get_user_bookings(booking_repo, user_id)
        return [_to_dict(b) for b in result]

    return app


# Module-level default app instance
def _make_default_app() -> FastAPI:
    db_path = get_db_path()
    return create_app(
        room_repo=SQLiteRoomRepo(db_path),
        booking_repo=SQLiteBookingRepo(db_path),
        user_repo=SQLiteUserRepo(db_path),
    )


app = _make_default_app()
