from db import getCritterTable
import json
from framework import handlerDecorator, LoggerInstance, notFound, ok
from util import getElementFromParams


def rawHandler(event, context, logger: LoggerInstance):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("ownerEmail", event)
    critterName = getElementFromParams("name", event)
    logger.addCtx(
        {"critterInput": {"ownerEmail": critterOwnerEmail, "name": critterName}}
    )
    response = table.get_item(
        Key={"name": critterName, "ownerEmail": critterOwnerEmail}
    )
    logger.addCtxItem("dbResponse", response)
    if "Item" not in response:
        logger.info("Could not find critter")
        return notFound(
            {
                "errorMessage": f"No critter with name:ownerEmail {critterName}:{critterOwnerEmail} found"
            }
        )

    logger.info("Found critter")
    critter = response["Item"]
    logger.addCtxItem("critterData", critter)
    return ok(critter)


handler = handlerDecorator(rawHandler)
