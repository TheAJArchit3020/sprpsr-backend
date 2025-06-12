import uuid
from firebase_admin import storage
from firebase_admin import credentials, initialize_app

def get_firebase_storage():
    """Get Firebase Storage bucket."""
    try:
        bucket = storage.bucket()
        return bucket
    except Exception as e:
        raise Exception(f"Error getting Firebase Storage bucket: {str(e)}")

def upload_to_firebase(file, folder='profile_images'):
    """
    Upload file to Firebase Storage and return public URL.
    
    Args:
        file: File object from request.files
        folder: Storage folder name (default: 'profile_images')
    
    Returns:
        str: Public URL of the uploaded file
    """
    if not file:
        raise ValueError('No file provided')
        
    try:
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{unique_filename}"
        
        bucket = get_firebase_storage()
        blob = bucket.blob(file_path)
        
        blob.metadata = {
            'firebaseStorageDownloadTokens': str(uuid.uuid4())
        }
        
        blob.upload_from_file(
            file,
            content_type=file.content_type,
        )
        
        blob.make_public()
        
        public_url = blob.public_url
        
        return public_url
        
    except Exception as e:
        raise Exception(f"Error uploading to Firebase Storage: {str(e)}") 