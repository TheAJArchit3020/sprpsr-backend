from flask import Blueprint
from src.controllers.auth_controller import AuthController


# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Register routes
@auth_bp.route('/auth/check-user', methods=['POST'])
def check_user():
    return AuthController.check_user()

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    return AuthController.verify_otp()

@auth_bp.route('/auth/update-location', methods=['PUT'])
def update_location():
    return AuthController.update_location()

@auth_bp.route('/auth/test-user', methods=['POST'])
def create_test_user():
    return AuthController.create_test_user()

@auth_bp.route('/auth/sign-in-test', methods=['POST'])
def sign_in_test_user():
    return AuthController.sign_in_test_user()

# 25.352327526796028, 74.62764455450775