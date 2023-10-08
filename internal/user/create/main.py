import json
from framework import handlerDecorator, LoggerInstance
from user import User
from db import getUserTable

from datetime import date

def rawHandler(event, context, logger: LoggerInstance):
    logger.info(f"Received event {event}")
    userPayload = event["body"]
    if isinstance(userPayload, str):
        logger.info(f"Received user of type str, deserialzing")
        userPayload = json.loads(userPayload)
    table = getUserTable()
    user = User(**userPayload)
    table.put_item(Item=user.__dict__)
    logger.info("Created item successfully", {"userEmail": user.email})
    return {"statusCode": 201}


handler = handlerDecorator(rawHandler)
