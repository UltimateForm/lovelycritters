from framework import httpHandlerDecorator, ok, HttpClient, LoggerInstance, response
from models import User
from util import getEmailFromPathParams, getInternalApi, dictWithoutKey, joinUrl
import json


def handlerRaw(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    userEmail = getEmailFromPathParams(event)
    userPayload = event["body"]
    if isinstance(userPayload, str):
        logger.info(f"Received user of type str, deserialzing")
        userPayload = json.loads(userPayload)
    (internalApiUrl, internalApiKey) = getInternalApi()
    user = User(email=userEmail, **userPayload)  # validation purposes
    userWithoutEmail = dictWithoutKey(user.__dict__, "email")
    updateUserUrl = joinUrl(internalApiUrl, "user", userEmail)
    (responseIsOk, statusCode, data) = httpClient.put(
        updateUserUrl, userWithoutEmail, {"x-api-key": internalApiKey}
    )
    if responseIsOk:
        return ok(data)
    else:
        return response(statusCode, body={**data, "source": "outbound"})


handler = httpHandlerDecorator(handlerRaw)
