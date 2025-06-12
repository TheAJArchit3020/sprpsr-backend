from flask import Blueprint
from src.controllers.auth_controller import AuthController
from src.middleware.auth_middleware import token_required


# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Register routes
@auth_bp.route('/auth/check-user', methods=['POST'])
def check_user():
    """
    Check if a user exists with the given phone number
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - phone
          properties:
            phone:
              type: string
              description: Phone number to check
              example: "+919876543210"
    responses:
      200:
        description: User existence check result
        schema:
          type: object
          properties:
            exists:
              type: boolean
              description: Whether the user exists
              example: true
      400:
        description: Bad request - Phone number is required
        schema:
          type: object
          properties:
            error:
              type: string
              example: Phone number is required
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return AuthController.check_user()

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP and authenticate user
    ---
    tags:
      - Authentication
    parameters:
      - in: formData
        name: idToken
        type: string
        required: true
        description: Firebase ID token
      - in: formData
        name: profile
        type: string
        required: false
        description: JSON string containing user profile data for new users
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            photo_url:
              type: string
      - in: formData
        name: photo
        type: file
        required: false
        description: User profile photo
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            token:
              type: string
              description: JWT token for authenticated user
            profile:
              type: object
              description: User profile data (only for new users)
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
              example: ID token is required
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return AuthController.verify_otp()

@auth_bp.route('/auth/update-location', methods=['PUT'])
@token_required
def update_location():
    """
    Update user's location
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - location
          properties:
            location:
              type: object
              description: GeoJSON Point format location data
              properties:
                type:
                  type: string
                  example: Point
                coordinates:
                  type: array
                  items:
                    type: number
                  example: [74.62764455450775, 25.352327526796028]
                  description: [longitude, latitude]
    responses:
      200:
        description: Location updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User location updated successfully
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
              example: Location data is required
      401:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid or missing token
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return AuthController.update_location()

@auth_bp.route('/auth/test-user', methods=['POST'])
def create_test_user():
    return AuthController.create_test_user()

@auth_bp.route('/auth/sign-in-test', methods=['POST'])
def sign_in_test_user():
    return AuthController.sign_in_test_user()

# 25.352327526796028, 74.62764455450775