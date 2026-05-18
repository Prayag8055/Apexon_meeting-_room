from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

try:
    from ..core.models import Room, Booking, User , LocationWiseRoom
except ImportError:
    from core.models import Room, Booking, User, LocationWiseRoom  # type: ignore


class RoomRepository(ABC):
    @abstractmethod
    def get(self, room_id: str) -> Optional[LocationWiseRoom]: ...

    @abstractmethod
    def list(self, capacity: int = None, amenities: list[str] = None, floor: int = None) -> list[LocationWiseRoom]: ...

    @abstractmethod
    def create(self, room: LocationWiseRoom) -> LocationWiseRoom: ...

    @abstractmethod
    def update(self, room: LocationWiseRoom) -> LocationWiseRoom: ...

    @abstractmethod
    def delete(self, room_id: str) -> None: ...




class BookingRepository(ABC):
    @abstractmethod
    def get(self, booking_id: str) -> Optional[Booking]: ...

    @abstractmethod
    def list(self, user_id: str = None, room_id: str = None, date: str = None, status: str = None) -> list[Booking]: ...

    @abstractmethod
    def create(self, booking: Booking) -> Booking: ...

    @abstractmethod
    def update(self, booking: Booking) -> Booking: ...

    @abstractmethod
    def cancel(self, booking_id: str) -> Booking: ...

    @abstractmethod
    def get_overlapping(self, room_id: str, start_time: str, end_time: str, exclude_booking_id: str = None) -> list[Booking]: ...


class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def list(self) -> list[User]: ...

    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def update(self, user: User) -> User: ...
