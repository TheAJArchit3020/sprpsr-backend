# sprpsr Database Schema

This document provides an overview of the main MongoDB collections and their fields used in the sprpsr backend.

---

## 1. users
**Collection:** `users`

| Field             | Type           | Description                        |
|-------------------|----------------|------------------------------------|
| _id               | ObjectId       | User ID (primary key)              |
| phone             | string         | User's phone number                |
| name              | string         | User's name                        |
| dob               | string/date    | Date of birth                      |
| gender            | string         | Gender                             |
| about             | string         | About/bio                          |
| photo_url         | string         | Profile photo URL                  |
| location          | GeoJSON Point  | User's location                    |
| created_at        | datetime       | Account creation time              |
| updated_at        | datetime       | Last update time                   |
| events_organized  | int            | Number of events organized         |
| latest_events     | [ObjectId]     | Recent event IDs                   |
| rating            | float          | (optional) Average rating          |
| rating_count      | int            | (optional) Number of ratings       |
| total_rating      | int            | (optional) Sum of all ratings      |
| comments          | [object]       | (optional) Recent comments         |

---

## 2. Events
**Collections:** `upcoming_events`, `active_events`, `archived_events`

| Field             | Type           | Description                        |
|-------------------|----------------|------------------------------------|
| _id               | ObjectId       | Event ID (primary key)             |
| user_id           | ObjectId       | Host user ID                       |
| title             | string         | Event title                        |
| description       | string         | Event description                  |
| location          | GeoJSON Point  | Event location                     |
| use_gps           | bool           | Use GPS for location?              |
| is_private        | bool           | Is the event private?              |
| activity_type     | string         | Activity type                      |
| start_time        | datetime       | Start time                         |
| end_time          | datetime       | End time                           |
| location_name     | string         | Location name                      |
| participants_min  | int            | Min participants                   |
| participants_max  | int            | Max participants                   |
| banner_url        | string         | Event banner URL                   |
| status            | string         | Event status (upcoming/active/archived) |
| participants      | [ObjectId]     | Participant user IDs               |
| created_at        | datetime       | Creation time                      |
| updated_at        | datetime       | Last update time                   |

---

## 3. event_requests
**Collection:** `event_requests`

| Field             | Type           | Description                        |
|-------------------|----------------|------------------------------------|
| _id               | ObjectId       | Request ID (primary key)           |
| event_id          | ObjectId       | Event being requested              |
| user_id           | ObjectId       | Requesting user                    |
| host_id           | ObjectId       | Host user ID                       |
| status            | string         | Request status (pending/accepted/rejected) |
| created_at        | datetime       | Creation time                      |
| updated_at        | datetime       | Last update time                   |

---

## 4. feedbacks / archived_feedbacks
**Collections:** `feedbacks`, `archived_feedbacks`

| Field             | Type           | Description                        |
|-------------------|----------------|------------------------------------|
| _id               | ObjectId       | Feedback ID (primary key)          |
| event_id          | ObjectId       | Event being rated                  |
| rater_user_id     | ObjectId       | User giving the rating             |
| rated_user_id     | ObjectId       | User being rated                   |
| rating            | int/float      | Rating value                       |
| comment           | string         | (optional) Feedback comment        |
| no_show           | bool           | (optional) Marked as no-show       |
| created_at        | datetime       | Feedback creation time             |
| is_archived       | bool           | Is this feedback archived?         |

---

## 5. chatMessages
**Collection:** `chatMessages`

| Field             | Type           | Description                        |
|-------------------|----------------|------------------------------------|
| _id               | ObjectId       | Message ID (primary key)           |
| event_id          | ObjectId       | Event this message belongs to      |
| user_id           | ObjectId       | User who sent the message          |
| message           | string         | Message content                    |
| timestamp         | datetime       | Message timestamp (IST)            |

---

**Note:**
- All ObjectId fields are MongoDB ObjectIds.
- All date/time fields are stored as UTC datetimes unless otherwise noted.
- GeoJSON Point format: `{ "type": "Point", "coordinates": [longitude, latitude] }`
- Some collections (like events) are split by status for performance/scalability. 