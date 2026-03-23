import re
import uuid
from datetime import datetime

import bcrypt

try:
    from .models import User, Booking, BookingError
    from ..db.base import UserRepository, BookingRepository
except ImportError:
    from core.models import User, Booking, BookingError  # type: ignore
    from db.base import UserRepository, BookingRepository  # type: ignore


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


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


def register_user(repo: UserRepository, data: dict) -> User:
    """Register a new user with email + password."""
    name = data.get("name", "")
    if not name or not str(name).strip():
        raise BookingError("name is required", http_status=422)

    email = data.get("email", "")
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+', str(email)):
        raise BookingError("invalid email", http_status=422)

    password = data.get("password", "")
    if not password or len(password) < 4:
        raise BookingError("password must be at least 4 characters", http_status=422)

    existing = repo.get_by_email(email)
    if existing is not None:
        raise BookingError("email already registered", http_status=409)

    role = data.get("role", "employee")
    if role not in ("admin", "employee"):
        role = "employee"

    user = User(
        user_id=str(uuid.uuid4()),
        name=str(name).strip(),
        email=email.strip().lower(),
        department=data.get("department", ""),
        role=role,
        password_hash=_hash_password(password),
        created_at=datetime.utcnow().isoformat(),
    )
    return repo.create(user)


def login_user(repo: UserRepository, email: str, password: str) -> User:
    """Authenticate user by email + password."""
    user = repo.get_by_email(email.strip().lower())
    if user is None:
        raise BookingError("invalid email or password", http_status=401)
    if not user.password_hash:
        raise BookingError("account not set up — please contact admin", http_status=401)
    if not _verify_password(password, user.password_hash):
        raise BookingError("invalid email or password", http_status=401)
    return user


def create_user(repo: UserRepository, data: dict) -> User:
    """Admin-created user (backward compat, sets default password)."""
    return register_user(repo, data)


def get_user_bookings(booking_repo: BookingRepository, user_id: str) -> list[Booking]:
    return booking_repo.list(user_id=user_id)
