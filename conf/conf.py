from os.path import abspath, join

# mode
BATCH_MODE = False
DEBUG_MODE = False

# image path configuration
FILENAME = ""
IMG_DIRPATH_DEFAULT = abspath("img/")
IMG_DIRPATH = IMG_DIRPATH_DEFAULT

# Model path configuration
MODELS_DIR = "model/"
MODEL_NAME = "CNN-ResNet"

# Image Preprocessing configuration
BG_PIXELS_INTENSITY = 0
DATA_PIXELS_INTENSITY = 255
MINIMUM_OBJECT_DIMENSION = 10

# Debug Out configuration
DEBUG_OUT_PATH = ""
DEBUG_OUT_PATH_SHAPE = "./out/{}/detected_shape"

# Shared Library
SO_DIRPATH = "lib/shared"
SO_FILE_BBOX = join(SO_DIRPATH, 'libbbox.so')
SO_FILE_IMAGES = join(SO_DIRPATH, 'libimage.so')
SO_FILE_THRESH = join(SO_DIRPATH, 'libthresh.so')
SO_FILE_COUNTER = join(SO_DIRPATH, 'libenhancer.so')