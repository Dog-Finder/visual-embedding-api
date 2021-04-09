import json
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import scan
from requests_aws4auth import AWS4Auth
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input, InceptionResNetV2
import numpy as np
import os
from collections import defaultdict

# import tensorflow as tf
# import tensorflow_hub as hub

from utils import url_to_array

IMAGE_WIDTH = 299
IMAGE_HEIGHT = 299

IMAGE_SHAPE = (IMAGE_WIDTH, IMAGE_HEIGHT)
# model = tf.keras.Sequential([hub.KerasLayer("model/", trainable=False)])
# model.build([None, IMAGE_WIDTH, IMAGE_HEIGHT, 3])

model = InceptionResNetV2(weights='imagenet', include_top=False, pooling='avg')


def make_connect():
    host = 'search-dog-finder-search-fcdwwfogeqqcr2dyrhjonwqmem.us-east-1.es.amazonaws.com'
    region = 'us-east-1'  # e.g. us-west-1
    service = 'es'

    sts_connection = boto3.client('sts')
    acct_b = sts_connection.assume_role(
        RoleArn="arn:aws:iam::111465656160:role/query-elasticsearch",
        RoleSessionName="cross_acct_lambda"
    )

    ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
    SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
    SESSION_TOKEN = acct_b['Credentials']['SessionToken']

    awsauth = AWS4Auth(ACCESS_KEY, SECRET_KEY,
                       region, service, session_token=SESSION_TOKEN)

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def hello(event, context):
    print(os.environ)
    return {'message': 'Hello World'}


def predict(event, context):
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
    body = json.loads(event['body'])
    url = body['url']
    array = url_to_array(url, IMAGE_SHAPE)
    array = preprocess_input(array[None])
    prediction = model(array)
    body = {'prediction': prediction.numpy().tolist()}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def predict_save(event, context):
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
    es = make_connect()
    body = json.loads(event['body'])
    imageLink = body['imageLink']
    userId = body['userId']
    entryId = body['entryId']
    index_type = 'found' if entryId.startswith('found') else 'lost'
    index_env = os.getenv('LAMBDA_ENV', 'local')
    index = f'{index_env}-{index_type}'
    array = url_to_array(imageLink, IMAGE_SHAPE)
    array = preprocess_input(array[None])
    prediction = model(array).numpy().tolist()[0]
    document = {
        "image-vector": prediction,
        "image-url": imageLink,
        "user-id": userId,
        "entry-id": entryId,
    }
    result = es.index(index=index, body=document)
    body = {'result': result}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def search(event, context):
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
    es = make_connect()
    body = json.loads(event['body'])
    url = body['url']
    index_type = body['index']
    index_env = os.getenv('LAMBDA_ENV', 'local')
    index = f'{index_env}-{index_type}'
    size = body['size']
    array = url_to_array(url, IMAGE_SHAPE)
    array = preprocess_input(array[None])
    prediction = model(array).numpy().tolist()[0]
    results = es.search(index=index, body={
        "size": size,
        "query": {
            "knn": {
                "image-vector": {
                    "vector": prediction,
                    "k": size
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
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
    array = np.random.random((1, IMAGE_HEIGHT, IMAGE_WIDTH, 3))
    prediction = model(array)
    body = {'prediction': prediction.numpy().tolist()}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def es_route(event, context):
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")
        return {}
    es = make_connect()
    index = 'vectors'
    body = {'index': es.indices.exists(index)}
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


def update_vectors(event, context):
    index_types = ['found', 'lost']
    index_env = os.getenv('LAMBDA_ENV', 'local')
    es = make_connect()
    counts = defaultdict(int)
    for index_type in index_types:

        index = f'{index_env}-{index_type}'
        results = scan(es, query={"query": {"match_all": {}}},
                       index=index, preserve_order=True)
        for item in results:
            _id = item['_id']
            url = item['_source']['image-url']
            array = url_to_array(url, IMAGE_SHAPE)
            array = preprocess_input(array[None])
            prediction = model(array).numpy().tolist()[0]
            document = {"doc": {
                "image-vector": prediction,
            }}
            result = es.update(index=index, id=_id, body=document)
            print(result)
            counts[index_type] += 1

    response = {
        "statusCode": 200,
        "body": json.dumps(counts)
    }
    return response
