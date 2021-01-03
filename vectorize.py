import requests
from PIL import Image
from io import BytesIO
import numpy as np
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input


def image_predict(model, url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize((299, 299))
    array = np.array(resized)[None]
    array = preprocess_input(array)
    prediction = model(array).numpy().tolist()[0]
    return prediction
