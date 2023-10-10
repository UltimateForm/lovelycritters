from db import getUserTable
import json
from framework import handlerDecorator, LoggerInstance


def rawHandler(event, context, logger: LoggerInstance):
    (dynamodb, table) = getUserTable()
    params = event["pathParameters"]
    userEmail = params["email"]
    logger.addCtxItem("userEmail", userEmail)
    response = table.get_item(Key={"email": userEmail})
    if "Item" not in response:
        logger.info("Could not find user")
        return {
            "statusCode": 404,
            "body": json.dumps(
                {"errorMessage": f"No user with email {userEmail} found"}
            ),
        }
    logger.info("Found user")
    user = response["Item"]
    logger.addCtxItem("userData", user)
    return {"statusCode": 200, "body": json.dumps(user)}


handler = handlerDecorator(rawHandler)
