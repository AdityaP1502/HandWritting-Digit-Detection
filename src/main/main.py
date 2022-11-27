import os.path
import os
assert os.path.abspath(".").split("/")[-1] != "main", "run main.py from root folder"

import getopt
from sys import argv
from multiprocessing import Pool, cpu_count
from time import time

from helper import *
from image import *
from load import load_models
from loadingAnimation import Loading, Color
from c_interface import serializeArray_c, toMatrix, bbox_pipeline, thresh_pipeline


IMG_DIRPATH = IMG_DIRPATH_DEFAULT
FILENAME = ""
BATCH_MODE = False

def showHelp():
  print("""Accepted Arguments:
          -h : show help screen
          -f : filename. (Use this if -b is not specified)
          -d : enable debug mode. will save detected shape.
          -b :  enable batch mode. Will load picture from path given in --img-path
          --img-path=<image_path> : Frame input path. Use absolute path. Use this if image not in default location.
          """)

def showInfo():
    print(Color.print_colored("IMG_NAME:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(FILENAME), color_fg=[10, 20,255]))
    print(Color.print_colored("INPUT_PATH:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(IMG_DIRPATH), color_fg=[10, 20,255]))
    
    if DEBUG_MODE:
        print(Color.print_colored("USING DEBUG MODE", utils=["bold"]))
        
    if BATCH_MODE:
        print(Color.print_colored("USING BATCH MODE", utils=["bold"]))

def pipeline(data):
    img, partition, j, idx = data
    shape = getShape(img, partition, j)
    out_path = DEBUG_OUT_PATH_SHAPE.format(FILENAME) 
    
    if len(shape) == 0:
      return []
    
    if DEBUG_MODE:
      save_image(shape, out_path, "shape{}.png".format(idx))
    
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
    
    if DEBUG_MODE:
        import pandas as pd
        for img in numbers:
            df = pd.DataFrame(img)
            print(df.to_string())
        
    # do prediction
    total_shapes = len(numbers)
    
    model = load_models()
    prediction_ = model.predict(numbers.reshape(total_shapes, 28, 28, 1))
    prediction = list(map(lambda x: np.argmax(x), prediction_))
    
    for i in range(len(prediction)):
        result.append(prediction[i])
        

def routine(img_path):
    # load image
    img2 = Images(img_path)
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
    print()
    
    return result

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
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0' 
            
        if (opt == "--img-path"):
            IMG_DIRPATH = arg
            
        if (opt == "-b"):
            BATCH_MODE = True

    showInfo()
    start_time = time()
    
    if not BATCH_MODE:
        assert FILENAME != "", "FILENAME must be specified. Run this with -f options"
        img_path = os.path.join(IMG_DIRPATH, FILENAME)
        assert os.path.isfile(img_path), "File not found in path specified: {}".format(img_path)
        result = routine(img_path)
        print("Here is the result:")
        for i in range(len(result)):
            print(result[i], end = " ")
        print()
            
    else:
        assert os.path.isdir(IMG_DIRPATH), "Directory does not exist"
        dir_list = os.listdir(IMG_DIRPATH)
        extension = map(lambda x: x.split(".")[0], dir_list)
        img_list  = [file for (i, file) in enumerate(dir_list) if extension[i] == 'jpg' or extension[i] == 'png']
        with Pool(cpu_count()) as pool:
            results = pool.map(routine, img_list)
        
        print("The results is:")
        for i, img_name in enumerate(img_list):
            prompt = Color.print_colored("{}: ".format(img_name), color_fg=[0, 255, 255], utils=["bold"])
            print(prompt, end = "")
            for pred in results[i]:
                print(pred, end=" ")
            print()
        
        
    end_time = time()
    elapsed_time = (end_time - start_time)
    elapsed_time_h = elapsed_time // 3600
    elapsed_time_m = (elapsed_time % 3600) // 60
    elapsed_time_s = (elapsed_time % 3600) % 60
    
    prompt = Color.print_colored("Took about {:.2f} hours {:.2f} minutes {:.2f} seconds".format(elapsed_time_h, elapsed_time_m, elapsed_time_s), color_fg=[0, 255, 255], utils=["bold"])
    print(prompt)
