from datetime import datetime
from src.config.database import get_database

db = get_database()
events_collection = db['events']

class Event:
    @staticmethod
    def find_by_id(id):
        """Find user by phone number."""
        return events_collection.find_one({'id': id})
    
    @staticmethod
    def create(userID, form_data):
        """Create new event."""
        new_event = {
            'user_id': userID,
            'event_name': form_data.get('event_name'),
            'description': form_data.get('description'),
            'location': form_data.get('location'),
            'use_gps': form_data.get('use_gps', False),

            'activity_type': form_data.get('activity_type'),
            'start_time': form_data.get('start_time'),
            'end_time': form_data.get('end_time'),

            'days': form_data.get('days', []),

            'participants_min': form_data.get('participants_min'),
            'participants_max': form_data.get('participants_max'),

            'banner_image_url': form_data.get('banner_image_url')
        }

        result = events_collection.insert_one(new_event)
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find all events by user ID."""
        return list(events_collection.find({'user_id': user_id}))
