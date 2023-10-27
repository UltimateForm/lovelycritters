from framework import handlerDecorator, LoggerInstance, okNoData, notFound
from db import getUserTable
from util import getEmailFromPathParams
from boto3.dynamodb.conditions import Attr


def rawHandler(event, _, logger: LoggerInstance, __, **kwargs):
    (dynamodb, table) = getUserTable()
    userEmail = getEmailFromPathParams(event)
    logger.addCtxItem("userEmail", userEmail)
    logger.info(f"Deleting user with email {userEmail}")
    deletion = None
    try:
        deletion = table.delete_item(
            Key={"email": userEmail}, ConditionExpression=Attr("email").exists()
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = f"No user with email {userEmail} found"
        logger.info(msg, {"dbResponse": deletion, "exception": e.response})
        return notFound({"errorMesssage": msg})

    logger.addCtxItem("dbResponse", deletion)
    logger.info(f"Deleted user {userEmail}")
    return okNoData()


handler = handlerDecorator(rawHandler)
