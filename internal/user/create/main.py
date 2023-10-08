import json
from util import generateUniqueId
from user import User
from db import getUserTable
from datetime import date

def handler(event, context):
	print(f"Received event {event}")
	userPayload = event["body"]
	print(f"Working with user {userPayload}")
	table = getUserTable()
	user = User(
		id=generateUniqueId(),
		name=userPayload["name"],
		accoundName=userPayload["accountName"],
		birthDate=date.fromisoformat(userPayload["birthDate"]).isoformat(),
		password=userPayload["password"],
		associatedAnimals=[])
	table.put_item(
		Item = user.__dict__
	)
	return {
		"statusCode": 201
	}