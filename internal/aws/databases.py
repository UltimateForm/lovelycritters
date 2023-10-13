from attr import dataclass
from aws_cdk import Stack, aws_dynamodb as dynamodb, RemovalPolicy


@dataclass
class Databases:
    billing: dynamodb.Table
    user: dynamodb.Table
    critter: dynamodb.Table


def createDatabases(stack: Stack) -> Databases:
    billing = dynamodb.TableV2(
        stack,
        "billingTable",
        partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        removal_policy=RemovalPolicy.DESTROY,
        table_name="billingTable",
    )
    user = dynamodb.TableV2(
        stack,
        "userTable",
        partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
        removal_policy=RemovalPolicy.DESTROY,
        table_name="userTable",
    )
    critter = dynamodb.TableV2(
        stack,
        "critterTable",
        partition_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
        sort_key=dynamodb.Attribute(name="ownerEmail", type=dynamodb.AttributeType.STRING),
        removal_policy=RemovalPolicy.DESTROY,
        table_name="critterTable",
    )
    databases = Databases(billing=billing, user=user, critter=critter)
    return databases
