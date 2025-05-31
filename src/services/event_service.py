from src.models.event import Event
from src.utils.jwt import verfiy_token

class EventService:

    @staticmethod
    def create_event(id_token,event_data):
        """Create a new event."""
        decoded_token = verfiy_token(id_token)
        user_id = decoded_token.get('userId')

        if not user_id:
            raise ValueError('User token is invalid or missing user ID')
        
        # Create the event if user exists
        eventID = Event.create(user_id, event_data)
        return {
            'message': 'Event created successfully',
            'event_id': str(eventID)
        }
    
    @staticmethod
    def get_all_events_of_user(id_token):
        """Get all events of a user."""
        decoded_token = verfiy_token(id_token)
        user_id = decoded_token.get('userId')

        if not user_id:
            raise ValueError('User token is invalid or missing user ID')
        
        # Fetch all events for the user
        events = Event.find_by_user_id(user_id)
        return events
    @staticmethod
    def serialize_event(event):
        event['_id'] = str(event['_id'])  # Convert ObjectId to string
        return event