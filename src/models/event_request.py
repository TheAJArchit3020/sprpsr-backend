from datetime import datetime
from bson import ObjectId
from src.config.database import get_database

db = get_database()
event_requests_collection = db['event_requests']

class EventRequest:
    @staticmethod
    def create(event_id, user_id, host_id):
        """Create a new event join request."""
        request = {
            'event_id': ObjectId(event_id),
            'user_id': ObjectId(user_id),
            'host_id': ObjectId(host_id),
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = event_requests_collection.insert_one(request)
        return result.inserted_id

    @staticmethod
    def get_pending_requests(host_id):
        """Get all pending requests for a host."""
        try:
            requests = list(event_requests_collection.find({
                'host_id': ObjectId(host_id),
                'status': 'pending'
            }))
            return [EventRequest._serialize_request(req) for req in requests]
        except:
            return []

    @staticmethod
    def accept_request(request_id):
        """Accept an event join request."""
        try:
            result = event_requests_collection.update_one(
                {'_id': ObjectId(request_id)},
                {
                    '$set': {
                        'status': 'accepted',
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.matched_count > 0 and result.modified_count > 0
        except:
            return False

    @staticmethod
    def reject_request(request_id):
        """Reject an event join request."""
        try:
            result = event_requests_collection.update_one(
                {'_id': ObjectId(request_id)},
                {
                    '$set': {
                        'status': 'rejected',
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.matched_count > 0 and result.modified_count > 0
        except:
            return False

    @staticmethod
    def _serialize_request(request):
        """Convert MongoDB request document to JSON-serializable format."""
        if not request:
            return None
            
        request_dict = request.copy()
        request_dict['_id'] = str(request_dict['_id'])
        request_dict['event_id'] = str(request_dict['event_id'])
        request_dict['user_id'] = str(request_dict['user_id'])
        request_dict['host_id'] = str(request_dict['host_id'])
        request_dict['created_at'] = request_dict['created_at'].isoformat()
        request_dict['updated_at'] = request_dict['updated_at'].isoformat()
        
        return request_dict 