# Room Booking API Documentation

## Overview

The Room Booking API is a RESTful service built with FastAPI for managing meeting room reservations. It provides endpoints for room management, booking operations, user management, and availability checking.

**Base URL**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)  
**OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Business Rules

- **Business Hours**: 08:00 - 20:00 (configurable via environment variables)
- **Minimum Booking Duration**: 15 minutes
- **Time Slot Granularity**: 30 minutes
- **Room Status**: `active` | `inactive`
- **Booking Status**: `confirmed` | `cancelled`

## Error Handling

All error responses follow this format:
```json
{
  "error": "short_error_code",
  "detail": "Human-readable error description"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `500` - Internal Server Error

---

## Health Check

### Check API Health
```http
GET /health
```

**Response**:
```json
{
  "status": "ok"
}
```

---

## Rooms

### List Rooms
```http
GET /rooms?capacity={int}&floor={int}&amenities={string}
```

**Query Parameters**:
- `capacity` (optional) - Filter by minimum capacity
- `floor` (optional) - Filter by floor number  
- `amenities` (optional) - Comma-separated amenities list

**Response**:
```json
[
  {
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Conference Room A",
    "floor": 1,
    "capacity": 10,
    "amenities": ["projector", "whiteboard"],
    "status": "active",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
]
```

### Create Room
```http
POST /rooms
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "Conference Room A",
  "floor": 1,
  "capacity": 10,
  "amenities": ["projector", "whiteboard"],
  "status": "active"
}
```

**Required Fields**: `name`, `capacity`

**Response**: `201 Created`
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Conference Room A",
  "floor": 1,
  "capacity": 10,
  "amenities": ["projector", "whiteboard"],
  "status": "active",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

**Validation Errors**:
- `422` - `name` is required
- `422` - `capacity` must be at least 1
- `422` - `status` must be 'active' or 'inactive'

### Get Room
```http
GET /rooms/{room_id}
```

**Response**: `200 OK` with room object or `404 Not Found`

### Update Room
```http
PUT /rooms/{room_id}
Content-Type: application/json
```

**Request Body** (partial update):
```json
{
  "name": "Updated Room Name",
  "capacity": 15
}
```

**Response**: `200 OK` with updated room object

### Deactivate Room
```http
DELETE /rooms/{room_id}
```

**Response**: `204 No Content`

**Note**: This performs a soft delete by setting status to `inactive`

### Get Room Availability
```http
GET /rooms/{room_id}/availability?date=2024-01-15
```

**Query Parameters**:
- `date` (required) - Date in YYYY-MM-DD format

**Response**:
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2024-01-15",
  "free_slots": [
    {
      "start_time": "2024-01-15T08:00:00",
      "end_time": "2024-01-15T08:30:00",
      "duration_minutes": 30
    },
    {
      "start_time": "2024-01-15T08:30:00",
      "end_time": "2024-01-15T09:00:00",
      "duration_minutes": 30
    }
  ],
  "booked_slots": [
    {
      "start_time": "2024-01-15T09:00:00",
      "end_time": "2024-01-15T10:00:00",
      "booking_id": "660e8400-e29b-41d4-a716-446655440000",
      "title": "Team Meeting"
    }
  ]
}
```

---

## Bookings

### List Bookings
```http
GET /bookings?user_id={string}&room_id={string}&date={string}&status={string}
```

**Query Parameters** (all optional):
- `user_id` - Filter by user ID
- `room_id` - Filter by room ID
- `date` - Filter by date (YYYY-MM-DD)
- `status` - Filter by status (`confirmed` | `cancelled`)

**Response**: Array of booking objects

### Create Booking
```http
POST /bookings
Content-Type: application/json
```

**Request Body**:
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "770e8400-e29b-41d4-a716-446655440000",
  "title": "Team Meeting",
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T10:00:00",
  "attendees": ["john@example.com", "jane@example.com"],
  "notes": "Weekly sync meeting"
}
```

**Required Fields**: `room_id`, `user_id`, `title`, `start_time`, `end_time`

**Response**: `201 Created` with booking object

**Validation Errors**:
- `404` - Room not found
- `404` - User not found
- `409` - Time slot unavailable (conflict)
- `422` - End time must be after start time
- `422` - Minimum booking duration is 15 minutes
- `422` - Room is not available for booking

### Get Booking
```http
GET /bookings/{booking_id}
```

**Response**: `200 OK` with booking object or `404 Not Found`

### Update Booking
```http
PUT /bookings/{booking_id}
Content-Type: application/json
```

**Request Body** (partial update):
```json
{
  "title": "Updated Meeting Title",
  "start_time": "2024-01-15T10:00:00",
  "end_time": "2024-01-15T11:00:00"
}
```

**Response**: `200 OK` with updated booking object

**Validation**: Same as create booking, plus:
- `409` - Time slot unavailable for new time
- `422` - Cannot update a cancelled booking

### Cancel Booking
```http
DELETE /bookings/{booking_id}
```

**Response**: `200 OK` with cancelled booking object

**Errors**:
- `404` - Booking not found
- `409` - Booking is already cancelled

---

## Users

### List Users
```http
GET /users
```

**Response**: Array of user objects
```json
[
  {
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### Create User
```http
POST /users
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering"
}
```

**Required Fields**: `name`, `email`

**Response**: `201 Created` with user object

**Validation Errors**:
- `409` - Email already registered
- `422` - Name is required
- `422` - Invalid email format

### Get User
```http
GET /users/{user_id}
```

**Response**: `200 OK` with user object or `404 Not Found`

### Get User Bookings
```http
GET /users/{user_id}/bookings
```

**Response**: Array of booking objects for the user

---

## Data Models

### Room
```json
{
  "room_id": "string (UUID)",
  "name": "string",
  "floor": "integer",
  "capacity": "integer (min: 1)",
  "amenities": ["string"],
  "status": "active | inactive",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)"
}
```

### Booking
```json
{
  "booking_id": "string (UUID)",
  "room_id": "string (UUID)",
  "user_id": "string (UUID)",
  "title": "string",
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)",
  "status": "confirmed | cancelled",
  "attendees": ["string"],
  "notes": "string",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)"
}
```

### User
```json
{
  "user_id": "string (UUID)",
  "name": "string",
  "email": "string (email format)",
  "department": "string",
  "created_at": "string (ISO datetime)"
}
```

### TimeSlot
```json
{
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)",
  "duration_minutes": "integer"
}
```

### BookedSlot
```json
{
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)",
  "booking_id": "string (UUID)",
  "title": "string"
}
```

### AvailabilityResult
```json
{
  "room_id": "string (UUID)",
  "date": "string (YYYY-MM-DD)",
  "free_slots": ["TimeSlot"],
  "booked_slots": ["BookedSlot"]
}
```

---

## Configuration

### Environment Variables
```bash
DB_PATH=bookings.db                # SQLite database file path
BUSINESS_HOURS_START=08:00         # Business day start time (HH:MM)
BUSINESS_HOURS_END=20:00           # Business day end time (HH:MM)
```

---

## Examples

### Complete Booking Flow

1. **List available rooms**:
```bash
curl -X GET "http://localhost:8000/rooms?capacity=5"
```

2. **Check room availability**:
```bash
curl -X GET "http://localhost:8000/rooms/550e8400-e29b-41d4-a716-446655440000/availability?date=2024-01-15"
```

3. **Create a booking**:
```bash
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "770e8400-e29b-41d4-a716-446655440000",
    "title": "Project Review",
    "start_time": "2024-01-15T14:00:00",
    "end_time": "2024-01-15T15:00:00"
  }'
```

4. **Update booking**:
```bash
curl -X PUT "http://localhost:8000/bookings/660e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2024-01-15T15:00:00",
    "end_time": "2024-01-15T16:00:00"
  }'
```

5. **Cancel booking**:
```bash
curl -X DELETE "http://localhost:8000/bookings/660e8400-e29b-41d4-a716-446655440000"
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Versioning

This is version 1.0 of the API. Future versions will maintain backward compatibility where possible.