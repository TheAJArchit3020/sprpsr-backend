from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    """Initialize and return MongoDB connection."""
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    
    try:
        client.admin.command('ping')
        print('MongoDB connected successfully.')
    except Exception as e:
        print(f'Failed to connect to MongoDB: {e}')
        exit(1)
        
    return client['sprpsr_db'] 