from flask import Blueprint
from src.controllers.event_request_controller import EventRequestController

event_request_bp = Blueprint('event_request', __name__)

# Create join request for private event
@event_request_bp.route('/events/<event_id>/request', methods=['POST'])
def create_event_request(event_id):
    return EventRequestController.create_join_request(event_id)

# Get all pending requests for host
@event_request_bp.route('/events/requests', methods=['GET'])
def get_pending_requests():
    return EventRequestController.get_pending_requests()

# Handle (accept/reject) a request
@event_request_bp.route('/events/requests/<request_id>', methods=['PUT'])
def handle_event_request(request_id):
    return EventRequestController.handle_request(request_id) 