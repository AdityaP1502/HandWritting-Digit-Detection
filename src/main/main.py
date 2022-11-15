import os.path
assert os.path.abspath(".").split("/")[-1] != "main", "run main.py from root folder"

from helper import *
from image import *
from c_interface import serializeArray_c, toMatrix, bbox_pipeline, thresh_pipeline
from loadingAnimation import *
import getopt
from sys import argv
from multiprocessing import Pool, cpu_count
from time import time

IMG_DIRPATH = IMG_DIRPATH_DEFAULT
FILENAME = ""

def showHelp():
  print("""Accepted Arguments:
          -h : show help screen
          -f : filename.
          --img-path=<image_path> : Frame input path. Use absolute path. Use this if image not in default location.
          """)

def showInfo():
    print(Color.print_colored("IMG_NAME:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(FILENAME), color_fg=[10, 20,255]))
    print(Color.print_colored("INPUT_PATH:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(IMG_DIRPATH), color_fg=[10, 20,255]))

def process(mat, s):
    # Detection Process
    data = []
    for i in range(len(s)):
        partition = s[i]
        for j in range(len(partition)):
            data.append([mat, partition, j])

    # Process frames to images in parallel
    chunksize = len(data) // cpu_count()
    with Pool(cpu_count()) as pool:
        numbers = pool.map(pipeline, data, chunksize=chunksize)

    numbers = np.array(numbers)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(argv[1:], shortopts="hf:", longopts=["img-path="])
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
    Loading.loading(process_fnc=process, args=(mat, s, ))
    print()
    end_time = time()
    elapsed_time = (end_time - start_time)
    elapsed_time_h = elapsed_time // 3600
    elapsed_time_m = (elapsed_time % 3600) // 60
    elapsed_time_s = (elapsed_time % 3600) % 60

    prompt = Color.print_colored("Finished processing in ", utils=["bold"]) + Color.print_colored("Took about {:.2f} hours {:.2f} minutes {:.2f} seconds".format(elapsed_time_h, elapsed_time_m, elapsed_time_s), color_fg=[0, 255, 255], utils=["bold"])
    print(prompt)