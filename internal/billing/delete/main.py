from framework import httpHandlerDecorator, LoggerInstance, okNoData
from db import getBillingTable
from util import getElementFromParams


def rawHandler(event, _, logger: LoggerInstance, __, **kwargs):
    (dynamodb, table) = getBillingTable()
    billingUserEmail = getElementFromParams("email", event)
    billingId = getElementFromParams("billingId", event)
    logger.addCtx(
        {
            "billingInput": {"email": billingUserEmail, "billingId": billingId},
            "email": billingUserEmail,
        }
    )
    logger.info(
        f"Deleting billing statement wit id {billingId} for user {billingUserEmail}"
    )
    deletion = None
    deletion = table.delete_item(
        Key={
            "email": billingUserEmail,
            "billingId": billingId,
        }
    )
    logger.addCtxItem("dbResponse", deletion)
    logger.info(f"Deleted billing statement for user {billingUserEmail}")
    return okNoData()


handler = httpHandlerDecorator(rawHandler)
