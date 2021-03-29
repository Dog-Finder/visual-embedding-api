import json


def handler(event, context):
    body = {
        "message": "Hello, world! Your function executed successfully!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def handler2(event, context):
    body = {
        "message": "This is the second handler!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
