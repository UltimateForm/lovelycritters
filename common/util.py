from typing import List


def generateUniqueId()->str:
	import uuid
	return str(uuid.uuid4())

def getElementFromParams(element:str, event) -> str:
	pathParams = event["pathParameters"]
	email = pathParams[element]
	return email

def getEmailFromPathParams(event):
	return getElementFromParams("email", event)

def dictWithoutKey(d:dict, *args:str) -> dict:
    newDict = d.copy()
    [newDict.pop(key) for key in args]
    return newDict