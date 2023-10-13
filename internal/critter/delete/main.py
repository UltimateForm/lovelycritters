from framework import handlerDecorator, LoggerInstance, okNoData
from db import getCritterTable
from util import getElementFromParams


def rawHandler(event, _, logger: LoggerInstance):
    (dynamodb, table) = getCritterTable()
    critterOwnerEmail = getElementFromParams("ownerEmail", event)
    critterName = getElementFromParams("name", event)
    logger.addCtx(
        {"critterInput": {"ownerEmail": critterOwnerEmail, "name": critterName}}
    )
    logger.info(f"Deleting critter with name:email  {critterName}:{critterOwnerEmail}")
    deletion = None
    deletion = table.delete_item(
        Key={"name": critterName, "ownerEmail": critterOwnerEmail}
    )
    logger.addCtxItem("dbResponse", deletion)
    logger.info(f"Deleted critter {critterName}{critterOwnerEmail}")
    return okNoData()


handler = handlerDecorator(rawHandler)
