import json
from framework import (
    HttpClient,
    LoggerInstance,
    handlerDecorator,
    badRequest,
    ok,
    response,
)
from util import getInternalApi, joinUrl
import os


def handlerRaw(
    event, context, logger: LoggerInstance, httpClient: HttpClient, laundry: dict
):
    authPayload = event["body"] or {}
    if isinstance(authPayload, str):
        logger.info(f"Received authPayload of type str, deserialzing")
        authPayload = json.loads(authPayload)
    userEmail = authPayload.get("email")
    password = authPayload.get("password")
    if not (userEmail and password):
        return badRequest({"errorMessage": "Email and Password are required for login"})
    (apiUrl, apiKey) = getInternalApi()
    userAuthUrl = joinUrl(apiUrl, "user", "auth")
    (resultOk, statusCode, data) = httpClient.post(
        userAuthUrl, {"email": userEmail, "password": password}, {"x-api-key": apiKey}
    )
    if not resultOk:
        return response(statusCode, {**data, "source": "outbound"})
    return ok(data)


handler = handlerDecorator(handlerRaw)
