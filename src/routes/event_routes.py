from flask import Blueprint, request, jsonify
from src.controllers.event_controller import EventController
from src.middleware.auth_middleware import token_required

event_bp = Blueprint('events', __name__)

@event_bp.route('/events', methods=['POST'])
@token_required
def create_event():
    """
    Create a new event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: formData
        name: event_data
        type: string
        required: true
        description: JSON string containing event details
        schema:
          type: object
          required:
            - title
            - description
            - start_time
            - end_time
            - location
            - activity_type
          properties:
            title:
              type: string
              example: "Beach Volleyball"
            description:
              type: string
              example: "Join us for a fun game of beach volleyball"
            start_time:
              type: string
              format: date-time
              example: "2024-03-20T15:00:00Z"
            end_time:
              type: string
              format: date-time
              example: "2024-03-20T17:00:00Z"
            location:
              type: object
              properties:
                type:
                  type: string
                  example: "Point"
                coordinates:
                  type: array
                  items:
                    type: number
            activity_type:
              type: string
              description: Type of activity/event
              example: "sports"
            is_private:
              type: boolean
              description: Whether the event is private
              example: false
            use_gps:
              type: boolean
              description: Whether to use GPS for location
              example: true
            days:
              type: array
              description: Array of days for recurring events
              items:
                type: string
                enum: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
              example: ["monday", "wednesday", "friday"]
            participants_min:
              type: integer
              description: Minimum number of participants required
              example: 2
            participants_max:
              type: integer
              description: Maximum number of participants allowed
              example: 10
      - in: formData
        name: banner
        type: file
        required: false
        description: Event banner image
    responses:
      201:
        description: Event created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            title:
              type: string
            description:
              type: string
            start_time:
              type: string
              format: date-time
            end_time:
              type: string
              format: date-time
            location:
              type: object
              properties:
                type:
                  type: string
                coordinates:
                  type: array
                  items:
                    type: number
            activity_type:
              type: string
            is_private:
              type: boolean
            use_gps:
              type: boolean
            days:
              type: array
              items:
                type: string
            participants_min:
              type: integer
            participants_max:
              type: integer
            banner_url:
              type: string
            status:
              type: string
              enum: [upcoming, active, archived]
            participants:
              type: array
              items:
                type: string
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    return EventController.create_event()

@event_bp.route('/events', methods=['GET'])
@token_required
def get_events():
    """
    Get all events for the authenticated user
    ---
    tags:
      - Events
    security:
      - Bearer: []
    responses:
      200:
        description: List of events
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              title:
                type: string
              description:
                type: string
              start_time:
                type: string
                format: date-time
              end_time:
                type: string
                format: date-time
              location:
                type: object
                properties:
                  type:
                    type: string
                  coordinates:
                    type: array
                    items:
                      type: number
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    return EventController.get_events()

@event_bp.route('/events/<event_id>', methods=['GET'])
@token_required
def get_event(event_id):
    """
    Get a specific event by ID
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event to retrieve
    responses:
      200:
        description: Event details
        schema:
          type: object
          properties:
            _id:
              type: string
            title:
              type: string
            description:
              type: string
            start_time:
              type: string
              format: date-time
            end_time:
              type: string
              format: date-time
            location:
              type: object
              properties:
                type:
                  type: string
                coordinates:
                  type: array
                  items:
                    type: number
      401:
        description: Unauthorized
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.get_event(event_id)

@event_bp.route('/events/nearby', methods=['GET'])
@token_required
def get_nearby_events():
    """
    Get events near the user's location
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: query
        name: max_distance_km
        type: number
        required: false
        default: 10
        description: Maximum distance in kilometers
    responses:
      200:
        description: List of nearby events
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              title:
                type: string
              description:
                type: string
              start_time:
                type: string
                format: date-time
              end_time:
                type: string
                format: date-time
              location:
                type: object
                properties:
                  type:
                    type: string
                  coordinates:
                    type: array
                    items:
                      type: number
              distance:
                type: number
                description: Distance in meters
      400:
        description: Bad request - User location not found
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    return EventController.get_nearby_events()

@event_bp.route('/events/<event_id>/join', methods=['POST'])
@token_required
def join_event(event_id):
    """
    Join an event or request to join a private event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event to join
    responses:
      200:
        description: Join request result
        schema:
          type: object
          properties:
            message:
              type: string
            status:
              type: string
              enum: [joined, pending]
            request_id:
              type: string
              description: Only present for private events
      400:
        description: Bad request
      401:
        description: Unauthorized
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.join_event(event_id)

@event_bp.route('/events/<event_id>/leave', methods=['POST'])
@token_required
def leave_event(event_id):
    """
    Leave an event
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event to leave
    responses:
      200:
        description: Successfully left event
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Bad request
      401:
        description: Unauthorized
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.leave_event(event_id)

@event_bp.route('/events/<event_id>/kick/<participant_user_id>', methods=['POST'])
@token_required
def kick_participant(event_id, participant_user_id):
    """
    Kick a participant from an event (host only)
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event
      - in: path
        name: participant_user_id
        type: string
        required: true
        description: ID of the participant to kick
    responses:
      200:
        description: Successfully kicked participant
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Bad request
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not the event host
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.kick_participant(event_id, participant_user_id)

@event_bp.route('/events/<event_id>/rate', methods=['POST'])
@token_required
def submit_rating(event_id):
    """
    Submit a rating for a participant in an event
    ---
    tags:
      - Events
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
        description: ID of the event
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - rated_user_id
            - rating
          properties:
            rated_user_id:
              type: string
              description: ID of the user being rated
            rating:
              type: number
              description: Rating value (1-5)
            comment:
              type: string
              description: Optional comment about the rating
            no_show:
              type: boolean
              description: Whether the user was a no-show
    responses:
      200:
        description: Rating submitted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Rating submitted successfully
      400:
        description: Invalid request or validation error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid rating value
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Token is missing
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: An error occurred while submitting the rating
    """
    data = request.get_json()
    rated_user_id = data.get('rated_user_id')
    rating = data.get('rating')
    comment = data.get('comment')
    no_show = data.get('no_show', False)
    
    # The rater is the current user from the token
    rater_user_id = request.user_id

    if not all([rated_user_id, rating is not None]):
        return jsonify({'error': 'Missing rated_user_id or rating'}), 400

    return EventController.submit_rating(
        event_id=event_id,
        rater_user_id=rater_user_id,
        rated_user_id=rated_user_id,
        rating=rating,
        comment=comment,
        no_show=no_show
    )

@event_bp.route('/events/<event_id>/host-details', methods=['GET'])
@token_required
def get_host_event_details(event_id):
    """
    Get detailed event information for host including participants and pending requests
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event
    responses:
      200:
        description: Event details with participants and pending requests
        schema:
          type: object
          properties:
            _id:
              type: string
            title:
              type: string
            description:
              type: string
            start_time:
              type: string
              format: date-time
            end_time:
              type: string
              format: date-time
            location:
              type: object
              properties:
                type:
                  type: string
                coordinates:
                  type: array
                  items:
                    type: number
            participants:
              type: array
              items:
                type: object
                properties:
                  _id:
                    type: string
                  name:
                    type: string
                  photo_url:
                    type: string
                  type:
                    type: string
                    enum: [participant]
            pending_requests:
              type: array
              items:
                type: object
                properties:
                  _id:
                    type: string
                  user:
                    type: object
                    properties:
                      _id:
                        type: string
                      name:
                        type: string
                      photo_url:
                        type: string
                  type:
                    type: string
                    enum: [pending_request]
                  created_at:
                    type: string
                    format: date-time
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not the event host
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.get_host_event_details(event_id)

@event_bp.route('/events/<event_id>', methods=['DELETE'])
@token_required
def delete_event(event_id):
    """
    Delete an event by ID (Host Only)
    ---
    tags:
      - Events
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event to delete
    responses:
      200:
        description: Event deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Event deleted successfully.
      400:
        description: Bad request (e.g., Event not found, Unauthorized)
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized (missing or invalid token)
      403:
        description: Forbidden (user is not the host)
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return EventController.delete_event(event_id)
