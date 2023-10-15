from aws_cdk import Stack, aws_lambda, CfnParameter, aws_apigateway
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion, PythonFunction
from .databases import Databases
from os import path


def createBillingApi(
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
        "environment": {"BILLING_TABLE_NAME": dbs.billing.table_name},
        "layers": [pythonLayer],
    }
    createBillingStatementLmbd = PythonFunction(
        stack,
        "createBillingStatement",
        entry=path.join(basePath, "billing/create"),
        function_name="lc-internal-createBillingStatement",
        **commonFunctionArgs,
    )
    readBillingStatementLmbd = PythonFunction(
        stack,
        "readBillingStatement",
        entry=path.join(basePath, "billing/read"),
        function_name="lc-internal-readBillingStatement",
        **commonFunctionArgs,
    )
    readBillingStatementByUserLmbd = PythonFunction(
        stack,
        "readBillingStatementByUser",
        entry=path.join(basePath, "billing/readByUser"),
        function_name="lc-internal-readBillingStatementByUser",
        **commonFunctionArgs,
    )
    deleteBillingStatementLmbd = PythonFunction(
        stack,
        "deleteBillingStatement",
        entry=path.join(basePath, "billing/delete"),
        function_name="lc-internal-deleteBillingStatement",
        **commonFunctionArgs,
    )
    dbs.billing.grant_read_data(readBillingStatementByUserLmbd)
    dbs.billing.grant_write_data(deleteBillingStatementLmbd)
    dbs.billing.grant_write_data(createBillingStatementLmbd)
    dbs.billing.grant_read_data(readBillingStatementLmbd)
    billingApi = api.root.add_resource("billing")
    billingApi.add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            createBillingStatementLmbd,
            request_templates={"application/json": '{"statusCode": "201"}'},
        ),
    )
    billingApiEmailPathed = billingApi.add_resource("{email}")
    billingApiFullPathed = billingApiEmailPathed.add_resource("{billingId}")
    billingApiEmailPathed.add_method(
        "GET",
        aws_apigateway.LambdaIntegration(
            readBillingStatementByUserLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    billingApiFullPathed.add_method(
        "GET",
        aws_apigateway.LambdaIntegration(
            readBillingStatementLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    billingApiFullPathed.add_method(
        "DELETE",
        aws_apigateway.LambdaIntegration(
            deleteBillingStatementLmbd,
            request_templates={"application/json": '{"statusCode": "204"}'},
        ),
    )
