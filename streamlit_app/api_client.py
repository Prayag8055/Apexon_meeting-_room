"""HTTP client for the Apexon Room Booking API."""
from __future__ import annotations
import os
from typing import Optional
import requests
import streamlit as st

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
_TIMEOUT = 5


class APIError(Exception):
    def __init__(self, status_code: int, message: str, detail: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.detail = detail

    def __str__(self):
        return self.detail or self.message


def _raise(resp: requests.Response) -> None:
    if resp.status_code < 400:
        return
    try:
        body = resp.json()
        msg = body.get("error", resp.reason)
        detail = body.get("detail", "")
    except Exception:
        msg = resp.reason
        detail = resp.text
    raise APIError(resp.status_code, msg, detail)


def _get(path: str, params: dict | None = None):
    resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=_TIMEOUT)
    _raise(resp)
    return resp.json()


def _post(path: str, payload: dict):
    resp = requests.post(f"{BASE_URL}{path}", json=payload, timeout=_TIMEOUT)
    _raise(resp)
    return resp.json()


def _put(path: str, payload: dict):
    resp = requests.put(f"{BASE_URL}{path}", json=payload, timeout=_TIMEOUT)
    _raise(resp)
    return resp.json()


def _delete(path: str):
    resp = requests.delete(f"{BASE_URL}{path}", timeout=_TIMEOUT)
    _raise(resp)
    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()


# ── Auth ─────────────────────────────────────────────────────────────────────

def register_user_auth(name: str, email: str, password: str, department: str = "", role: str = "employee") -> dict:
    return _post("/auth/register", {"name": name, "email": email, "password": password, "department": department, "role": role})


def login_user_auth(email: str, password: str) -> dict:
    return _post("/auth/login", {"email": email, "password": password})


# ── Health & Stats ───────────────────────────────────────────────────────────

def health_check() -> dict:
    try:
        return _get("/health")
    except Exception:
        return {"status": "error"}


def get_stats() -> dict:
    try:
        return _get("/stats")
    except Exception:
        return {}


# ── Rooms ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_rooms(capacity: Optional[int] = None, floor: Optional[int] = None, amenities: Optional[list] = None) -> list[dict]:
    params: dict = {}
    if capacity: params["capacity"] = capacity
    if floor: params["floor"] = floor
    if amenities: params["amenities"] = ",".join(amenities)
    return _get("/rooms", params or None)


def create_room(payload: dict) -> dict:
    result = _post("/rooms", payload); get_rooms.clear(); return result

def update_room(room_id: str, payload: dict) -> dict:
    result = _put(f"/rooms/{room_id}", payload); get_rooms.clear(); return result

def deactivate_room(room_id: str) -> None:
    _delete(f"/rooms/{room_id}"); get_rooms.clear()

def get_room_availability(room_id: str, date: str) -> dict:
    return _get(f"/rooms/{room_id}/availability", {"date": date})


# ── Bookings ─────────────────────────────────────────────────────────────────

def get_bookings(user_id: Optional[str] = None, room_id: Optional[str] = None, date: Optional[str] = None, status: Optional[str] = None) -> list[dict]:
    params: dict = {}
    if user_id: params["user_id"] = user_id
    if room_id: params["room_id"] = room_id
    if date: params["date"] = date
    if status: params["status"] = status
    return _get("/bookings", params or None)

def create_booking(payload: dict) -> dict:
    return _post("/bookings", payload)

def update_booking(booking_id: str, payload: dict) -> dict:
    return _put(f"/bookings/{booking_id}", payload)

def cancel_booking(booking_id: str) -> dict:
    return _delete(f"/bookings/{booking_id}")


# ── Users ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_users() -> list[dict]:
    return _get("/users")

def get_user(user_id: str) -> dict:
    return _get(f"/users/{user_id}")

def create_user(payload: dict) -> dict:
    result = _post("/users", payload); get_users.clear(); return result

def get_user_bookings(user_id: str) -> list[dict]:
    return _get(f"/users/{user_id}/bookings")
