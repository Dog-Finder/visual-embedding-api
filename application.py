
from flask import Flask, request

import numpy as np
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2

from vectorize import image_predict
from es_utils import elasticsearch_connect, search_knn, get_lost_object
import uuid
application = Flask(__name__)


def load_model():
    global model
    model = InceptionResNetV2(
        weights='imagenet', include_top=False, pooling='avg')


@application.before_first_request
def set_up():
    global model
    load_model()


@application.route('/')
def hello_world():
    return "Dog Finder Model API"


@application.route('/predict', methods=['POST'])
def predict():
    global model
    url = request.json['url']
    prediction = image_predict(model, url)
    return {'prediction': prediction}


@application.route('/predict-save', methods=['POST'])
def predict_save():
    global model
    es = elasticsearch_connect()
    data = request.json
    imageLink = data['imageLink']
    userId = data['userId']
    entryId = data['entryId']
    prediction = image_predict(model, imageLink)

    document = {
        "image-vector": prediction,
        "image-url": imageLink,
        "user-id": userId,
        "entry-id": entryId,
    }
    index = 'found' if entryId.startswith('found') else 'lost'
    doc_id = f"{entryId}-{imageLink}"
    result = es.index(index=index, body=document, id=doc_id)
    return {'result': result, 'id': doc_id}


@application.route('/search', methods=['POST'])
def search():
    es = elasticsearch_connect()
    imageLink = request.json['imageLink']
    entryId = request.json['entryId']
    item = get_lost_object(es, imageLink, entryId)
    prediction = item['_source']['image-vector']
    results = search_knn(es, prediction)
    return {'result': results}


@application.route('/random', methods=['GET'])
def random():
    global model
    array = np.random.random((1, 299, 299, 3))
    prediction = model(array)
    return {'prediction': prediction.numpy().tolist()}


@application.route('/es', methods=['GET'])
def es_route():
    es = elasticsearch_connect()
    index = 'vectors'
    return {'index': es.indices.exists(index)}


if __name__ == '__main__':
    application.run()
