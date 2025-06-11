from flask import Blueprint
from src.controllers.event_request_controller import EventRequestController
from src.middleware.auth_middleware import token_required

event_request_bp = Blueprint('event_requests', __name__)

# Create join request for private event
@event_request_bp.route('/events/<event_id>/request', methods=['POST'])
def create_event_request(event_id):
    return EventRequestController.create_join_request(event_id)

# Get all pending requests for host
@event_request_bp.route('/events/requests', methods=['GET'])
@token_required
def get_pending_requests(current_user):
    """
    Get all pending join requests for events hosted by the current user
    ---
    tags:
      - Event Requests
    security:
      - Bearer: []
    responses:
      200:
        description: List of pending requests
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              event_id:
                type: string
              user_id:
                type: string
              status:
                type: string
                enum: [pending]
              created_at:
                type: string
                format: date-time
              event:
                type: object
                properties:
                  _id:
                    type: string
                  title:
                    type: string
                  start_time:
                    type: string
                    format: date-time
              user:
                type: object
                properties:
                  _id:
                    type: string
                  name:
                    type: string
                  photo_url:
                    type: string
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    return EventRequestController.get_pending_requests(current_user)

# Handle (accept/reject) a request
@event_request_bp.route('/events/requests/<request_id>', methods=['PUT'])
@token_required
def handle_request(request_id):
    """
    Handle an event join request (accept/reject)
    ---
    tags:
      - Event Requests
    security:
      - Bearer: []
    parameters:
      - in: path
        name: request_id
        type: string
        required: true
        description: ID of the request to handle
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              enum: [accept, reject]
              description: Action to take on the request
    responses:
      200:
        description: Request handled successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Request accepted successfully"
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not the event host
      404:
        description: Request not found
      500:
        description: Internal server error
    """
    return EventRequestController.handle_request(request_id) 