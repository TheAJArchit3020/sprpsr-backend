from datetime import datetime
from bson import ObjectId
from src.config.database import get_database

db = get_database()
class Feedback:
    collection = db['feedbacks']
    archived_collection = db['archived_feedbacks']

    @staticmethod
    def create_feedback(event_id, rater_user_id, rated_user_id, rating, comment=None, no_show=False):
        """Create a new feedback entry."""
        feedback = {
            'event_id': ObjectId(event_id),
            'rater_user_id': ObjectId(rater_user_id),
            'rated_user_id': ObjectId(rated_user_id),
            'rating': rating,
            'comment': comment,
            'no_show': no_show,
            'created_at': datetime.utcnow(),
            'is_archived': False
        }
        result = Feedback.collection.insert_one(feedback)
        return str(result.inserted_id)

    @staticmethod
    def get_feedbacks_for_user(user_id):
        """Get all feedbacks for a specific user."""
        active_feedbacks = list(Feedback.collection.find({'rated_user_id': ObjectId(user_id)}))
        archived_feedbacks = list(Feedback.archived_collection.find({'rated_user_id': ObjectId(user_id)}))
        return active_feedbacks + archived_feedbacks

    @staticmethod
    def get_feedbacks_for_event(event_id):
        """Get all feedbacks for a specific event."""
        active_feedbacks = list(Feedback.collection.find({'event_id': ObjectId(event_id)}))
        archived_feedbacks = list(Feedback.archived_collection.find({'event_id': ObjectId(event_id)}))
        return active_feedbacks + archived_feedbacks

    @staticmethod
    def archive_feedbacks(event_id):
        """Archive all feedbacks for an event."""
        # Find all active feedbacks for the event
        feedbacks = list(Feedback.collection.find({'event_id': ObjectId(event_id)}))
        
        if feedbacks:
            # Insert into archived collection
            Feedback.archived_collection.insert_many(feedbacks)
            # Remove from active collection
            Feedback.collection.delete_many({'event_id': ObjectId(event_id)})

    @staticmethod
    def get_pending_feedbacks():
        """Get all non-archived feedbacks."""
        return list(Feedback.collection.find({'is_archived': False})) 