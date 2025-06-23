from flask import Blueprint, request, jsonify
from src.controllers.user_controller import UserController
from src.middleware.auth_middleware import token_required
from flasgger import swag_from

user_bp = Blueprint('user_bp', __name__, url_prefix='/api')

# Define user routes
@user_bp.route('/user/profile', methods=['PUT'])
@swag_from({
    'tags': ['User'],
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'in': 'formData',
            'name': 'update_data',
            'type': 'string',
            'required': False,
            'description': 'JSON string with profile fields to update'
        },
        {
            'in': 'formData',
            'name': 'photo',
            'type': 'file',
            'required': False,
            'description': 'Profile photo to upload'
        }
    ],
    'responses': {
        200: {
            'description': 'Profile updated successfully'
        },
        400: {
            'description': 'Bad request (invalid data or no data provided)'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def update_profile():
    return UserController.update_profile()

@user_bp.route('/users/<user_id>', methods=['GET'])
@swag_from({
    'tags': ['User'],
    'parameters': [
        {
            'in': 'path',
            'name': 'user_id',
            'type': 'string',
            'required': True,
            'description': 'The ID of the user to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'User profile found'
        },
        404: {
            'description': 'User not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_public_profile(user_id):
    return UserController.get_public_profile(user_id)

@user_bp.route('/events/<event_id>/participants', methods=['GET'])
@swag_from({
    'tags': ['User'],
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
        200: {
            'description': 'A list of event participants.',
            'schema': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/UserProfile'
                }
            }
        },
        404: {
            'description': 'Event not found or no participants found for the event.'
        },
        500: {
            'description': 'Internal server error.'
        }
    },
    'security': [{
        'BearerAuth': []
    }]
})
@token_required
def get_participants_by_event(event_id):
    return UserController.get_participants_by_event(event_id)

@user_bp.route('/user/profile', methods=['GET'])
@swag_from({
    'tags': ['User'],
    'summary': 'Get own user profile',
    'description': 'Get the authenticated user\'s own profile using the user ID from the token.',
    'responses': {
        200: {
            'description': 'User profile found',
            'schema': {
                'type': 'object',
                'properties': {
                    '_id': {'type': 'string'},
                    'name': {'type': 'string'},
                    'photo_url': {'type': 'string'},
                    'rating': {'type': 'number'},
                    'rating_count': {'type': 'integer'},
                    'total_rating': {'type': 'number'},
                    'comments': {'type': 'array', 'items': {'type': 'object'}},
                    'events_organized': {'type': 'integer'},
                    'latest_events': {'type': 'array', 'items': {'type': 'object'}},
                }
            }
        },
        404: {
            'description': 'User not found'
        },
        500: {
            'description': 'Internal server error'
        }
    },
    'security': [{
        'BearerAuth': []
    }]
})
@token_required
def get_own_profile():
    return UserController.get_own_profile() 