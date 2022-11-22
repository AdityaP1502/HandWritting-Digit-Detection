import os.path
assert os.path.abspath(".").split("/")[-1] != "main", "run main.py from root folder"

import getopt
from sys import argv
from multiprocessing import Pool, cpu_count
from time import time

from helper import *
from image import *
from c_interface import serializeArray_c, toMatrix, bbox_pipeline, thresh_pipeline
from loadingAnimation import *
from load import load_models


IMG_DIRPATH = IMG_DIRPATH_DEFAULT
FILENAME = ""

def showHelp():
  print("""Accepted Arguments:
          -h : show help screen
          -f : filename.
          -d : enable debug mode. Will save detected shape. 
          --img-path=<image_path> : Frame input path. Use absolute path. Use this if image not in default location.
          """)

def showInfo():
    print(Color.print_colored("IMG_NAME:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(FILENAME), color_fg=[10, 20,255]))
    print(Color.print_colored("INPUT_PATH:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(IMG_DIRPATH), color_fg=[10, 20,255]))
    
    if DEBUG_MODE:
        print(Color.print_colored("USING DEBUG MODE", utils=["bold"]))

def pipeline(data):
    img, partition, j, idx = data
    shape = getShape(img, partition, j)
    out_path = DEBUG_OUT_PATH_SHAPE.format(FILENAME) 
    
    if len(shape) == 0:
      return []
  
    if DEBUG_MODE:
      save_image(shape, out_path, "shape{}.png".format(idx))
      
    shape = serializeArray_c(shape, 28, 28)
    # shape_erode = cv2.erode(shape, np.ones((3, 3), np.uint8))
    # shape_erode = serializeArray_c(shape_erode, 28, 28)
    # # add lopp count features
    # cnt = loop_count_c(shape_erode, 28, 28)
    return shape

def process(result, mat, s):
    # Detection Process
    data = []
    idx = 0
    for i in range(len(s)):
        partition = s[i]
        for j in range(len(partition)):
            data.append([mat, partition, j, idx])
            idx += 1

    # Process frames to images in parallel
    chunksize = len(data) // cpu_count()
    with Pool(cpu_count()) as pool:
        numbers = pool.map(pipeline, data, chunksize=chunksize)
        
    # filter images that has dimension lower than minimum dimension
    numbers = [num for num in numbers if len(num) > 0]
    numbers = np.array(numbers)
    # do prediction
    model = load_models("KNeighbors")
    prediction = model.predict(numbers).reshape(-1)
    for i in range(len(prediction)):
        result.append(prediction[i])
        

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(argv[1:], shortopts="hdf:", longopts=["img-path="])
    except getopt.GetoptError as err:
        print(err)
        print("Error : Invalid Argument")
        showHelp()
        exit(1)

    for opt, arg in opts:
        if (opt == "-h"):
            showHelp()
            exit(0)

        if (opt == "-f"):
            FILENAME = arg
        
        if (opt == "-d"):
            DEBUG_MODE = True
            
        if (opt == "--img-path"):
            IMG_DIRPATH = arg

    showInfo()
    assert FILENAME != "", "FILENAME must be specified. Run this with -f options"

    IMG_FILEPATH = os.path.join(IMG_DIRPATH, FILENAME)
    assert os.path.isfile(IMG_FILEPATH), "File not found in path specified: {}".format(IMG_FILEPATH)
    start_time = time()
    # load image
    img2 = Images(IMG_FILEPATH)
    img2.toGrayscale()

    # removce shadow
    shr2 = ShadowRemoval(img2)
    shr2.remove()
    shr2.update()

    # serialize array
    ny, nx = np.shape(img2.pixels)
    pixels = serializeArray_c(img2.pixels, nx, ny)
    
    # Find thresh and thresh images
    X = fromPixelsToHistogram(pixels)
    peak = findPeak(X)
    thresh = fromPeakToThreshold(X, peak)
    pixels = thresh_pipeline(pixels, nx, ny, thresh)

    # Image Detection
    # FInd frames
    objs_c = bbox_pipeline(pixels, nx, ny)
    # Sort fraems
    s = sortObjs(objs_c)

    # Change serialize pixels to matrix
    mat = toMatrix(pixels, nx, ny)
    # do detection
    result = []
    Loading.loading(process_fnc=process, args=(result, mat, s, ))
    end_time = time()
    elapsed_time = (end_time - start_time)
    elapsed_time_h = elapsed_time // 3600
    elapsed_time_m = (elapsed_time % 3600) // 60
    elapsed_time_s = (elapsed_time % 3600) % 60
    print()
    prompt = Color.print_colored("Took about {:.2f} hours {:.2f} minutes {:.2f} seconds".format(elapsed_time_h, elapsed_time_m, elapsed_time_s), color_fg=[0, 255, 255], utils=["bold"])
    print(prompt)
    print("Here is the result:")
    for i in range(len(result)):
        print(result[i], end = " ")
    print()