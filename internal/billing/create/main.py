import json
from framework import HttpClient, conflict, handlerDecorator, LoggerInstance, okCreated
from models import BillingStatement
from db import getBillingTable


def rawHandler(event, context, logger: LoggerInstance, httpClient:HttpClient, **kwargs):
    logger.info(f"Received event {event}")
    billingPayload = event["body"]
    if isinstance(billingPayload, str):
        logger.info(f"Received billing statement of type str, deserialzing")
        billingPayload = json.loads(billingPayload)
    (dynamodb, table) = getBillingTable()
    billingStatement = BillingStatement(**billingPayload)
    print(f"Built billingStatement {repr(billingStatement)}")
    response = None
    try:
        response = table.put_item(
            Item=billingStatement.__dict__,
            ConditionExpression="attribute_not_exists(email) AND attribute_not_exists(bllingId)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = "Failed to create billing statement for {0} as one already exists".format(
            billingStatement.email
        )
        logger.info(msg, {"dbResponse": response, "exception": e.response})
        return conflict({"errorMessage": msg})
    logger.info("DB responded ctx", {"dbResponse": response})
    logger.info("Created item successfully")
    return okCreated(billingStatement.__dict__)


handler = handlerDecorator(rawHandler)
