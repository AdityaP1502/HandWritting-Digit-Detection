MODELS_DIR = "model/"
from os.path import join
import joblib

def load_models(model_name):
  # load model
  model_path = join(MODELS_DIR, model_name + ".sav")
  model = joblib.load(model_path)
  return model


  