# Room Booking API - Quick Reference

## Base URL
```
http://localhost:8000
```

## Health Check
```bash
GET /health
```

## Rooms

### List Rooms
```bash
GET /rooms
GET /rooms?capacity=10&floor=1&amenities=projector,whiteboard
```

### Create Room
```bash
POST /rooms
{
  "name": "Conference Room A",
  "floor": 1,
  "capacity": 10,
  "amenities": ["projector", "whiteboard"],
  "status": "active"
}
```

### Get Room
```bash
GET /rooms/{room_id}
```

### Update Room
```bash
PUT /rooms/{room_id}
{
  "name": "Updated Room Name",
  "capacity": 15
}
```

### Deactivate Room
```bash
DELETE /rooms/{room_id}
```

### Get Room Availability
```bash
GET /rooms/{room_id}/availability?date=2024-01-15
```

## Bookings

### List Bookings
```bash
GET /bookings
GET /bookings?user_id={uuid}&room_id={uuid}&date=2024-01-15&status=confirmed
```

### Create Booking
```bash
POST /bookings
{
  "room_id": "uuid",
  "user_id": "uuid",
  "title": "Team Meeting",
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T10:00:00",
  "attendees": ["john@example.com"],
  "notes": "Weekly sync"
}
```

### Get Booking
```bash
GET /bookings/{booking_id}
```

### Update Booking
```bash
PUT /bookings/{booking_id}
{
  "title": "Updated Meeting",
  "start_time": "2024-01-15T10:00:00",
  "end_time": "2024-01-15T11:00:00"
}
```

### Cancel Booking
```bash
DELETE /bookings/{booking_id}
```

## Users

### List Users
```bash
GET /users
```

### Create User
```bash
POST /users
{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering"
}
```

### Get User
```bash
GET /users/{user_id}
```

### Get User Bookings
```bash
GET /users/{user_id}/bookings
```

## Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error

## Common Errors

- `room not found` (404)
- `user not found` (404)
- `booking not found` (404)
- `time slot unavailable` (409)
- `email already registered` (409)
- `booking is already cancelled` (409)
- `name is required` (422)
- `end_time must be after start_time` (422)
- `minimum booking duration is 15 minutes` (422)

## Business Rules

- Business hours: 08:00 - 20:00
- Minimum booking: 15 minutes
- Time slots: 30-minute intervals
- Room status: active | inactive
- Booking status: confirmed | cancelled