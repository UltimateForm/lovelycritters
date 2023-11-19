from typing import Callable, Any, Optional
import json
import logging
from decimal import Decimal
import requests
import os


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
    _name: str
    _parent: str
    _primitiveLogging: bool

    def __init__(
        self,
        context: dict[str, Any] = {},
        name: str = "",
        parent: str = "",
        primitiveLogging=False,
    ) -> None:
        self._context = context
        self._name = name
        self._parent = parent
        self._primitiveLogging: bool = primitiveLogging
        if name:
            self._context["loggerName"] = name
        if parent:
            self._context["parentLoggerName"] = parent
        self._logger = logging.getLogger()
        pass

    def addCtxItem(self, key: str, msg: Any):
        self._context.update({key: msg})

    def addCtx(self, data: dict):
        self._context.update([(key, data[key]) for key in data.keys()])

    def _prepareLog(self, msg: str, ctx: dict[str, Any] = {}) -> str:
        if self._primitiveLogging:
            return msg
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

    def critical(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.critical(structedLog)

    def exception(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.exception(structedLog, stack_info=True, stacklevel=5)

    def debug(self, msg: str, ctx: dict[str, Any] = {}):
        structedLog = self._prepareLog(msg, ctx)
        self._logger.debug(structedLog)

    def branch(self, branchName: str):
        return LoggerInstance(
            {**self._context}, branchName, self._name, self._primitiveLogging
        )


def createResponseLogger(logger: LoggerInstance):
    def logResponse(r: requests.Response, *args, **kwargs):
        method = r.request.method
        statusCode = r.status_code
        statusCodeTxt = r.reason.replace(" ", "")
        url = r.url
        responsePayload = None
        try:
            responsePayload = r.json()
        except:
            pass
        requestPayload = (
            r.request.body.decode() if type(r.request.body) == bytes else r.request.body
        )
        requestJson = None
        if requestPayload:
            try:
                requestJson = json.loads(requestPayload)
            except Exception as e:
                logger.error(
                    "Failed to parse original request while writing HTTP event log",
                    {"error": str(e)},
                )
        ellapsedMicroSecs = r.elapsed.microseconds
        msg = f"HTTP {method} {url} {statusCode} {statusCodeTxt}"
        ctx = {
            "requestPayload": requestJson,
            "responsePayload": responsePayload,
            "http": {
                "url": url,
                "statusCode": statusCode,
                "statusCodeTxt": statusCodeTxt,
                "elapsedMicroSecs": ellapsedMicroSecs,
            },
        }
        logger.info(msg, ctx)

    return logResponse


class HttpClient:
    _responseLogger: Callable[[requests.Response, list, dict], Any] = None
    _logger: LoggerInstance

    def __init__(self, logger: LoggerInstance):
        self._logger = logger
        self._responseLogger = createResponseLogger(
            logger.branch("httpClientResponseLogger")
        )
        pass

    def send(
        self, method: str, url: str, payload: dict | None = None, headers: dict = {}
    ) -> requests.Response:
        # todo: consider adding logs here
        return requests.request(
            method=method,
            url=url,
            json=payload,
            headers=headers,
            hooks={"response": self._responseLogger},
        )

    def _getJsonFromResponse(self, response: requests.Response):
        try:
            jsonRes = response.json()
            return jsonRes
        # todo: figure out a way to catch the literal excpetion, it's one from simplejson but i don't want to add that dependency
        except Exception:
            return None

    def post(self, url: str, payload: dict, headers: dict):
        response = self.send("POST", url, payload, headers)
        responseJson = self._getJsonFromResponse(response)
        return (response.ok, response.status_code, responseJson)

    def get(self, url: str, payload: dict, headers: dict):
        response = self.send("GET", url, payload, headers)
        responseJson = self._getJsonFromResponse(response)
        return (response.ok, response.status_code, responseJson)

    def put(self, url: str, payload: dict, headers: dict):
        response = self.send("PUT", url, payload, headers)
        responseJson = self._getJsonFromResponse(response)
        return (response.ok, response.status_code, responseJson)

    def delete(self, url: str, headers: dict):
        response = self.send("DELETE", url, headers=headers)
        responseJson = self._getJsonFromResponse(response)
        return (response.ok, response.status_code, responseJson)


def httpHandlerDecorator(
    handler: Callable[[Any, Any, LoggerInstance, HttpClient, Optional[dict]], dict],
    laundryMachine: Optional[Callable[[dict], Any]] = None,
) -> Callable[[Any, Any], dict]:
    def handlerDecorated(event, context):
        awsSamLocal = os.environ.get("AWS_SAM_LOCAL")
        logger = LoggerInstance(
            {}, "framework", "", primitiveLogging=awsSamLocal == "true"
        )
        initLoggerConfig()
        resource = event.get("resource")
        logger.addCtx(
            {
                "Resource": resource,
                "Method": event.get("httpMethod"),
                "Event": event,
            }
        )
        logger.info(
            f"INCOMING REQUEST {event.get('httpMethod')} {event.get('resource')}"
        )
        httpClient = HttpClient(logger.branch(HttpClient.__name__))
        response = {}
        laundry = {}
        try:
            response = handler(
                event,
                context,
                logger.branch("handlerFunction"),
                httpClient,
                laundry=laundry,
            )
        except Exception as e:
            logger.exception(str(e))
            logger.error(f"Error occured while processing request: {str(e)}")
            response = {"statusCode": 500, "body": json.dumps({"errorMessage": str(e)})}
        responseStatusCode = response.get("statusCode")
        if (
            responseStatusCode >= 400 or responseStatusCode < 200
        ) and laundryMachine is not None:
            logger.info(
                f"Per bad status {responseStatusCode} initiating laundry cleanup"
            )
            try:
                # todo: this should be a separate  lambda
                # no sense in making user wait for a cleanup function
                laundryMachine(laundry, logger.branch("laundryMachine"), httpClient)
            except Exception as e:
                logger.exception(str(e))
                # Note: good place for alarm example
                logger.critical(f"ROLLBACK PROCEDURE FAILED FOR {resource}")
        logger.addCtx(
            {"StatusCode": response.get("statusCode"), "Body": response.get("body")}
        )
        logger.info(f"OUTGOING RESPONSE {response.get('statusCode')}")
        return response

    return handlerDecorated


def handlerDecorator(
    handler: Callable[[Any, Any, LoggerInstance], dict], methodName: str
) -> Callable[[Any, Any], dict]:
    def handlerDecorated(event, context):
        awsSamLocal = os.environ.get("AWS_SAM_LOCAL")
        logger = LoggerInstance(
            {}, "framework", "", primitiveLogging=awsSamLocal == "true"
        )
        initLoggerConfig()
        resource = methodName
        logger.addCtx(
            {
                "Resource": resource,
                "Event": event,
            }
        )
        logger.info(f"INCOMING REQUEST {resource}")
        response = {}
        response = handler(
            event,
            context,
            logger.branch("handlerFunction"),
        )
        logger.info(f"OUTGOING RESPONSE {response}")
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


def badRequest(body: dict = None):
    return response(400, body=body)


def unauthorized(body: dict = None):
    return response(401, body=body)


def internalServerError(body: dict = None):
    return response(500, body=body)
