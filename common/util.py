def generateUniqueId()->str:
	import uuid
	return str(uuid.uuid4())

def getEmailFromPathParams(event):
	pathParams = event["pathParameters"]
	email = pathParams["email"]
	return email