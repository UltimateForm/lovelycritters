import json
from framework import (
    handlerDecorator,
    LoggerInstance,
    ok,
    okNoData,
    HttpClient,
    response,
)
from util import joinUrl, dictWithoutKey
import os
from models import ClientUser, Critter, User
from typing import List


def deleteCreatedCritters(
    critterNames: List[str],
    userEmail: str,
    url: str,
    apiKey:str,
    httpClient: HttpClient,
    logger: LoggerInstance,
):
    commonHeaders = {"x-api-key": apiKey}
    logger.info(
        "Deleting critteras as part failure cleanup", {"crittersToDelete": critterNames}
    )
    for createdCritterName in critterNames:
        try:
            deletionUrl = joinUrl(url, userEmail, createdCritterName)
            httpClient.delete(deletionUrl, None, commonHeaders)
        except Exception as e:
            logger.error(
                "Failed to delete one or more critters as part of user creation failure rollback",
                {"error": e},
            )


class CreateCritterException(Exception):
    statusCode: int = 0
    data: dict = {}
    source: str = None
    createdCritters: List[str] = []

    def __init__(
        self,
        statusCode: int,
        data: dict,
        source: str,
        createdCritters: List[str],
        *args: object,
    ) -> None:
        super().__init__(*args)
        self.statusCode = statusCode
        self.data = data
        self.source = source
        self.createdCritters = createdCritters

    def __repr__(self) -> str:
        return f"Error while creating critter: {self.statusCode}"


def createCritters(
    critters: List[Critter],
    apiUrl: str,
    apiKey:str,
    httpClient: HttpClient,
    logger: LoggerInstance,
) -> List[str]:
    createdCritters: List[str] = []
    commonHeaders = {"x-api-key": apiKey}
    for critter in critters:
        logger.info(f"Creating critter {critter}")
        try:
            (ok, statusCode, data) = httpClient.post(
                apiUrl, critter.__dict__, commonHeaders
            )
            if ok:
                createdCritters.append(critter.petName)
            else:
                logger.error(
                    "User registering process failed due to critter creation failure",
                    {"errorData": data, "errorStatusCode": statusCode},
                )
                raise CreateCritterException(
                    statusCode, data, "outbound", createdCritters
                )
        except Exception as e:
            if type(e) == CreateCritterException:
                raise
            errorMsg = str(e)
            logger.exception(errorMsg)
            logger.error(
                f"User registering process failed due to unexcpexted critter creation exception: {errorMsg}"
            )
            raise CreateCritterException(
                500, {"errorMessage": errorMsg}, None, createdCritters
            )

    return createdCritters


def rollback(laundry: dict, logger: LoggerInstance, httpClient: HttpClient):
    userEmail = laundry.get("userEmail")
    critters = laundry.get("critters")
    internalApiUrl = os.environ.get("INTERNAL_API_URL")
    internalApiKey = os.environ.get("INTERNAL_API_KEY")
    critterApiUrl = joinUrl(internalApiUrl, "critter")
    if (
        userEmail == None
        or critters == None
        or internalApiUrl == None
        or critterApiUrl == None
    ):
        logger.error("Unable to proceed with cleaning due to missing parameters")
        return
    deleteCreatedCritters(
        critterNames=critters,
        userEmail=userEmail,
        url=critterApiUrl,
        apiKey=internalApiKey,
        httpClient=httpClient,
        logger=logger,
    )
    logger.info("Rollback complete")


def rawHandler(
    event, context, logger: LoggerInstance, httpClient: HttpClient, laundry: dict
):
    logger.info(f"Received event {event}")
    userPayload = event["body"]
    if isinstance(userPayload, str):
        logger.info(f"Received user of type str, deserialzing")
        userPayload = json.loads(userPayload)
    internalApiUrl = os.environ.get("INTERNAL_API_URL")
    internalApiKey = os.environ.get("INTERNAL_API_KEY")
    logger.info(f"HERES MY API KEY {internalApiKey}")
    userApiUrl = joinUrl(internalApiUrl, "user")
    critterApiUrl = joinUrl(internalApiUrl, "critter")
    logger.info(f"createUserUrl {userApiUrl}")
    user = ClientUser(**userPayload)
    laundry["userEmail"] = user.email
    critters = [
        Critter(email=user.email, **critter) for critter in user.associatedAnimals
    ]
    logger.info(f"before registering user, will create critters {critters}")
    createdCritters: List[str] = []
    try:
        createdCritters = createCritters(
            critters,
            critterApiUrl,
            internalApiKey,
            httpClient,
            logger.branch("critterCreationForUserCreation"),
        )
    except CreateCritterException as e:
        laundry["critters"] = e.createdCritters
        return response(
            e.statusCode,
            body={
                "errorMessage": f"Critter creation failed with error: {e.data.get('errorMessage')}",
                "source": e.source,
            },
        )
    laundry["critters"] = createdCritters
    internalUserPayload = User(
        **dictWithoutKey(user.__dict__, "associatedAnimals"),
        associatedAnimals=createdCritters,
    )
    (ok, statusCode, data) = httpClient.post(
        userApiUrl,
        internalUserPayload.__dict__,
        {"x-api-key": internalApiKey},
    )
    if ok:
        return okNoData()
    else:
        return response(statusCode, body={**data, "source": "outbound"})


handler = handlerDecorator(handler=rawHandler, laundryMachine=rollback)