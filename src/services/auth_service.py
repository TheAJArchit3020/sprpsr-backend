from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token
from src.utils.firebase_storage import upload_to_firebase

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