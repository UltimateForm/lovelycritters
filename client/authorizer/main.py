from framework import HttpClient, LoggerInstance, handlerDecorator
import jwt
import os

JWT_SECRET = os.environ.get("JWT_SECRET")


def handlerRaw(event, context, logger: LoggerInstance):
    methodArn = event[
        "methodArn"
    ]  # i.e: arn:aws:execute-api:eu-east-2:12451516336:dd35hs36/ESTestInvoke-stage/GET/
    authToken = event["authorizationToken"]
    decodedJwtData = {}
    try:
        decodedJwtData = jwt.decode(authToken, JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        logger.exception(str(e))
        raise Exception("Unauthorized")
    userEmail = decodedJwtData.get("userData").get("email")
    methodArnSplitByColon = methodArn.split(":")
    apiGatewayIds = methodArnSplitByColon[5].split("/")
    apiGatewayStage = apiGatewayIds[1]
    apiGatewayId = apiGatewayIds[0]
    region = methodArnSplitByColon[3]
    accountId = methodArnSplitByColon[4]
    tenancyResource = f"arn:aws:execute-api:{region}:{accountId}:{apiGatewayId}/{apiGatewayStage}/*/tenancy/{userEmail}"
    userResource = f"arn:aws:execute-api:{region}:{accountId}:{apiGatewayId}/{apiGatewayStage}/*/user/{userEmail}"
    return {
        "principalId": userEmail,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": tenancyResource,
                },
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": userResource,
                },
            ],
        }
    }


handler = handlerDecorator(handlerRaw, "client-authorizer")
