from framework import (
    HttpClient,
    LoggerInstance,
    httpHandlerDecorator,
    response,
    ok,
    notFound,
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
    tenancyId = getElementFromParams("tenancyId", event)
    logger.addCtx({"email": userEmail, "petName": petName, "tenancyId": tenancyId})
    petData = getPet(userEmail, petName, httpClient, logger.branch("getPetForCheckIn"))
    generator = (
        ten for ten in enumerate(petData.futureTenancy) if ten[1].tenancyId == tenancyId
    )
    foundTenancy = ()
    try:
        foundTenancy = next(generator)
    except (Exception, StopIteration) as e:
        if type(e) == StopIteration:
            errMessage = f"Selected tenancy ({tenancyId}) is not a known upcoming stay for {petName}"
            logger.info(f"CheckIn failure: {errMessage}")
            return notFound({"errorMessage": errMessage})
        else:
            raise
    tenancyIndex, tenancyData = foundTenancy
    if petData.tenancy is not None:
        logger.info(
            f"CheckIn failure: already checked in", {"tenancy": petData.tenancy}
        )
        return badRequest({"errorMessage": "Already checked in"})
    petData.tenancy = tenancyData
    petData.futureTenancy.pop(tenancyIndex)
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
    tenancyDict = modelToDict(tenancyData)
    logger.info(f"CheckIn {tenancyId} {petName} {userEmail}", {"tenancy": tenancyDict})
    return ok(tenancyDict)


handler = httpHandlerDecorator(handlerRaw)
