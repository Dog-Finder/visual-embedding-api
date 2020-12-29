import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from flask import Flask, request
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
import numpy as np
import requests as rqs
from PIL import Image
from io import BytesIO
application = Flask(__name__)



def make_connect():
    global es
    host = 'search-dog-finder-v2-7wjebliu7bqocjgom3d6csaxde.us-east-1.es.amazonaws.com'
    service = 'es'
    region = 'us-east-1'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

def load_model():
  global model
  model = InceptionResNetV2(weights='imagenet', include_top=False, pooling='avg')


@application.before_first_request
def set_up():
  global model
  make_connect()
  load_model()

@application.route('/')
def hello_world():
  return "Hello World"


@application.route('/predict', methods=['POST'])
def predict():
  global model
  url = request.json['url']
  response = rqs.get(url)
  img = Image.open(BytesIO(response.content))
  resized = img.resize((299,299))
  array = np.array(resized)[None]
  array = preprocess_input(array)
  prediction = model(array)
  return {'prediction': prediction.numpy().tolist()}

@application.route('/predict-save', methods=['POST'])
def predict_save():
  global model
  data = request.json
  imageLink = data['imageLink']
  userId = data['userId']
  entryId = data['entryId']
  response = rqs.get(imageLink)
  img = Image.open(BytesIO(response.content))
  resized = img.resize((299,299))
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
  return {'result': result}

@application.route('/search', methods=['POST'])
def search():
  global model
  url = request.json['url']
  response = rqs.get(url)
  img = Image.open(BytesIO(response.content))
  resized = img.resize((299,299))
  array = np.array(resized)[None]
  array = preprocess_input(array)
  prediction = model(array).numpy().tolist()[0]
  results = es.search(index='notices', body={
    "size": 5,
    "query": {
        "knn": {
            "image_vector": {
                "vector": prediction,
                "k": 5
            }
        }
    },
    "_source": ["image-url","notice-id"],
  })
  return {'result': results}

@application.route('/random', methods=['GET'])
def random():
  global model
  array = np.random.random((1,299,299,3))
  prediction = model(array)
  return {'prediction': prediction.numpy().tolist()}

@application.route('/es', methods=['GET'])
def es_route():
  global es
  index ='vectors'
  return {'index': es.indices.exists(index)}

if __name__ == '__main__':
  application.run()