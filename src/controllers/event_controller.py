from flask import jsonify, request
from src.services.event_service import EventService
from bson import ObjectId
from src.middleware.auth_middleware import token_required
import json 
from src.models.user import User 

class EventController:
    @staticmethod
    @token_required
    def create_event():
        """Create a new event."""
        # Get data from form-data
        event_data_str = request.form.get('event_data')
        banner = request.files.get('banner') if request.files else None
        user_id = request.user_id 

        if not event_data_str:
            return jsonify({'error': 'Event data is required'}), 400

        try:
            data = json.loads(event_data_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid event data JSON format'}), 400

        try:
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
        user_id = request.user_id 
        
        try:
            events = EventService.get_user_events(user_id)
            return jsonify(events)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @token_required
    def get_event(event_id):
        """Get a specific event."""
        user_id = request.user_id  
        
        try:
            event = EventService.get_event(user_id, event_id)
            if not event:
                return jsonify({'error': 'Event not found'}), 404
            return jsonify(event)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_nearby_events():
        """Get events near the authenticated user's location."""
        user_id = request.user_id  
        max_distance_km = request.args.get('max_distance_km', type=float, default=10)  # Default to 10 km

        # Fetch the user to get their location
        user = User.find_by_id(user_id)

        if not user or 'location' not in user or not user['location']:
            return jsonify({'error': 'User location not found. Please update your location.'}), 400
            
        user_location = user['location']
        
        # Ensure location is in the correct GeoJSON Point format
        if not isinstance(user_location, dict) or user_location.get('type') != 'Point' or not isinstance(user_location.get('coordinates'), list) or len(user_location['coordinates']) != 2:
            return jsonify({'error': 'Invalid user location data format.'}), 500  

        longitude = user_location['coordinates'][0]
        latitude = user_location['coordinates'][1]

        try:
            # Call the service method to get nearby events using user's location
            nearby_events = EventService.get_nearby_events(latitude, longitude, max_distance_km)
            return jsonify(nearby_events)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def join_event(event_id):
        """Handle authenticated user joining an event or requesting to join a private event."""
        user_id = request.user_id 

        try:
            result = EventService.join_or_request_event(event_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required 
    def leave_event(event_id):
        """Handle authenticated user leaving an event."""
        user_id = request.user_id 

        try:
            result = EventService.leave_event(event_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required 
    def kick_participant(event_id, participant_user_id):
        """Handle authenticated host kicking a participant from an event."""
        host_user_id = request.user_id 

        try:
            result = EventService.kick_participant(event_id, host_user_id, participant_user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required 
    def get_participants(event_id):
        """Get participants for a specific event."""
        try:
            participants = EventService.get_event_participants(event_id)
            return jsonify(participants), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404 
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def submit_rating(event_id, rater_user_id, rated_user_id, rating, comment=None, no_show=False):
        """Submit a rating for a participant in an event."""
        try:
            result = EventService.submit_rating(
                event_id=event_id,
                rater_user_id=rater_user_id,
                rated_user_id=rated_user_id,
                rating=rating,
                comment=comment,
                no_show=no_show
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def get_host_event_details(event_id):
        """Get detailed event information for host including participants and pending requests."""
        host_id = request.user_id  

        try:
            event_details = EventService.get_host_event_details(event_id, host_id)
            return jsonify(event_details), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500



