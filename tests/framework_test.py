import unittest
from common import framework as f
from unittest import mock
from typing import Callable

testEvent = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/path/to/resource",
    "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
    "cookies": ["cookie1", "cookie2"],
    "headers": {"Header1": "value1", "Header2": "value1,value2"},
    "queryStringParameters": {"parameter1": "value1,value2", "parameter2": "value"},
    "requestContext": {
        "accountId": "123456789012",
        "apiId": "api-id",
        "authentication": {
            "clientCert": {
                "clientCertPem": "CERT_CONTENT",
                "subjectDN": "www.example.com",
                "issuerDN": "Example issuer",
                "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                "validity": {
                    "notBefore": "May 28 12:30:02 2019 GMT",
                    "notAfter": "Aug  5 09:36:04 2021 GMT",
                },
            }
        },
        "authorizer": {
            "jwt": {
                "claims": {"claim1": "value1", "claim2": "value2"},
                "scopes": ["scope1", "scope2"],
            }
        },
        "domainName": "id.execute-api.us-east-1.amazonaws.com",
        "domainPrefix": "id",
        "http": {
            "method": "POST",
            "path": "/path/to/resource",
            "protocol": "HTTP/1.1",
            "sourceIp": "192.168.0.1/32",
            "userAgent": "agent",
        },
        "requestId": "id",
        "routeKey": "$default",
        "stage": "$default",
        "time": "12/Mar/2020:19:03:58 +0000",
        "timeEpoch": 1583348638390,
    },
    "body": "eyJ0ZXN0IjoiYm9keSJ9",
    "pathParameters": {"parameter1": "value1"},
    "isBase64Encoded": True,
    "stageVariables": {"stageVariable1": "value1", "stageVariable2": "value2"},
}


class HandlerDecorator(unittest.TestCase):
    def test_withoutLaundry(self):
        decorator = f.httpHandlerDecorator

        def handlerRaw(
            event, context, logger: f.LoggerInstance, httpClient: f.HttpClient, **kwargs
        ):
            return f.internalServerError({"errorMessage": "error"})

        decoratedFunction = decorator(handler=handlerRaw)
        response = decoratedFunction(testEvent, {})
        statusCode = response.get("statusCode")
        self.assertEqual(statusCode, 500)

    def test_laundryMachine(self):
        decorator = f.httpHandlerDecorator
        laundryMachine = mock.Mock()

        def handlerRaw(
            event,
            context,
            logger: f.LoggerInstance,
            httpClient: f.HttpClient,
            laundry: dict = {},
        ):
            laundry["itemToClean"] = "sd124"
            return f.internalServerError({"errorMessage": "error"})

        decoratedFunction = decorator(handler=handlerRaw, laundryMachine=laundryMachine)
        decoratedFunction(testEvent, {})
        args = laundryMachine.call_args[0]
        laundryMachine.assert_called_once()
        self.assertEqual(
            {"itemToClean": "sd124"},
            args[0],
            "Laundry machine not called with expected cleanup data",
        )


if __name__ == "__main__":
    unittest.main()
