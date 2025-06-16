from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from src.config.database import get_database

db = get_database()
users_collection = db['users']

# Create a 2dsphere index on the location field
users_collection.create_index([('location', '2dsphere')])

class User:
    @staticmethod
    def find_by_phone(phone):
        """Find user by phone number."""
        return users_collection.find_one({'phone': phone})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID."""
        # MongoDB stores _id as ObjectId, so convert string ID to ObjectId
        try:
            return users_collection.find_one({'_id': ObjectId(user_id)})
        except InvalidId:
            print(f"Invalid ObjectId format for user_id: {user_id}")
            return None
        except Exception as e:
            print(f"Error finding user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    def create(phone, profile):
        """Create new user with profile."""
        new_user = {
            'phone': phone,
            'name': profile.get('name'),
            'dob': profile.get('dob'),
            'gender': profile.get('gender'),
            'about': profile.get('about'),
            'photo_url': profile.get('photo_url'),
            'location': profile.get('location'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'events_organized': 0,
            'latest_events': []
        }
        result = users_collection.insert_one(new_user)
        return str(result.inserted_id)

    @staticmethod
    def update_location(user_id, location):
        """Update user's location."""
        try:
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    'location': location,
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.matched_count > 0
        except Exception as e:
            print(f"Error updating user location: {e}")
            return False

    @staticmethod
    def update(user_id, update_data):
        """Update user profile fields."""
        try:
            # Remove _id from update_data if present to prevent updating the immutable _id
            update_data.pop('_id', None)
            
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {
                    **update_data,
                    'updated_at': datetime.utcnow()
                }}
            )
            return result.matched_count > 0
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    @staticmethod
    def serialize(user):
        """Convert MongoDB user document to JSON-serializable format."""
        if not user:
            return None
        
        user_dict = user.copy()
        user_dict['_id'] = str(user_dict['_id'])
        # Convert ObjectId user_id to string if it exists (not needed for user model)
        # Convert datetime fields to ISO format strings
        if 'created_at' in user_dict and isinstance(user_dict['created_at'], datetime):
            user_dict['created_at'] = user_dict['created_at'].isoformat()
        if 'updated_at' in user_dict and isinstance(user_dict['updated_at'], datetime):
            user_dict['updated_at'] = user_dict['updated_at'].isoformat()
        
        # Return location as is (should be GeoJSON already)
        
        # Convert latest_events ObjectIds to strings
        if 'latest_events' in user_dict and isinstance(user_dict['latest_events'], list):
            user_dict['latest_events'] = [str(event_id) for event_id in user_dict['latest_events']]

        return user_dict

    @staticmethod
    def update_rating(user_id, rating, comment=None):
        """Update user's rating and comments."""
        user = User.find_by_id(user_id)
        if not user:
            return False

        # Get current rating stats
        current_rating = user.get('rating', 0)
        rating_count = user.get('rating_count', 0)
        total_rating = user.get('total_rating', 0)
        comments = user.get('comments', [])

        # Update rating stats
        new_total_rating = total_rating + rating
        new_rating_count = rating_count + 1
        new_avg_rating = new_total_rating / new_rating_count

        # Add new comment if provided
        if comment:
            comments.append({
                'comment': comment,
                'created_at': datetime.utcnow()
            })
            # Keep only last 5 comments
            comments = comments[-5:]

        # Update user document
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'rating': new_avg_rating,
                    'rating_count': new_rating_count,
                    'total_rating': new_total_rating,
                    'comments': comments
                }
            }
        )
        return True

    @staticmethod
    def increment_event_counts(user_id, completed=False, participated=False):
        """Increment event participation counts."""
        update = {}
        if completed:
            update['$inc'] = {'events_completed': 1}
        if participated:
            update['$inc'] = {'events_participated': 1}
        
        if update:
            User.collection.update_one(
                {'_id': ObjectId(user_id)},
                update
            )

    @staticmethod
    def get_profile_with_ratings(user_id):
        """Get user profile with rating information."""
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return None

            # Ensure rating fields exist
            if 'ratings' not in user:
                user['ratings'] = {
                    'total_ratings': 0,
                    'average_rating': 0,
                    'ratings_given': 0
                }
            if 'comments' not in user:
                user['comments'] = []

            # Serialize the user data
            user_dict = user.copy()
            user_dict['_id'] = str(user_dict['_id'])
            
            # Format dates in comments
            if 'comments' in user_dict:
                for comment in user_dict['comments']:
                    if 'created_at' in comment:
                        comment['created_at'] = comment['created_at'].isoformat()

            return user_dict
        except:
            return None 