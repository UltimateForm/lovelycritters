import json
from framework import handlerDecorator, LoggerInstance, okCreated
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
    response = table.put_item(Item=critter.__dict__)
    logger.info("DB responded ctx", {"dbResponse": response})
    logger.info("Created item successfully")
    return okCreated()


handler = handlerDecorator(rawHandler)
