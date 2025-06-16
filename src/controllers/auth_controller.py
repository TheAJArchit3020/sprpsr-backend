from flask import jsonify, request
from src.services.auth_service import AuthService
from src.middleware.auth_middleware import token_required
import json

class AuthController:
    @staticmethod
    def check_user():
        """Handle user existence check request."""
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        try:
            result = AuthService.check_user(phone)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    
    @staticmethod
    def verify_otp():
        """Handle OTP verification and user authentication."""
        # Get data from form-data
        id_token = request.form.get('idToken')
        # The profile data is sent as a string, so we need to parse it
        profile_str = request.form.get('profile')
        profile = None
        if profile_str and profile_str.strip():
            try:
                profile = json.loads(profile_str)
            except json.JSONDecodeError:
                 return jsonify({'error': 'Invalid profile JSON format'}), 400
                 
        photo = request.files.get('photo') if request.files else None
        
        if not id_token:
            return jsonify({'error': 'ID token is required'}), 400
            
        # Ensure profile data is present for new users if no photo is provided
        # This check is now handled in the service, but good to have a basic check here.
        # if not profile and not photo:
        #      return jsonify({'error': 'Profile information or photo required for new users'}), 400
        
        try:
            result = AuthService.verify_and_authenticate(id_token, profile, photo)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 

    @staticmethod
    @token_required 
    def update_location():
        """Update the authenticated user\'s location."""
        data = request.get_json()
        user_id = request.user_id 
        location_data = data.get('location')

        if not location_data:
            return jsonify({'error': 'Location data is required'}), 400

        try:
            result = AuthService.update_user_location(user_id, location_data)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 

    @staticmethod
    def create_test_user():
        """Create a test user for testing purposes."""
        data = request.get_json()
        phone = data.get('phone')
        profile = data.get('profile') 

        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        try:
            result = AuthService.create_test_user(phone, profile)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 

    @staticmethod
    def sign_in_test_user():
        """Sign in a test user by phone number."""
        data = request.get_json()
        phone = data.get('phone')

        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400

        try:
            result = AuthService.sign_in_test_user(phone)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 