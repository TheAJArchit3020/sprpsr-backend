from flask import jsonify, request
from src.services.chat_service import ChatService
from src.middleware.auth_middleware import token_required

class ChatController:
    @staticmethod
    @token_required
    def post_message(event_id):
        """Post a new message to an event chat."""
        user_id = request.user_id  # From auth middleware
        data = request.get_json()
        message = data.get('message')

        if not message:
            return jsonify({'error': 'Message content is required'}), 400

        try:
            result = ChatService.post_message(event_id, user_id, message)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def get_event_chats(event_id):
        """Get all chat messages for a specific event."""
        user_id = request.user_id  # From auth middleware

        try:
            messages = ChatService.get_event_messages(event_id, user_id)
            return jsonify(messages), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 