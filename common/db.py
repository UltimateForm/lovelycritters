import boto3
import os

def getUserTable():
	tableName = os.environ["USER_TABLE_NAME"]
	dynamodb = boto3.resource("dynamodb")
	table = dynamodb.Table(tableName)