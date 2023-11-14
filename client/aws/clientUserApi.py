from aws_cdk import Stack, aws_lambda, aws_apigateway
from aws_cdk.aws_apigateway import IAuthorizer, MethodOptions
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from os import path


def createUserApi(
    stack: Stack,
    commonFunctionArgs: aws_lambda.Runtime,
    basePath: str,
    api: aws_apigateway.RestApi,
    authorizer: IAuthorizer,
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
    updateUserLmbd = PythonFunction(
        stack,
        "updateUser",
        entry=path.join(basePath, "user/update"),
        function_name="lc-client-updateUser",
        **commonFunctionArgs,
    )
    deleteUserLmbd = PythonFunction(
        stack,
        "deleteUser",
        entry=path.join(basePath, "user/deleteAccount"),
        function_name="lc-client-deleteUser",
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
    userApiEmailPathed = userApi.add_resource(
        "{email}", default_method_options=MethodOptions(authorizer=authorizer)
    )
    userApiEmailPathed.add_method(
        "PUT",
        aws_apigateway.LambdaIntegration(
            updateUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    userApiEmailPathed.add_method(
        "DELETE",
        aws_apigateway.LambdaIntegration(
            deleteUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
