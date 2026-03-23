# Requirements Document

## Introduction

A backend API for managing room reservations in an office or facility setting. The system operates in two deployment phases: Phase 1 runs locally using FastAPI + SQLite for development, and Phase 2 deploys to AWS using Lambda + API Gateway + DynamoDB for production. The API manages three core domains: rooms (physical spaces with capacity and amenities), bookings (time-bounded reservations with conflict detection), and users (people who make reservations). A repository pattern abstracts the storage layer so business logic is identical across both phases.

## Glossary

- **API**: The Room Booking REST API service
- **Room**: A physical space with capacity, floor, amenities, and active/inactive status
- **Booking**: A time-bounded reservation linking a User to a Room
- **User**: A person who creates bookings, identified by a unique email address
- **Repository**: An abstract storage interface implemented by either the SQLite adapter (Phase 1) or the DynamoDB adapter (Phase 2)
- **Conflict**: Two confirmed bookings for the same room whose time intervals overlap
- **Availability**: The set of free time slots for a room on a given date within business hours
- **Business_Day**: The time window from BUSINESS_HOURS_START (08:00) to BUSINESS_HOURS_END (20:00)
- **Slot**: A fixed-duration time interval used to represent availability (default 30 minutes)
- **Validator**: The component responsible for enforcing data integrity rules before persistence
- **Conflict_Checker**: The component that detects overlapping confirmed bookings for a room
- **Availability_Calculator**: The component that computes free and booked slots for a room on a date

---

## Requirements

### Requirement 1: Room Management

**User Story:** As a facility manager, I want to create, read, update, and deactivate rooms, so that I can maintain an accurate inventory of bookable spaces.

#### Acceptance Criteria

1. WHEN a POST /rooms request is received with valid room data, THE API SHALL create a new room record and return it with HTTP 201.
2. WHEN a GET /rooms request is received, THE API SHALL return the list of all rooms, optionally filtered by `capacity`, `floor`, or `amenities` query parameters.
3. WHEN a GET /rooms/{room_id} request is received for an existing room, THE API SHALL return the room details with HTTP 200.
4. IF a GET /rooms/{room_id} request is received for a non-existent room_id, THEN THE API SHALL return HTTP 404 with error `"room not found"`.
5. WHEN a PUT /rooms/{room_id} request is received with valid update data, THE API SHALL update the room record and return the updated room with HTTP 200.
6. WHEN a DELETE /rooms/{room_id} request is received, THE API SHALL set the room status to `"inactive"` (soft delete) and return HTTP 200.
7. THE Validator SHALL reject any room where `capacity` is less than 1 with HTTP 422.
8. THE Validator SHALL reject any room where `name` is empty with HTTP 422.
9. THE Validator SHALL reject any room where `status` is not one of `"active"` or `"inactive"` with HTTP 422.

---

### Requirement 2: Booking Management

**User Story:** As a user, I want to create, view, reschedule, and cancel bookings, so that I can reserve rooms for meetings and manage my reservations.

#### Acceptance Criteria

1. WHEN a POST /bookings request is received with valid booking data, THE API SHALL create a new booking with `status = "confirmed"` and return it with HTTP 201.
2. WHEN a GET /bookings request is received, THE API SHALL return bookings optionally filtered by `user_id`, `room_id`, `date`, or `status` query parameters.
3. WHEN a GET /bookings/{booking_id} request is received for an existing booking, THE API SHALL return the booking details with HTTP 200.
4. IF a GET /bookings/{booking_id} request is received for a non-existent booking_id, THEN THE API SHALL return HTTP 404 with error `"booking not found"`.
5. WHEN a PUT /bookings/{booking_id} request is received with valid update data, THE API SHALL update the booking (reschedule) and return the updated booking with HTTP 200.
6. WHEN a DELETE /bookings/{booking_id} request is received for a confirmed booking, THE API SHALL set the booking status to `"cancelled"` and return HTTP 200.
7. IF a DELETE /bookings/{booking_id} request is received for an already-cancelled booking, THEN THE API SHALL return HTTP 409 with error `"booking is already cancelled"`.

---

### Requirement 3: User Management

**User Story:** As a system administrator, I want to register and retrieve users, so that bookings can be associated with identifiable people.

#### Acceptance Criteria

1. WHEN a POST /users request is received with valid user data, THE API SHALL create a new user record and return it with HTTP 201.
2. WHEN a GET /users request is received, THE API SHALL return the list of all registered users with HTTP 200.
3. WHEN a GET /users/{user_id} request is received for an existing user, THE API SHALL return the user profile with HTTP 200.
4. IF a GET /users/{user_id} request is received for a non-existent user_id, THEN THE API SHALL return HTTP 404 with error `"user not found"`.
5. WHEN a GET /users/{user_id}/bookings request is received for an existing user, THE API SHALL return all bookings associated with that user with HTTP 200.
6. THE Validator SHALL reject any user registration where `name` is empty with HTTP 422.
7. THE Validator SHALL reject any user registration where `email` is not a valid email format with HTTP 422.
8. IF a POST /users request is received with an email that is already registered, THEN THE API SHALL return HTTP 409 with error `"email already registered"`.

---

### Requirement 4: Room Availability

**User Story:** As a user, I want to query the available time slots for a room on a specific date, so that I can choose a suitable time for my booking.

#### Acceptance Criteria

1. WHEN a GET /rooms/{room_id}/availability request is received with a valid `date` query parameter, THE Availability_Calculator SHALL return a response containing `free_slots` and `booked_slots` for that date with HTTP 200.
2. IF a GET /rooms/{room_id}/availability request is received for a non-existent room_id, THEN THE API SHALL return HTTP 404 with error `"room not found"`.
3. THE Availability_Calculator SHALL compute `free_slots` as fixed-duration intervals (default 30 minutes) covering all unbooked time within the Business_Day.
4. THE Availability_Calculator SHALL compute `booked_slots` from all confirmed bookings for the room on the given date.
5. THE Availability_Calculator SHALL ensure that `free_slots` and `booked_slots` together cover the entire Business_Day without gaps.
6. THE Availability_Calculator SHALL ensure that no time interval appears in both `free_slots` and `booked_slots`.
7. WHEN a room has no bookings on a date, THE Availability_Calculator SHALL return `free_slots` covering the entire Business_Day and an empty `booked_slots` list.

---

### Requirement 5: Conflict Detection

**User Story:** As a user, I want the system to prevent double-booking of rooms, so that I can trust that my confirmed reservation will not be overridden.

#### Acceptance Criteria

1. WHEN a POST /bookings request is received and a confirmed booking for the same room already overlaps the requested time interval, THE Conflict_Checker SHALL reject the request with HTTP 409 and error `"time slot unavailable"`.
2. WHEN a PUT /bookings/{booking_id} request is received to reschedule a booking and the new time interval overlaps another confirmed booking for the same room, THE Conflict_Checker SHALL reject the request with HTTP 409 and error `"time slot unavailable"`.
3. THE Conflict_Checker SHALL consider two time intervals as overlapping if and only if `start_A < end_B AND start_B < end_A`.
4. WHEN checking conflicts during a reschedule, THE Conflict_Checker SHALL exclude the booking being rescheduled from the conflict check.
5. THE Conflict_Checker SHALL only consider bookings with `status = "confirmed"` when detecting conflicts; cancelled bookings SHALL be ignored.

---

### Requirement 6: Booking Validation Rules

**User Story:** As a system, I want to enforce booking constraints, so that only valid reservations are accepted.

#### Acceptance Criteria

1. THE Validator SHALL reject any booking where `end_time` is not strictly greater than `start_time` with HTTP 422 and error `"end_time must be after start_time"`.
2. THE Validator SHALL reject any booking where the duration (`end_time - start_time`) is less than 15 minutes with HTTP 422 and error `"minimum booking duration is 15 minutes"`.
3. IF a booking is requested for a room with `status = "inactive"`, THEN THE Validator SHALL reject the request with HTTP 422 and error `"room is not available for booking"`.
4. IF a booking is requested with a `user_id` that does not reference an existing user, THEN THE Validator SHALL reject the request with HTTP 404 and error `"user not found"`.
5. IF a booking is requested with a `room_id` that does not reference an existing room, THEN THE Validator SHALL reject the request with HTTP 404 and error `"room not found"`.
6. THE Validator SHALL reject any request with a missing required field with HTTP 422 and error `"field '{name}' is required"`.

---

### Requirement 7: Storage Abstraction

**User Story:** As a developer, I want the storage layer to be fully abstracted behind a repository interface, so that the SQLite adapter (Phase 1) can be swapped for the DynamoDB adapter (Phase 2) without modifying any business logic.

#### Acceptance Criteria

1. THE Repository SHALL expose abstract interfaces `RoomRepository`, `BookingRepository`, and `UserRepository` that define all storage operations.
2. THE API SHALL wire business logic exclusively to the abstract repository interfaces, with no direct references to SQLite or DynamoDB in `core/`.
3. WHERE Phase 1 is active, THE Repository SHALL implement all abstract interfaces using SQLite.
4. WHERE Phase 2 is active, THE Repository SHALL implement all abstract interfaces using DynamoDB.
5. WHEN the storage adapter is swapped from SQLite to DynamoDB, THE API SHALL continue to pass all functional tests without modification to `core/`, `fastapi_app/`, or `lambda_handler.py`.

---

### Requirement 8: Error Responses

**User Story:** As an API consumer, I want all error responses to follow a consistent JSON structure, so that I can handle errors programmatically.

#### Acceptance Criteria

1. WHEN THE API returns any error response, THE API SHALL include a JSON body with an `"error"` field containing a short error code and a `"detail"` field containing a human-readable description.
2. THE API SHALL return HTTP 404 for all not-found conditions.
3. THE API SHALL return HTTP 409 for all conflict conditions (time slot unavailable, duplicate email, already-cancelled booking).
4. THE API SHALL return HTTP 422 for all validation failures.
5. IF an unexpected internal error occurs, THEN THE API SHALL return HTTP 500 with error `"internal server error"`.

---

### Requirement 9: Health Check

**User Story:** As an operator, I want a health check endpoint, so that I can verify the service is running in both Phase 1 and Phase 2 deployments.

#### Acceptance Criteria

1. WHEN a GET /health request is received, THE API SHALL return HTTP 200 with a response indicating the service is healthy.
2. THE API SHALL serve the GET /health endpoint without requiring authentication or any query parameters.
