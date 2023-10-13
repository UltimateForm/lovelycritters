from framework import handlerDecorator, LoggerInstance, ok
from boto3.dynamodb.conditions import Attr



def rawHandler(event, context, logger: LoggerInstance):
    return ok({})


handler = handlerDecorator(rawHandler)
