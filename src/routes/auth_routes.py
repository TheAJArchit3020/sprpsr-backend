from flask import Blueprint
from src.controllers.auth_controller import AuthController


# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Register routes
@auth_bp.route('/check-user', methods=['POST'])
def check_user():
    return AuthController.check_user()

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    return AuthController.verify_otp() 

