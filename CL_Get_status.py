import json
import os
import pymongo
from bson.objectid import ObjectId

def lambda_handler(event, context):
    try:
        request_body = json.loads(event['body'])

        player_id = request_body.get('player_id')
        status = request_body.get('status')

        if not player_id:
            raise Exception("'player_id' key not found in the request body")
        if not status:
            raise Exception("'status' key not found in the request body")

        connection_string = os.environ['MONGO_CONNECTION_STRING']
        client = pymongo.MongoClient(connection_string)
        db = client["CoachLife"]

        if status.lower() == "not completed":
            all_learning_pathways = db["Learning Pathway"].find({}, {"pathwayId": 1, "Activity": 1})
            all_pathway_ids = {str(doc["pathwayId"]): doc["Activity"] for doc in all_learning_pathways}

            player_learning_docs = db["Player Learning"].find({"playerId": ObjectId(player_id)})
            player_learning_pathway_ids = {str(doc["pathwayId"]) for doc in player_learning_docs}

            remaining_pathways = {pathway_id: activity for pathway_id, activity in all_pathway_ids.items() if pathway_id not in player_learning_pathway_ids}

            pathway_activities = [{"pathwayId": pathway_id, "activity": activity} for pathway_id, activity in remaining_pathways.items()]

        elif status.lower() == "completed":
            player_learning_docs = db["Player Learning"].find({"playerId": ObjectId(player_id), "status": "Completed"})
            completed_pathway_ids = {str(doc["pathwayId"]): doc["_id"] for doc in player_learning_docs}

            pathway_activities = []
            for pathway_id, doc_id in completed_pathway_ids.items():
                learning_pathway_doc = db["Learning Pathway"].find_one({"pathwayId": ObjectId(pathway_id)})
                if learning_pathway_doc:
                    activity = learning_pathway_doc.get("Activity")
                    pathway_activities.append({"pathwayId": pathway_id, "activity": activity, "player_document_id": str(doc_id)})

        else:
            raise Exception("Invalid status value. Please provide 'Completed' or 'Not Completed'.")

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"pathway_data": pathway_activities})
        }
        return response

    except Exception as e:
        error_response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"errorType": "InternalServerError", "message": str(e)})
        }
        return error_response
