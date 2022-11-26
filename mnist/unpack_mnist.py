import os
import os.path
import sys
from os.path import abspath, join
assert os.path.abspath(".").split("/")[-1] != "main", "run main.py from root folder"

import cv2
import numpy as np
from PIL import Image
sys.path.append(".")
from src.main.loop_enhancer import LoopEnhancer
from src.main.image import clean_image
from time import time
from multiprocessing import Pool, cpu_count, Value
from threading import Thread
from time import sleep, time
  
"""
This is module to unpack mnist dataset and do initial preprocess to get the loop labels 
"""
# PATH VARIABLES
# RELATIVE PATH

# MNIST DATASET FILE PATH
MNIST_DIR = "./mnist"
MNIST_TRAIN_DATASET_IMAGES = "train-images-idx3-ubyte"
MNIST_TRAIN_DATASET_LABELS = "train-labels-idx1-ubyte"
MNIST_TEST_DATASET_IMAGES = "test-images-idx3-ubyte"
MNIST_TEST_DATASET_LABELS = "t10k-labels-idx1-ubyte"

# MNIST FILE COUNT
MNIST_N_TRAIN = 60000
MNIST_N_TEST = 10000
MNIST_DATA_LENGTH = 28 * 28

# OUTPUT PATH DIR
TRAIN_IMAGES_DIR = "./mnist/images/train_images" 
TEST_IMAGES_DIR = "./mnist/images/test_images"
TRAIN_LABELS_DIR = "./mnist/labels/train_labels"
TEST_LABELS_DIR =  "./mnist/labels/test_labels"

# OUTPUT PATH NAME
IMAGE_NAME = "number{}.png"
LABELS_NAME = "labels.txt"
LOOP_LABELS_NAME = "loops.txt"

# FLAG TO USE C LOOP COUNTER, MUST BE ON LINUX
USE_C = True

def save(data):
  global n_finished
  pix_arr = [0 for i in range(MNIST_DATA_LENGTH)]
  i, start, content, img_dir = data
  
  for j in range(MNIST_DATA_LENGTH):
    pix_arr[j] = content[start + j]
      
  
  pix_arr = np.array(pix_arr, dtype="ubyte")
  pix_arr = pix_arr.reshape(28, 28)
  # enhance loop 
  enhance(pix_arr)
  
  img_path = join(img_dir, IMAGE_NAME.format(i + 1))
  img = Image.fromarray(pix_arr, mode="L")
  img.save(img_path, mode="L")
  
  with n_finished.get_lock():
    n_finished.value += 1

def process(data):
  with Pool(cpu_count()) as pool:
    _ = pool.map(save, data)

def write(data, dir, filename):
  with open(os.path.join(dir, filename), "w") as f:
    f.write(data)
    
def readBinaryContent(path, filename):
  with open(os.path.join(path, filename), "rb") as f:
    content = f.read()
    
  return content 

def enhance(img):
  # global n_finished
  # idx, img_dir = data
  # img_dir = join(img_dir, IMAGE_NAME.format(idx))
  # images = cv2.imread(img_dir, 0)
  
  assert isinstance(img, np.ndarray), "image must be a ndarray, get {}".format(type(img).__name__)
  assert len(np.shape(img)) == 2, "Image must be a matrix and has one channel"
  
  # first clean the image
  clean_image(img)
  
  if not USE_C:
    enhancer = LoopEnhancer(img)
    enhancer.enhance()

  else:
    loop_enhance_c(img.reshape(1, -1)[0], 28, 28)
  
  # with n_finished.get_lock():
  #   n_finished.value += 1
  
  # if cnt > 2:
  #   cnt = fallback(images)
  #   if cnt > 2:
  #     return (cnt, idx)
  

def processLoop(X, data):  
  with Pool(cpu_count()) as pool:
      X_ = pool.map(enhance, data)
  
  X.append([X_[i][0] for i in range(len(data))])
  X.append([X_[i][1] for i in range(len(data))])
  
  return X




def routine(routine_name):
  print("Processing {}".format(routine_name))
  
if __name__ == "__main__":
  if len(sys.argv) > 1:
    if int(sys.argv[1]) == 0:
      USE_C = False

  if USE_C:
    print("[INFO] Using C library...\nLoading library...")
    try:
      from src.main.c_interface import loop_enhance_c
    except Exception as e:
      print("[ERROR] Cannot load c shared library with error:")
      print("[ERROR] " + e)
      print("[ERROR] Make sure you are on linux to use c library")
    print("[DONE] Done")
  
  else:
    print("[INFO] Using python to count loops. May require extra time to complete.")

  # check if path dir exist
  if not os.path.isdir(TRAIN_IMAGES_DIR):
    os.makedirs(TRAIN_IMAGES_DIR)
  
  if not os.path.isdir(TEST_IMAGES_DIR):
    os.makedirs(TEST_IMAGES_DIR)
    
  if not os.path.isdir(TRAIN_LABELS_DIR):
    os.makedirs(TRAIN_LABELS_DIR)
  
  if not os.path.isdir(TEST_LABELS_DIR):
    os.makedirs(TEST_LABELS_DIR)
  
  start_time = time()
  print("[INFO] PROCESSING TRAIN DATASET...\nPlease Wait!")
  # read mnist image data
  train_dataset_images_content = readBinaryContent(MNIST_DIR, MNIST_TRAIN_DATASET_IMAGES)
  offset = 16
  data = [(i, offset + MNIST_DATA_LENGTH * i, train_dataset_images_content, TRAIN_IMAGES_DIR) for i in range(MNIST_N_TRAIN)]
  
  n_finished = Value("i", 0)
  t = Thread(target=process, args=(data, ), daemon=True)
  t.start()
  while t.is_alive():
    chars = "/—\|" 
    for char in chars:
        sys.stdout.write('\r'+ 'loading...' + char + " Processed: {}/{} Files".format(n_finished.value, MNIST_N_TRAIN))
        sleep(.1)
        sys.stdout.flush()
  sys.stdout.write("\rDone!                                     ")
  print()
  print("[INFO] Finished saving train iamges file in {}".format(TRAIN_IMAGES_DIR))
        
  # read mnist train labels
  train_dataset_labels_content = readBinaryContent(MNIST_DIR, MNIST_TRAIN_DATASET_LABELS)
  arr_of_labels_train = [0 for i in range(MNIST_N_TRAIN)]
  offset = 8
  
  for i in range(MNIST_N_TRAIN):
    arr_of_labels_train[i] = str(train_dataset_labels_content[offset + i])
  
  data = ",".join(arr_of_labels_train)
  write(data, TRAIN_LABELS_DIR, LABELS_NAME)
  print("[INFO] Finished saving train labels file in {}".format(TRAIN_LABELS_DIR))
  
  # # get loop labels
  # images_id = [(i + 1, TRAIN_IMAGES_DIR) for i in range(MNIST_N_TRAIN)]
  # return_values = []
  # n_finished = Value("i", 0)
  # t = Thread(target=processLoop, args=(return_values, images_id, ), daemon=True)
  # t.start()
  # while t.is_alive():
  #   chars = "/—\|" 
  #   for char in chars:
  #       sys.stdout.write('\r'+ 'loading...' + char + " Processed: {}/{} Files".format(n_finished.value, MNIST_N_TRAIN))
  #       sleep(.1)
  #       sleep(.1)
  #       sys.stdout.flush()
        

  # loop_labels = return_values[0]
  # err_idx = return_values[1]
  # sys.stdout.write("\rDone!                                     ")
  # print()
  # print("IGNORE ERROR BELOW IF the COUNT IS equal to 3. It's just a baddly written 8")
  
  # for i in range(len(err_idx)):
  #   if err_idx[i] == None: continue
  #   print(f"[Error at: {err_idx[i]}] Received count {loop_labels[i]} which greater than 2")
  
  # data = ",".join(map(lambda x: str(x), loop_labels))
  # write(data, TRAIN_LABELS_DIR, LOOP_LABELS_NAME)
  # print("[INFO] Finished saving train labels-loop file in {}".format(TRAIN_LABELS_DIR))
  
  # read mnist test data
  print("[INFO] PROCESSING TEST DATASET...\nPlease Wait")
  TEST_dataset_images_content = readBinaryContent(MNIST_DIR, MNIST_TEST_DATASET_IMAGES)
  offset = 16
  data = [(i, offset + MNIST_DATA_LENGTH * i, TEST_dataset_images_content, TEST_IMAGES_DIR) for i in range(MNIST_N_TEST)]
  
  n_finished = Value("i", 0)
  t = Thread(target=process, args=(data, ), daemon=True)
  t.start()
  while t.is_alive():
    chars = "/—\|" 
    for char in chars:
        sys.stdout.write('\r'+ 'loading...' + char + " Processed: {}/{} Files".format(n_finished.value, MNIST_N_TEST))
        sleep(.1)
        sleep(.1)
        sys.stdout.flush()
  sys.stdout.write("\rDone!                                     ")
  print()
  print("[INFO] Finished saving test iamges file in {}".format(TEST_IMAGES_DIR))      
        
  # read mnist TEST labels
  TEST_dataset_labels_content = readBinaryContent(MNIST_DIR, MNIST_TEST_DATASET_LABELS)
  arr_of_labels_TEST = [0 for i in range(MNIST_N_TEST)]
  offset = 8
  
  for i in range(MNIST_N_TEST):
    arr_of_labels_TEST[i] = str(TEST_dataset_labels_content[offset + i])
  
  data = ",".join(arr_of_labels_TEST)
  write(data, TEST_LABELS_DIR, LABELS_NAME)
  print("[INFO] Finished saving test labels file in {}".format(TEST_LABELS_DIR))
  
  # # get loop labels
  # images_id = [(i + 1, TEST_IMAGES_DIR) for i in range(MNIST_N_TEST)]
  # return_values = []
  # n_finished = Value("i", 0)
  # t = Thread(target=processLoop, args=(return_values, images_id, ), daemon=True)
  # t.start()
  # while t.is_alive():
  #   chars = "/—\|" 
  #   for char in chars:
  #       sys.stdout.write('\r'+ 'loading...' + char + " Processed: {}/{} Files".format(n_finished.value, MNIST_N_TEST))
  #       sleep(.1)
  #       sys.stdout.flush()
  # sys.stdout.write("\rDone!                                     ")
  # loop_labels = return_values[0]
  # err_idx = return_values[1]
  # print()
  # print("IGNORE ERROR BELOW IF the COUNT IS equal to 3. It's just a baddly written 8")
  
  # for i in range(len(err_idx)):
  #   if err_idx[i] == None: continue
  #   print(f"[Error at: {err_idx[i]}] Received count {loop_labels[i]} which greater than 2")
  
  # data = ",".join(map(lambda x: str(x), loop_labels))
  # write(data, TEST_LABELS_DIR, LOOP_LABELS_NAME)
  # print("[INFO] Finished saving test labels-loop file in {}".format(TEST_LABELS_DIR))   
  end_time = time()
  
  dt = end_time - start_time
  time_h = dt // 3600
  time_m = dt % 3600 // 60
  time_s = dt % 3600 % 60
  print("[DONE] Done.")
  print("Finished in: {:02.2f}h {:02.2f}m {:02.2f}s".format(time_h, time_m, time_s))
  
  
    
    
  
  