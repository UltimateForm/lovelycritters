from attr import dataclass
from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda,
    aws_apigateway,
    CfnOutput,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    # aws_sqs as sqs,
)
from .databases import createDatabases
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion
from os import path, getcwd
from constructs import Construct


class LC_InternalStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        cwd = getcwd()
        basePath = f"{cwd}/internal"
        dbs = createDatabases(self)
        runtime: aws_lambda.Runtime = aws_lambda.Runtime.PYTHON_3_11
        pythonLayer = PythonLayerVersion(
            self, "lc_common", entry=f"{cwd}/common", compatible_runtimes=[runtime]
        )
        commonFunctionArgs = {
            "runtime": runtime,
            "index": "main.py",
            "handler": "handler",
            "environment": {"USER_TABLE_NAME": dbs.user.table_name},
            "layers": [pythonLayer],
        }
        createUserLmbd = PythonFunction(
            self,
            "createUser",
            entry=path.join(basePath, "user/create"),
            function_name="lc-internal-createUser",
            **commonFunctionArgs,
        )
        readUserLmbd = PythonFunction(
            self,
            "readUser",
            entry=path.join(basePath, "user/read"),
            function_name="lc-internal-readUser",
            **commonFunctionArgs,
        )
        updateUserLmbd = PythonFunction(
            self,
            "updateUser",
            entry=path.join(basePath, "user/update"),
            function_name="lc-internal-updateUser",
            **commonFunctionArgs,
        )
        deleteUserLmbd = PythonFunction(
            self,
            "deleteUser",
            entry=path.join(basePath, "user/delete"),
            function_name="lc-internal-deleteUser",
            **commonFunctionArgs,
        )
        dbs.user.grant_read_data(readUserLmbd)
        dbs.user.grant_write_data(createUserLmbd)
        dbs.user.grant_write_data(deleteUserLmbd)
        dbs.user.grant_write_data(updateUserLmbd)
        api = aws_apigateway.RestApi(
            self,
            "internal-api",
            rest_api_name="Lovely Critters Internal API",
            description="This API is an internal catalog of services meant to be use across the LC ecosystem",
            default_method_options={
                "api_key_required": True,
            },
        )
        userApi = api.root.add_resource("user")
        userApiEmailPathed = userApi.add_resource("{email}")
        userApiEmailPathed.add_method(
            "GET",
            aws_apigateway.LambdaIntegration(
                readUserLmbd,
                request_templates={"application/json": '{"statusCode": "200"}'},
            ),
        )
        userApi.add_method(
            "POST",
            aws_apigateway.LambdaIntegration(
                createUserLmbd,
                request_templates={"application/json": '{"statusCode": "201"}'},
            ),
        )
        userApiEmailPathed.add_method(
            "DELETE",
            aws_apigateway.LambdaIntegration(
                deleteUserLmbd,
                request_templates={"application/json": '{"statusCode": "204"}'},
            ),
        )
        userApiEmailPathed.add_method(
            "PUT",
            aws_apigateway.LambdaIntegration(
                updateUserLmbd,
                request_templates={"application/json": '{"statusCode": "200"}'},
            ),
        )
        throttleSettings = aws_apigateway.ThrottleSettings(
            rate_limit=10, burst_limit=10
        )
        usagePlan: aws_apigateway.UsagePlan = api.add_usage_plan(
            "internalApiUsagePlan",
            name="Main Usage Plan",
            throttle=throttleSettings,
            api_stages=[
                aws_apigateway.UsagePlanPerApiStage(
                    stage=api.deployment_stage,
                )
            ],
        )
        apiKey = api.add_api_key(id="internalApiKey", api_key_name="Main API Key")
        usagePlan.add_api_key(apiKey)
        CfnOutput(self, "internalApi", value=api.url)
        CfnOutput(self, "internalAPIKey", value=apiKey.key_id)
