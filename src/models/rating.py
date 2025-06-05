from datetime import datetime
from bson import ObjectId
from src.config.database import get_database

db = get_database()
ratings_collection = db['ratings']

class Rating:
    @staticmethod
    def create(event_id, rater_user_id, rated_user_id, rating, comment=None):
        """Create a new rating document."""
        new_rating = {
            'event_id': ObjectId(event_id),
            'rater_user_id': ObjectId(rater_user_id),
            'rated_user_id': ObjectId(rated_user_id),
            'rating': rating,
            'comment': comment,
            'created_at': datetime.utcnow()
        }
        result = ratings_collection.insert_one(new_rating)
        return str(result.inserted_id)

    @staticmethod
    def find_latest_for_user(user_id, limit=5):
        """Find the latest ratings/comments received by a user."""
        # Aggregate to fetch ratings, lookup rater user info, and sort by date
        pipeline = [
            { '$match': { 'rated_user_id': ObjectId(user_id) } },
            { '$sort': { 'created_at': -1 } },
            { '$limit': limit },
            { 
                '$lookup': {
                    'from': 'users', # The collection to join with
                    'localField': 'rater_user_id', # Field from the ratings collection
                    'foreignField': '_id', # Field from the users collection
                    'as': 'rater_info' # Output array field name
                }
            },
            { '$unwind': '$rater_info' }, # Deconstruct the rater_info array
            { 
                '$project': { # Reshape the output documents
                    '_id': 0, # Exclude the rating document's _id
                    'event_id': { '$toString': '$event_id' },
                    'rater_user_id': { '$toString': '$rater_user_id' },
                    'rated_user_id': { '$toString': '$rated_user_id' },
                    'rating': 1,
                    'comment': 1,
                    'created_at': { '$dateToString': { 'format': '%Y-%m-%dT%H:%M:%SZ', 'date': '$created_at' } },
                    'rater_name': '$rater_info.name', # Include rater's name
                    'rater_photo_url': '$rater_info.photo_url' # Include rater's photo URL
                }
            }
        ]
        
        return list(ratings_collection.aggregate(pipeline))

    @staticmethod
    def calculate_average_rating(user_id):
        """Calculate the average rating for a user."""
        pipeline = [
            { '$match': { 'rated_user_id': ObjectId(user_id), 'rating': { '$exists': True, '$ne': None } } },
            { 
                '$group': {
                    '_id': '$rated_user_id', # Group by the rated user
                    'average_rating': { '$avg': '$rating' },
                    'total_ratings': { '$sum': 1 } # Count the number of ratings
                }
            }
        ]
        
        result = list(ratings_collection.aggregate(pipeline))
        
        if result:
            # Return the average rating and total count, rounded to 2 decimal places
            return {
                'average_rating': round(result[0]['average_rating'], 2),
                'total_ratings': result[0]['total_ratings']
            }
        else:
            return {'average_rating': 0, 'total_ratings': 0} # No ratings yet 