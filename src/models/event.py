from datetime import datetime
from bson import ObjectId
from src.config.database import get_database

db = get_database()
events_collection = db['events']

class Event:
    @staticmethod
    def find_by_id(id):
        """Find event by ID."""
        try:
            return events_collection.find_one({'_id': ObjectId(id)})
        except:
            return None
    
    @staticmethod
    def create(user_id, data):
        """Create new event."""
        new_event = {
            'user_id': ObjectId(user_id),  
            'event_name': data.get('event_name'),
            'description': data.get('description'),
            'location': data.get('location'),
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

        result = events_collection.insert_one(new_event)
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find all events by user ID."""
        try:
            return list(events_collection.find({'user_id': ObjectId(user_id)}))
        except:
            return []
