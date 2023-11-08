import json
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, notFound, ok
from models import User
from db import getUserTable
from boto3.dynamodb.conditions import Attr

from util import getEmailFromPathParams


def rawHandler(event, context, logger: LoggerInstance, httpClient:HttpClient, **kwargs):
    userEmail = getEmailFromPathParams(event)
    userPayload = event["body"]
    if isinstance(userPayload, str):
        logger.info(f"Received user of type str, deserialzing")
        userPayload = json.loads(userPayload)
    (dynamodb, table) = getUserTable()
    user = User(email=userEmail, **userPayload)
    dbResponse = None
    try:
        dbResponse = table.update_item(
            Key={"email": userEmail},
            UpdateExpression="set birthDate=:bd, associatedAnimals=:aa, #n=:n, password=:p",
            ExpressionAttributeValues={
                ":bd": user.birthDate,
                ":aa": user.associatedAnimals,
                ":n": user.name,
                ":p": user.password,
            },
            ExpressionAttributeNames={
                "#n": "name"
            },
            ReturnValues="UPDATED_NEW",
            ConditionExpression=Attr("email").exists(),
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = f"No user with email {userEmail} found"
        logger.info(msg, {"dbResponse": dbResponse, "exception": e.response})
        return notFound({"errorMesssage": msg})

    logger.info("DB responded ctx", {"dbResponse": dbResponse})
    updatedUser = dbResponse.get("Attributes")
    logger.info("Updated item successfully", {"userData": updatedUser})
    return ok(updatedUser)


handler = httpHandlerDecorator(rawHandler)
