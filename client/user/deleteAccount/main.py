import json
from framework import (
    HttpClient,
    LoggerInstance,
    httpHandlerDecorator,
    okNoData,
    response,
)
from util import getEmailFromPathParams, getInternalApi, joinUrl
import os


def handlerRaw(event, context, logger: LoggerInstance, httpClient: HttpClient, laundry:dict):
    userEmail = getEmailFromPathParams(event)
    logger.addCtxItem("userEmail", userEmail)
    logger.info(f"Client request deletion of user with email {userEmail}")
    (apiUrl, apiKey) = getInternalApi()
    deleteUserApiUrl = joinUrl(apiUrl, "user", userEmail)
    (ok, statusCode, data) = httpClient.delete(deleteUserApiUrl,  {"x-api-key": apiKey})
    if not ok:
        return response(statusCode, {**data, "source": "outbound"})
    return okNoData()


handler = httpHandlerDecorator(handlerRaw)
