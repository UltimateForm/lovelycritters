import json

def handler(event, context):
	print("Running?? WOAH!!")
	return {
		"statusCode": 200,
		"body": json.dumps({
			"msg":"hello world  created helio test test"
		})
	}