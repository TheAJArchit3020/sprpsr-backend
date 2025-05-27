from datetime import datetime
from src.config.database import get_database

db = get_database()
users_collection = db['users']

class User:
    @staticmethod
    def find_by_phone(phone):
        """Find user by phone number."""
        return users_collection.find_one({'phone': phone})
    
    @staticmethod
    def create(phone, profile):
        """Create new user with profile."""
        new_user = {
            'phone': phone,
            'name': profile.get('name'),
            'dob': profile.get('dob'),
            'gender': profile.get('gender'),
            'about': profile.get('about'),
            'created_at': datetime.utcnow()
        }
        result = users_collection.insert_one(new_user)
        return result.inserted_id 