from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token
from src.utils.firebase_storage import upload_to_firebase
from bson.objectid import ObjectId
from datetime import datetime
from src.config.database import get_database
from src.models.rating import Rating

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
        """Fetches a user's profile including their average rating and latest comments."""
        user_obj = User.find_by_id(user_id)
        if user_obj:
            # Convert ObjectId to string for consistent data structure
            user_obj['_id'] = str(user_obj['_id'])

            # Fetch average rating
            average_rating_result = Rating.calculate_average_rating(user_id)
            # The aggregation pipeline might return an empty list if no ratings exist
            average_rating = average_rating_result['average_rating'] if average_rating_result else 0.0
            user_obj['average_rating'] = average_rating

            # Fetch latest comments
            latest_comments = Rating.find_latest_for_user(user_id)
            # Serialize ObjectIds in comments if necessary
            serialized_comments = []
            for comment in latest_comments:
                # The Rating.find_latest_for_user method already serializes ObjectIds
                # We just need to ensure the structure is as expected if not already.
                # Based on the model, it should return serialized data.
                serialized_comments.append(comment)

            user_obj['latest_comments'] = serialized_comments

            return user_obj
        return None