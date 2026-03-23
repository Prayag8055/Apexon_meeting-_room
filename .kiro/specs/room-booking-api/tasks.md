# Implementation Plan: Room Booking API

## Overview

Incremental build of the Room Booking API in Python. Phase 1 targets FastAPI + SQLite for local development. Phase 2 (optional) adds Lambda + DynamoDB for AWS production. The repository pattern keeps business logic identical across both phases — only the adapter changes.

## Tasks

- [x] 1. Project scaffolding
  - Create the full directory structure: `core/`, `db/`, `fastapi_app/`, `shared/`, `tests/`
  - Create `requirements.txt` with all Phase 1 and shared dependencies (`fastapi`, `uvicorn`, `pydantic`, `hypothesis`, `pytest`, `python-dateutil`, `boto3`)
  - Create `shared/config.py` — reads from environment variables (Phase 1); stub `get_parameter_value()` for Phase 2 SSM path
  - Create `shared/utils.py` — implement `response()`, `json_default()`, `parse_event()`, `normalize_path()`
  - Create empty `__init__.py` files in each package directory
  - _Requirements: 8.1_

- [x] 2. Core data models
  - [x] 2.1 Implement `core/models.py`
    - Define `Room`, `Booking`, `User` as `@dataclass` with all fields from the design
    - Add `BookingError` exception class
    - Add `AvailabilityResult`, `TimeSlot` dataclasses for availability responses
    - _Requirements: 1.1, 2.1, 3.1, 6.1, 6.2_

  - [ ]* 2.2 Write property test for data model validation (Property 8, Property 9)
    - **Property 8: Booking Duration Validation** — any request with `end_time - start_time < 15 min` or `end_time <= start_time` must be rejected
    - **Property 9: Invalid Room Capacity Rejected** — any room with `capacity < 1` must be rejected
    - **Validates: Requirements 6.1, 6.2, 1.7**

- [x] 3. Abstract repository interfaces
  - [x] 3.1 Implement `db/base.py`
    - Define `RoomRepository`, `BookingRepository`, `UserRepository` as `ABC` with all abstract methods from the design
    - Include `get_overlapping()` on `BookingRepository` for conflict detection
    - _Requirements: 1.1, 2.1, 3.1_

- [x] 4. SQLite adapter
  - [x] 4.1 Implement `db/sqlite_adapter.py`
    - Implement `SQLiteRoomRepo`, `SQLiteBookingRepo`, `SQLiteUserRepo` extending the abstract base classes
    - Include `_init_schema()` that creates all three tables and indexes on first connection (DDL from design)
    - Serialize/deserialize `amenities` and `attendees` JSON columns
    - Implement `get_overlapping()` using the SQL overlap condition: `start_time < ? AND end_time > ?`
    - _Requirements: 1.1–1.6, 2.1–2.6, 3.1–3.4_

  - [ ]* 4.2 Write property test for SQLite round-trip (Property 11)
    - **Property 11: Create-Then-Retrieve Round Trip** — for any valid entity created via the repo, retrieving by ID returns identical fields
    - **Validates: Requirements 1.3, 2.3, 3.3**

- [x] 5. Core business logic
  - [x] 5.1 Implement `core/rooms.py`
    - `get_room(room_id)`, `list_rooms(capacity, amenities, floor)`, `create_room(data)`, `update_room(room_id, data)`, `deactivate_room(room_id)`
    - Validate `capacity >= 1`, `status` enum, non-empty `name`
    - Soft-delete sets `status = "inactive"`
    - _Requirements: 1.1–1.7_

  - [ ]* 5.2 Write property test for soft delete (Property 13)
    - **Property 13: Soft Delete Sets Status to Inactive** — after DELETE, GET must return the room with `status = "inactive"`, not 404
    - **Validates: Requirements 1.6**

  - [x] 5.3 Implement `core/users.py`
    - `get_user(user_id)`, `get_user_by_email(email)`, `list_users()`, `create_user(data)`
    - Validate non-empty `name`, valid email format, unique email (raise `BookingError` on duplicate)
    - _Requirements: 3.1–3.8_

  - [ ]* 5.4 Write property test for duplicate email rejection (Property 14)
    - **Property 14: Duplicate Email Rejected** — second registration with same email must raise `BookingError` regardless of other fields
    - **Validates: Requirements 3.8**

  - [x] 5.5 Implement `check_conflicts()` in `core/bookings.py`
    - Accept `room_id`, `start_time`, `end_time`, optional `exclude_booking_id`
    - Call `repo.get_overlapping()`, filter out cancelled bookings and the excluded booking
    - Return list of conflicting confirmed bookings
    - _Requirements: 5.1–5.5_

  - [ ]* 5.6 Write property tests for conflict detection (Properties 1, 2, 3, 4)
    - **Property 1: No Double Booking** — after a booking exists, `check_conflicts` for the same slot returns non-empty
    - **Property 2: Conflict Symmetry** — if A conflicts with B then B conflicts with A
    - **Property 3: Cancelled Bookings Are Invisible** — cancelled bookings never appear in conflict results
    - **Property 4: Reschedule Excludes Self** — rescheduling to own slot succeeds (exclude_booking_id works)
    - **Validates: Requirements 5.1–5.5**
    - Place in `tests/test_conflicts.py`

  - [x] 5.7 Implement `create_booking()`, `cancel_booking()`, `update_booking()` in `core/bookings.py`
    - `create_booking`: validate room active, user exists, time range, call `check_conflicts`, persist
    - `cancel_booking`: guard against double-cancel (raise `BookingError` with 409)
    - `update_booking`: support reschedule by passing `exclude_booking_id` to `check_conflicts`
    - _Requirements: 2.1–2.6, 5.1–5.5, 6.1–6.3_

  - [x] 5.8 Implement `get_room_availability()` and `compute_free_slots()` in `core/bookings.py`
    - `compute_free_slots(bookings, date, slot_minutes=30)`: implement the pseudocode algorithm from the design
    - `get_room_availability(room_id, date)`: fetch room + bookings, call `compute_free_slots`, return `AvailabilityResult`
    - Business hours: 08:00–20:00
    - _Requirements: 4.1–4.6_

  - [ ]* 5.9 Write property tests for availability computation (Properties 5, 6, 7)
    - **Property 5: Free Slots Never Overlap** — for any booking list, consecutive free slots satisfy `slots[i].end_time <= slots[i+1].start_time`
    - **Property 6: Free + Booked Slots Cover Full Business Day** — union covers 08:00–20:00 without gaps > slot duration
    - **Property 7: Booked Slots Contain Only Confirmed Bookings** — cancelled bookings must not appear in booked_slots
    - **Validates: Requirements 4.3–4.6, 5.5**
    - Place in `tests/test_availability.py`

- [x] 6. Checkpoint — core logic complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. FastAPI application
  - [-] 7.1 Implement `fastapi_app/main.py` — app factory and dependency injection
    - `create_app(room_repo, booking_repo, user_repo)` factory function
    - Wire SQLite adapters as defaults via `shared/config.py` (`DB_PATH` env var)
    - Add global exception handler for `BookingError` → appropriate HTTP status + `{"error": ..., "detail": ...}` body
    - _Requirements: 8.1_

  - [-] 7.2 Implement Rooms routes in `fastapi_app/main.py`
    - `GET /rooms`, `POST /rooms`, `GET /rooms/{room_id}`, `PUT /rooms/{room_id}`, `DELETE /rooms/{room_id}`
    - `GET /rooms/{room_id}/availability?date=YYYY-MM-DD`
    - Map `BookingError` codes to 404 / 409 / 422 per the error table in the design
    - _Requirements: 1.1–1.7, 4.1–4.6_

  - [-] 7.3 Implement Bookings routes in `fastapi_app/main.py`
    - `GET /bookings`, `POST /bookings`, `GET /bookings/{booking_id}`, `PUT /bookings/{booking_id}`, `DELETE /bookings/{booking_id}`
    - Return 201 on create, 409 on conflict, 422 on validation errors
    - _Requirements: 2.1–2.6, 5.1–5.5, 6.1–6.3_

  - [ ] 7.4 Implement Users routes and health check in `fastapi_app/main.py`
    - `GET /users`, `POST /users`, `GET /users/{user_id}`, `GET /users/{user_id}/bookings`
    - `GET /health` → `{"status": "ok"}`
    - _Requirements: 3.1–3.8_

- [ ] 8. Integration tests
  - [ ] 8.1 Implement `tests/test_api.py`
    - Use FastAPI `TestClient` with an in-memory SQLite database (`:memory:`)
    - Test full CRUD cycle for rooms, bookings, and users
    - Test conflict detection end-to-end: create two overlapping bookings, assert second returns 409
    - Test availability endpoint before and after creating bookings
    - Test all error scenarios from the error table (404, 409, 422)
    - _Requirements: 1.1–1.7, 2.1–2.6, 3.1–3.8, 4.1–4.6, 5.1–5.5_

  - [ ]* 8.2 Write property test for list filters (Property 10)
    - **Property 10: List Filters Return Only Matching Records** — querying with any filter returns only records satisfying the predicate
    - **Validates: Requirements 1.2, 2.2**

  - [ ]* 8.3 Write property test for error response shape (Property 12)
    - **Property 12: Error Responses Always Contain Required Fields** — any 4xx/5xx response body contains both `"error"` and `"detail"` fields
    - **Validates: Requirements 8.1**

- [ ] 9. Final checkpoint — all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 10. Lambda handler stub (Phase 2 prep)
  - [ ]* 10.1 Implement `lambda_handler.py`
    - Follow the routing pattern from `sample_lambda_as_api.py`
    - Use `parse_event()` and `normalize_path()` from `shared/utils.py` to normalize API Gateway v1/v2 events
    - Pure Python `if/elif` dispatch to the same core functions used by FastAPI
    - Wire `DynamoRoomRepo`, `DynamoBookingRepo`, `DynamoUserRepo` (from stub adapter)
    - _Requirements: Phase 2 deployment_

  - [ ]* 10.2 Implement `db/dynamo_adapter.py` stub
    - Define `DynamoRoomRepo`, `DynamoBookingRepo`, `DynamoUserRepo` extending the abstract base classes
    - Raise `NotImplementedError` on all methods (stub for Phase 2 implementation)
    - _Requirements: Phase 2 deployment_

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Phase 2 tasks (10.*) require AWS credentials and DynamoDB tables — skip for local dev
- Property tests use `hypothesis`; run with `pytest tests/test_conflicts.py tests/test_availability.py`
- Integration tests use FastAPI `TestClient` with in-memory SQLite — no external services needed
- Each property test references a numbered property from the design document for traceability
