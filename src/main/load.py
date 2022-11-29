import os
from os.path import join
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow
from tensorflow import keras

MODELS_DIR = "model/"
def load_models():
  # load model
  model = keras.models.load_model(join(MODELS_DIR, "CNN-ResNet"))
  return model


  