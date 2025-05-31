from flask import jsonify, request
from src.services.event_service import EventService
from bson import ObjectId
class EventController:    
    @staticmethod
    def create_event():
        """Handle event creation request."""
        data = request.get_json()
        print("Received data:", data)
        auth_header = request.headers.get('Authorization')
        print("auth_header:", auth_header)
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            event_data = data.get('event')
                         
            if not token:
                return jsonify({'error': 'Authorization token is required'}), 401
            if not event_data:
                return jsonify({'error': 'Event data is required'}), 400
            
            try:
                new_event = EventService.create_event(token,event_data)
                return jsonify(new_event), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
    @staticmethod
    def getAllEventofUser():
        """Get all events of a user."""
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = None

            if not token:
                return jsonify({'error': 'Authorization token is required'}), 401

            events = EventService.get_all_events_of_user(token)
            serialized_events = [EventService.serialize_event(event) for event in events]
            print("Fetched events:", serialized_events)
            return jsonify(serialized_events), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500



