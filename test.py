from src.main.outline import Outline
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pandas as pd
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

# Struct
class dynArr(Structure):
    _fields_ = [
        ("arr", POINTER(c_void_p)), 
        ("end", c_int), 
        ("max", c_int), 
    ]

class Image(Structure):
  _fields_ = [
    ("img", POINTER(c_ubyte)), 
    ("nx", c_int), 
    ("ny", c_int), 
  ]

class Position(Structure):
   _fields_ = [
     ("x", c_uint32), 
     ("y", c_uint32), 
   ]

class Data(Structure):
  _fields_ = [
    ("object", POINTER(POINTER(POINTER(Position)))), 
    ("length", c_int)
  ]

SO_DIRPATH = "src/libs/"

# BBOX
SO_FILE_BBOX = SO_DIRPATH + 'libbbox.so'
bbox_c = CDLL(SO_FILE_BBOX)
bbox_c.python_bbox_find.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
bbox_c.python_bbox_find.restype = POINTER(Data)
bbox_c.get_shapes.argtypes = [POINTER(Image), POINTER(Data), c_int, c_int]
bbox_c.get_shapes.restype = POINTER(Image)
bbox_c.sortObjs.argtypes = [POINTER(Data)]
bbox_c.sortObjs.restypes = POINTER(dynArr)

# Loop Counter
SO_FILE_COUNTER = SO_DIRPATH + "libcounter.so"
counter_c = CDLL(SO_FILE_COUNTER)
counter_c.python_loop_count.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
counter_c.python_loop_count.restypes = c_int

# Image To Serial and Serial To Images
SO_FILE_IMAGES = SO_DIRPATH + 'libimage.so'
image_c = CDLL(SO_FILE_IMAGES)
image_c.image_to_serial.argtypes = [POINTER(POINTER(c_ubyte)), c_int, c_int]
image_c.image_to_serial.restype = POINTER(c_ubyte)
image_c.serial_to_image.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
image_c.serial_to_image.restype = POINTER(POINTER(c_ubyte))

def sortObjs(objs : Data):
    if not isinstance(objs, Data): 
        raise TypeError("objs must have type of Data, get {}".format(type(objs).__name__))
    try:
        partitions_ptr = bbox_c.sortObjs(byref(objs))
        partitions_ptr = (dynArr * 1).from_address(partitions_ptr)
        partition = partitions_ptr[0]
        print(type(partition))
    except Exception as e:
        print(e)
        exit(-1)

    print(partition.end)

def bbox_pipeline(img : np.ndarray, nx, ny):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 1), "Image must be serialized"

    #pixels_serialize = serializeArray(img, nx, ny)
  
    try:
        data_ptr = bbox_c.python_bbox_find(img, nx, ny)
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined bbox. Make sure to load bbox library first before running this function\n")
        print("Make sure to defined the restype and argtype of bbox_python_find")
        exit(-1)
  
    
    data : Data = data_ptr.contents
    arr_of_arr_of_pos_ptr = data.object
    arr_length = data.length
    objs = []
  
    for i in range(arr_length):
        arr_of_pos_ptr = arr_of_arr_of_pos_ptr[i]
        pos_min = arr_of_pos_ptr[0].contents
        pos_max = arr_of_pos_ptr[1].contents
    
        objs.append([[pos_min.y, pos_min.x], [pos_max.y, pos_max.x]])
    
    return objs, data_ptr
    #print(objs)
    #result = BoundingBox.createBoudingBox(img, objs)
    #showPicture(result, False)
    #plt.show()

def serializeArray_c(pixels, nx, ny):
    pixels_ptr = POINTER(c_ubyte) * ny
    temp = []
    for i in range(ny):
        temp.append(cast(np.ctypeslib.as_ctypes(pixels[i]), POINTER(c_ubyte)))
    
    pixels_ptr = cast(pixels_ptr(*temp), POINTER(POINTER(c_ubyte)))
    
    data_ptr = image_c.image_to_serial(pixels_ptr, nx, ny)
    return np.ctypeslib.as_array(data_ptr, (nx * ny,))

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

def serializeArray(pixels, nx, ny):
    total_pixels = nx * ny
    x = [0 for i in range(total_pixels)]
    for i in range(total_pixels):
        x[i] = pixels[i // nx][i % nx]
  
    return np.array(x, dtype=np.ubyte)

FILENAME = "301914"
images = cv2.imread("out/{}.jpg/frame_out.png".format(FILENAME))

images = cv2.cvtColor(images, cv2.COLOR_BGR2GRAY)

# df = pd.DataFrame(images)
# print(df.to_string())

plt.imshow(images, cmap='gray')
plt.show()

ny, nx = np.shape(images)
arr = serializeArray_c(images, nx, ny)
s, ptr = bbox_pipeline(arr, ny, nx)
sortObjs(ptr.contents)

# cnt = loop_count_c(arr, nx, ny)
# print(cnt)
# outline_s = Outline(images)
# vertexs = outline_s.findOutline()
# # for (i, vertex) in enumerate(vertexs):
# #     print('outline-{}'.format(i + 1))
# #     vertex.tranverseNode()

# print(len(vertexs) - 1)
# res = outline_s.makeOutline(vertexs)
# plt.imshow(res, cmap='gray')
# plt.show()