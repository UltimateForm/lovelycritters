from db import getBillingTable
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, notFound, ok
from util import getElementFromParams


def rawHandler(event, context, logger: LoggerInstance, httpClient:HttpClient, **kwargs):
    (dynamodb, table) = getBillingTable()
    billingEmail = getElementFromParams("email", event)
    billingId = getElementFromParams("billingId", event)
    logger.addCtx(
        {"billingInput": {"email": billingEmail, "billingId": billingId}}
    )
    response = table.get_item(
        Key={
            "email": billingEmail,
            "billingId": billingId,
        }
    )
    logger.addCtxItem("dbResponse", response)
    if "Item" not in response:
        logger.info(f"Could not find billing statement with id {billingId} for user {billingEmail}")
        return notFound(
            {
                "errorMessage": f"No billing statement with billingId:email {billingId}:{billingEmail} found"
            }
        )

    logger.info("Found *")
    billidnData = response["Item"]
    logger.addCtxItem("billingData", billidnData)
    return ok(billidnData)


handler = httpHandlerDecorator(rawHandler)
