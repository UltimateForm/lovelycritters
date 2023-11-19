from typing import List, Any
from models import asdict

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

def joinUrl(*args:str):
    partsNormal = [url.rstrip("/").lstrip("/") for url in args]
    joinedUrl = "/".join(partsNormal)
    return joinedUrl

def getInternalApi():
    import os
    internalApiUrl = os.environ.get("INTERNAL_API_URL")
    internalApiKey = os.environ.get("INTERNAL_API_KEY")
    return (internalApiUrl, internalApiKey)

def modelToDict(model:Any):
    # note: mode.__dict__ is reportedly faster than asdict by a lot, should only use this for recursive conversions
    return asdict(model)