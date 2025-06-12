from datetime import datetime
from bson import ObjectId
from src.config.database import get_database
import pytz # Import pytz for timezone handling
from dateutil import parser # Import parser for more flexible datetime parsing

db = get_database()
upcoming_events_collection = db['upcoming_events']
active_events_collection = db['active_events']
archived_events_collection = db['archived_events']

# Create a 2dsphere index on the location field for upcoming and active events
upcoming_events_collection.create_index([('location', '2dsphere')])
active_events_collection.create_index([('location', '2dsphere')])

# Define the Kolkata timezone
kolkata_timezone = pytz.timezone('Asia/Kolkata')

class Event:
    @staticmethod
    def find_by_id(id):
        """Find event by ID across all collections."""
        try:
            # First check upcoming events
            event = upcoming_events_collection.find_one({'_id': ObjectId(id)})
            if event: return event

            # Then check active events
            event = active_events_collection.find_one({'_id': ObjectId(id)})
            if event: return event

            # Finally check archived events
            event = archived_events_collection.find_one({'_id': ObjectId(id)})
            if event: return event
            
            return None
        except:
            return None
    
    @staticmethod
    def create(user_id, data):
        """Create new event in the upcoming_events collection, with timezone-aware times."""
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        if not start_time_str or not end_time_str:
            raise ValueError("Start time and end time are required.")

        try:
            # Use dateutil.parser.isoparse for more flexible ISO 8601 parsing
            start_time_utc = parser.isoparse(start_time_str)
            end_time_utc = parser.isoparse(end_time_str)

            # Convert the UTC-aware datetime to Asia/Kolkata timezone
            start_time_kolkata = start_time_utc.astimezone(kolkata_timezone)
            end_time_kolkata = end_time_utc.astimezone(kolkata_timezone)
        except ValueError as e:
            raise ValueError(f"Invalid time format provided: {e}")

        new_event = {
            'user_id': ObjectId(user_id),  
            'title': data.get('title'),
            'description': data.get('description'),
            'location': data.get('location'),
            'use_gps': data.get('use_gps', False),
            'is_private': data.get('is_private', False),
            'activity_type': data.get('activity_type'),
            'start_time': start_time_kolkata,
            'end_time': end_time_kolkata,    
            'participants_min': data.get('participants_min'),
            'participants_max': data.get('participants_max'),
            'banner_url': data.get('banner_url'),
            'status': 'upcoming',
            'participants': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = upcoming_events_collection.insert_one(new_event)
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find all events by user ID across all collections."""
        try:
            upcoming = list(upcoming_events_collection.find({'user_id': ObjectId(user_id)}))
            active = list(active_events_collection.find({'user_id': ObjectId(user_id)}))
            archived = list(archived_events_collection.find({'user_id': ObjectId(user_id)}))
            return upcoming + active + archived
        except:
            return []

    @staticmethod
    def add_participant(event_id, user_id):
        """Add a participant to an active event."""
        try:
            result = active_events_collection.update_one(
                {'_id': ObjectId(event_id)}, 
                {'$addToSet': {'participants': ObjectId(user_id)}}
            )
            return result.matched_count > 0 and result.modified_count > 0
        except Exception as e:
            print(f"Error adding participant: {e}")
            return False

    @staticmethod
    def remove_participant(event_id, user_id_to_remove):
        """Remove a participant from an active event."""
        try:
            result = active_events_collection.update_one(
                {'_id': ObjectId(event_id)}, 
                {'$pull': {'participants': ObjectId(user_id_to_remove)}}
            )
            return result.matched_count > 0 and result.modified_count > 0
        except Exception as e:
            print(f"Error removing participant: {e}")
            return False

    @staticmethod
    def move_to_active(event_id):
        """Moves an event from upcoming to active collection."""
        try:
            event = upcoming_events_collection.find_one({'_id': ObjectId(event_id)})
            if event:
                event['status'] = 'active'
                active_events_collection.insert_one(event)
                upcoming_events_collection.delete_one({'_id': ObjectId(event_id)})
                return True
            return False
        except Exception as e:
            print(f"Error moving event to active: {e}")
            return False

    @staticmethod
    def move_to_archived(event_id):
        """Moves an event from active to archived collection."""
        try:
            event = active_events_collection.find_one({'_id': ObjectId(event_id)})
            if event:
                event['status'] = 'archived'
                archived_events_collection.insert_one(event)
                active_events_collection.delete_one({'_id': ObjectId(event_id)})
                return True
            return False
        except Exception as e:
            print(f"Error moving event to archived: {e}")
            return False
