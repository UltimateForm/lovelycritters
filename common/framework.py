from typing import Callable, Any
import json
import logging


def initLoggerConfig():
    if logging.getLogger().hasHandlers:
        # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
        # `.basicConfig` does not execute. Thus we set the level directly.
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)


class LoggerInstance:
    _context: dict[str, Any]
    _logger: logging.Logger

    def __init__(self, context: dict[str, Any] = {}) -> None:
        self._context = context
        self._logger = logging.getLogger()
        pass

    def addCtxItem(self, key: str, msg: Any):
        self._context.update({key: msg})

    def addCtx(self, data: dict):
        self._context.update([(key, data[key]) for key in data.keys()])

    def _prepareLog(self, msg: str, ctx: dict[str, Any] = {}) -> str:
        combinedDict = {**self._context, **ctx, "message": msg}
        jsonLog = json.dumps(combinedDict)
        return jsonLog

    def info(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.info(structedLog)

    def warning(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.warning(structedLog)

    def error(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.error(structedLog)

    def debug(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.debug(structedLog)


def handlerDecorator(
    handler: Callable[[Any, Any, LoggerInstance], dict]
) -> Callable[[Any, Any], dict]:

    def handlerDecorated(event, context):
        logger = LoggerInstance({"loggerName": "framework"})
        initLoggerConfig()
        logger.addCtx(
            {
                "Resource": event.get("resource"),
                "Method": event.get("httpMethod"),
                "Event": event,
            }
        )
        logger.info(
            f"INCOMING REQUEST {event.get('httpMethod')} {event.get('resource')}"
        )
        response = {}
        try:
            response = handler(event, context, logger)
        except Exception as e:
            logger.error(f"Error occured while processing request: {str(e)}")
            response = {"statusCode": 500, "body": json.dumps({"errorMessage": str(e)})}
        logger.addCtx(
            {"StatusCode": response.get("statusCode"), "Body": response.get("body")}
        )
        logger.info(f"OUTGOING RESPONSE {response.get('statusCode')}")
        return response

    return handlerDecorated


def response(statusCode: int, body: dict = None):
    response = {"statusCode": statusCode}
    if body is not None:
        response["body"] = json.dumps(body)
    return response


def notFound(body: dict = None):
    return response(404, body=body)


def conflict(body: dict = None):
    return response(409, body=body)


def okNoData():
    return response(204)


def ok(body: dict = None):
    return response(200, body=body)


def okCreated(body: dict = None):
    return response(201, body=body)
