from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token
from src.utils.firebase_storage import upload_to_firebase
from bson.objectid import ObjectId

class AuthService:
    # ... (existing methods: check_user, verify_and_authenticate, update_user_location, create_test_user, sign_in_test_user) ...
    pass # Placeholder for now

# New UserService for user-specific operations
class UserService:
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