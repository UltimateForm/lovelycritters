from aws_cdk import Stack, aws_lambda, CfnParameter, aws_apigateway
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from .databases import Databases
from os import path


def createCritterApi(
    stack: Stack,
    runtime: aws_lambda.Runtime,
    pythonLayer: PythonLayerVersion,
    dbs: Databases,
    basePath: str,
    api: aws_apigateway.RestApi,
):
    commonFunctionArgs = {
        "runtime": runtime,
        "index": "main.py",
        "handler": "handler",
        "environment": {"CRITTER_TABLE_NAME": dbs.critter.table_name},
        "layers": [pythonLayer],
    }
    createCritterLmbd = PythonFunction(
        stack,
        "createCritter",
        entry=path.join(basePath, "critter/create"),
        function_name="lc-internal-createCritter",
        **commonFunctionArgs,
    )
    readCritterLmbd = PythonFunction(
        stack,
        "readCritter",
        entry=path.join(basePath, "critter/read"),
        function_name="lc-internal-readCritter",
        **commonFunctionArgs,
    )
    readCritterByEmailLmbd = PythonFunction(
        stack,
        "readByOwner",
        entry=path.join(basePath, "critter/readByOwner"),
        function_name="lc-internal-readByOwner",
        **commonFunctionArgs,
    )
    updateCritterLmbd = PythonFunction(
        stack,
        "updateCritter",
        entry=path.join(basePath, "critter/update"),
        function_name="lc-internal-updateCritter",
        **commonFunctionArgs,
    )
    deleteCritterLmbd = PythonFunction(
        stack,
        "deleteCritter",
        entry=path.join(basePath, "critter/delete"),
        function_name="lc-internal-deleteCritter",
        **commonFunctionArgs,
    )
    dbs.critter.grant_read_data(readCritterLmbd)
    dbs.critter.grant_read_data(readCritterByEmailLmbd)
    dbs.critter.grant_write_data(createCritterLmbd)
    dbs.critter.grant_write_data(deleteCritterLmbd)
    dbs.critter.grant_write_data(updateCritterLmbd)
    critterApi = api.root.add_resource("critter")
    critterApiEmailPathed = critterApi.add_resource("{ownerEmail}")
    critterApiFullPathed = critterApiEmailPathed.add_resource("{petName}")
    critterApiEmailPathed.add_method(
        "GET",
        aws_apigateway.LambdaIntegration(
            readCritterByEmailLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    critterApiFullPathed.add_method(
        "GET",
        aws_apigateway.LambdaIntegration(
            readCritterLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    critterApi.add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            createCritterLmbd,
            request_templates={"application/json": '{"statusCode": "201"}'},
        ),
    )
    critterApiFullPathed.add_method(
        "DELETE",
        aws_apigateway.LambdaIntegration(
            deleteCritterLmbd,
            request_templates={"application/json": '{"statusCode": "204"}'},
        ),
    )
    critterApiFullPathed.add_method(
        "PUT",
        aws_apigateway.LambdaIntegration(
            updateCritterLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
