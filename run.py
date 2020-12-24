from keras.applications.inception_resnet_v2 import InceptionResNetV2
import json
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import flask
import io
import tensorflow as tf
from tensorflow.python.keras.backend import set_session


model = None
sess = None
graph = None

def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model, graph, sess
    sess = tf.Session()
    graph = tf.get_default_graph()
    set_session(sess)
    model = InceptionResNetV2(include_top=False, pooling='avg')


load_model()
app = flask.Flask(__name__)




@app.route("/predict", methods=["POST"])
def predict():
    global graph, model, sess
    url = flask.request.json['url']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299,299))
    array = np.array(resized)[None]
    with graph.as_default():
        set_session(sess)
        prediction = model.predict(array)
    data = {'array': prediction.tolist()}
    return flask.jsonify(data)

@app.route("/predict/example", methods=["GET"])
def example_predict():
    global graph, model, sess
    url = 'https://s14-eu5.startpage.com/cgi-bin/serveimage?url=https%3A%2F%2Fencrypted-tbn0.gstatic.com%2Fimages%3Fq%3Dtbn%3AANd9GcSHzq32crTiETfj0IGPn2xLnKbpYPfxOmkisFMJhRy8aT3AZVRi-A%26s&sp=9408c2909fdbc8ebbe0dd38d0d4697fb&anticache=759980'
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299,299))
    array = np.array(resized)[None]
    with graph.as_default():
        set_session(sess)
        prediction = model.predict(array)
    data = {'array': prediction.tolist()}
    return flask.jsonify(data)

@app.route("/hello", methods=["GET"])
def hello():
    return 'app is running'

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
        "please wait until server has fully started"))
    
    app.run()