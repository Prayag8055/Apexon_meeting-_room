from __future__ import annotations

import json
import sqlite3
from typing import Optional

try:
    from ..core.models import Room, Booking, User
    from .base import RoomRepository, BookingRepository, UserRepository
except ImportError:
    from core.models import Room, Booking, User  # type: ignore
    from db.base import RoomRepository, BookingRepository, UserRepository  # type: ignore

_DDL = """
CREATE TABLE IF NOT EXISTS rooms (
    room_id    TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    floor      INTEGER NOT NULL,
    capacity   INTEGER NOT NULL CHECK (capacity >= 1),
    amenities  TEXT NOT NULL DEFAULT '[]',
    status     TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id    TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    room_id    TEXT NOT NULL REFERENCES rooms(room_id),
    user_id    TEXT NOT NULL REFERENCES users(user_id),
    title      TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time   TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed','cancelled')),
    attendees  TEXT NOT NULL DEFAULT '[]',
    notes      TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bookings_room_time ON bookings(room_id, start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
"""


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _row_to_room(row: sqlite3.Row) -> Room:
    return Room(
        room_id=row["room_id"],
        name=row["name"],
        floor=row["floor"],
        capacity=row["capacity"],
        amenities=json.loads(row["amenities"]),
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_booking(row: sqlite3.Row) -> Booking:
    return Booking(
        booking_id=row["booking_id"],
        room_id=row["room_id"],
        user_id=row["user_id"],
        title=row["title"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        status=row["status"],
        attendees=json.loads(row["attendees"]),
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        department=row["department"],
        created_at=row["created_at"],
    )


class SQLiteRoomRepo(RoomRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(_DDL)

    def get(self, room_id: str) -> Optional[Room]:
        with _connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM rooms WHERE room_id = ?", (room_id,)
            ).fetchone()
        return _row_to_room(row) if row else None

    def list(
        self,
        capacity: int = None,
        amenities: list[str] = None,
        floor: int = None,
    ) -> list[Room]:
        query = "SELECT * FROM rooms WHERE 1=1"
        params: list = []

        if capacity is not None:
            query += " AND capacity >= ?"
            params.append(capacity)
        if floor is not None:
            query += " AND floor = ?"
            params.append(floor)

        with _connect(self._db_path) as conn:
            rows = conn.execute(query, params).fetchall()

        rooms = [_row_to_room(r) for r in rows]

        if amenities:
            rooms = [
                r for r in rooms
                if all(a in r.amenities for a in amenities)
            ]

        return rooms

    def create(self, room: Room) -> Room:
        with _connect(self._db_path) as conn:
            conn.execute(
                """INSERT INTO rooms
                   (room_id, name, floor, capacity, amenities, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    room.room_id,
                    room.name,
                    room.floor,
                    room.capacity,
                    json.dumps(room.amenities),
                    room.status,
                    room.created_at,
                    room.updated_at,
                ),
            )
        return room

    def update(self, room: Room) -> Room:
        with _connect(self._db_path) as conn:
            conn.execute(
                """UPDATE rooms
                   SET name=?, floor=?, capacity=?, amenities=?, status=?, updated_at=?
                   WHERE room_id=?""",
                (
                    room.name,
                    room.floor,
                    room.capacity,
                    json.dumps(room.amenities),
                    room.status,
                    room.updated_at,
                    room.room_id,
                ),
            )
        return room

    def delete(self, room_id: str) -> None:
        with _connect(self._db_path) as conn:
            conn.execute(
                "UPDATE rooms SET status = 'inactive' WHERE room_id = ?",
                (room_id,),
            )


class SQLiteBookingRepo(BookingRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(_DDL)

    def get(self, booking_id: str) -> Optional[Booking]:
        with _connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM bookings WHERE booking_id = ?", (booking_id,)
            ).fetchone()
        return _row_to_booking(row) if row else None

    def list(
        self,
        user_id: str = None,
        room_id: str = None,
        date: str = None,
        status: str = None,
    ) -> list[Booking]:
        query = "SELECT * FROM bookings WHERE 1=1"
        params: list = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        if room_id is not None:
            query += " AND room_id = ?"
            params.append(room_id)
        if date is not None:
            query += " AND start_time LIKE ?"
            params.append(f"{date}%")
        if status is not None:
            query += " AND status = ?"
            params.append(status)

        with _connect(self._db_path) as conn:
            rows = conn.execute(query, params).fetchall()

        return [_row_to_booking(r) for r in rows]

    def create(self, booking: Booking) -> Booking:
        with _connect(self._db_path) as conn:
            conn.execute(
                """INSERT INTO bookings
                   (booking_id, room_id, user_id, title, start_time, end_time,
                    status, attendees, notes, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    booking.booking_id,
                    booking.room_id,
                    booking.user_id,
                    booking.title,
                    booking.start_time,
                    booking.end_time,
                    booking.status,
                    json.dumps(booking.attendees),
                    booking.notes,
                    booking.created_at,
                    booking.updated_at,
                ),
            )
        return booking

    def update(self, booking: Booking) -> Booking:
        with _connect(self._db_path) as conn:
            conn.execute(
                """UPDATE bookings
                   SET room_id=?, user_id=?, title=?, start_time=?, end_time=?,
                       status=?, attendees=?, notes=?, updated_at=?
                   WHERE booking_id=?""",
                (
                    booking.room_id,
                    booking.user_id,
                    booking.title,
                    booking.start_time,
                    booking.end_time,
                    booking.status,
                    json.dumps(booking.attendees),
                    booking.notes,
                    booking.updated_at,
                    booking.booking_id,
                ),
            )
        return booking

    def cancel(self, booking_id: str) -> Booking:
        with _connect(self._db_path) as conn:
            conn.execute(
                "UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?",
                (booking_id,),
            )
            row = conn.execute(
                "SELECT * FROM bookings WHERE booking_id = ?", (booking_id,)
            ).fetchone()
        return _row_to_booking(row)

    def get_overlapping(
        self,
        room_id: str,
        start_time: str,
        end_time: str,
        exclude_booking_id: str = None,
    ) -> list[Booking]:
        query = (
            "SELECT * FROM bookings "
            "WHERE room_id = ? AND start_time < ? AND end_time > ? AND status = 'confirmed'"
        )
        params: list = [room_id, end_time, start_time]

        if exclude_booking_id is not None:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)

        with _connect(self._db_path) as conn:
            rows = conn.execute(query, params).fetchall()

        return [_row_to_booking(r) for r in rows]


class SQLiteUserRepo(UserRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        with _connect(self._db_path) as conn:
            conn.executescript(_DDL)

    def get(self, user_id: str) -> Optional[User]:
        with _connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return _row_to_user(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        with _connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
        return _row_to_user(row) if row else None

    def list(self) -> list[User]:
        with _connect(self._db_path) as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
        return [_row_to_user(r) for r in rows]

    def create(self, user: User) -> User:
        with _connect(self._db_path) as conn:
            conn.execute(
                """INSERT INTO users (user_id, name, email, department, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user.user_id, user.name, user.email, user.department, user.created_at),
            )
        return user
