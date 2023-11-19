from db import getCritterTable
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, ok
from util import getElementFromParams
from boto3.dynamodb.conditions import Key


def rawHandler(event, context, logger: LoggerInstance, httpClient:HttpClient, **kwargs):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("email", event)
    logger.addCtxItem("email", critterOwnerEmail)
    response = table.query(
        KeyConditionExpression=Key("email").eq(critterOwnerEmail)
    )
    logger.addCtxItem("dbResponse", response)
    if "Items" not in response:
        logger.info("No critters found")
        return ok({"critters": [], "count": 0})
    logger.info("Found critters")
    critters = response.get("Items")
    count = response.get("Count")
    return ok({"critters": critters, "count": count})


handler = httpHandlerDecorator(rawHandler)
