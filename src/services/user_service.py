from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token
from src.utils.firebase_storage import upload_to_firebase
from bson.objectid import ObjectId
from datetime import datetime
from src.config.database import get_database

class AuthService:
    # ... (existing methods: check_user, verify_and_authenticate, update_user_location, create_test_user, sign_in_test_user) ...
    pass # Placeholder for now

# New UserService for user-specific operations
class UserService:
    @staticmethod
    def create_user(firebase_uid, phone_number=None, name=None):
        """Creates a new user in the database."""
        db = get_database()
        users_collection = db.users
        
        existing_user = users_collection.find_one({'firebase_uid': firebase_uid})
        if existing_user:
            raise ValueError("User with this Firebase UID already exists")
            
        new_user = {
            'firebase_uid': firebase_uid,
            'phone_number': phone_number,
            'name': name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(new_user)
        # Return the inserted user with _id as string
        new_user['_id'] = str(result.inserted_id)
        return new_user

    @staticmethod
    def get_user_by_firebase_uid(firebase_uid):
        """Finds a user by their Firebase UID."""
        db = get_database()
        users_collection = db.users
        user = users_collection.find_one({'firebase_uid': firebase_uid})
        return User.serialize(user) if user else None

    @staticmethod
    def get_user_by_id(user_id):
        """Finds a user by their MongoDB _id."""
        db = get_database()
        users_collection = db.users
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            return User.serialize(user) if user else None
        except:
            return None # Handle invalid ObjectId

    @staticmethod
    def update_profile(user_id, update_data, photo=None):
        """Update user profile, including optional photo upload."""
        # Handle photo upload if present
        if photo:
            try:
                # Upload photo to Firebase Storage
                photo_url = upload_to_firebase(photo, folder='profile_photos')
                # Add the photo URL to the update data
                update_data['photo_url'] = photo_url
            except Exception as e:
                raise ValueError(f'Error uploading profile photo: {str(e)}')

        # Update the user document in the database using the User model
        success = User.update(user_id, update_data)

        if not success:
             raise Exception("Failed to update user profile in database")

        # Fetch the updated user to return the latest profile data
        updated_user = User.find_by_id(user_id)

        # Serialize the updated user data for the response
        return User.serialize(updated_user)

    @staticmethod
    def get_user_profile_with_ratings(user_id):
        """Get user profile with rating information."""
        try:
            user = User.find_by_id(user_id) # Use User model's find_by_id
            if not user:
                return None

            # Serialize the user data first
            user_dict = User.serialize(user)

            # Ensure rating fields exist (if not already handled by serialize or model)
            if 'rating' not in user_dict: # Check for rating field directly
                user_dict['rating'] = 0
            if 'rating_count' not in user_dict:
                user_dict['rating_count'] = 0
            if 'total_rating' not in user_dict:
                user_dict['total_rating'] = 0
            if 'comments' not in user_dict:
                user_dict['comments'] = []
            if 'events_organized' not in user_dict:
                user_dict['events_organized'] = 0
            if 'latest_events' not in user_dict:
                user_dict['latest_events'] = []

            # Populate latest_events with event names
            if 'latest_events' in user_dict and user_dict['latest_events']:
                from src.models.event import Event # Import Event model locally
                detailed_latest_events = []
                for event_id_obj in user_dict['latest_events']:
                    # Ensure event_id_obj is an ObjectId. If it's a string, convert it.
                    event = Event.find_by_id(str(event_id_obj))
                    if event:
                        detailed_latest_events.append({
                            '_id': str(event['_id']),
                            'title': event.get('title', 'Unknown Event')
                        })
                user_dict['latest_events'] = detailed_latest_events

            # Comments should already be formatted if coming from User.serialize and updated correctly
            # Re-format dates in comments just in case, or if they were added manually without formatting
            if 'comments' in user_dict and user_dict['comments']:
                for comment in user_dict['comments']:
                    if 'created_at' in comment and isinstance(comment['created_at'], datetime):
                        comment['created_at'] = comment['created_at'].isoformat()

            return user_dict
        except Exception as e: # Catching specific exception
            print(f"Error in get_user_profile_with_ratings: {e}") # Log the actual error
            return None

    @staticmethod
    def get_participants_by_event(event_id, requesting_user_id):
        """Get all participants for a given event, fetching their public profiles, with status and authorization checks."""
        from src.models.event import Event # Import locally to avoid circular dependency

        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        # 1. Check Event Status: Only allow for upcoming or active events
        event_status = event.get('status')
        if event_status not in ['upcoming', 'active']:
            raise ValueError("Cannot view participants for an event that is not upcoming or active.")

        # 2. Check User Authorization: User must be a participant or the host
        event_host_id = str(event.get('user_id'))
        event_participants = [str(p_id) for p_id in event.get('participants', [])]

        if requesting_user_id != event_host_id and requesting_user_id not in event_participants:
            raise ValueError("Unauthorized: You must be a participant or the host of this event to view participants.")

        participant_ids = event.get('participants', [])
        participants_details = []
        for p_id in participant_ids:
            user = User.find_by_id(str(p_id)) # Use User.find_by_id to get user details
            if user:
                participants_details.append(User.serialize(user)) # Serialize user for consistent output
        return participants_details