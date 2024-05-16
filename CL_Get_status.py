import json
from pymongo import MongoClient
from bson.objectid import ObjectId

def lambda_handler(event, context):
    try:
        # Print the incoming event for debugging
        print("Event:", json.dumps(event))

        # Extract playerId and status from the event body
        body = json.loads(event['body'])
        player_id = body.get("player_id")
        status = body.get("status")

        # Validate input
        if player_id is None:
            raise Exception("'player_id' key not found in the request payload")
        if status is None:
            raise Exception("'status' key not found in the request payload")

        # Connect to MongoDB
        connection_string = "mongodb+srv://tgdev:technology-1@cluster0.0pefygc.mongodb.net/"
        client = MongoClient(connection_string)
        db = client["CoachLife"]

        # Fetch player learning documents for the provided playerId and status
        player_learning_docs = db["Player Learning"].find({"playerId": player_id, "status": status})

        # List to store pathway IDs and activities
        pathway_activities = []

        # Iterate over player learning documents
        for doc in player_learning_docs:
            pathway_id = doc.get("pathwayId")

            # Fetch details from Learning Pathway collection using pathwayId
            learning_pathway_doc = db["Learning Pathway"].find_one({"pathwayId": pathway_id})
            if learning_pathway_doc:
                activity = learning_pathway_doc.get("Activity")
                pathway_activities.append({"pathwayId": pathway_id, "activity": activity})
            else:
                print(f"No learning pathway found for pathwayId: {pathway_id}")

        # Construct response
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # Allow requests from any origin
            },
            "body": json.dumps({"pathway_activities": pathway_activities})
        }
        return response

    except Exception as e:
        # Log the error message for debugging
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # Allow requests from any origin
            },
            "body": json.dumps({"errorType": "InternalServerError", "message": str(e)})
        }
