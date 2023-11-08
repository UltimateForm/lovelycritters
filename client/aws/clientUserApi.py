from aws_cdk import Stack, aws_lambda, CfnParameter, aws_apigateway, Duration
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from os import path


def createUserApi(
    stack: Stack,
    commonFunctionArgs: aws_lambda.Runtime,
    basePath: str,
    api: aws_apigateway.RestApi,
):
    registerUserLmbd = PythonFunction(
        stack,
        "registerUser",
        entry=path.join(basePath, "user/register"),
        function_name="lc-client-registerUser",
        **commonFunctionArgs,
    )
    loginUserLmbd = PythonFunction(
        stack,
        "loginUser",
        entry=path.join(basePath, "user/login"),
        function_name="lc-client-loginUser",
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
    userApi.add_resource("login").add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            loginUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
