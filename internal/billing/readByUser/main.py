from db import getBillingTable
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, ok
from util import getElementFromParams
from boto3.dynamodb.conditions import Key


def rawHandler(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    (dynamodb, table) = getBillingTable()
    billingEmail = getElementFromParams("email", event)
    logger.addCtx({"billingInput": {"email": billingEmail}, "email": billingEmail})
    response = table.query(KeyConditionExpression=Key("email").eq(billingEmail))
    logger.addCtxItem("dbResponse", response)
    if "Items" not in response:
        logger.info("No statements found")
        return ok({"statements": [], "count": 0})
    logger.info("Found statements")
    statements = response.get("Items")
    count = response.get("Count")
    return ok({"statements": statements, "count": count})


handler = httpHandlerDecorator(rawHandler)
