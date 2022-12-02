from image import *
from loadingAnimation import Loading, Color


from sys import argv
from time import time

import getopt
import os.path
import os

assert os.path.abspath(".").split(
    "/")[-1] != "main", "run main.py from root folder"


IMG_DIRPATH = IMG_DIRPATH_DEFAULT
DEBUG_OUT_PATH = ""
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
    if not BATCH_MODE:
        print(Color.print_colored("IMG_NAME:", utils=["bold"]), end=" ")
        print(Color.print_colored("{}".format(
            FILENAME), color_fg=[10, 20, 255]))

    print(Color.print_colored("INPUT_PATH:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(
        IMG_DIRPATH), color_fg=[10, 20, 255]))

    if DEBUG_MODE:
        print(Color.print_colored("USING DEBUG MODE", utils=["bold"]))

    if BATCH_MODE:
        print(Color.print_colored("USING BATCH MODE", utils=["bold"]))


def pipeline(data):
    img, partition, j, idx = data
    shape = getShape(img, partition, j)

    if len(shape) == 0:
        return []

    if DEBUG_MODE:
        save_image(shape, DEBUG_OUT_PATH, "shape{}.png".format(idx))

    return shape

def detection(mat, s):
    global DEBUG_OUT_PATH
    # Detection Process
    data = []
    idx = 0
    for i in range(len(s)):
        partition = s[i]
        for j in range(len(partition)):
            data.append([mat, partition, j, idx])
            idx += 1

    # create debug folder if not exist when debug mode is on
    if DEBUG_MODE:
        DEBUG_OUT_PATH = os.path.join(DEBUG_OUT_PATH_SHAPE.format(FILENAME))
        if not os.path.isdir(DEBUG_OUT_PATH):
            os.makedirs(DEBUG_OUT_PATH)

    # Process frames to images in parallel
    chunksize = len(data) // cpu_count()
    with Pool(cpu_count()) as pool:
        numbers = pool.map(pipeline, data, chunksize=chunksize)

    # filter images that has dimension lower than minimum dimension
    numbers = [num for num in numbers if len(num) > 0]
    numbers = np.array(numbers)

    # do prediction
    total_shapes = len(numbers)

    model = load_model()
    prediction_ = model.predict(numbers.reshape(total_shapes, 28, 28, 1))
    prediction = list(map(lambda x: np.argmax(x), prediction_))

    return prediction


def routine(img_path):
    assert os.path.isfile(
        img_path), "File not found in path specified: {}".format(img_path)

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
    result = detection(mat, s)

    return result


def normal_process(img_path, result):
    result.append(routine(img_path))


def batch_process(img_paths, result):
    global FILENAME
    for img_path, filename in img_paths:
        result.append(routine(img_path))
        FILENAME = filename


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(
            argv[1:], shortopts="hbdf:", longopts=["img-path="])
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
    
    from load import load_model
    from multiprocessing import Pool, cpu_count
    from c_interface import serializeArray_c, toMatrix, bbox_pipeline, thresh_pipeline
    from helper import *
    

    if not BATCH_MODE:
        assert FILENAME != "", "FILENAME must be specified. Run this with -f options"
        img_path = os.path.join(IMG_DIRPATH, FILENAME)
        result = []
        Loading.loading(process_fnc=normal_process, args=(img_path, result, ))
        print()
        result = result[0]
        print("Here is the result:")
        for i in range(len(result)):
            print(result[i], end=" ")
        print()

    else:
        assert os.path.isdir(IMG_DIRPATH), "Directory does not exist"
        results = []

        dir_list = os.listdir(IMG_DIRPATH)
        extension = list(map(lambda x: x.split(".")[-1], dir_list))
        img_list = [(os.path.join(IMG_DIRPATH, file), file) for (i, file) in enumerate(
            dir_list) if extension[i] == 'jpg' or extension[i] == 'png']
        print(img_list)
        Loading.loading(process_fnc=batch_process, args=(img_list, results))
        print()

        print("The results is:")
        for i, img_name in enumerate(img_list):
            prompt = Color.print_colored("{}: ".format(img_name), color_fg=[
                                         0, 255, 255], utils=["bold"])
            print(prompt, end="")
            for pred in results[i]:
                print(pred, end=" ")
            print()

    end_time = time()
    elapsed_time = (end_time - start_time)
    elapsed_time_h = elapsed_time // 3600
    elapsed_time_m = (elapsed_time % 3600) // 60
    elapsed_time_s = (elapsed_time % 3600) % 60

    prompt = Color.print_colored("Took about {:.2f} hours {:.2f} minutes {:.2f} seconds".format(
        elapsed_time_h, elapsed_time_m, elapsed_time_s), color_fg=[0, 255, 255], utils=["bold"])
    print(prompt)
