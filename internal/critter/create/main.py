import json
from framework import conflict, handlerDecorator, LoggerInstance, okCreated
from models import Critter
from db import getCritterTable

from datetime import date


def rawHandler(event, context, logger: LoggerInstance):
    logger.info(f"Received event {event}")
    critterPayload = event["body"]
    if isinstance(critterPayload, str):
        logger.info(f"Received critter of type str, deserialzing")
        critterPayload = json.loads(critterPayload)
    (dynamodb, table) = getCritterTable()
    critter = Critter(**critterPayload)
    response = None
    try:
        response = table.put_item(Item=critter.__dict__, ConditionExpression="attribute_not_exists(petName) AND attribute_not_exists(ownerEmail)")
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = "Failed to create item with petName:ownerEmail {0}:{1} as one already exists".format(
            critter.petName,
            critter.ownerEmail
        )
        logger.info(msg, {"dbResponse": response, "exception": e.response})
        return conflict({"errorMessage": msg})
    logger.info("DB responded ctx", {"dbResponse": response})
    logger.info("Created item successfully")
    return okCreated()


handler = handlerDecorator(rawHandler)
