from db import getUserTable
import json

def handler(event, context):
	table = getUserTable();
	userId = event["body"]
	response = table.get_item(Key={"id": userId})
	user = response["Item"]
	return {
		"statusCode": 200,
		"body": json.dumps(user)
	}