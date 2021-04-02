import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
import numpy as np
import requests
from PIL import Image
from io import BytesIO

model = InceptionResNetV2(weights='imagenet', include_top=False, pooling='avg')


def make_connect():
    host = 'search-dog-finder-search-fcdwwfogeqqcr2dyrhjonwqmem.us-east-1.es.amazonaws.com'
    region = 'us-east-1'  # e.g. us-west-1

    service = 'es'
    credentials = boto3.Session(profile_name='elasticsearch').get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                       region, service, session_token=credentials.token)

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def hello(event, context):
    body = {'message': 'Hello World'}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def predict(event, context):
    body = json.loads(event['body'])
    url = body['url']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299, 299))
    array = np.array(resized)[None]
    array = preprocess_input(array)
    prediction = model(array)
    body = {'prediction': prediction.numpy().tolist()}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def predict_save(event, context):
    es = make_connect()
    body = json.loads(event['body'])
    imageLink = body['imageLink']
    userId = body['userId']
    entryId = body['entryId']
    response = requests.get(imageLink)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299, 299))
    array = np.array(resized)[None]
    array = preprocess_input(array)
    prediction = model(array).numpy().tolist()[0]
    document = {
        "image-vector": prediction,
        "image-url": imageLink,
        "user-id": userId,
        "entry-id": entryId,
    }
    result = es.index(index='vectors', body=document)
    body = {'result': result}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def search(event, context):
    es = make_connect()
    body = json.loads(event['body'])
    url = body['url']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299, 299))
    array = np.array(resized)[None]
    array = preprocess_input(array)
    prediction = model(array).numpy().tolist()[0]
    results = es.search(index='vectors', body={
        "size": 5,
        "query": {
            "knn": {
                "image-vector": {
                    "vector": prediction,
                    "k": 5
                }
            }
        },
        "_source": ["image-url", "user-id", "entry-id"],
    })
    body = {'result': results}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def random(event, context):
    array = np.random.random((1, 299, 299, 3))
    prediction = model(array)
    body = {'prediction': prediction.numpy().tolist()}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def es_route(event, context):
    es = make_connect()
    index = 'vectors'
    body = {'index': es.indices.exists(index)}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response
