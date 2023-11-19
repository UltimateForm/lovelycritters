from aws_cdk import Stack, aws_lambda, aws_apigateway
from aws_cdk.aws_apigateway import IAuthorizer, MethodOptions
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from os import path


def createTenancyApi(
    stack: Stack,
    commonFunctionArgs: aws_lambda.Runtime,
    basePath: str,
    api: aws_apigateway.RestApi,
    authorizer: IAuthorizer,
):
    registerTenancyLmbd = PythonFunction(
        stack,
        "registerTenancy",
        entry=path.join(basePath, "tenancy/register"),
        function_name="lc-client-registerTenancy",
        **commonFunctionArgs,
    )
    cancelTenancyLmbd = PythonFunction(
        stack,
        "cancelTenancy",
        entry=path.join(basePath, "tenancy/cancel"),
        function_name="lc-client-cancelTenancy",
        **commonFunctionArgs,
    )
    tenancyApi = api.root.add_resource("tenancy")
    tenancyApiEmailPathed = tenancyApi.add_resource(
        "{email}", default_method_options=MethodOptions(authorizer=authorizer)
    )
    tenancyApiEmailPathed.add_method(
        "POST",
        aws_apigateway.LambdaIntegration(
            registerTenancyLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )
    tenancyApiPetPathed = tenancyApiEmailPathed.add_resource("{petName}")
    tenancyApiTenancyIdPathed = tenancyApiPetPathed.add_resource("{tenancyId}")
    tenancyApiTenancyIdPathed.add_method(
        "DELETE",
        aws_apigateway.LambdaIntegration(
            cancelTenancyLmbd,
            request_templates={"application/json": '{"statusCode": "200"}'},
        ),
    )