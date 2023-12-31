import json
from framework import HttpClient, httpHandlerDecorator, LoggerInstance, notFound, ok
from models import Critter
from db import getCritterTable

from util import getElementFromParams


def rawHandler(
    event, context, logger: LoggerInstance, httpClient: HttpClient, **kwargs
):
    critterOwnerEmail = getElementFromParams("email", event)
    critterName = getElementFromParams("petName", event)
    critterPayload = event["body"]
    if isinstance(critterPayload, str):
        logger.info(f"Received critter of type str, deserialzing")
        critterPayload = json.loads(critterPayload)
    (dynamodb, table) = getCritterTable()
    critter = Critter(petName=critterName, email=critterOwnerEmail, **critterPayload)
    dbResponse = None
    try:
        dbResponse = table.update_item(
            Key={
                "email": critterOwnerEmail,
                "petName": critterName,
            },
            UpdateExpression="set birthDate=:bd, breed=:br, neutered=:ne, futureTenancy=:ft, tenancy=:tn, pastTenancy=:pt, species=:sp, vaccines=:vc",
            ExpressionAttributeValues={
                ":bd": critter.birthDate,
                ":br": critter.breed,
                ":ne": critter.neutered,
                ":ft": critter.futureTenancy,
                ":tn": critter.tenancy,
                ":pt": critter.pastTenancy,
                ":sp": critter.species,
                ":vc": critter.vaccines,
            },
            ReturnValues="UPDATED_NEW",
            ConditionExpression="attribute_exists(petName) AND attribute_exists(email)",
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e:
        msg = f"No critter with petName:email {critterName}:{critterOwnerEmail} found"
        logger.info(msg, {"dbResponse": dbResponse, "exception": e.response})
        return notFound({"errorMesssage": msg})

    logger.info("DB responded ctx", {"dbResponse": dbResponse})
    updatedCritter = dbResponse.get("Attributes")
    logger.info("Updated item successfully", {"critterData": updatedCritter})
    return ok(updatedCritter)


handler = httpHandlerDecorator(rawHandler)
