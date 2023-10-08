import json
from util import handlerDecorator
from user import User
from db import getUserTable
from datetime import date

def rawHandler(event, context):
	print(f"Received event {event}")
	userPayload = event["body"]
	if isinstance(userPayload, str):
		print(f"Received user of type str, deserialzing")
		userPayload = json.loads(userPayload)
	table = getUserTable()
	user = User(**userPayload)
	table.put_item(
		Item = user.__dict__
	)
	return {
		"statusCode": 201
	}

handler = handlerDecorator(rawHandler)