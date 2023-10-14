from db import getUserTable
from framework import handlerDecorator, LoggerInstance, notFound, ok
from util import getEmailFromPathParams


def rawHandler(event, context, logger: LoggerInstance):
    (dynamodb, table) = getUserTable()
    userEmail = getEmailFromPathParams(event)
    logger.addCtxItem("userEmail", userEmail)
    response = table.get_item(Key={"email": userEmail})
    if "Item" not in response:
        logger.info("Could not find user")
        return notFound({"errorMessage": f"No user with email {userEmail} found"})

    logger.info("Found user")
    user = response["Item"]
    logger.addCtxItem("userData", user)
    return ok(user)


handler = handlerDecorator(rawHandler)
