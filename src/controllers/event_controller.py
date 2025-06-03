from flask import jsonify, request
from src.services.event_service import EventService
from bson import ObjectId
from src.middleware.auth_middleware import token_required
import json # Import json to parse the event data string

class EventController:    
    @staticmethod
    @token_required
    def create_event():
        """Create a new event."""
        # Get data from form-data
        event_data_str = request.form.get('event_data')
        banner = request.files.get('banner') if request.files else None
        user_id = request.user_id  # This comes from the auth middleware

        if not event_data_str:
            return jsonify({'error': 'Event data is required'}), 400

        try:
            # Parse the event data JSON string
            data = json.loads(event_data_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid event data JSON format'}), 400

        try:
            # Pass user_id, data, and banner to the service
            result = EventService.create_event(user_id, data, banner)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @token_required
    def get_events():
        """Get all events for the authenticated user."""
        user_id = request.user_id  # This comes from the auth middleware
        
        try:
            events = EventService.get_user_events(user_id)
            return jsonify(events)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @token_required
    def get_event(event_id):
        """Get a specific event."""
        user_id = request.user_id  # This comes from the auth middleware
        
        try:
            event = EventService.get_event(user_id, event_id)
            if not event:
                return jsonify({'error': 'Event not found'}), 404
            return jsonify(event)
        except Exception as e:
            return jsonify({'error': str(e)}), 500



