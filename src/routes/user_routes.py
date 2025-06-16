from flask import Blueprint, request, jsonify
from src.controllers.user_controller import UserController
from src.middleware.auth_middleware import token_required

user_bp = Blueprint('user_bp', __name__, url_prefix='/api')

# Define user routes
user_bp.route('/user/profile', methods=['PUT'])(UserController.update_profile)
user_bp.route('/users/<user_id>', methods=['GET'])(UserController.get_public_profile)
user_bp.route('/events/<event_id>/participants', methods=['GET'])(UserController.get_participants_by_event)

# Swagger documentation for /api/events/<event_id>/participants
user_bp.route('/events/<event_id>/participants', methods=['GET'])( 
    token_required(
        user_bp.add_url_rule(
            '/events/<event_id>/participants',
            'get_participants_by_event_docs',
            lambda event_id:
                jsonify({
                    'description': 'Retrieve a list of participants for a specific event.',
                    'parameters': [
                        {
                            'name': 'event_id',
                            'in': 'path',
                            'type': 'string',
                            'required': True,
                            'description': 'The ID of the event to retrieve participants for.'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'A list of event participants.',
                            'schema': {
                                'type': 'array',
                                'items': {
                                    '$ref': '#/definitions/UserProfile'
                                }
                            }
                        },
                        '404': {
                            'description': 'Event not found or no participants found for the event.'
                        },
                        '500': {
                            'description': 'Internal server error.'
                        }
                    },
                    'security': [{
                        'BearerAuth': []
                    }]
                })
        )
    )
) 