from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token
from src.utils.firebase_storage import upload_to_firebase
from bson.objectid import ObjectId

class AuthService:
    @staticmethod
    def check_user(phone):
        """Check if user exists."""
        user = User.find_by_phone(phone)
        return {'exists': bool(user)}
    
    @staticmethod
    def verify_and_authenticate(id_token, profile=None, photo=None):
        """Verify Firebase token and handle user authentication."""
        # Verify Firebase token
        try:      
            decoded_token = verify_firebase_token(id_token)
            phone_number = decoded_token.get('phone_number')
        except Exception as e:
            raise ValueError('Error verifying token: {}'.format(str(e)))
        
        if not phone_number:
            raise ValueError('Phone number not found in token')
    
        user = User.find_by_phone(str(phone_number))
    
        if user:
            token = generate_token(str(user['_id']))
            return {
                'message': 'Login successful',
                'token': token
            }
        else:
            # New user - create profile
            if not profile:
                raise ValueError('Profile information required for new users')
            
            # Handle photo upload if present
            if photo:
                try:
                    photo_url = upload_to_firebase(photo)
                    profile['photo_url'] = photo_url
                except Exception as e:
                    raise ValueError(f'Error uploading photo: {str(e)}')
            
            user_id = User.create(phone_number, profile)
            token = generate_token(user_id)
            
            return {
                'message': 'Registration successful',
                'token': token,
                'profile': profile
            }

    @staticmethod
    def update_user_location(user_id, location_data):
        """Update the authenticated user\'s location."""
        # Validate location data format (GeoJSON Point)
        if not isinstance(location_data, dict) or location_data.get('type') != 'Point' or not isinstance(location_data.get('coordinates'), list) or len(location_data['coordinates']) != 2:
             raise ValueError("Invalid GeoJSON Point format for location")
             
        # You might want to add more validation for longitude and latitude values here

        success = User.update_location(user_id, location_data)
        if not success:
            raise Exception("Failed to update user location in database")
            
        return {'message': 'User location updated successfully'}

    @staticmethod
    def create_test_user(phone, profile=None):
        """Create a test user without OTP verification and generate a token."""
        # Check if user already exists by phone
        existing_user = User.find_by_phone(phone)
        if existing_user:
            return {
                'message': 'User with this phone number already exists',
                'user_id': str(existing_user['_id'])
            }
        
        # Create the new user
        # We assume profile data might include location or photo_url directly
        user_id = User.create(phone, profile if profile is not None else {})
        
        # Generate a JWT token for the new user
        token = generate_token(user_id)
        
        return {
            'message': 'Test user created successfully',
            'user_id': str(user_id),
            'token': token,
            'profile': profile # Return profile data if provided
        }

    @staticmethod
    def sign_in_test_user(phone):
        """Sign in a test user by phone number and return a token."""
        user = User.find_by_phone(phone)
        if not user:
            raise ValueError("User with this phone number not found")

        token = generate_token(str(user['_id']))
        return {
            "message": "Sign in successful",
            "token": token,
            "user_id": str(user['_id'])
        } 