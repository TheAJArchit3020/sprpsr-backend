from flask import jsonify, request
from src.services.auth_service import AuthService

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
        data = request.get_json()
        id_token = data.get('idToken')
        profile = data.get('profile')
        
        if not id_token:
            return jsonify({'error': 'ID token is required'}), 400
        
        try:
            result = AuthService.verify_and_authenticate(id_token, profile)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 