from aws_cdk import Stack, aws_lambda, CfnParameter, aws_apigateway, Duration
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from os import path


def createUserApi(
    stack: Stack,
    runtime: aws_lambda.Runtime,
    pythonLayer: PythonLayerVersion,
    basePath: str,
    api: aws_apigateway.RestApi,
    internalApiUrl: str,
):
    commonFunctionArgs = {
        "runtime": runtime,
        "index": "main.py",
        "handler": "handler",
        "environment": {"INTERNAL_API_URL": internalApiUrl, "INTERNAL_API_KEY": ""},
        "timeout": Duration.seconds(30),
        "layers": [pythonLayer],
    }
    registerUserLmbd = PythonFunction(
        stack,
        "registerUser",
        entry=path.join(basePath, "user/register"),
        function_name="lc-client-registerUser",
        **commonFunctionArgs,
    )
    userApi = api.root.add_resource("user")
    userApi.add_resource("register").add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            registerUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
