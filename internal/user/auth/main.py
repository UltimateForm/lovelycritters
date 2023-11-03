from db import getUserTable
from framework import handlerDecorator, LoggerInstance, unauthorized, badRequest, ok
import json
from boto3.dynamodb.conditions import Attr, Key
import jwt
import os
from datetime import datetime, timedelta

JWT_SECRET = os.environ.get("JWT_SECRET")


def rawHandler(event, _, logger: LoggerInstance, __, **kwargs):
    (dynamodb, table) = getUserTable()
    authPayload = event["body"] or {}
    if isinstance(authPayload, str):
        logger.info(f"Received authPayload of type str, deserialzing")
        authPayload = json.loads(authPayload)
    userEmail = authPayload.get("email")
    password = authPayload.get("password")
    if not userEmail.strip() or not password.strip():
        return badRequest(
            {"errorMessage": "Both email and password and required for authentication"}
        )
    logger.addCtxItem("userEmail", authPayload.get("email"))
    logger.info(f"Authenticating {userEmail}...")
    response = table.query(
        KeyConditionExpression=Key("email").eq(userEmail),
        FilterExpression=Attr("password").eq(password),
        Limit=1,
    )
    matchedCount = response.get("Count")
    logger.addCtxItem("dbResponse", response)
    logger.info("Auth: db responded")
    if matchedCount != 1 or "Items" not in response:
        logger.info("Authentication failure")
        return unauthorized({"errorMessage": "Bad credentials"})
    user: dict = response["Items"][0]
    userWithoutPwd = dict((i, user[i]) for i in user.keys() if i != "password")
    logger.info("userWithoutPassword generated", {"userWithoutPwd": userWithoutPwd})
    dateTimeNow = datetime.now()
    dateTimeExpiry = dateTimeNow + timedelta(hours=72)
    encodedJwt = jwt.encode(
        {
            "userData": userWithoutPwd,
            "timestamp": {
                "created": dateTimeNow.timestamp(),
                "expiry": dateTimeExpiry.timestamp(),
            },
        },
        JWT_SECRET,
        algorithm="HS256",
    )
    logger.addCtxItem("userData", user)
    logger.info("Authentication success")
    return ok({"accessToken": encodedJwt})


handler = handlerDecorator(rawHandler)
