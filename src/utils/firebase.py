import firebase_admin
from firebase_admin import credentials, auth
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase-credentials.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'superposr.firebasestorage.app'
        })

def verify_firebase_token(id_token):
    """Verify Firebase ID token and return decoded token."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise ValueError('Invalid ID token')
    except Exception as e:
        raise Exception(f'Error verifying token: {str(e)}') 