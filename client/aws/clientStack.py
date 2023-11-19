from aws_cdk import (
    Stack,
    aws_lambda,
    aws_apigateway,
    CfnOutput,
    Duration,
    Fn,
    CfnParameter,
)
from os import path, getcwd, environ
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from .clientUserApi import createUserApi
from .clientTenancyApi import createTenancyApi

class LC_ClientStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        cwd = getcwd()
        basePath = f"{cwd}/client"
        runtime: aws_lambda.Runtime = aws_lambda.Runtime.PYTHON_3_11
        jwtSecretParam = CfnParameter(
            self,
            "jwtSecret",
            type="String",
            description="The jwt secret (should be in parameter store but i dont have patience)",
            default=environ.get("JWT_SECRET"),
        )
        pythonLayer = PythonLayerVersion(
            self, "lc_common", entry=f"{cwd}/common", compatible_runtimes=[runtime]
        )
        internalApiUrl = Fn.import_value("internalApiUrl")
        internalApiKey = environ.get("INTERNAL_API_KEY")
        api = aws_apigateway.RestApi(
            self,
            "client-api",
            rest_api_name="Lovely Critters Client API",
            description="This API serves as a bridge between client applications and internal services",
            default_method_options={
                "api_key_required": True,
            },
        )
        commonFunctionArgs = {
            "runtime": runtime,
            "index": "main.py",
            "handler": "handler",
            "environment": {
                "INTERNAL_API_URL": internalApiUrl,
                "INTERNAL_API_KEY": internalApiKey,
            },
            "timeout": Duration.seconds(30),
            "layers": [pythonLayer],
        }
        authorizerLmbd = PythonFunction(
            self,
            "authorizer",
            entry=path.join(basePath, "authorizer"),
            function_name="lc-client-authorizer",
            **{
                **commonFunctionArgs,
                "environment": {
                    "JWT_SECRET": jwtSecretParam.value_as_string,
                },
            },
        )
        tokenAuthorizer = aws_apigateway.TokenAuthorizer(
            self,
            "token-authorizer",
            handler=authorizerLmbd,
            authorizer_name="lc-client-apigw-authorizer",
            identity_source=aws_apigateway.IdentitySource.header("Authorization"),
        )
        # todo: create framework way of automatically building the api per filesystem or json connfig
        # the way it is it creates too much repeated code
        createUserApi(self, commonFunctionArgs, basePath, api, tokenAuthorizer)
        createTenancyApi(self, commonFunctionArgs, basePath, api, tokenAuthorizer)
        throttleSettings = aws_apigateway.ThrottleSettings(
            rate_limit=10, burst_limit=10
        )
        usagePlan: aws_apigateway.UsagePlan = api.add_usage_plan(
            "clientApiUsagePlan",
            name="Main Usage Plan",
            throttle=throttleSettings,
            api_stages=[
                aws_apigateway.UsagePlanPerApiStage(
                    stage=api.deployment_stage,
                )
            ],
        )
        apiKey = api.add_api_key(id="clientApiKey", api_key_name="Main Client API Key")
        usagePlan.add_api_key(apiKey)
        CfnOutput(self, "clientAPIUrl", value=api.url)
        CfnOutput(self, "clientAPIKeyId", value=apiKey.key_id)
