import json
from framework import conflict, handlerDecorator, LoggerInstance, okCreated
from user import User
from db import getUserTable

from datetime import date


def rawHandler(event, context, logger: LoggerInstance):
    logger.info(f"Received event {event}")
    userPayload = event["body"]
    if isinstance(userPayload, str):
        logger.info(f"Received user of type str, deserialzing")
        userPayload = json.loads(userPayload)
    (dynamodb, table) = getUserTable()
    user = User(**userPayload)
    response = None
    try:
        response = table.put_item(
            Item=user.__dict__, ConditionExpression="attribute_not_exists(email)"
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = "Failed to create item with email {0} as one already exists".format(
            user.email
        )
        logger.info(msg, {"dbPutResponse": response, "exception": e.response})
        return conflict({"errorMessage": msg})

    logger.info("DB responded ctx", {"dbPutResponse": response})
    logger.info("Created item successfully", {"userEmail": user.email})
    return okCreated()


handler = handlerDecorator(rawHandler)
