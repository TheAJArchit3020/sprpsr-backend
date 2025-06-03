import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
#JWT_SECRET = "HElloWorld"  # For testing purposes, replace with your actual secret
def generate_token(user_id):
    """Generate JWT token for authenticated user."""
    payload = {
        'userId': str(user_id),
        'exp':  datetime.now(timezone.utc)  + timedelta(days=7)
    } 
    jwtToken = jwt.encode(payload, JWT_SECRET, algorithm='HS256') 
    return jwtToken

def verfiy_token(token):
    """Verify JWT token and return user ID."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        print("Invalid token")
        raise ValueError('Invalid token')
    
       

#user {'_id': ObjectId('6839575207aad1733a9d6218'), 
# 'phone': '+919963504761', 'name': 'John Doe', 
# 'dob': '01/01/1990', 'gender': 'Male', 
# 'about': 'Software engineer and music lover', 
# 'created_at': datetime.datetime(2025, 5, 30, 6, 59, 30, 541000)}
