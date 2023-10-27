from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda,
    aws_apigateway,
    CfnOutput,
    Fn,
    # aws_sqs as sqs,
)
from os import path, getcwd
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from .clientUserApi import createUserApi


class LC_ClientStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        cwd = getcwd()
        basePath = f"{cwd}/client"
        runtime: aws_lambda.Runtime = aws_lambda.Runtime.PYTHON_3_11
        pythonLayer = PythonLayerVersion(
            self, "lc_common", entry=f"{cwd}/common", compatible_runtimes=[runtime]
        )
        internalApiUrl = Fn.import_value("internalApiUrl")
        api = aws_apigateway.RestApi(
            self,
            "client-api",
            rest_api_name="Lovely Critters Client API",
            description="This API serves as a bridge between client applications and internal services",
            default_method_options={
                "api_key_required": True,
            },
        )
        createUserApi(self, runtime, pythonLayer, basePath, api, internalApiUrl)
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
