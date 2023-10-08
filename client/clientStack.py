from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda,
    aws_apigateway,
    CfnOutput,
    # aws_sqs as sqs,
)
from os import path, getcwd
from constructs import Construct


class LC_ClientStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        cwd = getcwd()
        basePath = f"{cwd}/client"
        getUserDataLmbd = aws_lambda.Function(
            self,
            "getUserData",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=aws_lambda.Code.from_asset(path.join(basePath, "user/data")),
            handler="main.handler",
            function_name="lc-client-getUserData",
        )
        createUserLmbd = aws_lambda.Function(
            self,
            "createUser",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            code=aws_lambda.Code.from_asset(path.join(basePath, "user/create")),
            handler="main.handler",
            function_name="lc-client-createUser",
        )
        api = aws_apigateway.RestApi(
            self,
            "client-api",
            rest_api_name="Lovely Critters Client API",
            description="This API serves as a bridge between client applications and internal services",
            default_method_options={
                "api_key_required": True,
            },
        )
        aws_apigateway.Stage()
        apiPlan = api.add_usage_plan(
            "mainApiUsagePlan",
            name="Main Usage Plan",
            throttle=aws_apigateway.ThrottleSettings(rate_limit=10, burst_limit=10),
        )
        apiKey = api.add_api_key(id="clientApiKey", api_key_name="Main API Key")
        apiPlan.add_api_key(apiKey)
        apiPlan.add_api_stage(stage=api.deployment_stage)
        userApi = api.root.add_resource("user")
        userApi.add_resource("{userId}").add_method(
            "GET",
            aws_apigateway.LambdaIntegration(
                getUserDataLmbd,
                request_templates={"application/json": '{"statusCode": "200"}'},
            ),
        )
        userApi.add_method(
            "POST",
            aws_apigateway.LambdaIntegration(
                createUserLmbd,
                request_templates={"application/json": '{"statusCode": "200"}'},
            ),
        )
        CfnOutput(self, "clientAPIUrl", value=api.url)
        CfnOutput(self, "clientAPIKey", value=apiKey.key_id)
