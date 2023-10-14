from db import getCritterTable
from framework import handlerDecorator, LoggerInstance, notFound, ok
from util import getElementFromParams


def rawHandler(event, context, logger: LoggerInstance):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("ownerEmail", event)
    critterName = getElementFromParams("petName", event)
    logger.addCtx(
        {"critterInput": {"ownerEmail": critterOwnerEmail, "petName": critterName}}
    )
    response = table.get_item(
        Key={"petName": critterName, "ownerEmail": critterOwnerEmail}
    )
    logger.addCtxItem("dbResponse", response)
    if "Item" not in response:
        logger.info("Could not find critter")
        return notFound(
            {
                "errorMessage": f"No critter with petName:ownerEmail {critterName}:{critterOwnerEmail} found"
            }
        )

    logger.info("Found critter")
    critter = response["Item"]
    logger.addCtxItem("critterData", critter)
    return ok(critter)


handler = handlerDecorator(rawHandler)
