from dataclasses import dataclass, field


@dataclass
class Room:
    room_id: str
    name: str
    floor: int
    capacity: int
    amenities: list[str]
    status: str
    created_at: str
    updated_at: str


@dataclass
class Booking:
    booking_id: str
    room_id: str
    user_id: str
    title: str
    start_time: str
    end_time: str
    status: str
    attendees: list[str]
    notes: str
    created_at: str
    updated_at: str


@dataclass
class User:
    user_id: str
    name: str
    email: str
    department: str
    created_at: str


@dataclass
class TimeSlot:
    start_time: str
    end_time: str
    duration_minutes: int


@dataclass
class BookedSlot:
    start_time: str
    end_time: str
    booking_id: str
    title: str


@dataclass
class AvailabilityResult:
    room_id: str
    date: str
    free_slots: list[TimeSlot] = field(default_factory=list)
    booked_slots: list[BookedSlot] = field(default_factory=list)


class BookingError(Exception):
    def __init__(self, message: str, http_status: int = 400, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.detail = detail
