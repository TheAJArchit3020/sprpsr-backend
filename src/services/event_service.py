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
        
        # Validate and include location data if provided
        location_data = data.get('location')
        if location_data:
            if not isinstance(location_data, dict) or location_data.get('type') != 'Point' or not isinstance(location_data.get('coordinates'), list) or len(location_data['coordinates']) != 2:
                 raise ValueError("Invalid GeoJSON Point format for event location")
                 
        db = get_database()
        events_collection = db.events
        
        event = {
            'user_id': ObjectId(user_id),  
            'title': data.get('title'),
            'description': data.get('description'),
            'location': location_data, # Include location data
            'use_gps': data.get('use_gps', False),

            'activity_type': data.get('activity_type'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),

            'days': data.get('days', []),

            'participants_min': data.get('participants_min'),
            'participants_max': data.get('participants_max'),
            'banner_url': data.get('banner_url'),
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
        
        # Include banner_url and location in the response if they exist
        if 'banner_url' in event_dict:
            event_dict['banner_url'] = event_dict['banner_url']
            
        if 'location' in event_dict and event_dict['location']:
            event_dict['location'] = event_dict['location'] # Location is already in GeoJSON format
            
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
            
        # Include banner_url and location if they exist
        if 'banner_url' in event_dict:
            event_dict['banner_url'] = event_dict['banner_url']
            
        if 'location' in event_dict and event_dict['location']:
             event_dict['location'] = event_dict['location'] # Location is already in GeoJSON format
            
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

    @staticmethod
    def get_nearby_events(latitude, longitude, max_distance_km):
        """Find events near a given location within a specified radius."""
        db = get_database()
        events_collection = db.events
        
        # Convert max_distance from kilometers to meters
        max_distance_meters = max_distance_km * 1000
        
        # GeoJSON Point for the query origin
        # Note: GeoJSON uses [longitude, latitude] order
        near_location = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
        
        # Aggregation pipeline with $geoNear
        pipeline = [
            {
                "$geoNear": {
                    "near": near_location,
                    "distanceField": "distance",  # Output distance in meters
                    "maxDistance": max_distance_meters,
                    "spherical": True
                }
            },
            { "$match": { "location": { "$exists": True, "$ne": None } } }, # Ensure location exists
            { "$sort": { "distance": 1 } }  # Sort by distance
        ]
        
        # Execute the aggregation pipeline
        nearby_events = list(events_collection.aggregate(pipeline))
        
        # Serialize the results
        return [EventService._serialize_event(event) for event in nearby_events]