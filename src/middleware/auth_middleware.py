from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
from src.models.user import User # Import User model

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # Assuming the token contains a 'user_id' field
            user_id = data.get('userId')

            if not user_id:
                return jsonify({'message': 'Token is invalid or missing user ID!'}), 401
            
            # Fetch the user from the database
            current_user = User.find_by_id(user_id)
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404

            # Pass the fetched user object to the decorated function
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    
    return decorated 