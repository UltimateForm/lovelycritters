from framework import (
    HttpClient,
    LoggerInstance,
    httpHandlerDecorator,
    response,
    ok,
    badRequest,
)
from models import Critter, Tenancy
from util import (
    dictWithoutKey,
    getElementFromParams,
    getEmailFromPathParams,
    getInternalApi,
    joinUrl,
    modelToDict,
)


# todo: find way to reuse this, framework option?
# maybe have a way for this to directly call the lambda that gets pet? feels insecure tho
def getPet(
    email: str, petName: str, httpClient: HttpClient, logger: LoggerInstance
) -> Critter:
    internalApiUrl, internalApiKey = getInternalApi()
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
    critter.futureTenancy = [Tenancy(**ten) for ten in critter.futureTenancy]
    return critter


def handlerRaw(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    userEmail = getEmailFromPathParams(event)
    petName = getElementFromParams("petName", event)
    logger.addCtx({"email": userEmail, "petName": petName})
    petData = getPet(userEmail, petName, httpClient, logger.branch("getPetForCheckIn"))
    tenancy = petData.tenancy
    if tenancy == None:
        errMsg = f"{petName} ({userEmail}) is not checked in"
        logger.info(f"CheckOut failure: {errMsg}")
        return badRequest({"errorMessage": errMsg})
    logger.addCtxItem("tenancyId", petData.tenancy.get("tenancyId"))
    logger.addCtxItem("tenancy", petData.tenancy)
    if petData.pastTenancy == None:
        petData.pastTenancy = []
    petData.pastTenancy.append(tenancy)
    petData.tenancy = None
    internalApiUrl, internalApiKey = getInternalApi()
    petDataDict = modelToDict(petData)
    updatePetPayload = dictWithoutKey(petDataDict, "email", "petName")
    updatePetUrl = joinUrl(internalApiUrl, "critter", userEmail, petName)
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
    tenancyDict = petDataDict.get("tenancy")
    logger.info(f"CheckOut {tenancyDict} {petName} {userEmail}")
    return ok(tenancyDict)


handler = httpHandlerDecorator(handlerRaw)
