from src.models.event_request import EventRequest
from src.models.event import Event
from src.models.user import User

class EventRequestService:
    @staticmethod
    def create_join_request(event_id, user_id):
        """Create a join request for a private event."""
        # Get event details to check if it's private and get host_id
        event = Event.find_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
            
        # Check if event is private
        if not event.get('is_private', False):
            raise ValueError("This event is public. Use join_event instead.")
            
        # Check if user already has a pending request
        existing_requests = EventRequest.get_pending_requests(event['user_id'])
        for req in existing_requests:
            if req['user_id'] == user_id and req['event_id'] == event_id:
                raise ValueError("You already have a pending request for this event")
                
        # Create the request
        request_id = EventRequest.create(event_id, user_id, event['user_id'])
        return {'message': 'Join request sent successfully', 'request_id': str(request_id)}

    @staticmethod
    def get_host_pending_requests(host_id):
        """Get all pending requests for a host with user details."""
        requests = EventRequest.get_pending_requests(host_id)
        
        # Enhance requests with user details
        enhanced_requests = []
        for req in requests:
            user = User.find_by_id(req['user_id'])
            if user:
                req['user_details'] = {
                    'name': user.get('name'),
                    'photo_url': user.get('photo_url')
                }
            enhanced_requests.append(req)
            
        return enhanced_requests

    @staticmethod
    def handle_request(request_id, host_id, action):
        """Handle (accept/reject) a join request."""
        # Get the request
        request = EventRequest.get_pending_requests(host_id)
        target_request = None
        for req in request:
            if req['_id'] == request_id:
                target_request = req
                break
                
        if not target_request:
            raise ValueError("Request not found or already handled")
            
        if action == 'accept':
            # Accept the request
            success = EventRequest.accept_request(request_id)
            if success:
                # Add user to event participants
                Event.add_participant(target_request['event_id'], target_request['user_id'])
                return {'message': 'Request accepted successfully'}
            else:
                raise Exception("Failed to accept request")
        elif action == 'reject':
            # Reject the request
            success = EventRequest.reject_request(request_id)
            if success:
                return {'message': 'Request rejected successfully'}
            else:
                raise Exception("Failed to reject request")
        else:
            raise ValueError("Invalid action. Use 'accept' or 'reject'") 