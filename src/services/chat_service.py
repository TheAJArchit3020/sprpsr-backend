from src.models.chat_message import ChatMessage
from src.models.event import Event
from src.models.user import User # Assuming User model exists and has find_by_id
from bson import ObjectId

class ChatService:
    @staticmethod
    def post_message(event_id, user_id, message):
        """Post a new message to an event chat."""
        # Check if the user is a participant of the event
        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
            
        # Ensure user_id is ObjectId for comparison
        try:
            user_obj_id = ObjectId(user_id)
        except:
             raise ValueError("Invalid User ID format")
             
        # Check if user is host or a participant
        is_host = event.get('user_id') == user_obj_id
        is_participant = user_obj_id in event.get('participants', [])
        
        if not is_host and not is_participant:
            raise ValueError("You must be a participant of this event to chat")

        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
            
        # Create the message
        message_id = ChatMessage.create(event_id, user_id, message.strip())
        return {'message': 'Message sent successfully', 'message_id': message_id}

    @staticmethod
    def get_event_messages(event_id, user_id):
        """Get chat messages for an event if the user is a participant."""
        # Check if the user is a participant of the event
        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
            
        # Ensure user_id is ObjectId for comparison
        try:
            user_obj_id = ObjectId(user_id)
        except:
             raise ValueError("Invalid User ID format")
             
        # Check if user is host or a participant
        is_host = event.get('user_id') == user_obj_id
        is_participant = user_obj_id in event.get('participants', [])
        
        if not is_host and not is_participant:
            raise ValueError("You must be a participant of this event to view chat")

        # Get messages for the event
        messages = ChatMessage.get_messages_for_event(event_id)
        
        # Enhance messages with user details
        enhanced_messages = []
        for message in messages:
            # Get user details
            user = User.find_by_id(str(message.get('user_id')))
            if user:
                enhanced_message = message.copy()
                enhanced_message['user'] = {
                    '_id': str(user.get('_id')),
                    'name': user.get('name'),
                    'photo_url': user.get('photo_url')
                }
                enhanced_messages.append(enhanced_message)
            else:
                # If user not found, still include message but with minimal user info
                enhanced_message = message.copy()
                enhanced_message['user'] = {
                    '_id': str(message.get('user_id')),
                    'name': 'Unknown User',
                    'photo_url': None
                }
                enhanced_messages.append(enhanced_message)

        return enhanced_messages 