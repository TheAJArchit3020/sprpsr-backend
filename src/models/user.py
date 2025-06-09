from datetime import datetime
from bson import ObjectId
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
        except:
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
            'updated_at': datetime.utcnow()
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
        return user_dict 

    @staticmethod
    def update_rating(user_id, new_rating, comment=None):
        """Update user's rating and comments."""
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
            if not user:
                return False

            # Initialize rating fields if they don't exist
            if 'ratings' not in user:
                user['ratings'] = {
                    'total_ratings': 0,
                    'average_rating': 0,
                    'ratings_given': 0
                }
            if 'comments' not in user:
                user['comments'] = []

            # Update rating statistics
            current_total = user['ratings']['total_ratings']
            current_count = user['ratings']['ratings_given']
            
            new_total = current_total + new_rating
            new_count = current_count + 1
            new_average = new_total / new_count

            # Prepare comment object if provided
            comment_obj = None
            if comment:
                comment_obj = {
                    'comment': comment,
                    'created_at': datetime.utcnow()
                }

            # Update user document
            update_data = {
                'ratings.total_ratings': new_total,
                'ratings.ratings_given': new_count,
                'ratings.average_rating': new_average
            }

            # Add comment if provided
            if comment_obj:
                # Add new comment and keep only last 5
                update_data['$push'] = {
                    'comments': {
                        '$each': [comment_obj],
                        '$slice': -5  # Keep only last 5 comments
                    }
                }

            result = users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating rating: {e}")
            return False

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