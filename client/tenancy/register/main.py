from framework import (
    httpHandlerDecorator,
    HttpClient,
    LoggerInstance,
    ok,
)
from models import TenancyCollection, CritterTenancy, Critter, Tenancy
from util import (
    getEmailFromPathParams,
    getInternalApi,
    dictWithoutKey,
    joinUrl,
    modelToDict,
)
import json
from typing import List


def getPet(
    email: str, petName: str, httpClient: HttpClient, logger: LoggerInstance
) -> dict:
    (internalApiUrl, internalApiKey) = getInternalApi()
    petUrl = joinUrl(internalApiUrl, "critter", email, petName)
    (responseOk, statusCode, data) = httpClient.get(
        petUrl, None, {"x-api-key": internalApiKey}
    )
    if not responseOk:
        raise Exception(
            f"Failure ({statusCode}) at retrieving pet {petName} from user {email}"
        )
    critter = Critter(**data)
    return critter


def updatePetTenancy(
    email: str,
    petData: Critter,
    tenancy: CritterTenancy,
    httpClient: HttpClient,
    logger: LoggerInstance,
):
    (internalApiUrl, internalApiKey) = getInternalApi()
    petUrl = joinUrl(internalApiUrl, "critter", email, petData.petName)
    tenancy = Tenancy(tenancy.checkInDate, tenancy.checkOutDate)
    if petData.futureTenancy == None:
        petData.futureTenancy = []
    petData.futureTenancy.append(tenancy)
    petUpdatePayload = dictWithoutKey(modelToDict(petData), "petName", "email")
    (responseOk, statusCode, data) = httpClient.put(
        petUrl,
        petUpdatePayload,
        {"x-api-key": internalApiKey},
    )
    if not responseOk:
        # todo: create OutboundHttpException in framework so we can have standard in dealing with these
        errorMsg: str | None = (
            f"Oubound pet update error: {data.get('errorMessage')}"
            if data != None
            else None
        )
        raise Exception(
            errorMsg
            or f"Failure ({statusCode}) at retrieving pet {petData.petName} from user {email}"
        )
    addedCritterTenancy = CritterTenancy(petName=petData.petName, **tenancy.__dict__)
    return addedCritterTenancy


def handlerRaw(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    userEmail = getEmailFromPathParams(event)
    logger.addCtxItem("email", userEmail)
    payload = event["body"]
    if isinstance(payload, str):
        logger.info(f"Received payload of type str, deserialzing")
        payload = json.loads(payload)
    registry = TenancyCollection(
        critters=[CritterTenancy(**critter) for critter in payload.get("critters")]
    )  # validation purposes
    petTenancies = registry.critters
    createdTenancies = TenancyCollection([], 0)
    for petTenancy in petTenancies:
        currentPetLogger = logger.branch("petIteratorForTenacyRegistry")
        currentPetLogger.addCtxItem("petName", petTenancy.petName)
        currentPetLogger.info(
            f"Registering future tenancy for pet {petTenancy.petName}({userEmail}), from {petTenancy.checkInDate} to {petTenancy.checkOutDate}"
        )
        petData = getPet(
            userEmail,
            petTenancy.petName,
            httpClient,
            currentPetLogger.branch("getPetForTenancyRegistry"),
        )
        createdTenacy = updatePetTenancy(
            userEmail,
            petData,
            petTenancy,
            httpClient,
            currentPetLogger.branch("updatePetForTenancyRegistry"),
        )
        currentPetLogger.info(
            f"Registered future tenancy with id {createdTenacy.tenancyId} for pet {petTenancy.petName}({userEmail}), from {petTenancy.checkInDate} to {petTenancy.checkOutDate}"
        )
        createdTenancies.critters.append(createdTenacy)
    createdTenancies.count = len(createdTenancies.critters)
    logger.info(f"Added {len(createdTenancies.count)} tenancies")
    return ok(modelToDict(createdTenancies))


handler = httpHandlerDecorator(handlerRaw)
