from datetime import datetime
from bson import ObjectId
from src.config.database import get_database
import pytz

db = get_database()
chat_messages_collection = db['chatMessages']

class ChatMessage:
    @staticmethod
    def create(event_id, user_id, message):
        """Create a new chat message."""
        # Store timestamp in IST
        ist = pytz.timezone('Asia/Kolkata')
        timestamp_ist = datetime.now(ist)

        new_message = {
            'event_id': ObjectId(event_id),
            'user_id': ObjectId(user_id),
            'message': message,
            'timestamp': timestamp_ist,
        }
        
        result = chat_messages_collection.insert_one(new_message)
        return str(result.inserted_id)

    @staticmethod
    def get_messages_for_event(event_id):
        """Get all chat messages for a specific event, sorted by timestamp."""
        try:
            messages = list(chat_messages_collection.find({
                'event_id': ObjectId(event_id)
            }).sort('timestamp', 1))
            return [ChatMessage._serialize_message(msg) for msg in messages]
        except:
            return []

    @staticmethod
    def _serialize_message(message):
        """Convert MongoDB message document to JSON-serializable format."""
        if not message:
            return None
            
        message_dict = message.copy()
        message_dict['_id'] = str(message_dict['_id'])
        message_dict['event_id'] = str(message_dict['event_id'])
        message_dict['user_id'] = str(message_dict['user_id'])
        
        if 'timestamp' in message_dict and isinstance(message_dict['timestamp'], datetime):
            message_dict['timestamp'] = message_dict['timestamp'].isoformat()
            
        return message_dict 