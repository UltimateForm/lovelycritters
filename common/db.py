import boto3
import os

def getTable(tableName:str):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(tableName)
    return (dynamodb, table)

def getUserTable():
	tableName = os.environ["USER_TABLE_NAME"]
	return getTable(tableName)

def getCritterTable():
	tableName = os.environ["CRITTER_TABLE_NAME"]
	return getTable(tableName)