from src.main.outline import Outline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cv2
from ctypes import *

def print_images(pixels):
    f = open('test.txt', 'w')
    ny, nx = np.shape(pixels)
    print(ny, nx)
    for i in range(ny):
        line = ""
        for j in range(nx):
            line += "{:03d} ".format(pixels[i][j])
        f.write(line + '\n')
    f.close()

def to_txt(arr):
    a = ",".join(map(lambda x: str(x), arr.reshape(784, )))
    a = "{" + a + "}"
    with (open("test.txt", "w") as f):
        f.write(a)
    

# Loop Counter
SO_FILE_COUNTER = "src/libs/" + 'libcounter.so'
counter_c = CDLL(SO_FILE_COUNTER)
counter_c.python_loop_count.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
counter_c.python_loop_count.restypes = c_int

def loop_count_c(img, nx, ny):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 1), "Image must be serialized"
    
    try:
        cnt = counter_c.python_loop_count(img, nx, ny)
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined counter. Make sure to load counter_c library first before running this function\n")
        print("Make sure to defined the restype and argtype of python_loop_count")
        exit(-1)
        
    return cnt

i = 2
images = cv2.imread("mnist/images/train_images/number{}.png".format(i), 0)
to_txt(images)
df = pd.DataFrame(images)
print(df.to_string())

# plt.imshow(images, cmap='gray')
# plt.show()


# cnt = loop_count_c(arr, nx, ny)
# print(cnt)
# images = cv2.dilate(images, np.ones((3, 3), np.uint8))
# images_erode = cv2.erode(images, np.full((3, 3), -1))
# images = images_erode

outline = Outline(images)
cnt = outline.loop_count()
print(cnt)
# plt.imshow(res, cmap='gray')
# plt.show()

cnt = loop_count_c(images.reshape(1, -1)[0], 28, 28)
print(cnt)