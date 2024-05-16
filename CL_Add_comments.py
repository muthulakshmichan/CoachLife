import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient('Mongo connecting string ')
db = client['CoachLife'] 
player_learning_collection = db['Player Learning']
players_collection = db['Players']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        document_id = ObjectId(body['document_id']) 
        comment = body['comment']
        commented_by = body.get('commented_by', 'Anonymous')  
        commented_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_comment = {
            "_id": ObjectId(),
            "Comment": comment,
            "CommentedBy": commented_by,
            "CommentedOn": commented_on
        }

        result = player_learning_collection.update_one(
            {'_id': document_id},  
            {'$push': {'Comments': new_comment}}
        )
        
        if result.matched_count == 0:
            raise ValueError("No document found with the provided ID.")

        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow requests from any origin
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"message": "Comment added successfully."})
        }
        
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow requests from any origin
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": str(e)})
        }
    
    return response

