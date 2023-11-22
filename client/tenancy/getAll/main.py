from framework import HttpClient, LoggerInstance, httpHandlerDecorator, response, ok
from models import TenancyCollection, CritterTenancy
from util import getEmailFromPathParams, getInternalApi, joinUrl, parseDate, modelToDict


def dictToCritterTenancy(petName: str, source: dict) -> CritterTenancy:
    ten = CritterTenancy(
        petName,
        parseDate(source.get("checkInDate")),
        parseDate(source.get("checkOutDate")),
        source.get("tenancyId"),
    )
    return ten


def handlerRaw(event, ctx, logger: LoggerInstance, httpClient: HttpClient, **kwargs):
    userEmail = getEmailFromPathParams(event)
    logger.addCtxItem("email", userEmail)
    (internalApiUrl, internalApiKey) = getInternalApi()
    getAllPetsUrl = joinUrl(internalApiUrl, "critter", userEmail)
    (responseOk, statusCode, data) = httpClient.get(
        getAllPetsUrl, None, {"x-api-key": internalApiKey}
    )
    if not responseOk:
        errorMsg = (
            data.get("errorMessage")
            if data is not None
            # todo: would be interesting to have a framework way of creatinng this human error messages
            else f"Failed to retrieve critters for {userEmail}, error {statusCode}"
        )
        return response(statusCode, {"errorMessage": errorMsg, "source": "outbound"})
    logger.info(f"Retrieved {data.get('count')} critter from user {userEmail}")
    coll = TenancyCollection([], 0)
    for critter in data.get("critters"):
        iterLogger = logger.branch("iterLoggerForGetAllTenancies")
        petName = critter.get("petName")
        iterLogger.addCtxItem("petName", petName)
        currentTenancy = critter.get("tenancy")
        listOfCurrentTenancy = [currentTenancy] if currentTenancy else []
        futureTenancy = critter.get("futureTenancy") or []
        pastTenancy = critter.get("pastTenancy") or []
        allTenancies = [*listOfCurrentTenancy, *futureTenancy, *pastTenancy]
        allTenanciesTyped = [
            dictToCritterTenancy(petName, tenancy) for tenancy in allTenancies
        ]
        coll.critters.extend(allTenanciesTyped)
        count = len(allTenanciesTyped)
        coll.count += count
        iterLogger.info(
            f"Aggregated {count} critter tenancies for {petName} ({userEmail})",
            {"critterTenancies": allTenancies},
        )
    collDict = modelToDict(coll)
    logger.info(
        f"Aggregated {coll.count} tenancies for {userEmail}", {"tenancies": collDict}
    )
    return ok(collDict)


handler = httpHandlerDecorator(handlerRaw)
