from framework import handlerDecorator, LoggerInstance, okNoData
from db import getCritterTable
from util import getElementFromParams


def rawHandler(event, _, logger: LoggerInstance):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("ownerEmail", event)
    critterName = getElementFromParams("petName", event)
    logger.addCtx(
        {"critterInput": {"ownerEmail": critterOwnerEmail, "petName": critterName}}
    )
    logger.info(
        f"Deleting critter with petName:email  {critterName}:{critterOwnerEmail}"
    )
    deletion = None
    deletion = table.delete_item(
        Key={
            "ownerEmail": critterOwnerEmail,
            "petName": critterName,
        }
    )
    logger.addCtxItem("dbResponse", deletion)
    logger.info(f"Deleted critter {critterName}:{critterOwnerEmail}")
    return okNoData()


handler = handlerDecorator(rawHandler)
