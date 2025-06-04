from datetime import datetime
from bson import ObjectId
from src.config.database import get_database

db = get_database()
events_collection = db['events']

# Create a 2dsphere index on the location field
events_collection.create_index([('location', '2dsphere')])

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
            'status': 'active',
            'participants': [],
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

    @staticmethod
    def add_participant(event_id, user_id):
        """Add a participant to an event.
           Returns True if added, False otherwise (e.g., user already in list).
        """
        try:
            result = events_collection.update_one(
                {'_id': ObjectId(event_id)}, 
                {'$addToSet': {'participants': ObjectId(user_id)}}
            )
            return result.matched_count > 0 and result.modified_count > 0
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False

    @staticmethod
    def remove_participant(event_id, user_id_to_remove):
        """Remove a participant from an event.
           Returns True if removed, False otherwise (e.g., user not in list).
        """
        try:
            result = events_collection.update_one(
                {'_id': ObjectId(event_id)}, 
                {'$pull': {'participants': ObjectId(user_id_to_remove)}}
            )
            return result.matched_count > 0 and result.modified_count > 0
        except Exception as e:
            print(f"Error removing participant: {e}")
            return False
