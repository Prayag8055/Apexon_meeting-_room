import re
import uuid
from datetime import datetime

try:
    from .models import User, Booking, BookingError
    from ..db.base import UserRepository, BookingRepository
except ImportError:
    from core.models import User, Booking, BookingError  # type: ignore
    from db.base import UserRepository, BookingRepository  # type: ignore


def get_user(repo: UserRepository, user_id: str) -> User:
    user = repo.get(user_id)
    if user is None:
        raise BookingError("user not found", http_status=404)
    return user


def get_user_by_email(repo: UserRepository, email: str) -> User:
    user = repo.get_by_email(email)
    if user is None:
        raise BookingError("user not found", http_status=404)
    return user


def list_users(repo: UserRepository) -> list[User]:
    return repo.list()


def create_user(repo: UserRepository, data: dict) -> User:
    name = data.get("name", "")
    if not name or not str(name).strip():
        raise BookingError("name is required", http_status=422)

    email = data.get("email", "")
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+', str(email)):
        raise BookingError("invalid email", http_status=422)

    existing = repo.get_by_email(email)
    if existing is not None:
        raise BookingError("email already registered", http_status=409)

    user = User(
        user_id=str(uuid.uuid4()),
        name=str(name).strip(),
        email=email,
        department=data.get("department", ""),
        created_at=datetime.utcnow().isoformat(),
    )
    return repo.create(user)


def get_user_bookings(booking_repo: BookingRepository, user_id: str) -> list[Booking]:
    return booking_repo.list(user_id=user_id)
