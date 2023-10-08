from typing import (Callable, Any)
import json

def generateUniqueId()->str:
	import uuid
	return str(uuid.uuid4())

def handlerDecorator(handler:Callable[[Any, Any], dict]) -> Callable[[Any, Any], dict]:
	def handlerDecorated(event, context):
		print(f"INCOMING REQUEST\n\tResource:{event.get('resource')},\n\tMethod:{event.get('httpMethod')}\n\tPathParameters:{event.get('pathParameters')}")
		response = {}
		try:	
			response = handler(event, context)
		except Exception as e:
			print(f"Error occured while processing request: {str(e)}")
			response = {
				"statusCode": 500,
				"body": json.dumps({
					"errorMessage": str(e)
				})
			}
		print(f"OUTGOING RESPONSE:\n\tStatusCode:{response.get('statusCode')},\n\tBody:{response.get('body')}")
		return response
	return handlerDecorated