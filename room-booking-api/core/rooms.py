import uuid
from datetime import datetime

try:
    from .models import Room, BookingError , LocationWiseRoom
    from ..db.base import RoomRepository
except ImportError:
    from core.models import Room, BookingError , LocationWiseRoom # type: ignore
    from db.base import RoomRepository  # type: ignore


def get_room(repo: RoomRepository, room_id: str) -> LocationWiseRoom:
    room = repo.get(room_id)
    if room is None:
        raise BookingError("room not found", http_status=404)
    return room


def list_rooms(
    repo: RoomRepository,
    capacity: int = None,
    amenities: list[str] = None,
    floor: int = None,
) -> list[LocationWiseRoom]:
    return repo.list(capacity=capacity, amenities=amenities, floor=floor)


def _validate_room_data(data: dict, require_name: bool = True) -> None:
    name = data.get("name")
    if require_name or "name" in data:
        if not name or not isinstance(name, str) or not name.strip():
            raise BookingError("name is required", http_status=422)

    capacity = data.get("capacity")
    if capacity is not None:
        if not isinstance(capacity, int) or capacity < 1:
            raise BookingError("capacity must be at least 1", http_status=422)

    status = data.get("status")
    if status is not None and status not in ("active", "inactive"):
        raise BookingError("invalid status", http_status=422)


def create_room(repo: RoomRepository, data: dict) -> LocationWiseRoom:
    _validate_room_data(data, require_name=True)

    if data.get("capacity") is None:
        raise BookingError("capacity must be at least 1", http_status=422)

    now = datetime.utcnow().isoformat()
    room = LocationWiseRoom(
        room_id=str(uuid.uuid4()),
        name=data["name"].strip(),
        floor=data.get("floor", 1),
        capacity=data["capacity"],
        amenities=data.get("amenities", []),
        status=data.get("status", "active"),
        created_at=now,
        updated_at=now,
    )
    return repo.create(room)


def update_room(repo: RoomRepository, room_id: str, data: dict) -> LocationWiseRoom:
    room = repo.get(room_id)
    if room is None:
        raise BookingError("room not found", http_status=404)

    _validate_room_data(data, require_name=False)

    if "name" in data:
        room.name = data["name"].strip()
    if "floor" in data:
        room.floor = data["floor"]
    if "capacity" in data:
        room.capacity = data["capacity"]
    if "amenities" in data:
        room.amenities = data["amenities"]
    if "status" in data:
        room.status = data["status"]

    room.updated_at = datetime.utcnow().isoformat()
    return repo.update(room)


def deactivate_room(repo: RoomRepository, room_id: str) -> None:
    room = repo.get(room_id)
    if room is None:
        raise BookingError("room not found", http_status=404)

    room.status = "inactive"
    room.updated_at = datetime.utcnow().isoformat()
    repo.update(room)
