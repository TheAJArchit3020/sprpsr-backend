from flask import Blueprint
from src.controllers.event_controller import EventController

event_bp=Blueprint('event',__name__)
@event_bp.route('/create-event', methods=['POST'])
def create_event():
    return EventController.create_event()
@event_bp.route('/get-all-events', methods=['GET'])
def get_all_events_of_user():
    return EventController.getAllEventofUser()