
from core.interface.loading_animation import Color, Loading
from core.io.path_handler import *


from sys import argv
from time import time

import conf.conf as conf
import getopt
import os.path
import os

assert os.path.abspath(".").split(
    "/")[-1] != "main", "run main.py from root folder"


def showHelp():
    print("""Accepted Arguments:
          -h : show help screen
          -f : filename. (Use this if -b is not specified)
          -d : enable debug mode. will save detected shape.
          -b :  enable batch mode. Will load picture from path given in --img-path
          --img-path=<image_path> : Frame input path. Use absolute path. Use this if image not in default location.
          """)


def showInfo():
    if not conf.BATCH_MODE:
        print(Color.print_colored("IMG_NAME:", utils=["bold"]), end=" ")
        print(Color.print_colored("{}".format(
            conf.FILENAME), color_fg=[10, 20, 255]))

    print(Color.print_colored("INPUT_PATH:", utils=["bold"]), end=" ")
    print(Color.print_colored("{}".format(
        conf.IMG_DIRPATH), color_fg=[10, 20, 255]))

    if conf.DEBUG_MODE:
        print(Color.print_colored("USING DEBUG MODE", utils=["bold"]))

    if conf.BATCH_MODE:
        print(Color.print_colored("USING BATCH MODE", utils=["bold"]))


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
            conf.FILENAME = arg

        if (opt == "-d"):
            conf.DEBUG_MODE = True

        if (opt == "--img-path"):
            # check path existance
            if (not PathHandler.check_path(arg)):
                raise FileNotFoundError("Directory not exist: {}".format(arg))
            conf.IMG_DIRPATH = arg

        if (opt == "-b"):
            conf.BATCH_MODE = True

    showInfo()
    start_time = time()
    print("[INFO] Importing Library. Please Wait!")
    from core.routine import *
    print("[DONE]")
    if not conf.BATCH_MODE:
        assert conf.FILENAME != "", "FILENAME must be specified. Run this with -f options"
        PathHandler.check_file(conf.FILENAME)
        result = [None]
        Loading.loading(process_fnc=routine_single_file, args=(result, ))
        result = result[0]

        if result == None:
            print("Error occured when detecting images. Exitting...")
            exit(-1)

        print("Here is the result:")
        for i in range(len(result)):
            print(result[i], end=" ")
        print()

    else:
        results = [None]

        Loading.loading(process_fnc=routine_batch_files, args=(results, ))
        results = results[0]

        if results == None:
            print("Error occured when detecting images. Exitting...")
            exit(-1)

        print("The results is:")
        for filename, result in results:
            prompt = Color.print_colored("{}: ".format(filename), color_fg=[
                                         0, 255, 255], utils=["bold"])
            print(prompt, end="")
            for pred in result:
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
