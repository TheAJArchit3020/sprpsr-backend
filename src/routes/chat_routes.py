from flask import Blueprint
from src.controllers.chat_controller import ChatController
from src.middleware.auth_middleware import token_required

chat_bp = Blueprint('chat', __name__)

# Post a message to an event chat
@chat_bp.route('/events/<event_id>/chat', methods=['POST'])
@token_required
def post_event_message(event_id):
    """
    Post a message to an event chat
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              description: Chat message content
              example: "Hey everyone! Looking forward to the event!"
    responses:
      200:
        description: Message sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Message sent successfully"
            message_id:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not a participant of the event
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return ChatController.post_message(event_id)

# Get all chat messages for an event
@chat_bp.route('/events/<event_id>/chat', methods=['GET'])
@token_required
def get_event_chats(event_id):
    """
    Get all chat messages for an event
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: path
        name: event_id
        type: string
        required: true
        description: ID of the event
    responses:
      200:
        description: List of chat messages
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              event_id:
                type: string
              user_id:
                type: string
              message:
                type: string
              created_at:
                type: string
                format: date-time
              user:
                type: object
                properties:
                  _id:
                    type: string
                  name:
                    type: string
                  photo_url:
                    type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not a participant of the event
      404:
        description: Event not found
      500:
        description: Internal server error
    """
    return ChatController.get_event_chats(event_id) 