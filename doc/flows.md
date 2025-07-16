# sprpsr API Flows

This document describes the main API flows for the sprpsr backend, starting with authentication and chat. Each flow outlines the request, processing steps, and response.

---

## 1. Authentication Flows (`auth_controller.py`)

### a. Check User
- **Endpoint:** `POST /api/auth/check-user`
- **Flow:**
  1. Client sends a JSON body with `phone`.
  2. Controller validates presence of `phone`.
  3. Calls `AuthService.check_user(phone)`.
  4. Returns result as JSON (user exists or not).

### b. Verify OTP
- **Endpoint:** `POST /api/auth/verify-otp`
- **Flow:**
  1. Client sends form-data with `idToken` (required), `profile` (optional, JSON string), and `photo` (optional file).
  2. Controller parses and validates input.
  3. Calls `AuthService.verify_and_authenticate(id_token, profile, photo)`.
  4. Returns authentication result (JWT token, user info, etc.) or error.

### c. Update Location
- **Endpoint:** `PUT /api/auth/update-location`
- **Flow:**
  1. Client sends JSON with `location` (GeoJSON Point), with JWT token in header.
  2. Controller extracts `user_id` from token and validates input.
  3. Calls `AuthService.update_user_location(user_id, location_data)`.
  4. Returns update result or error.

### d. Create Test User
- **Endpoint:** `POST /api/auth/test-user`
- **Flow:**
  1. Client sends JSON with `phone` and `profile`.
  2. Controller validates input.
  3. Calls `AuthService.create_test_user(phone, profile)`.
  4. Returns creation result or error.

### e. Sign In Test User
- **Endpoint:** `POST /api/auth/sign-in-test`
- **Flow:**
  1. Client sends JSON with `phone`.
  2. Controller validates input.
  3. Calls `AuthService.sign_in_test_user(phone)`.
  4. Returns sign-in result or error.

---

## 2. Chat Flows (`chat_controller.py`)

### a. Post Message
- **Endpoint:** `POST /api/events/<event_id>/chat`
- **Flow:**
  1. Client sends JSON with `message` and JWT token in header.
  2. Controller extracts `user_id` from token and validates input.
  3. Calls `ChatService.post_message(event_id, user_id, message)`.
  4. Returns message creation result or error.

### b. Get Event Chats
- **Endpoint:** `GET /api/events/<event_id>/chat`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `ChatService.get_event_messages(event_id, user_id)`.
  4. Returns list of chat messages or error.

---

## 3. Event Flows (`event_controller.py`)

### a. Create Event
- **Endpoint:** `POST /api/events`
- **Flow:**
  1. Client sends form-data with `event_data` (JSON string) and optional `banner` file, with JWT token in header.
  2. Controller parses and validates input.
  3. Calls `EventService.create_event(user_id, data, banner)`.
  4. Service validates data, uploads banner if present, and creates event in DB.
  5. Returns serialized event data or error.

### b. Get User Events
- **Endpoint:** `GET /api/events`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventService.get_user_events(user_id)`.
  4. Service fetches all events for user, migrates status if needed, serializes, and returns list.

### c. Get Event by ID
- **Endpoint:** `GET /api/events/<event_id>`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventService.get_event(user_id, event_id)`.
  4. Service fetches event, host, participants, and join/request status for user.
  5. Returns event details or error.

### d. Get Nearby Events
- **Endpoint:** `GET /api/events/nearby`
- **Flow:**
  1. Client sends request with JWT token in header and optional query params (`max_distance_km`, `event_type`).
  2. Controller fetches user location and validates.
  3. Calls `EventService.get_nearby_events(latitude, longitude, max_distance_km, event_type, requesting_user_id)`.
  4. Service queries for nearby events, filters, and returns list.

### e. Join Event
- **Endpoint:** `POST /api/events/<event_id>/join`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventService.join_or_request_event(event_id, user_id)`.
  4. Service checks event privacy:
     - If public: adds user as participant.
     - If private: creates join request (see event request flows).
  5. Returns join or request result.

### f. Leave Event
- **Endpoint:** `POST /api/events/<event_id>/leave`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventService.leave_event(event_id, user_id)`.
  4. Service removes user from participants.
  5. Returns result or error.

### g. Kick Participant
- **Endpoint:** `POST /api/events/<event_id>/kick/<participant_user_id>`
- **Flow:**
  1. Host sends request with JWT token in header.
  2. Controller extracts `host_user_id` from token.
  3. Calls `EventService.kick_participant(event_id, host_user_id, participant_user_id)`.
  4. Service validates host, removes participant.
  5. Returns result or error.

### h. Get Event Participants
- **Endpoint:** `GET /api/events/<event_id>/participants`
- **Flow:**
  1. Client sends request.
  2. Controller calls `EventService.get_event_participants(event_id)`.
  3. Service fetches and returns participant details.

### i. Submit Rating
- **Endpoint:** `POST /api/events/<event_id>/rate`
- **Flow:**
  1. Client sends rating data (rater, rated, rating, comment, no_show).
  2. Controller calls `EventService.submit_rating(...)`.
  3. Service validates and creates feedback entry.
  4. Returns result or error.

### j. Get Host Event Details
- **Endpoint:** `GET /api/events/<event_id>/host-details`
- **Flow:**
  1. Host sends request with JWT token in header.
  2. Controller extracts `host_id` from token.
  3. Calls `EventService.get_host_event_details(event_id, host_id)`.
  4. Service fetches event, validates host, gets participants and pending requests.
  5. Returns detailed event info.

### k. Delete Event
- **Endpoint:** `DELETE /api/events/<event_id>`
- **Flow:**
  1. Host sends request with JWT token in header.
  2. Controller extracts `host_user_id` from token.
  3. Calls `EventService.delete_event(event_id, host_user_id)`.
  4. Service validates host and deletes event.
  5. Returns result or error.

### l. Get Joined Events
- **Endpoint:** `GET /api/events/joined`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventService.get_joined_events(user_id)`.
  4. Service fetches events where user is participant or host, serializes, and returns list.

---

## 4. Event Request Flows (`event_request_controller.py`)

### a. Create Join Request
- **Endpoint:** `POST /api/events/<event_id>/request`
- **Flow:**
  1. User sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `EventRequestService.create_join_request(event_id, user_id)`.
  4. Service checks event privacy, host, and existing requests, then creates join request.
  5. Returns result or error.

### b. Get Pending Requests
- **Endpoint:** `GET /api/events/requests`
- **Flow:**
  1. Host sends request with JWT token in header.
  2. Controller extracts `host_id` from token.
  3. Calls `EventRequestService.get_host_pending_requests(host_id)`.
  4. Service fetches pending requests, adds user details, and returns list.

### c. Handle Request (Accept/Reject)
- **Endpoint:** `PUT /api/events/requests/<request_id>`
- **Flow:**
  1. Host sends request with JWT token in header and action in JSON body (`accept` or `reject`).
  2. Controller extracts `host_id` from token and validates action.
  3. Calls `EventRequestService.handle_request(request_id, host_id, action)`.
  4. Service finds request, updates status, and (if accepted) adds user to event participants.
  5. Returns result or error.

---

## 5. User Flows (`user_controller.py`)

### a. Update Profile
- **Endpoint:** `PUT /api/user/profile`
- **Flow:**
  1. Client sends form-data with `update_data` (JSON string) and optional `photo` file, with JWT token in header.
  2. Controller extracts `user_id` from token, parses and validates input.
  3. Calls `UserService.update_profile(user_id, update_data, photo)`.
  4. Service uploads photo if present, updates user document, and returns updated profile.
  5. Returns updated user profile or error.

### b. Get Public Profile
- **Endpoint:** `GET /api/users/<user_id>`
- **Flow:**
  1. Client sends request with target `user_id` in path and JWT token in header.
  2. Controller calls `UserService.get_user_profile_with_ratings(user_id)`.
  3. Service fetches user, serializes profile, ensures rating fields, and returns profile.
  4. Returns user profile or 404 if not found.

### c. Get Participants by Event
- **Endpoint:** `GET /api/events/<event_id>/participants`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `requesting_user_id` from token.
  3. Calls `UserService.get_participants_by_event(event_id, requesting_user_id)`.
  4. Service fetches event, checks status and authorization, and returns participant profiles.
  5. Returns list of participants or error.

### d. Get Own Profile
- **Endpoint:** `GET /api/user/profile`
- **Flow:**
  1. Client sends request with JWT token in header.
  2. Controller extracts `user_id` from token.
  3. Calls `UserService.get_user_profile_with_ratings(user_id)`.
  4. Service fetches and serializes user profile, ensures rating fields, and returns profile.
  5. Returns user profile or 404 if not found.

---
