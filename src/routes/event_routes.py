from flask import Blueprint
from src.controllers.event_controller import EventController

event_bp = Blueprint('events', __name__)

# Event routes
event_bp.route('/events', methods=['POST'])(EventController.create_event)
event_bp.route('/events', methods=['GET'])(EventController.get_events)
event_bp.route('/events/<event_id>', methods=['GET'])(EventController.get_event)