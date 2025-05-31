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
        try:
            print(id_token)       
            decoded_token = verify_firebase_token(id_token)
            print("token decoded:", decoded_token)
            phone_number = decoded_token.get('phone_number')
        except Exception as e:
            raise ValueError('Error verifying token: {}'.format(str(e)))
            

        
        if not phone_number:
            raise ValueError('Phone number not found in token')
        
        # Check if user exists
        print("phone_number", phone_number," ",type(phone_number))
        user = User.find_by_phone(str(phone_number))
        print("user", user)
    
        if user:
            # Existing user - generate JWT
            print("user_id", str(user['_id']))
            token = generate_token(str(user['_id']))
            print("token", token)
            return {
                'message': 'Login successful',
                'token': token
            }
        else:
            # New user - create profile
            if not profile:
                raise ValueError('Profile information required for new users')
            
            print("profile", profile)
            user_id = User.create(phone_number, profile)
            print("user_id", user_id)
            token = generate_token(user_id)
            
            return {
                'message': 'Registration successful',
                'token': token
            } 