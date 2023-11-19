import json
from framework import (
    okNoData,
    badRequest,
    LoggerInstance,
    HttpClient,
    httpHandlerDecorator,
    response,
)
from models import Critter
from util import (
    getElementFromParams,
    getEmailFromPathParams,
    getInternalApi,
    joinUrl,
    dictWithoutKey,
    modelToDict,
)


def getPet(
    email: str, petName: str, httpClient: HttpClient, logger: LoggerInstance
) -> Critter:
    (internalApiUrl, internalApiKey) = getInternalApi()
    petUrl = joinUrl(internalApiUrl, "critter", email, petName)
    (responseOk, statusCode, data) = httpClient.get(
        petUrl, None, {"x-api-key": internalApiKey}
    )
    if not responseOk:
        raise Exception(
            f"Failure ({statusCode}) at retrieving pet {petName} from user {email}"
        )
    # todo: find framework way of properly converting dicts to models
    # this one is keeping future tenancies as an array of dicts
    critter = Critter(**data)
    return critter


def handlerRaw(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    userEmail = getEmailFromPathParams(event)
    tenancyId = getElementFromParams("tenancyId", event)
    petName = getElementFromParams("petName", event)
    logger.addCtx({"email": userEmail, "petName": petName, "tenancyId": tenancyId})
    (internalApiUrl, internalApiKey) = getInternalApi()
    petData = getPet(
        userEmail, petName, httpClient, logger.branch("getPetForTenancyCancel")
    )
    if petData.futureTenancy is None or not len(petData.futureTenancy):
        errorMsg = f"Pet {petName}({userEmail}) does not have any upcoming stay"
        logger.info(errorMsg)
        return badRequest({"errorMessage": errorMsg})
    # todo: use generator to only compute past here if tenancyId is present in list
    petData.futureTenancy = [
        tenancy for tenancy in petData.futureTenancy if tenancy.get("tenancyId") != tenancyId
    ]
    petDataDict = modelToDict(petData)
    logger.info(
        f"Canceling tenancy({tenancyId}) for {petName}({userEmail})",
        {"updated": petDataDict},
    )
    updatePetPayload = dictWithoutKey(petDataDict, "email", "petName")
    updatePetUrl = joinUrl(internalApiUrl, "critter", userEmail, petData.petName)
    (responseOk, statusCode, data) = httpClient.put(
        updatePetUrl, updatePetPayload, {"x-api-key": internalApiKey}
    )
    if not responseOk:
        errorMsg = data.get("errorMessage") if data is not None else None
        return response(
            statusCode,
            {
                "errorMessage": errorMsg or f"Failed to update pet tenancy",
                "source": "outbound",
            },
        )
    return okNoData()


handler = httpHandlerDecorator(handlerRaw)
