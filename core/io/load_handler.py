import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
from cv2 import imread


import conf.conf as conf
from core.io.path_handler import PathHandler

class LoadHandler():
    @staticmethod
    def load_model():
        # load model
        path = PathHandler.make_path("MODEL", conf.MODEL_NAME, "LOAD")
        model = keras.models.load_model(path)
        return model

    @staticmethod
    def load_image(filename):
        path = PathHandler.make_path("IMAGE", filename, "LOAD")
        return imread(path)
