import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from flask import Flask, request
from tensorflow import keras
import numpy as np
import requests
from PIL import Image
from io import BytesIO
application = Flask(__name__)


@application.before_first_request
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

@application.route('/')
def hello_world():
  return "Hello World"


@application.route('/predict', methods=['POST'])
def predict():
  url = request.json['url']
  response = requests.get(url)
  model = keras.models.load_model('vgg16')
  response = requests.get(url)
  img = Image.open(BytesIO(response.content))
  resized = img.resize((299,299))
  array = np.array(resized)[None]
  prediction = model(array)
  return {'prediction': prediction.numpy().tolist()}

@application.route('/random', methods=['GET'])
def random():
  model = keras.models.load_model('vgg16')
  array = np.random.random((1,64,64,3))
  prediction = model(array)
  return {'prediction': prediction.numpy().tolist()}

@application.route('/es', methods=['GET'])
def es_route():
  global es
  index ='vectors'
  return {'index': es.indices.exists(index)}

if __name__ == '__main__':
  application.run()