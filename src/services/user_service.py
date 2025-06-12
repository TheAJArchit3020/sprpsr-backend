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
            user_profile = User.get_profile_with_ratings(user_id)
            if not user_profile:
                return None

            # Return only necessary fields
            return {
                '_id': user_profile['_id'],
                'name': user_profile.get('name'),
                'photo_url': user_profile.get('photo_url'),
                'ratings': user_profile.get('ratings', {
                    'total_ratings': 0,
                    'average_rating': 0,
                    'ratings_given': 0
                }),
                'comments': user_profile.get('comments', [])
            }
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None