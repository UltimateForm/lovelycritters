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
from aws_cdk.aws_lambda_python_alpha import (
    PythonFunction, PythonLayerVersion)
from os import path, getcwd
from constructs import Construct


@dataclass
class Databases:
    billing: dynamodb.Table
    user: dynamodb.Table
    critter: dynamodb.Table


def createDatabases(stack: Stack) -> Databases:
    billing = dynamodb.TableV2(stack, "billingTable",
                               partition_key=dynamodb.Attribute(
                                   name="id", type=dynamodb.AttributeType.STRING),
                               removal_policy=RemovalPolicy.DESTROY,
                               table_name="billingTable"
                               )
    user = dynamodb.TableV2(stack, "userTable",
                            partition_key=dynamodb.Attribute(
                                name="id", type=dynamodb.AttributeType.STRING),
                            removal_policy=RemovalPolicy.DESTROY,
                            table_name="userTable"
                            )
    critter = dynamodb.TableV2(stack, "critterTable",
                               partition_key=dynamodb.Attribute(
                                   name="id", type=dynamodb.AttributeType.STRING),
                               removal_policy=RemovalPolicy.DESTROY,
                               table_name="crittersTable"
                               )
    databases = Databases(billing=billing, user=user, critter=critter)
    return databases


class LC_InternalStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        cwd = getcwd()
        basePath = f"{cwd}/internal"
        dbs = createDatabases(self)
        runtime: aws_lambda.Runtime = aws_lambda.Runtime.PYTHON_3_11
        pythonLayer = PythonLayerVersion(
            self, "lc_common", entry=f"{cwd}/common", compatible_runtimes=[runtime])
        createUserLmbd = PythonFunction(self, "createUser",
                                        entry=path.join(
                                            basePath, "user/create"),
                                        runtime=runtime,
                                        index="main.py",
                                        handler="handler",
                                        environment={
                                            "USER_TABLE_NAME": dbs.user.table_name
                                        },
                                        layers=[pythonLayer])
        readUserLmbd = PythonFunction(self, "readUser",
                                        entry=path.join(
                                            basePath, "user/read"),
                                        runtime=runtime,
                                        index="main.py",
                                        handler="handler",
                                        environment={
                                            "USER_TABLE_NAME": dbs.user.table_name
                                        },
                                        layers=[pythonLayer])
        # createUserLmbd = aws_lambda.Function(self, "createUser",
        #                                      runtime=runtime,
        #                                      code=aws_lambda.Code.from_asset(
        #                                          path.join(
        #                                              basePath, "user/create"),
        #                                          bundling={
        #                                              "image": runtime.bundling_image,
        #                                              "local":
        #                                          }),
        #                                      handler="main.handler",
        #                                      function_name="lc-internal-createUser",
        #                                      environment={
        #                                          "TABLE_NAME": dbs.user.table_name
        #                                      },
        #                                      )7
        dbs.user.grant_read_write_data(readUserLmbd)
        dbs.user.grant_read_write_data(createUserLmbd)
