from datetime import datetime
from bson import ObjectId
from src.config.database import get_database
from src.models.event import Event
from src.utils.jwt import verfiy_token
from src.utils.firebase_storage import upload_to_firebase

class EventService:

    @staticmethod
    def create_event(user_id, data, banner=None):
        """Create a new event in the database."""
        if not data:
            raise ValueError("Event data is required")
            
        # Handle banner upload if present
        if banner:
            try:
                banner_url = upload_to_firebase(banner, folder='event_banners')
                data['banner_url'] = banner_url
            except Exception as e:
                raise ValueError(f'Error uploading banner: {str(e)}')
        
        db = get_database()
        events_collection = db.events
        
        event = {
            'user_id': ObjectId(user_id),  
            'title': data.get('title'),
            'description': data.get('description'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'location': data.get('location'),
            'banner_url': data.get('banner_url'), # Include banner_url from data
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = events_collection.insert_one(event)
        # Convert the event to a dict and serialize ObjectIds
        event_dict = event.copy()
        event_dict['_id'] = str(result.inserted_id)
        event_dict['user_id'] = str(event['user_id'])
        event_dict['created_at'] = event_dict['created_at'].isoformat()
        event_dict['updated_at'] = event_dict['updated_at'].isoformat()
        
        # Include banner_url in the response if it exists
        if 'banner_url' in event_dict:
            event_dict['banner_url'] = event_dict['banner_url']
            
        return event_dict
    
    @staticmethod
    def get_user_events(user_id):
        """Get all events for a specific user."""
        db = get_database()
        events_collection = db.events
        
        try:
            events = list(events_collection.find({'user_id': ObjectId(user_id)}))
            return [EventService._serialize_event(event) for event in events]
        except:
            return []
    
    @staticmethod
    def get_event(user_id, event_id):
        """Get a specific event by ID."""
        db = get_database()
        events_collection = db.events
        
        try:
            event = events_collection.find_one({
                '_id': ObjectId(event_id),
                'user_id': ObjectId(user_id)
            })
            return EventService._serialize_event(event) if event else None
        except:
            return None
    
    @staticmethod
    def _serialize_event(event):
        """Convert MongoDB event document to JSON-serializable format."""
        if not event:
            return None
            
        # Create a copy of the event to avoid modifying the original
        event_dict = event.copy()
        
        # Convert ObjectId fields to strings
        event_dict['_id'] = str(event_dict['_id'])
        event_dict['user_id'] = str(event_dict['user_id'])
        
        # Convert datetime fields to ISO format strings
        if 'created_at' in event_dict:
            event_dict['created_at'] = event_dict['created_at'].isoformat()
        if 'updated_at' in event_dict:
            event_dict['updated_at'] = event_dict['updated_at'].isoformat()
            
        # Include banner_url if it exists
        if 'banner_url' in event_dict:
            event_dict['banner_url'] = event_dict['banner_url']
            
        return event_dict

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