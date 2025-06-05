from flask import Blueprint, request, jsonify
from src.controllers.user_controller import UserController
from src.middleware.auth_middleware import token_required

user_bp = Blueprint('user_bp', __name__, url_prefix='/api')

# Define user routes
user_bp.route('/user/profile', methods=['PUT'])(UserController.update_profile)
user_bp.route('/users/<user_id>', methods=['GET'])(UserController.get_public_profile) 