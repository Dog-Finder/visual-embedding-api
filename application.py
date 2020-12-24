from boto.connection import AWSAuthConnection
from flask import Flask, request
from tensorflow import keras
import numpy as np
import requests
from PIL import Image
from io import BytesIO
application = Flask(__name__)

class ESConnection(AWSAuthConnection):
    def __init__(self, region, **kwargs):
        super(ESConnection, self).__init__(**kwargs)
        self._set_auth_region_name(region)
        self._set_auth_service_name("es")
    def _required_auth_capability(self):
        return ['hmac-v4']

@application.before_first_request
def make_connect():
    global client
        # Note, BOTO receives credentials from the EC2 instance's IAM Role
    client = ESConnection(
      region='us-east-1',
      # Be sure to enter the URL of YOUR Elasticsearch Service!!!
      host='search-dog-finder-v2-7wjebliu7bqocjgom3d6csaxde.us-east-1.es.amazonaws.com',
      is_secure=False)

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

if __name__ == '__main__':
  application.run()