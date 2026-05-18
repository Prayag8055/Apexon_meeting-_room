import uuid
from datetime import datetime, timedelta

try:
    from .models import Booking, BookingError, TimeSlot, BookedSlot, AvailabilityResult
    from ..db.base import BookingRepository, RoomRepository, UserRepository
    from ..shared.config import get_business_hours_start, get_business_hours_end
except ImportError:
    from core.models import Booking, BookingError, TimeSlot, BookedSlot, AvailabilityResult  # type: ignore
    from db.base import BookingRepository, RoomRepository, UserRepository  # type: ignore
    from shared.config import get_business_hours_start, get_business_hours_end  # type: ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_dt(value: str) -> datetime:
    """Parse an ISO 8601 datetime string, trying fromisoformat first."""
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        try:
            from dateutil.parser import isoparse
            return isoparse(value)
        except Exception:
            raise BookingError(f"invalid datetime format: {value!r}", http_status=422)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


# ---------------------------------------------------------------------------
# Task 5.5 — check_conflicts
# ---------------------------------------------------------------------------

def check_conflicts(
    booking_repo: BookingRepository,
    room_id: str,
    start_time: str,
    end_time: str,
    exclude_booking_id: str = None,
) -> list[Booking]:
    """Return confirmed bookings that overlap [start_time, end_time) for room_id."""
    candidates = booking_repo.get_overlapping(room_id, start_time, end_time, exclude_booking_id)
    conflicts = []
    for booking in candidates:
        if booking.status == "cancelled":
            continue
        if exclude_booking_id and booking.booking_id == exclude_booking_id:
            continue
        conflicts.append(booking)
    return conflicts


# ---------------------------------------------------------------------------
# Task 5.7 — CRUD helpers + create / cancel / update
# ---------------------------------------------------------------------------

def get_booking(booking_repo: BookingRepository, booking_id: str) -> Booking:
    booking = booking_repo.get(booking_id)
    if booking is None:
        raise BookingError("booking not found", http_status=404)
    return booking


def list_bookings(
    booking_repo: BookingRepository,
    user_id: str = None,
    room_id: str = None,
    date: str = None,
    status: str = None,
) -> list[Booking]:
    return booking_repo.list(user_id=user_id, room_id=room_id, date=date, status=status)


def _validate_required_fields(data: dict) -> None:
    for field in ("room_id", "user_id", "title", "start_time", "end_time"):
        if not data.get(field):
            raise BookingError(f"field '{field}' is required", http_status=422)


def _validate_time_range(start_time: str, end_time: str) -> tuple[datetime, datetime]:
    start_dt = _parse_dt(start_time)
    end_dt = _parse_dt(end_time)
    if end_dt <= start_dt:
        raise BookingError("end_time must be after start_time", http_status=422)
    if (end_dt - start_dt) < timedelta(minutes=15):
        raise BookingError("minimum booking duration is 15 minutes", http_status=422)
    return start_dt, end_dt


def create_booking(
    booking_repo: BookingRepository,
    room_repo: RoomRepository,
    user_repo: UserRepository,
    data: dict,
) -> Booking:
    _validate_required_fields(data)
    _validate_time_range(data["start_time"], data["end_time"])

    # Check room exists and is active
    room = room_repo.get(data["room_id"])
    if room is None:
        raise BookingError("room not found", http_status=404)
    if room.status != "active":
        raise BookingError("room is not available for booking", http_status=422)

    # Check user exists
    user = user_repo.get(data["user_id"])
    if user is None:
        raise BookingError("user not found", http_status=404)

    # Check for conflicts
    conflicts = check_conflicts(booking_repo, data["room_id"], data["start_time"], data["end_time"])
    if conflicts:
        raise BookingError("time slot unavailable", http_status=409)

    now = _now_iso()
    booking = Booking(
        booking_id=str(uuid.uuid4()),
        room_id=data["room_id"],
        user_id=data["user_id"],
        title=data["title"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        status="confirmed",
        attendees=data.get("attendees", []),
        notes=data.get("notes", ""),
        created_at=now,
        updated_at=now,
    )
    return booking_repo.create(booking)


def cancel_booking(booking_repo: BookingRepository, booking_id: str) -> Booking:
    booking = get_booking(booking_repo, booking_id)
    if booking.status == "cancelled":
        raise BookingError("booking is already cancelled", http_status=409)
    return booking_repo.cancel(booking_id)


def update_booking(
    booking_repo: BookingRepository,
    room_repo: RoomRepository,
    user_repo: UserRepository,
    booking_id: str,
    data: dict,
) -> Booking:
    booking = get_booking(booking_repo, booking_id)
    if booking.status == "cancelled":
        raise BookingError("cannot update a cancelled booking", http_status=422)

    # Determine new time values (may or may not change)
    new_start = data.get("start_time", booking.start_time)
    new_end = data.get("end_time", booking.end_time)

    time_changed = (new_start != booking.start_time) or (new_end != booking.end_time)
    if time_changed:
        _validate_time_range(new_start, new_end)
        conflicts = check_conflicts(
            booking_repo, booking.room_id, new_start, new_end,
            exclude_booking_id=booking_id,
        )
        if conflicts:
            raise BookingError("time slot unavailable", http_status=409)

    # Apply updates
    if "start_time" in data:
        booking.start_time = data["start_time"]
    if "end_time" in data:
        booking.end_time = data["end_time"]
    if "title" in data:
        booking.title = data["title"]
    if "notes" in data:
        booking.notes = data["notes"]
    if "attendees" in data:
        booking.attendees = data["attendees"]

    booking.updated_at = _now_iso()
    return booking_repo.update(booking)

# Save booking (for check-in/out)
def save_booking(booking_repo: BookingRepository, booking: Booking) -> Booking:
    booking.updated_at = _now_iso()
    return booking_repo.update(booking)
# ---------------------------------------------------------------------------
# Task 5.8 — compute_free_slots + get_room_availability
# ---------------------------------------------------------------------------

def compute_free_slots(
    bookings: list[Booking],
    date_str: str,
    slot_minutes: int = 30,
) -> list[TimeSlot]:
    """Slice the business-hours window into free slots around confirmed bookings."""
    biz_start_str = get_business_hours_start()  # e.g. "08:00"
    biz_end_str = get_business_hours_end()       # e.g. "20:00"

    start_h, start_m = map(int, biz_start_str.split(":"))
    end_h, end_m = map(int, biz_end_str.split(":"))

    date_obj = datetime.fromisoformat(date_str).date() if "T" in date_str else datetime.strptime(date_str, "%Y-%m-%d").date()
    day_start = datetime(date_obj.year, date_obj.month, date_obj.day, start_h, start_m)
    day_end = datetime(date_obj.year, date_obj.month, date_obj.day, end_h, end_m)
    slot_delta = timedelta(minutes=slot_minutes)

    # Only confirmed bookings, sorted by start time
    confirmed = sorted(
        [b for b in bookings if b.status == "confirmed"],
        key=lambda b: _parse_dt(b.start_time),
    )

    free_slots: list[TimeSlot] = []
    cursor = day_start

    for booking in confirmed:
        b_start = _parse_dt(booking.start_time)
        b_end = _parse_dt(booking.end_time)

        # Clamp booking to business hours
        b_start = max(b_start, day_start)
        b_end = min(b_end, day_end)

        if cursor < b_start:
            slot_start = cursor
            while slot_start + slot_delta <= b_start:
                slot_end = slot_start + slot_delta
                free_slots.append(TimeSlot(
                    start_time=slot_start.isoformat(),
                    end_time=slot_end.isoformat(),
                    duration_minutes=slot_minutes,
                ))
                slot_start = slot_end

        cursor = max(cursor, b_end)

    # Remaining time after last booking
    slot_start = cursor
    while slot_start + slot_delta <= day_end:
        slot_end = slot_start + slot_delta
        free_slots.append(TimeSlot(
            start_time=slot_start.isoformat(),
            end_time=slot_end.isoformat(),
            duration_minutes=slot_minutes,
        ))
        slot_start = slot_end

    return free_slots


def get_room_availability(
    booking_repo: BookingRepository,
    room_repo: RoomRepository,
    room_id: str,
    date_str: str,
) -> AvailabilityResult:
    room = room_repo.get(room_id)
    if room is None:
        raise BookingError("room not found", http_status=404)

    bookings = booking_repo.list(room_id=room_id, date=date_str, status="confirmed")
    free_slots = compute_free_slots(bookings, date_str)

    booked_slots = [
        BookedSlot(
            start_time=b.start_time,
            end_time=b.end_time,
            booking_id=b.booking_id,
            title=b.title,
        )
        for b in bookings
        if b.status == "confirmed"
    ]

    return AvailabilityResult(
        room_id=room_id,
        date=date_str,
        free_slots=free_slots,
        booked_slots=booked_slots,
    )
