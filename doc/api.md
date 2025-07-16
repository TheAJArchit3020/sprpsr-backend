# sprpsr API Overview

This document provides an overview of the main API endpoints and modules for the sprpsr backend. For full, interactive API documentation, visit the Swagger UI at `/docs` when the server is running.

---

## Authentication
- **Firebase-based authentication** is used for user sign-in and registration.
- JWT tokens are issued for authenticated requests.
- Most endpoints require the `Authorization: Bearer <token>` header.

---

## Main API Modules & Endpoints

### Auth
- `POST /api/auth/check-user` — Check if a user exists by phone number
- `POST /api/auth/verify-otp` — Verify OTP and authenticate user (Firebase)
- `PUT /api/auth/update-location` — Update user location

### User
- `GET /api/user/profile` — Get own user profile
- `PUT /api/user/profile` — Update own user profile
- `GET /api/users/<user_id>` — Get public profile of another user
- `GET /api/events/<event_id>/participants` — List participants for an event

### Events
- `POST /api/events` — Create a new event
- `GET /api/events` — List all events for the authenticated user
- `GET /api/events/<event_id>` — Get details of a specific event
- `GET /api/events/nearby` — List nearby events
- `POST /api/events/<event_id>/join` — Join an event
- `POST /api/events/<event_id>/leave` — Leave an event
- `POST /api/events/<event_id>/kick/<participant_user_id>` — Remove a participant (host only)
- `POST /api/events/<event_id>/rate` — Submit a rating for an event
- `GET /api/events/joined` — List events the user has joined or is hosting
- `DELETE /api/events/<event_id>` — Delete an event (host only)

### Event Requests (for Private Events)
- `POST /api/events/<event_id>/request` — Request to join a private event
- `GET /api/events/requests` — List pending join requests for events you host
- `PUT /api/events/requests/<request_id>` — Accept or reject a join request

### Chat
- `POST /api/events/<event_id>/chat` — Post a message to an event chat
- `GET /api/events/<event_id>/chat` — Get all chat messages for an event

---

## API Documentation

- **Interactive Swagger UI:**
  - Visit `http://localhost:8890/docs` after starting the server for detailed, try-it-out API documentation.
  - All request/response schemas, authentication requirements, and error codes are documented there.

---

## Notes
- All endpoints (except authentication) require a valid JWT token in the `Authorization` header.
- For file uploads (profile photos, event banners), use `multipart/form-data`.
- For geolocation, use GeoJSON Point format: `{ "type": "Point", "coordinates": [longitude, latitude] }`

---

For further details, see the codebase or contact the backend team. 