import requests
from PIL import Image
from io import BytesIO
import numpy as np


def url_to_array(url, image_shape):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    resized = img.resize(image_shape)
    return np.array(resized)
