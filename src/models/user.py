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