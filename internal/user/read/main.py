from db import getUserTable
import json
from util import handlerDecorator

def rawHandler(event, context):
	table = getUserTable()
	params = event["pathParameters"]
	userEmail = params["email"]
	response = table.get_item(Key={"email": userEmail})
	if "Item" not in response:
		return {
			"statusCode": 404,
			"body": json.dumps({
				"errorMessage": f"No user with email {userEmail} found"
			})
		}
	user = response["Item"]
	return {
		"statusCode": 200,
		"body": json.dumps(user)
	}

handler = handlerDecorator(rawHandler)