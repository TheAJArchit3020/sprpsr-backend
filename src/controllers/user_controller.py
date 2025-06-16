from flask import jsonify, request
from src.services.user_service import UserService
from src.middleware.auth_middleware import token_required
import json # Import json to parse the update data string

class UserController:
    @staticmethod
    @token_required # Protect this endpoint with auth middleware
    def update_profile():
        """Update authenticated user's profile."""
        user_id = request.user_id 

        # Profile update data is sent as a JSON string within form-data
        update_data_str = request.form.get('update_data')
        photo = request.files.get('photo') if request.files else None

        update_data = {}
        if update_data_str:
            try:
                update_data = json.loads(update_data_str)
            except json.JSONDecodeError:
                 return jsonify({'error': 'Invalid update data JSON format'}), 400

        # Ensure at least some update data or a photo is provided
        if not update_data and not photo:
             return jsonify({'error': 'No update data or photo provided'}), 400
             
        try:
            # Call the UserService to update the profile
            updated_user_profile = UserService.update_profile(user_id, update_data, photo)
            return jsonify(updated_user_profile), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def get_public_profile(user_id):
        """Get a user's public profile including ratings and comments."""
        try:
            user_profile = UserService.get_user_profile_with_ratings(user_id)
            if user_profile:
                return jsonify(user_profile), 200
            return jsonify({'message': 'User not found'}), 404
        except Exception as e:
            return jsonify({'message': 'An error occurred while fetching user profile', 'error': str(e)}), 500

    @staticmethod
    @token_required
    def get_participants_by_event(event_id):
        """Get all participants for a specific event."""
        requesting_user_id = request.user_id # Get user ID from the token
        try:
            participants = UserService.get_participants_by_event(event_id, requesting_user_id)
            return jsonify(participants), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400 # Changed 404 to 400 for more specific error
        except Exception as e:
            return jsonify({'message': 'An error occurred while fetching participants', 'error': str(e)}), 500 