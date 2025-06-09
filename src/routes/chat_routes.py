from flask import Blueprint
from src.controllers.chat_controller import ChatController

chat_bp = Blueprint('chat', __name__)

# Post a message to an event chat
@chat_bp.route('/events/<event_id>/chat', methods=['POST'])
def post_event_message(event_id):
    return ChatController.post_message(event_id)

# Get all chat messages for an event
@chat_bp.route('/events/<event_id>/chat', methods=['GET'])
def get_event_chats(event_id):
    return ChatController.get_event_chats(event_id) 