from flask import jsonify, request
from src.services.event_request_service import EventRequestService
from src.middleware.auth_middleware import token_required

class EventRequestController:
    @staticmethod
    @token_required
    def create_join_request(event_id):
        """Create a join request for a private event."""
        user_id = request.user_id  # From auth middleware
        
        try:
            result = EventRequestService.create_join_request(event_id, user_id)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def get_pending_requests():
        """Get all pending requests for the authenticated host."""
        host_id = request.user_id  # From auth middleware
        
        try:
            requests = EventRequestService.get_host_pending_requests(host_id)
            return jsonify(requests), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @token_required
    def handle_request(request_id):
        """Handle (accept/reject) a join request."""
        host_id = request.user_id  # From auth middleware
        data = request.get_json()
        action = data.get('action')
        
        if not action or action not in ['accept', 'reject']:
            return jsonify({'error': 'Invalid action. Use "accept" or "reject"'}), 400
            
        try:
            result = EventRequestService.handle_request(request_id, host_id, action)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500 