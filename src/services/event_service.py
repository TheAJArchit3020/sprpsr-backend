from datetime import datetime, timedelta
from bson import ObjectId
from src.config.database import get_database
from src.models.event import Event, upcoming_events_collection, active_events_collection, archived_events_collection # Import new collections
from src.models.user import User 
from src.models.rating import Rating
from src.utils.jwt import verfiy_token
from src.utils.firebase_storage import upload_to_firebase
import pytz
from dateutil import parser 

class EventService:

    @staticmethod
    def create_event(user_id, data, banner=None):
        """Create a new event in the upcoming_events collection."""
        if not data:
            raise ValueError("Event data is required")
            
        if banner:
            try:
                banner_url = upload_to_firebase(banner, folder='event_banners')
                data['banner_url'] = banner_url
            except Exception as e:
                raise ValueError(f'Error uploading banner: {str(e)}')
        
        location_data = data.get('location')
        if location_data:
            if not isinstance(location_data, dict) or location_data.get('type') != 'Point' or not isinstance(location_data.get('coordinates'), list) or len(location_data['coordinates']) != 2:
                 raise ValueError("Invalid GeoJSON Point format for event location")
                 
        event_id = Event.create(user_id, data)
        
        new_event = upcoming_events_collection.find_one({'_id': ObjectId(event_id)})

        return EventService._serialize_event(new_event)
    
    @staticmethod
    def get_user_events(user_id):
        """Get all events for a specific user across all collections, migrating as needed."""
        all_user_events = Event.find_by_user_id(user_id)
        current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        
        upcoming = []
        active = []
        archived = []

        for event in all_user_events:
            event_id = event['_id']
            status = event['status']
            
            try:
                start_time = parser.isoparse(str(event['start_time'])).replace(tzinfo=pytz.utc)
                end_time = parser.isoparse(str(event['end_time'])).replace(tzinfo=pytz.utc)
            except Exception as e:
                print(f"Warning: Invalid event time format. Skipping event {event_id}. Error: {e}")
                continue

            # Handle upcoming events
            if status == 'upcoming' and current_time >= start_time:
                if Event.move_to_active(event_id):
                    event['status'] = 'active'
                    active.append(event)
                else:
                    upcoming.append(event)
            elif status == 'upcoming':
                upcoming.append(event)
            
            # Handle active events
            elif status == 'active':
                if current_time - end_time > timedelta(hours=48):
                    if Event.move_to_archived(event_id):
                        event['status'] = 'archived'
                        archived.append(event)
                    else:
                        active.append(event)
                else:
                    active.append(event)
            
            # Handle archived events
            elif status == 'archived':
                archived.append(event)
        
        return [EventService._serialize_event(e) for e in upcoming + active]

    @staticmethod
    def get_event(user_id, event_id):
        """Get a specific event by ID, searching across all collections."""
        event = Event.find_by_id(event_id) 

        if not event:
            return None
        
        return EventService._serialize_event(event)

    @staticmethod
    def _serialize_event(event):
        """Convert MongoDB event document to JSON-serializable format."""
        if not event:
            return None
            
        event_dict = event.copy()
        
        event_dict['_id'] = str(event_dict['_id'])
        event_dict['user_id'] = str(event_dict['user_id'])
        
        if 'created_at' in event_dict and isinstance(event_dict['created_at'], datetime):
            event_dict['created_at'] = event_dict['created_at'].isoformat()
        if 'updated_at' in event_dict and isinstance(event_dict['updated_at'], datetime):
            event_dict['updated_at'] = event_dict['updated_at'].isoformat()
        if 'start_time' in event_dict and isinstance(event_dict['start_time'], datetime):
            event_dict['start_time'] = event_dict['start_time'].isoformat()
        if 'end_time' in event_dict and isinstance(event_dict['end_time'], datetime):
            event_dict['end_time'] = event_dict['end_time'].isoformat()
            
        if 'banner_url' in event_dict:
            event_dict['banner_url'] = event_dict['banner_url']
            
        if 'location' in event_dict and event_dict['location']:
             event_dict['location'] = event_dict['location']
            
        if 'participants' in event_dict:
            event_dict['participants'] = [str(p) for p in event_dict['participants']]
            
        return event_dict
    
    @staticmethod
    def get_all_events_of_user(id_token):
        """Get all events of a user."""
        decoded_token = verfiy_token(id_token)
        user_id = decoded_token.get('userId')

        if not user_id:
            raise ValueError('User token is invalid or missing user ID')
        
        events = Event.find_by_user_id(user_id)
        return [EventService._serialize_event(e) for e in events]

    @staticmethod
    def get_nearby_events(latitude, longitude, max_distance_km):
        """Find upcoming events near a given location within a specified radius."""
        current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        max_distance_meters = max_distance_km * 1000
        
        # GeoJSON Point for the query origin
        near_location = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
        
        # Common pipeline for both collections
        geo_pipeline = [
            {
                "$geoNear": {
                    "near": near_location,
                    "distanceField": "distance",
                    "maxDistance": max_distance_meters,
                    "spherical": True
                }
            },
            { "$match": { "location": { "$exists": True, "$ne": None } } },
            { "$sort": { "distance": 1 } }
        ]

        # Get only upcoming events
        upcoming_events = list(upcoming_events_collection.aggregate(geo_pipeline))
        
        # Process upcoming events
        processed_events = []
        for event in upcoming_events:
            try:
                start_time = parser.isoparse(str(event['start_time'])).replace(tzinfo=pytz.utc)
                if current_time >= start_time:
                    Event.move_to_active(event['_id'])
                else:
                    processed_events.append(event)
            except Exception as e:
                print(f"Warning: Invalid event time format. Skipping event {event['_id']}. Error: {e}")
                continue

        # Return only upcoming events
        return [EventService._serialize_event(event) for event in processed_events]

    @staticmethod
    def join_or_request_event(event_id, user_id):
        """Handle both direct joining (for public events) and join requests (for private events)."""
        # Find the event in both collections
        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
            
        # Check if user is already a participant
        if ObjectId(user_id) in event.get('participants', []):
            raise ValueError("User is already a participant of this event")
            
        # Check if event is full
        max_participants = event.get('participants_max')
        current_participants_count = len(event.get('participants', []))
        
        if max_participants is not None and current_participants_count >= max_participants:
            raise ValueError("Event is full, cannot join")
            
        # Handle based on event privacy
        if event.get('is_private', False):
            # For private events, create a join request
            from src.services.event_request_service import EventRequestService
            result = EventRequestService.create_join_request(event_id, user_id)
            return {
                'message': 'Join request sent successfully',
                'request_id': result.get('request_id'),
                'status': 'pending'
            }
        else:
            # For public events, join directly
            success = Event.add_participant(event_id, user_id)
            if not success:
                raise Exception("Failed to add participant to event")
            return {
                'message': 'Successfully joined event',
                'status': 'joined'
            }

    @staticmethod
    def leave_event(event_id, user_id):
        """Handle a user leaving an event. This now targets active events."""
        # Find the event in the active collection
        try:
            event_obj = active_events_collection.find_one({'_id': ObjectId(event_id)})
        except:
            raise ValueError("Invalid Event ID")

        if not event_obj:
            raise ValueError("Event not found or not active")

        # Check if user is a participant
        if ObjectId(user_id) not in event_obj.get('participants', []):
            raise ValueError("User is not a participant of this event")

        # Remove participant using the method in the model (which targets active_events_collection)
        success = Event.remove_participant(event_id, user_id)
        
        if not success:
            raise Exception("Failed to remove participant from event")
            
        return {'message': 'Successfully left event'}

    @staticmethod
    def kick_participant(event_id, host_user_id, participant_user_id_to_kick):
        """Handle a host kicking a participant from an event. This now targets active events."""
        # Find the event in the active collection
        try:
            event_obj = active_events_collection.find_one({'_id': ObjectId(event_id)})
        except:
            raise ValueError("Invalid Event ID")

        if not event_obj:
            raise ValueError("Event not found or not active")
            
        # Check if the host_user_id is the actual host of the event
        if event_obj.get('user_id') != ObjectId(host_user_id):
             raise ValueError("Only the event host can kick participants")

        # Check if the participant to kick is in the participants list
        if ObjectId(participant_user_id_to_kick) not in event_obj.get('participants', []):
            raise ValueError("Participant to kick is not in this event")
            
        # Check if the host is trying to kick themselves (optional but good to prevent)
        if ObjectId(host_user_id) == ObjectId(participant_user_id_to_kick):
             raise ValueError("Host cannot kick themselves")

        # Remove participant using the method in the model (which targets active_events_collection)
        success = Event.remove_participant(event_id, participant_user_id_to_kick)
        
        if not success:
            raise Exception("Failed to remove participant from event")
            
        return {'message': 'Successfully kicked participant'}

    @staticmethod
    def get_event_participants(event_id):
        """Get participants for a specific active event."""
        # Find the event in the active collection
        try:
            event_obj = active_events_collection.find_one({'_id': ObjectId(event_id)})
        except:
            raise ValueError("Invalid Event ID")

        if not event_obj:
            raise ValueError("Event not found or not active")

        participant_ids = event_obj.get('participants', [])
        participants_details = []
        for p_id in participant_ids:
            user = User.find_by_id(str(p_id))
            if user:
                participants_details.append({
                    '_id': str(user.get('_id')),
                    'name': user.get('name'),
                    'photo_url': user.get('photo_url')
                })
        return participants_details

    @staticmethod
    def submit_rating(event_id, rater_user_id, rated_user_id, rating, comment=None):
        """Submit a rating and optional comment for a participant in an event."""
        # Ensure the event is in the active or archived collection to allow rating
        event_obj = active_events_collection.find_one({'_id': ObjectId(event_id)})
        if not event_obj:
            event_obj = archived_events_collection.find_one({'_id': ObjectId(event_id)})
        
        if not event_obj:
            raise ValueError("Event not found in active or archived states")

        # Check if rater_user_id is a participant of the event or the host
        if ObjectId(rater_user_id) not in event_obj.get('participants', []) and event_obj.get('user_id') != ObjectId(rater_user_id):
            raise ValueError("Only participants or the host can rate for this event")
            
        # Check if rated_user_id is a participant of the event or the host
        is_rated_participant = ObjectId(rated_user_id) in event_obj.get('participants', [])
        is_rated_host = event_obj.get('user_id') == ObjectId(rated_user_id)
        
        if not is_rated_participant and not is_rated_host:
             raise ValueError("User being rated is not a participant or host of this event")

        # Check if rater is trying to rate themselves
        if ObjectId(rater_user_id) == ObjectId(rated_user_id):
            raise ValueError("Cannot rate yourself")

        # Validate the rating value (e.g., between 1 and 5)
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            raise ValueError("Invalid rating value")

        # Update the user's rating using the User model
        success = User.update_rating(rated_user_id, rating, comment)
        if not success:
            raise Exception("Failed to update user rating")

        return {'message': 'Rating submitted successfully'}

    @staticmethod
    def get_host_event_details(event_id, host_id):
        """Get detailed event information for host including participants and pending requests."""
        # Get event details from active events
        event = EventService.get_event(host_id, event_id)
        if not event:
            raise ValueError("Event not found")

        # Verify if the user is the host
        if str(event.get('user_id')) != host_id:
            raise ValueError("You are not the host of this event")

        # Get participants details
        participants = []
        for participant_id in event.get('participants', []):
            user = User.find_by_id(str(participant_id))
            if user:
                participants.append({
                    '_id': str(user.get('_id')),
                    'name': user.get('name'),
                    'photo_url': user.get('photo_url'),
                    'type': 'participant'
                })

        # Get pending requests
        from src.services.event_request_service import EventRequestService
        pending_requests = EventRequestService.get_host_pending_requests(host_id)
        
        # Filter requests for this specific event
        event_pending_requests = []
        for req in pending_requests:
            if str(req.get('event_id')) == str(event_id):
                user = User.find_by_id(str(req.get('user_id')))
                if user:
                    event_pending_requests.append({
                        '_id': str(req.get('_id')),
                        'user': {
                            '_id': str(user.get('_id')),
                            'name': user.get('name'),
                            'photo_url': user.get('photo_url')
                        },
                        'type': 'pending_request',
                        'created_at': req.get('created_at')
                    })

        # Combine all data
        event_details = event  
        event_details['participants'] = participants
        event_details['pending_requests'] = event_pending_requests

        return event_details