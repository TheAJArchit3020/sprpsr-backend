from src.models.user import User
from src.utils.firebase import verify_firebase_token
from src.utils.jwt import generate_token

class AuthService:
    @staticmethod
    def check_user(phone):
        """Check if user exists and return appropriate status."""
        user = User.find_by_phone(phone)
        
        if user:
            return {
                'status': 'login',
                'message': 'Send OTP'
            }
        return {
            'status': 'register',
            'message': 'Collect profile info and send OTP'
        }
    
    @staticmethod
    def verify_and_authenticate(id_token, profile=None):
        """Verify Firebase token and handle user authentication."""
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        phone_number = decoded_token.get('phone_number')
        
        if not phone_number:
            raise ValueError('Phone number not found in token')
        
        # Check if user exists
        user = User.find_by_phone(phone_number)
        
        if user:
            # Existing user - generate JWT
            token = generate_token(user['_id'])
            return {
                'message': 'Login successful',
                'token': token
            }
        else:
            # New user - create profile
            if not profile:
                raise ValueError('Profile information required for new users')
            
            user_id = User.create(phone_number, profile)
            token = generate_token(user_id)
            
            return {
                'message': 'Registration successful',
                'token': token
            } 