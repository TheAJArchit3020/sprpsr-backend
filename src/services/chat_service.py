from src.models.chat_message import ChatMessage
from src.models.event import Event
from src.models.user import User # Assuming User model exists and has find_by_id
from bson import ObjectId
from datetime import datetime, timedelta
from src.config.database import get_database
from src.models.feedback import Feedback
import pytz
from dateutil import parser

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
        """Get all chat messages for a specific event."""
        # First check if the event is old enough to be archived
        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        # Check if event is more than 48 hours old
        event_end_time = event.get('end_time')
        if event_end_time:
            # Parse the event end time and ensure it's timezone-aware
            event_end = parser.isoparse(str(event_end_time))
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=pytz.utc)
            
            # Get current time in UTC
            current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
            
            hours_since_end = (current_time - event_end).total_seconds() / 3600

            if hours_since_end >= 48:
                # Get all feedbacks for this event BEFORE archiving
                feedbacks = Feedback.get_feedbacks_for_event(event_id)
                
                # Group feedbacks by rated user
                user_feedbacks = {}
                for feedback in feedbacks:
                    rated_user_id = str(feedback['rated_user_id'])
                    if rated_user_id not in user_feedbacks:
                        user_feedbacks[rated_user_id] = []
                    user_feedbacks[rated_user_id].append(feedback)
                
                # Update each user's ratings and event counts
                for rated_user_id, user_feedback_list in user_feedbacks.items():
                    # Get all feedbacks for this user (including archived ones)
                    all_user_feedbacks = Feedback.get_feedbacks_for_user(rated_user_id)
                    
                    # Calculate total rating and count from all feedbacks
                    total_rating = sum(feedback['rating'] for feedback in all_user_feedbacks)
                    rating_count = len(all_user_feedbacks)
                    avg_rating = total_rating / rating_count if rating_count > 0 else 0
                    
                    # Get unique events the user has participated in
                    unique_events = set(str(feedback['event_id']) for feedback in all_user_feedbacks)
                    events_completed = len(unique_events)
                    
                    # Get all comments from feedbacks
                    comments = []
                    for feedback in all_user_feedbacks:
                        if feedback.get('comment'):
                            comments.append({
                                'comment': feedback['comment'],
                                'created_at': feedback['created_at']
                            })
                    # Keep only last 5 comments, sorted by date
                    comments = sorted(comments, key=lambda x: x['created_at'], reverse=True)[:5]
                    
                    # Get events organized by this user
                    organized_events = Event.find_by_user_id_as_host(rated_user_id)
                    events_organized_count = len(organized_events)
                    
                    # Get the 5 latest organized event IDs
                    latest_organized_events = sorted(organized_events, key=lambda x: x.get('created_at', datetime.min), reverse=True)[:5]
                    latest_organized_event_ids = [event['_id'] for event in latest_organized_events]

                    # Update user document
                    User.update(rated_user_id, {
                        'rating': avg_rating,
                        'rating_count': rating_count,
                        'total_rating': total_rating,
                        'events_completed': events_completed,
                        'comments': comments,
                        'events_organized': events_organized_count,
                        'latest_events': latest_organized_event_ids
                    })
                
                # AFTER updating all users, archive the feedbacks
                Feedback.archive_feedbacks(event_id)
                
                # Move event to archived collection
                Event.move_to_archived(event_id)

        # Get messages from both active and archived collections
        messages = ChatMessage.get_messages_for_event(event_id)
        
        # Format messages with user details
        formatted_messages = []
        for message in messages:
            user = User.find_by_id(str(message['user_id']))
            if user:
                formatted_message = {
                    '_id': str(message['_id']),
                    'event_id': str(message['event_id']),
                    'user_id': str(message['user_id']),
                    'user_name': user.get('name'),
                    'user_photo': user.get('photo_url'),
                    'message': message['message']
                }
                # Add created_at only if it exists
                if 'created_at' in message:
                    formatted_message['created_at'] = message['created_at'].isoformat() if isinstance(message['created_at'], datetime) else message['created_at']
                else:
                    formatted_message['created_at'] = datetime.utcnow().isoformat()
                
                formatted_messages.append(formatted_message)

        return formatted_messages