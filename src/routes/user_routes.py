from flask import Blueprint
from src.controllers.user_controller import UserController

user_bp = Blueprint('user', __name__)

# Define user routes
user_bp.route('/user/profile', methods=['PUT'])(UserController.update_profile) 