from db import getCritterTable
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, notFound, ok
from util import getElementFromParams


def rawHandler(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("email", event)
    critterName = getElementFromParams("petName", event)
    logger.addCtx({"email": critterOwnerEmail, "petName": critterName})
    response = table.get_item(
        Key={
            "email": critterOwnerEmail,
            "petName": critterName,
        }
    )
    logger.addCtxItem("dbResponse", response)
    if "Item" not in response:
        logger.info("Could not find critter")
        return notFound(
            {
                "errorMessage": f"No critter with petName:email {critterName}:{critterOwnerEmail} found"
            }
        )

    logger.info("Found critter")
    critter = response["Item"]
    logger.addCtxItem("critterData", critter)
    return ok(critter)


handler = httpHandlerDecorator(rawHandler)
