from aws_cdk import Duration, Stack, aws_lambda, CfnParameter, aws_apigateway
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from .databases import Databases
from os import path


def createUserApi(
    stack: Stack,
    runtime: aws_lambda.Runtime,
    pythonLayer: PythonLayerVersion,
    dbs: Databases,
    basePath: str,
    jwtSecretParam: CfnParameter,
    api: aws_apigateway.RestApi,
):
    commonFunctionArgs = {
        "runtime": runtime,
        "index": "main.py",
        "handler": "handler",
        "environment": {"USER_TABLE_NAME": dbs.user.table_name},
        "layers": [pythonLayer],
        "timeout": Duration.seconds(30),
    }
    createUserLmbd = PythonFunction(
        stack,
        "createUser",
        entry=path.join(basePath, "user/create"),
        function_name="lc-internal-createUser",
        **commonFunctionArgs,
    )
    readUserLmbd = PythonFunction(
        stack,
        "readUser",
        entry=path.join(basePath, "user/read"),
        function_name="lc-internal-readUser",
        **commonFunctionArgs,
    )
    updateUserLmbd = PythonFunction(
        stack,
        "updateUser",
        entry=path.join(basePath, "user/update"),
        function_name="lc-internal-updateUser",
        **commonFunctionArgs,
    )
    deleteUserLmbd = PythonFunction(
        stack,
        "deleteUser",
        entry=path.join(basePath, "user/delete"),
        function_name="lc-internal-deleteUser",
        **commonFunctionArgs,
    )
    authFunctionArgs = {
        **commonFunctionArgs,
        "environment": {
            **commonFunctionArgs.get("environment"),
            "JWT_SECRET": jwtSecretParam.value_as_string,
        },
    }
    authUserLmbd = PythonFunction(
        stack,
        "authUser",
        entry=path.join(basePath, "user/auth"),
        function_name="lc-internal-authUser",
        **authFunctionArgs,
    )
    dbs.user.grant_read_data(readUserLmbd)
    dbs.user.grant_write_data(createUserLmbd)
    dbs.user.grant_write_data(deleteUserLmbd)
    dbs.user.grant_write_data(updateUserLmbd)
    dbs.user.grant_read_data(authUserLmbd)
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
    userApi.add_resource("auth").add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            authUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
