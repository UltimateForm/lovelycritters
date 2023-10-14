import json
from framework import handlerDecorator, LoggerInstance, notFound, ok
from models import Critter
from db import getCritterTable

from util import getElementFromParams


def rawHandler(event, context, logger: LoggerInstance):
    critterOwnerEmail = getElementFromParams("ownerEmail", event)
    critterName = getElementFromParams("petName", event)
    critterPayload = event["body"]
    if isinstance(critterPayload, str):
        logger.info(f"Received critter of type str, deserialzing")
        critterPayload = json.loads(critterPayload)
    (dynamodb, table) = getCritterTable()
    critter = Critter(
        petName=critterName, ownerEmail=critterOwnerEmail, **critterPayload
    )
    dbResponse = None
    try:
        dbResponse = table.update_item(
            Key={"petName": critterName, "ownerEmail": critterOwnerEmail},
            UpdateExpression="set birthDate=:bd, breed=:br, neutered=:ne, pastTenancy=:pt, species=:sp, vaccines=:vc",
            ExpressionAttributeValues={
                ":bd": critter.birthDate,
                ":br": critter.breed,
                ":ne": critter.neutered,
                ":pt": critter.pastTenancy,
                ":sp": critter.species,
                ":vc": critter.vaccines,
            },
            ReturnValues="UPDATED_NEW",
            ConditionExpression="attribute_exists(petName) AND attribute_exists(ownerEmail)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = f"No critter with petName:ownerEmail {critterName}:{critterOwnerEmail} found"
        logger.info(msg, {"dbResponse": dbResponse, "exception": e.response})
        return notFound({"errorMesssage": msg})

    logger.info("DB responded ctx", {"dbResponse": dbResponse})
    updatedCritter = dbResponse.get("Attributes")
    logger.info("Updated item successfully", {"critterData": updatedCritter})
    return ok(updatedCritter)


handler = handlerDecorator(rawHandler)
